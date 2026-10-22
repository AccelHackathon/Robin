"""Workstream A — ElevenLabs post-call webhook, browser widget fallback, internal call trigger."""

import html
import json
import logging

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

from app import db
from app.channels.voice import elevenlabs
from app.channels.voice.call import build_dynamic_variables, start_call
from app.channels.voice.results import finalize_call, get_call_by_conversation
from app.config import settings

log = logging.getLogger(__name__)
router = APIRouter(tags=["voice"])


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
    if not conversation_id or kind == "post_call_audio":
        return {"received": True, "ignored": kind}

    call = await get_call_by_conversation(conversation_id)
    if not call:
        log.warning("post-call webhook for unknown conversation %s", conversation_id)
        return {"received": True, "ignored": "unknown conversation"}

    await finalize_call(call, kind=kind, data=data, source="webhook")
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
    attr = html.escape(json.dumps(variables), quote=True)
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Robin — voice session (simulated insurer line)</title>
<style>body{{font-family:system-ui;margin:3rem;max-width:720px}} .tag{{background:#fde68a;padding:.2rem .5rem;border-radius:.3rem;font-size:.8rem}}</style></head>
<body><span class="tag">SIMULATED INSURER LINE — browser widget, no telephony</span>
<h1>Robin is calling the claims department</h1>
<p><b>Goal:</b> {html.escape(variables['call_goal'])}</p><pre>{html.escape(variables['questions'])}</pre>
<elevenlabs-convai agent-id="{html.escape(settings.elevenlabs_agent_id or '')}" dynamic-variables="{attr}"></elevenlabs-convai>
<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>
</body></html>"""


# --- internal trigger (operators / rehearsal) --------------------------------------------------

class StartCallRequest(BaseModel):
    claim_id: str
    to_number: str | None = None
    goal: str
    questions: list[str] = Field(min_length=1, max_length=5)
    brief: dict = Field(default_factory=dict)


@router.post("/internal/calls")
async def internal_start_call(body: StartCallRequest, authorization: str | None = Header(default=None)):
    """Start a call for an existing claim. Protected by INTERNAL_API_TOKEN (bearer). Used for rehearsals
    and by operators; the Claims Agent uses the `start_call` tool directly."""
    if not settings.internal_api_token or authorization != f"Bearer {settings.internal_api_token}":
        raise HTTPException(status_code=401)
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT c.id, c.account_id, c.loss_date, c.summary, b.name AS business_name, b.insurer_name
                FROM claims c LEFT JOIN businesses b ON b.account_id = c.account_id
                WHERE c.id = %s
                """,
                (body.claim_id,),
            )
            claim = await cur.fetchone()
    if not claim:
        raise HTTPException(status_code=404, detail="unknown claim")
    to_number = body.to_number or settings.insurer_test_phone
    if not to_number:
        raise HTTPException(status_code=400, detail="no destination number")
    brief = {
        "business_name": claim["business_name"], "insurer_name": claim["insurer_name"],
        "claim_ref": f"RB-{str(claim['id'])[:8]}", "loss_date": str(claim["loss_date"] or ""),
        "loss_summary": claim["summary"] or "", **body.brief,
    }
    call_id = await start_call(account_id=str(claim["account_id"]), claim_id=str(claim["id"]), to_number=to_number,
                               goal=body.goal, questions=body.questions, brief=brief)
    return {"call_id": call_id, "widget_url": f"{settings.public_base_url or ''}/voice/widget/{call_id}"}
