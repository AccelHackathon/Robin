"""Outbound tools: everything that leaves the system goes through the review gate first.

Adapters are owned by other streams (A: email/voice, C: telegram). When an adapter is not yet
available the communication is still recorded with delivery_status = 'pending_adapter' so the
flow is observable and nothing is silently lost.
"""

from __future__ import annotations

import logging
from typing import Any

from app import db
from app.agents.audit import timed_action
from app.agents.claims import memory as mem
from app.agents.review.gate import review
from app.contracts import CommId, OutboundDraft, ReviewContext, ReviewResult

log = logging.getLogger(__name__)
AGENT = "claims"


def build_context(claim_id: str, memory: dict[str, Any], draft: dict[str, Any]) -> ReviewContext:
    buckets = mem.amounts_for_review(memory)
    confirmed = [str(f["id"]) for f in memory["facts"] if f.get("status") == "confirmed"]
    return ReviewContext(
        claim_id=claim_id,
        evidence_amounts_eur=buckets["evidence"],
        derived_amounts_eur=buckets["derived"],
        client_instruction_amounts_eur=buckets["client_instruction"],
        confirmed_fact_ids=confirmed,
        cited_clause_ids=[int(c) for c, _ in draft.get("quotes", [])],
        loss_item_ids=draft.get("loss_item_ids", []),
        quotes=[(int(c), q) for c, q in draft.get("quotes", [])],
        fact_ids_used=draft.get("fact_ids_used", []),
    )


async def gate(claim_id: str, memory: dict[str, Any], draft: dict[str, Any]) -> ReviewResult:
    od = OutboundDraft(
        channel=draft["channel"], language=draft["language"], recipient_role=draft["recipient_role"],
        subject=draft.get("subject"), body=draft["body"], attachment_ids=draft.get("attachment_ids", []),
        amounts_eur=draft.get("amounts_eur", []),
    )
    return await review(od, build_context(claim_id, memory, draft))


async def _record_pending(account_id: str, claim_id: str, channel: str, to: str | None, subject: str | None, body: str,
                          attachments: list[str], language: str, reason: str) -> str:
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                """INSERT INTO communications (account_id, claim_id, channel, direction, counterpart, subject, body, attachments, delivery_status, failed_reason, language)
                   VALUES (%s,%s,%s,'outbound',%s,%s,%s,%s::uuid[],'pending_adapter',%s,%s) RETURNING id""",
                (account_id, claim_id, channel, to, subject, body, attachments or [], reason, language),
            )
        ).fetchone()
        await conn.commit()
    return str(row[0])


async def send_telegram(account_id: str, claim_id: str | None, text: str, document_ids: list[str] = ()) -> str:
    try:
        from app.channels.telegram.send import send_telegram as _send  # C's adapter (bot token required at runtime)

        return await _send(account_id=account_id, text=text, document_ids=list(document_ids), claim_id=claim_id)
    except ImportError:
        return await _record_pending(account_id, claim_id, "telegram", None, None, text, list(document_ids), "en", "telegram adapter unavailable")
    except Exception as exc:  # bot not configured, chat not linked, provider error
        log.warning("telegram send failed: %r", exc)
        return await _record_pending(account_id, claim_id, "telegram", None, None, text, list(document_ids), "en", repr(exc))


async def send_email(account_id: str, claim_id: str, to: str, subject: str, body: str, attachment_ids: list[str], language: str) -> str:
    try:
        from app.channels.email.send import send_email as _send  # workstream A

        return await _send(account_id=account_id, claim_id=claim_id, to=to, subject=subject, body=body,
                           attachment_document_ids=attachment_ids, language=language)
    except ImportError:
        return await _record_pending(account_id, claim_id, "email", to, subject, body, attachment_ids, language, "email adapter unavailable")
    except Exception as exc:
        log.warning("email send failed: %r", exc)
        return await _record_pending(account_id, claim_id, "email", to, subject, body, attachment_ids, language, repr(exc))


async def dispatch(claim_id: str, memory: dict[str, Any], draft: dict[str, Any]) -> CommId:
    """Send one gate-approved draft on its channel and record the action."""
    account_id = memory["account_id"]
    async with timed_action(AGENT, f"send_{draft['channel']}", {"purpose": draft.get("purpose"), "to": draft.get("to")}, claim_id=claim_id, account_id=account_id) as a:
        if draft["channel"] == "telegram":
            cid = await send_telegram(account_id, claim_id, draft["body"], draft.get("attachment_ids", []))
        elif draft["channel"] == "email":
            cid = await send_email(account_id, claim_id, draft["to"] or "", draft.get("subject") or "", draft["body"],
                                   draft.get("attachment_ids", []), draft.get("language", "fr"))
        else:
            cid = await _record_pending(account_id, claim_id, draft["channel"], draft.get("to"), draft.get("subject"), draft["body"],
                                        draft.get("attachment_ids", []), draft.get("language", "fr"), "channel has no adapter")
        a["result"] = {"communication_id": cid}
        return CommId(communication_id=cid)
