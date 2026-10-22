"""Workstream C — worker handlers that route events into the Claims Agent graph.

Routing (docs/workstreams/README.md "Event queue"):
  telegram/message|document        → the account's open claim, or a new claim
  agentmail/email_received         → the claim resolved by A (claim_id) — only for mailbox role `agent`
  elevenlabs/call_ended            → the claim on the event
  scheduler/followup_due           → the claim on the event

If the claim's thread is parked on an interrupt the event resumes it; otherwise it starts the thread.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from psycopg.rows import dict_row

from app import db
from app.agents.claims import graph as G
from app.worker import handles

log = logging.getLogger(__name__)

OPEN_STATUSES = ("open", "awaiting_client", "awaiting_insurer_email", "awaiting_call_result", "awaiting_followup", "awaiting_signature_decision")


def _event_dict(event: dict[str, Any]) -> dict[str, Any]:
    return {"source": event["source"], "kind": event["kind"], "account_id": str(event["account_id"]) if event.get("account_id") else None,
            "claim_id": str(event["claim_id"]) if event.get("claim_id") else None, "payload": event.get("payload") or {},
            "received_at": (event.get("created_at") or datetime.now(timezone.utc)).isoformat(), "event_id": event.get("id")}


async def _open_claim_for(account_id: str) -> str | None:
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                "SELECT id FROM claims WHERE account_id = %s AND status = ANY(%s) ORDER BY created_at DESC LIMIT 1",
                (account_id, list(OPEN_STATUSES)),
            )
        ).fetchone()
    return str(row[0]) if row else None


async def _match_riot_event(loss_date) -> str | None:
    if not loss_date:
        return None
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                "SELECT id FROM riot_events WHERE started_at::date <= %s AND coalesce(ended_at, started_at + interval '2 days')::date >= %s LIMIT 1",
                (loss_date, loss_date),
            )
        ).fetchone()
    return str(row[0]) if row else None


async def create_claim(account_id: str, summary: str | None, loss_date=None, loss_type: str | None = None) -> str:
    riot_id = await _match_riot_event(loss_date)
    async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "INSERT INTO claims (account_id, status, loss_date, loss_type, summary, riot_event_id) VALUES (%s,'open',%s,%s,%s,%s) RETURNING id",
            (account_id, loss_date, loss_type, (summary or "")[:500] or None, riot_id),
        )
        row = await cur.fetchone()
        await conn.commit()
    claim_id = str(row["id"])
    try:
        from app.deadlines.instantiate import instantiate_for_claim  # C4

        await instantiate_for_claim(claim_id)
    except ImportError:
        pass
    except Exception:
        log.exception("deadline instantiation failed for claim %s", claim_id)
    return claim_id


async def _run(claim_id: str, event: dict[str, Any]) -> None:
    try:
        G.graph()
    except RuntimeError:
        log.warning("claims graph not available; event %s for claim %s left unprocessed", event.get("id"), claim_id)
        return
    await G.run_event(claim_id, _event_dict(event))


@handles("telegram", "message")
@handles("telegram", "document")
async def on_client_input(event: dict[str, Any]) -> None:
    account_id = str(event.get("account_id") or event.get("payload", {}).get("account_id") or "")
    if not account_id:
        log.warning("telegram event %s without account_id (unlinked chat?) — ignored", event.get("id"))
        return
    claim_id = event.get("claim_id") and str(event["claim_id"]) or await _open_claim_for(account_id)
    if not claim_id:
        text = (event.get("payload") or {}).get("text") or (event.get("payload") or {}).get("caption")
        claim_id = await create_claim(account_id, text)
        log.info("new claim %s for account %s", claim_id, account_id)
    await _run(claim_id, event)


@handles("agentmail", "email_received")
async def on_email(event: dict[str, Any]) -> None:
    p = event.get("payload") or {}
    if p.get("mailbox_role", "agent") != "agent":
        return  # the simulator (workstream A) handles its own mailbox
    claim_id = event.get("claim_id") and str(event["claim_id"])
    if not claim_id and event.get("account_id"):
        claim_id = await _open_claim_for(str(event["account_id"]))
    if not claim_id:
        log.warning("email event %s could not be matched to a claim", event.get("id"))
        return
    await _run(claim_id, event)


@handles("elevenlabs", "call_ended")
@handles("scheduler", "followup_due")
async def on_claim_event(event: dict[str, Any]) -> None:
    claim_id = event.get("claim_id") and str(event["claim_id"])
    if not claim_id:
        log.warning("%s/%s event %s without claim_id", event.get("source"), event.get("kind"), event.get("id"))
        return
    await _run(claim_id, event)
