"""Claim memory: one dict read straight from the tables (no LangGraph Store needed).

Everything the prompts and nodes need about a claim, in one round trip set. Account isolation:
every query is keyed on the claim's account_id.
"""

from __future__ import annotations

from typing import Any

from psycopg.rows import dict_row

from app import db


async def _rows(conn, sql: str, params: tuple) -> list[dict[str, Any]]:
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(sql, params)
        return [dict(r) for r in await cur.fetchall()]


async def _one(conn, sql: str, params: tuple) -> dict[str, Any] | None:
    rows = await _rows(conn, sql, params)
    return rows[0] if rows else None


async def get_claim_memory(claim_id: str) -> dict[str, Any]:
    async with db.pool.connection() as conn:
        claim = await _one(conn, "SELECT * FROM claims WHERE id = %s", (claim_id,))
        if not claim:
            raise LookupError(f"claim {claim_id} not found")
        acct = str(claim["account_id"])
        business = await _one(conn, "SELECT * FROM businesses WHERE account_id = %s ORDER BY created_at DESC LIMIT 1", (acct,))
        mandate = await _one(conn, "SELECT * FROM mandates WHERE account_id = %s AND revoked_at IS NULL ORDER BY signed_at DESC NULLS LAST LIMIT 1", (acct,))
        contracts = await _rows(
            conn,
            """SELECT id, doc_type, filename, insurer_name, product_name, version_label, document_date, valid_from, valid_to, page_count
               FROM documents WHERE account_id = %s AND doc_type IN ('general_conditions','particular_conditions','endorsement','ipid')
               ORDER BY created_at""",
            (acct,),
        )
        # Latest version per guarantee (rows superseded by a newer row are hidden).
        coverage = await _rows(
            conn,
            """SELECT cp.* FROM coverage_profile cp
               WHERE cp.account_id = %s AND NOT EXISTS (SELECT 1 FROM coverage_profile n WHERE n.supersedes = cp.id)
               ORDER BY cp.guarantee""",
            (acct,),
        )
        levers = await _rows(
            conn,
            """SELECT l.* FROM contract_levers l JOIN documents d ON d.id = l.document_id
               WHERE d.account_id = %s OR l.account_id = %s ORDER BY l.kind""",
            (acct, acct),
        )
        facts = await _rows(
            conn,
            """SELECT f.* FROM facts f WHERE f.claim_id = %s AND NOT EXISTS (SELECT 1 FROM facts n WHERE n.supersedes = f.id)
               ORDER BY f.created_at""",
            (claim_id,),
        )
        evidence = await _rows(conn, "SELECT * FROM evidence WHERE claim_id = %s ORDER BY created_at", (claim_id,))
        loss_items = await _rows(
            conn,
            """SELECT li.* FROM loss_items li WHERE li.claim_id = %s AND NOT EXISTS (SELECT 1 FROM loss_items n WHERE n.supersedes = li.id)
               ORDER BY li.category, li.label""",
            (claim_id,),
        )
        communications = await _rows(
            conn, "SELECT * FROM communications WHERE claim_id = %s ORDER BY created_at DESC LIMIT 50", (claim_id,)
        )
        actions = await _rows(
            conn, "SELECT id, tool, arguments, ok, created_at FROM actions WHERE claim_id = %s ORDER BY created_at DESC LIMIT 50", (claim_id,)
        )
        deadlines = await _rows(conn, "SELECT * FROM scheduled_tasks WHERE claim_id = %s ORDER BY due_at", (claim_id,))
        offers = await _rows(conn, "SELECT * FROM offers WHERE claim_id = %s ORDER BY created_at DESC", (claim_id,))
        documents = await _rows(
            conn,
            "SELECT id, doc_type, origin, filename, mime_type, sha256, document_date, readable, created_at FROM documents WHERE claim_id = %s ORDER BY created_at",
            (claim_id,),
        )
        catalog = await _rows(conn, "SELECT * FROM loss_catalog ORDER BY category, key", ())
        riot = await _one(conn, "SELECT * FROM riot_events WHERE id = %s", (claim["riot_event_id"],)) if claim.get("riot_event_id") else None
        digest = await _one(conn, "SELECT * FROM claim_digest WHERE claim_id = %s", (claim_id,))

    from app.agents.claims.brain import profiles  # local import: brain depends on memory

    insurer_profile = await profiles.get((business or {}).get("insurer_name"))

    return {
        "digest": digest or {"narrative": None, "open_asks": [], "insurer_positions": [], "next_steps": [], "turn_count": 0},
        "insurer_profile": insurer_profile,
        "claim": claim, "account_id": acct, "business": business, "mandate": mandate, "contracts": contracts,
        "coverage": coverage, "levers": levers, "facts": facts, "evidence": evidence, "loss_items": loss_items,
        "communications": communications, "actions": actions, "deadlines": deadlines, "offers": offers,
        "documents": documents, "catalog": catalog, "riot_event": riot,
    }


def amounts_for_review(memory: dict[str, Any]) -> dict[str, list[float]]:
    """Split the claim's known amounts into the three traceable buckets the gate accepts."""
    evidence = [float(e["amount_eur"]) for e in memory["evidence"] if e.get("amount_eur") is not None and not e.get("duplicate_of")]
    derived, instructed = [], []
    for li in memory["loss_items"]:
        if li.get("amount_claimed_eur") is None:
            continue
        a = float(li["amount_claimed_eur"])
        if li.get("amount_basis") == "client_instruction":
            instructed.append(a)
        elif li.get("amount_basis") == "formula" and li.get("clause_id"):
            derived.append(a)
    for o in memory["offers"]:
        if o.get("total_eur") is not None:
            evidence.append(float(o["total_eur"]))  # the insurer's own figure is a documented fact
        for item in (o.get("breakdown") or []):
            if isinstance(item, dict) and item.get("amount_eur") is not None:
                evidence.append(float(item["amount_eur"]))
    for cov in memory["coverage"]:
        for key in ("ceiling", "deductible_detail"):
            v = (cov.get(key) or {}).get("amount") if isinstance(cov.get(key), dict) else None
            if v is not None and (cov.get(key) or {}).get("unit", "EUR") == "EUR":
                evidence.append(float(v))  # contractual caps/deductibles are cited figures, not agent inventions
    # The loss-statement total is a sum of traceable items: derived by construction.
    total = round(sum(float(li["amount_claimed_eur"]) for li in memory["loss_items"] if li.get("amount_claimed_eur") is not None), 2)
    if total:
        derived.append(total)
    return {"evidence": evidence, "derived": derived, "client_instruction": instructed}
