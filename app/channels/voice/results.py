"""Turn an ElevenLabs conversation result into `calls` + `communications` updates and a
("elevenlabs", "call_ended") event. Used by the post-call webhook and by the reconciliation
watcher (lost webhook, no answer, voicemail).
"""

import asyncio
import json
import logging

from psycopg.rows import dict_row

import httpx

from app import db
from app.channels.voice import elevenlabs
from app.config import settings
from app.worker import enqueue

log = logging.getLogger(__name__)

CALL_TIMEOUT_SECS = 8 * 60
EARLY_CHECKS_SECS = (90, 240)          # ask Twilio early: voicemail / no answer / trial prompt never acknowledged
TWILIO_TERMINAL = {"completed", "busy", "no-answer", "failed", "canceled"}
_watchers: set[asyncio.Task] = set()


async def twilio_call_status(call_sid: str) -> str | None:
    if not (settings.twilio_account_sid and settings.twilio_auth_token and call_sid):
        return None
    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Calls/{call_sid}.json"
    try:
        async with httpx.AsyncClient(timeout=15, auth=(settings.twilio_account_sid, settings.twilio_auth_token)) as http:
            r = await http.get(url)
            r.raise_for_status()
            return r.json().get("status")
    except Exception:
        log.exception("twilio status lookup failed for %s", call_sid)
        return None


def structured_result_from_payload(data: dict) -> dict:
    """Normalise the ElevenLabs analysis block into the shape workstream C consumes.

    Oral answers are provisional by construction: C stores them as insurer_oral / to_confirm.
    """
    analysis = data.get("analysis") or {}
    collected = analysis.get("data_collection_results") or {}
    transcript = data.get("transcript") or []
    user_turns = [t.get("message", "") for t in transcript if t.get("role") == "user" and t.get("message")]

    def entry(name: str) -> tuple:
        v = collected.get(name)
        if isinstance(v, dict):
            return v.get("value"), v.get("rationale")
        return v, None

    def field(name: str):
        return entry(name)[0]

    answers = []
    for i in range(1, 6):
        value, rationale = entry(f"answer_{i}")
        if value is None and rationale is None:
            continue
        answered = value not in (None, "", "null")
        answers.append({
            "question_index": i,
            "answered": answered,
            "answer_summary": str(value) if answered else None,
            "answer_verbatim": None,
            "rationale": rationale,            # why the analysis judged it answered / not answered
            "confidence": "medium" if answered else "none",
        })
    # Drop trailing unanswered slots beyond the questions that were actually asked.
    while answers and not answers[-1]["answered"] and len(answers) > 1 and not answers[-2]["answered"]:
        answers.pop()
    # Verbatim: pair each agent question (turn ending with "?") with the user turn that follows it,
    # skipping the opening "is now a good time" exchange, then align with the answered questions in order.
    qa_pairs = []
    for prev, nxt in zip(transcript, transcript[1:]):
        if prev.get("role") == "agent" and nxt.get("role") == "user" and (prev.get("message") or "").rstrip().endswith("?"):
            if "good time" in (prev.get("message") or "").lower():
                continue
            qa_pairs.append(nxt.get("message", ""))
    for ans, verbatim in zip([a for a in answers if a["answered"]], qa_pairs or user_turns[1:] or user_turns):
        ans["answer_verbatim"] = verbatim

    reached_flag = field("reached_human")
    reached_human = bool(user_turns) and reached_flag not in (False, "false", "False", "no")
    return {
        "reached_human": reached_human,
        "callback_requested": field("callback_requested") in (True, "true", "True", "yes"),
        "insurer_reference": field("insurer_reference") or None,
        "documents_requested": field("documents_requested") or None,
        "answers": answers,
        "summary": analysis.get("transcript_summary"),
        "call_successful": analysis.get("call_successful"),
        "raw_data_collection": collected,
    }


async def get_call_by_conversation(conversation_id: str) -> dict | None:
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT id, claim_id, account_id, status, provider_ref FROM calls WHERE provider_ref = %s", (conversation_id,))
            return await cur.fetchone()


