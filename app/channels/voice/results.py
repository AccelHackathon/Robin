"""Turn an ElevenLabs conversation result into `calls` + `communications` updates and a
("elevenlabs", "call_ended") event. Used by the post-call webhook and by the reconciliation
watcher (lost webhook, no answer, voicemail).
"""

import asyncio
import json
import logging

from psycopg.rows import dict_row

from app import db
from app.channels.voice import elevenlabs
from app.worker import enqueue

log = logging.getLogger(__name__)

CALL_TIMEOUT_SECS = 8 * 60
_watchers: set[asyncio.Task] = set()


def structured_result_from_payload(data: dict) -> dict:
    """Normalise the ElevenLabs analysis block into the shape workstream C consumes.

    Oral answers are provisional by construction: C stores them as insurer_oral / to_confirm.
    """
    analysis = data.get("analysis") or {}
    collected = analysis.get("data_collection_results") or {}
    transcript = data.get("transcript") or []
    user_turns = [t.get("message", "") for t in transcript if t.get("role") == "user" and t.get("message")]

    def field(name: str):
        v = collected.get(name)
        return v.get("value") if isinstance(v, dict) else v

    answers = []
    for i in range(1, 6):
        summary = field(f"answer_{i}")
        if summary in (None, "", "null"):
            continue
        answers.append({"question_index": i, "answer_summary": str(summary), "answer_verbatim": None, "confidence": "medium"})
    for ans, verbatim in zip(answers, user_turns):
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
        structured = {"reached_human": False, "reason": "no_result_within_timeout", "answers": [], "summary": None}
        status, failure_reason, duration, transcript_text = "failed", "no_result_within_timeout", None, None
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


async def reconcile_call(call_id: str) -> None:
    """Fetch the conversation from ElevenLabs and finalize it; used when no webhook arrived."""
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT id, claim_id, account_id, status, provider_ref FROM calls WHERE id = %s", (call_id,))
            call = await cur.fetchone()
    if not call or call["status"] not in ("requested", "in_progress"):
        return
    if not call["provider_ref"]:
        await finalize_call(call, kind="timeout", data={}, source="watcher")
        return
    try:
        convo = await elevenlabs.get_conversation(call["provider_ref"])
    except Exception:
        log.exception("could not fetch conversation %s for reconciliation", call["provider_ref"])
        convo = {}
    if convo.get("status") in ("done", "failed") and (convo.get("transcript") or convo.get("analysis")):
        await finalize_call(call, kind="post_call_transcription", data=convo, source="watcher")
    else:
        await finalize_call(call, kind="timeout", data={}, source="watcher")


def watch_call(call_id: str, timeout: int = CALL_TIMEOUT_SECS) -> None:
    """Background safety net: finalize the call if no webhook arrives within `timeout` seconds."""

    async def _watch():
        await asyncio.sleep(timeout)
        try:
            await reconcile_call(call_id)
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
