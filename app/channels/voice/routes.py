"""Workstream A — ElevenLabs post-call webhook and the browser widget fallback."""

import json
import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from psycopg.rows import dict_row

from app import db
from app.channels.voice import elevenlabs
from app.channels.voice.call import build_dynamic_variables
from app.config import settings
from app.worker import enqueue

log = logging.getLogger(__name__)
router = APIRouter(tags=["voice"])


def structured_result_from_payload(data: dict) -> dict:
    """Normalise the ElevenLabs analysis block into the shape workstream C consumes.

    Per question: {question, answer_verbatim, answer_summary, confidence}; plus reached_human,
    callback_requested, insurer_reference, summary. Oral answers are provisional by construction:
    C stores them as insurer_oral / to_confirm.
    """
    analysis = data.get("analysis") or {}
    collected = analysis.get("data_collection_results") or {}
    transcript = data.get("transcript") or []
    user_turns = [t.get("message", "") for t in transcript if t.get("role") == "user" and t.get("message")]

    def field(name: str):
        v = collected.get(name)
        if isinstance(v, dict):
            return v.get("value")
        return v

    answers = []
    for i in range(1, 6):
        summary = field(f"answer_{i}")
        if summary in (None, "", "null"):
            continue
        answers.append({
            "question_index": i,
            "answer_summary": str(summary),
            "answer_verbatim": None,   # filled below from the transcript when we can match it
            "confidence": "medium",
        })
    # best-effort verbatim: align the i-th user turn with the i-th answer
    for ans, verbatim in zip(answers, user_turns):
        ans["answer_verbatim"] = verbatim

    return {
        "reached_human": bool(user_turns) and field("reached_human") not in (False, "false", "no"),
        "callback_requested": field("callback_requested") in (True, "true", "yes"),
        "insurer_reference": field("insurer_reference") or None,
        "answers": answers,
        "summary": analysis.get("transcript_summary"),
        "call_successful": analysis.get("call_successful"),
        "raw_data_collection": collected,
    }


@router.post("/webhooks/elevenlabs")
async def elevenlabs_webhook(request: Request):
    raw = await request.body()
    if settings.elevenlabs_webhook_secret:
        if not elevenlabs.verify_signature(raw, request.headers.get("elevenlabs-signature"), settings.elevenlabs_webhook_secret):
            raise HTTPException(status_code=401, detail="invalid signature")
    else:
        log.warning("ELEVENLABS_WEBHOOK_SECRET not set; accepting unsigned webhook")

    event = json.loads(raw)
    kind = event.get("type")
    data = event.get("data") or {}
    conversation_id = data.get("conversation_id")
    if not conversation_id:
        return {"received": True, "ignored": "no conversation_id"}

    if kind == "post_call_audio":
        return {"received": True, "ignored": "audio"}

    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT id, claim_id, account_id FROM calls WHERE provider_ref = %s", (conversation_id,))
            call = await cur.fetchone()
    if not call:
        log.warning("post-call webhook for unknown conversation %s", conversation_id)
        return {"received": True, "ignored": "unknown conversation"}

    transcript_text = None
    structured: dict
    if kind == "call_initiation_failure":
        reason = data.get("failure_reason") or "unknown"
        structured = {"reached_human": False, "reason": reason, "answers": [], "summary": None}
        status, failure_reason, duration = "failed", reason, 0
    else:  # post_call_transcription
        transcript = data.get("transcript") or []
        transcript_text = "\n".join(f"{t.get('role')}: {t.get('message')}" for t in transcript if t.get("message"))
        structured = structured_result_from_payload(data)
        meta = data.get("metadata") or {}
        duration = meta.get("call_duration_secs")
        status = "completed" if structured["reached_human"] else "failed"
        failure_reason = None if structured["reached_human"] else "no_human_answer"

    async with db.pool.connection() as conn:
        await conn.execute(
            """
            UPDATE calls SET status = %s, transcript = %s, result = %s, summary = %s, duration_secs = %s,
                             failure_reason = %s, ended_at = now(), confidence = 'oral_unconfirmed'
            WHERE id = %s
            """,
            (status, transcript_text, json.dumps(structured), structured.get("summary"), duration, failure_reason, call["id"]),
        )
        await conn.execute(
            "UPDATE communications SET delivery_status = %s, body = coalesce(%s, body) WHERE channel = 'phone' AND provider_ref = %s",
            (status, transcript_text, conversation_id),
        )
        await conn.commit()

    await enqueue(
        "elevenlabs", "call_ended",
        {
            "call_id": str(call["id"]),
            "transcript": transcript_text,
            "structured_result": structured,
            "status": status,
            "provider_ref": f"elevenlabs:{conversation_id}:{kind}",
        },
        account_id=call["account_id"], claim_id=call["claim_id"],
    )
    return {"received": True}


@router.get("/voice/widget/{call_id}", response_class=HTMLResponse)
async def voice_widget(call_id: str):
    """Browser fallback: the 'insurer' answers from a web page instead of a phone (no telephony)."""
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT goal, questions, brief FROM calls WHERE id = %s", (call_id,))
            call = await cur.fetchone()
    if not call:
        raise HTTPException(status_code=404)
    variables = build_dynamic_variables(brief=call["brief"], goal=call["goal"], questions=call["questions"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Robin — voice session (simulated insurer line)</title>
<style>body{{font-family:system-ui;margin:3rem;max-width:720px}} .tag{{background:#fde68a;padding:.2rem .5rem;border-radius:.3rem;font-size:.8rem}}</style></head>
<body><span class="tag">SIMULATED INSURER LINE — browser widget, no telephony</span>
<h1>Robin is calling the claims department</h1>
<p><b>Goal:</b> {variables['call_goal']}</p><pre>{variables['questions']}</pre>
<elevenlabs-convai agent-id="{settings.elevenlabs_agent_id}" dynamic-variables='{json.dumps(variables)}'></elevenlabs-convai>
<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>
</body></html>"""