async def finalize_call(call: dict, *, kind: str, data: dict, source: str) -> None:
    """Persist the outcome and emit call_ended exactly once per call."""
    conversation_id = call["provider_ref"]
    if kind == "call_initiation_failure":
        reason = data.get("failure_reason") or "unknown"
        structured = {"reached_human": False, "reason": reason, "answers": [], "summary": None}
        status, failure_reason, duration, transcript_text = "failed", reason, 0, None
    elif kind == "timeout":
        reason = data.get("reason") or "no_result_within_timeout"
        structured = {"reached_human": False, "reason": reason, "answers": [], "summary": None}
        status, failure_reason, duration, transcript_text = "failed", reason, data.get("duration_secs"), None
    else:
        transcript = data.get("transcript") or []
        transcript_text = "\n".join(f"{t.get('role')}: {t.get('message')}" for t in transcript if t.get("message")) or None
        structured = structured_result_from_payload(data)
        duration = (data.get("metadata") or {}).get("call_duration_secs")
        status = "completed" if structured["reached_human"] else "failed"
        failure_reason = None if structured["reached_human"] else "no_human_answer"

    async with db.pool.connection() as conn:
        updated = await conn.execute(
            """
            UPDATE calls SET status = %s, transcript = %s, result = %s, summary = %s, duration_secs = %s,
                             failure_reason = %s, ended_at = now(), confidence = 'oral_unconfirmed'
            WHERE id = %s AND status IN ('requested', 'in_progress')
            """,
            (status, transcript_text, json.dumps(structured), structured.get("summary"), duration, failure_reason, call["id"]),
        )
        if updated.rowcount == 0:
            await conn.rollback()
            log.info("call %s already finalized; ignoring %s from %s", call["id"], kind, source)
            return
        await conn.execute(
            "UPDATE communications SET delivery_status = %s, body = coalesce(%s, body) WHERE channel = 'phone' AND provider_ref = %s",
            (status, transcript_text, conversation_id),
        )
        await conn.commit()

    await enqueue(
        "elevenlabs", "call_ended",
        {"call_id": str(call["id"]), "transcript": transcript_text, "structured_result": structured, "status": status,
         "finalized_by": source, "provider_ref": f"elevenlabs:{conversation_id}:ended"},
        account_id=call["account_id"], claim_id=call["claim_id"],
    )


async def reconcile_call(call_id: str, *, final: bool = True) -> bool:
    """Finalize a call that got no webhook. Returns True if the call was finalized.

    Order: ElevenLabs conversation finished with content -> completed/failed on content;
    Twilio leg terminal but no conversation -> failed (voicemail, no answer, trial prompt not
    acknowledged); otherwise finalize as timeout only when `final`.
    """
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT id, claim_id, account_id, status, provider_ref, twilio_call_sid FROM calls WHERE id = %s", (call_id,))
            call = await cur.fetchone()
    if not call or call["status"] not in ("requested", "in_progress"):
        return False
    if not call["provider_ref"]:
        await finalize_call(call, kind="timeout", data={"reason": "never_started"}, source="watcher")
        return True

    convo: dict = {}
    try:
        convo = await elevenlabs.get_conversation(call["provider_ref"])
    except Exception:
        log.exception("could not fetch conversation %s for reconciliation", call["provider_ref"])
    has_content = bool(convo.get("transcript")) or bool((convo.get("analysis") or {}).get("transcript_summary"))
    if convo.get("status") in ("done", "failed") and has_content:
        await finalize_call(call, kind="post_call_transcription", data=convo, source="watcher")
        return True

    twilio_status = await twilio_call_status(call["twilio_call_sid"])
    if twilio_status in TWILIO_TERMINAL and not has_content:
        reason = "voicemail_or_no_answer" if twilio_status == "completed" else f"twilio_{twilio_status.replace('-', '_')}"
        await finalize_call(call, kind="timeout", data={"reason": reason}, source="watcher")
        return True

    if final:
        await finalize_call(call, kind="timeout", data={"reason": "no_result_within_timeout"}, source="watcher")
        return True
    return False


def watch_call(call_id: str, timeout: int = CALL_TIMEOUT_SECS) -> None:
    """Background safety net: early Twilio checks, then a hard timeout, if no webhook arrives."""

    async def _watch():
        elapsed = 0
        try:
            for t in EARLY_CHECKS_SECS:
                await asyncio.sleep(t - elapsed)
                elapsed = t
                if await reconcile_call(call_id, final=False):
                    return
            await asyncio.sleep(max(timeout - elapsed, 0))
            await reconcile_call(call_id, final=True)
        except Exception:
            log.exception("call watcher failed for %s", call_id)

    task = asyncio.create_task(_watch())
    _watchers.add(task)
    task.add_done_callback(_watchers.discard)


async def reconcile_stale_calls(older_than_secs: int = CALL_TIMEOUT_SECS) -> int:
    """Startup sweep: calls left in_progress by a previous process (restart) get reconciled."""
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT id FROM calls WHERE status IN ('requested','in_progress') AND created_at < now() - make_interval(secs => %s)",
                (older_than_secs,),
            )
            rows = await cur.fetchall()
    for r in rows:
        await reconcile_call(str(r["id"]))
    return len(rows)
