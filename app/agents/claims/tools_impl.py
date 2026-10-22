"""Database-backed tool implementations (PRD §5). Each call records an `actions` row.

Outbound tools (ask_client, send_email, request_insurer_document, present_offer) live in
`outbound.py` because they go through the review gate and cross-stream adapters.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from psycopg.rows import dict_row

from app import db
from app.agents.audit import timed_action
from app.agents.claims import memory as mem
from app.contracts import Clause, FactId, FactSource, LossItemInput, TaskId

AGENT = "claims"


async def get_claim_memory(claim_id: str) -> dict:
    async with timed_action(AGENT, "get_claim_memory", {"claim_id": claim_id}, claim_id=claim_id) as a:
        m = await mem.get_claim_memory(claim_id)
        a["result"] = {"facts": len(m["facts"]), "evidence": len(m["evidence"]), "loss_items": len(m["loss_items"])}
        return m


async def search_clauses(contract_id: str, query: str, k: int = 8) -> list[Clause]:
    async with timed_action(AGENT, "search_clauses", {"contract_id": contract_id, "query": query, "k": k}) as a:
        try:
            from app.ingestion.search import search_clauses as _b  # workstream B

            rows = await _b(contract_id, query, k)
            out = [r if isinstance(r, Clause) else Clause(**r) for r in rows]
        except (ImportError, AttributeError):
            async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """SELECT id, document_id, page, heading, body FROM clauses
                       WHERE document_id = %s AND tsv @@ websearch_to_tsquery('french', %s)
                       ORDER BY ts_rank(tsv, websearch_to_tsquery('french', %s)) DESC LIMIT %s""",
                    (contract_id, query, query, k),
                )
                out = [Clause(id=r["id"], document_id=str(r["document_id"]), page=r["page"], heading=r["heading"], body=r["body"]) for r in await cur.fetchall()]
        a["result"] = [{"id": c.id, "page": c.page} for c in out]
        return out


async def update_loss_statement(claim_id: str, items: list[LossItemInput]) -> list[dict]:
    """Insert a new version for each item; a same-label previous version is superseded, never overwritten."""
    async with timed_action(AGENT, "update_loss_statement", {"claim_id": claim_id, "items": [i.label for i in items]}, claim_id=claim_id) as a:
        stored: list[dict[str, Any]] = []
        async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            for it in items:
                await cur.execute(
                    """SELECT id, version FROM loss_items WHERE claim_id = %s AND lower(label) = lower(%s)
                       AND NOT EXISTS (SELECT 1 FROM loss_items n WHERE n.supersedes = loss_items.id)
                       ORDER BY version DESC LIMIT 1""",
                    (claim_id, it.label),
                )
                prev = await cur.fetchone()
                await cur.execute(
                    """INSERT INTO loss_items (claim_id, label, category, amount_claimed_eur, computation, evidence_ids, clause_id, clause_page,
                                               clause_quote, condition_note, status, version, supersedes, amount_basis, computation_detail, catalog_key)
                       VALUES (%s,%s,%s,%s,%s,%s::uuid[],%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
                    (claim_id, it.label, it.category, it.amount_claimed_eur, it.computation, it.evidence_ids or [], it.clause_id, it.clause_page,
                     it.clause_quote, it.condition_note, it.status, (prev["version"] + 1) if prev else 1, prev["id"] if prev else None,
                     it.amount_basis, json.dumps(it.computation_detail) if it.computation_detail else None, it.catalog_key),
                )
                stored.append(dict(await cur.fetchone()))
            await conn.commit()
        a["result"] = [{"id": str(r["id"]), "label": r["label"], "version": r["version"]} for r in stored]
        return stored


