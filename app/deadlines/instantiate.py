"""Deadline machine, database part: instantiate `scheduled_tasks` for a claim (idempotent per kind+due)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, time, timezone
from typing import Any

from psycopg.rows import dict_row

from app import db
from app.agents.audit import record_action
from app.deadlines import rules as R

log = logging.getLogger(__name__)


async def _claim_context(claim_id: str) -> dict[str, Any] | None:
    async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT c.*, r.name AS riot_name, r.declaration_deadline_days, r.state_claim_deadline FROM claims c LEFT JOIN riot_events r ON r.id = c.riot_event_id WHERE c.id = %s", (claim_id,))
        claim = await cur.fetchone()
        if not claim:
            return None
        await cur.execute("SELECT kind, source_clause_id, page, quote, rule FROM deadline_rules WHERE account_id = %s ORDER BY created_at", (claim["account_id"],))
        rules = [dict(r) for r in await cur.fetchall()]
        await cur.execute("SELECT min(created_at) FROM communications WHERE claim_id = %s AND channel = 'email' AND direction = 'outbound'", (claim_id,))
        declared = (await cur.fetchone())["min"]
        await cur.execute("SELECT min(decided_at) FROM offers WHERE claim_id = %s AND client_decision = 'accept'", (claim_id,))
        agreed = (await cur.fetchone())["min"]
    return {"claim": dict(claim), "rules": rules, "declared_at": declared, "agreement_at": agreed}


async def instantiate_for_claim(claim_id: str, *, now: datetime | None = None) -> list[dict[str, Any]]:
    ctx = await _claim_context(claim_id)
    if not ctx:
        return []
    claim = ctx["claim"]
    loss_date = claim.get("loss_date")
    if not loss_date:
        return []  # dated from the loss; re-run once the narrative gives a date
    loss_at = datetime.combine(loss_date, time(12, 0), tzinfo=timezone.utc)
    riot = {"name": claim.get("riot_name"), "declaration_deadline_days": claim.get("declaration_deadline_days"), "state_claim_deadline": claim.get("state_claim_deadline")} \
        if claim.get("riot_event_id") else None
    tasks = R.plan(loss_at=loss_at, loss_type=claim.get("loss_type"), contract_rules=ctx["rules"], riot_event=riot,
                   declared_at=ctx["declared_at"], agreement_at=ctx["agreement_at"], now=now)
    created = []
    async with db.pool.connection() as conn:
        for t in tasks:
            row = await (await conn.execute(
                """INSERT INTO scheduled_tasks (claim_id, due_at, reason, status, kind, source_clause_id, legal_basis)
                   SELECT %s, %s, %s, 'pending', %s, %s, %s
                   WHERE NOT EXISTS (SELECT 1 FROM scheduled_tasks WHERE claim_id = %s AND kind = %s AND status IN ('pending','fired','done'))
                   RETURNING id""",
                (claim_id, t.due_at, t.reason, t.kind, t.source_clause_id, t.legal_basis, claim_id, t.kind))).fetchone()
            if row:
                created.append({"id": str(row[0]), "kind": t.kind, "due_at": t.due_at.isoformat()})
        # Mark past-due pending tasks as missed (informational), never delete them.
        await conn.execute("UPDATE scheduled_tasks SET missed_at = now() WHERE claim_id = %s AND status = 'pending' AND due_at < now() AND missed_at IS NULL", (claim_id,))
        await conn.commit()
    await record_action("claims", "instantiate_deadlines", {"claim_id": claim_id, "rules": len(ctx["rules"])}, {"created": created}, claim_id=claim_id)
    return created