async def log_fact(claim_id: str, text: str, source: FactSource, confidence: str, supersedes: str | None = None,
                   status: str | None = None) -> FactId:
    status = status or ("to_confirm" if source in ("insurer_oral", "agent_inference") else "confirmed")
    async with timed_action(AGENT, "log_fact", {"claim_id": claim_id, "source": source, "status": status}, claim_id=claim_id) as a:
        async with db.pool.connection() as conn:
            row = await (
                await conn.execute(
                    "INSERT INTO facts (claim_id, statement, source, source_kind, confidence, status, supersedes) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    (claim_id, text, source, source, confidence, status, supersedes),
                )
            ).fetchone()
            await conn.commit()
        a["result"] = {"fact_id": str(row[0])}
        return FactId(fact_id=str(row[0]))


async def schedule_followup(claim_id: str, when: datetime, reason: str, source_clause_id: int | None = None) -> TaskId:
    return await register_deadline(claim_id, "insurer_followup", when, source_clause_id, None, reason=reason)


async def register_deadline(claim_id: str, kind: str, due_at: datetime, source_clause_id: int | None, legal_basis: str | None = None,
                            *, reason: str | None = None) -> TaskId:
    async with timed_action(AGENT, "register_deadline", {"claim_id": claim_id, "kind": kind, "due_at": due_at.isoformat()}, claim_id=claim_id) as a:
        async with db.pool.connection() as conn:
            existing = await (
                await conn.execute(
                    "SELECT id FROM scheduled_tasks WHERE claim_id = %s AND kind = %s AND due_at = %s AND status = 'pending'",
                    (claim_id, kind, due_at),
                )
            ).fetchone()
            if existing:
                a["result"] = {"task_id": str(existing[0]), "deduplicated": True}
                return TaskId(task_id=str(existing[0]))
            row = await (
                await conn.execute(
                    """INSERT INTO scheduled_tasks (claim_id, due_at, reason, status, kind, source_clause_id, legal_basis)
                       VALUES (%s,%s,%s,'pending',%s,%s,%s) RETURNING id""",
                    (claim_id, due_at, reason or kind, kind, source_clause_id, legal_basis),
                )
            ).fetchone()
            await conn.commit()
        a["result"] = {"task_id": str(row[0])}
        return TaskId(task_id=str(row[0]))


async def add_evidence(claim_id: str, *, document_id: str | None, evidence_type: str, amount_eur: float | None, issued_on: str | None,
                       vendor: str | None, description: str | None, extracted: dict | None, sha256: str | None) -> dict:
    """Insert an evidence row with duplicate detection: sha256 first, then (amount, date, vendor)."""
    async with timed_action(AGENT, "add_evidence", {"claim_id": claim_id, "type": evidence_type, "amount": amount_eur}, claim_id=claim_id) as a:
        async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
            dup = None
            if sha256:
                await cur.execute(
                    """SELECT e.id FROM evidence e JOIN documents d ON d.id = e.document_id
                       WHERE e.claim_id = %s AND d.sha256 = %s AND e.duplicate_of IS NULL ORDER BY e.created_at LIMIT 1""",
                    (claim_id, sha256),
                )
                dup = await cur.fetchone()
            if not dup and amount_eur is not None and issued_on and vendor:
                await cur.execute(
                    """SELECT id FROM evidence WHERE claim_id = %s AND amount_eur = %s AND issued_on = %s AND lower(vendor) = lower(%s)
                       AND duplicate_of IS NULL ORDER BY created_at LIMIT 1""",
                    (claim_id, amount_eur, issued_on, vendor),
                )
                dup = await cur.fetchone()
            await cur.execute(
                """INSERT INTO evidence (claim_id, document_id, evidence_type, amount_eur, issued_on, vendor, description, extracted, duplicate_of)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
                (claim_id, document_id, evidence_type, amount_eur, issued_on, vendor, description, json.dumps(extracted or {}), dup["id"] if dup else None),
            )
            row = dict(await cur.fetchone())
            await conn.commit()
        a["result"] = {"evidence_id": str(row["id"]), "duplicate_of": str(row["duplicate_of"]) if row["duplicate_of"] else None}
        return row
