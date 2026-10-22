"""Cross-claim memory about insurers: what Robin has observed across every file with the same insurer.

Updated from outcomes (first reply delay, first offer vs documented total, documents requested,
release language), idempotent per (claim, metric). Read at triage so the digest and the client
message can state, factually, "across N files with this insurer the first reply took on average
X hours" — an observation, never a prediction or advice.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from psycopg.rows import dict_row

from app import db

log = logging.getLogger(__name__)


async def get(insurer_name: str | None) -> dict[str, Any] | None:
    if not insurer_name or db.pool is None:
        return None
    async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM insurer_profiles WHERE lower(insurer_name) = lower(%s)", (insurer_name,))
        row = await cur.fetchone()
    if not row:
        return None
    p = dict(row)
    p["avg_first_reply_hours"] = round(float(p["first_reply_hours_sum"]) / p["first_reply_count"], 1) if p["first_reply_count"] else None
    p["avg_first_offer_ratio"] = round(float(p["first_offer_ratio_sum"]) / p["first_offer_count"], 2) if p["first_offer_count"] else None
    return p


async def _mark(conn, claim_id: str, metric: str) -> bool:
    row = await (await conn.execute(
        "INSERT INTO insurer_profile_marks (claim_id, metric) VALUES (%s, %s) ON CONFLICT DO NOTHING RETURNING claim_id", (claim_id, metric))).fetchone()
    return row is not None


async def _ensure(conn, insurer: str) -> None:
    await conn.execute("INSERT INTO insurer_profiles (insurer_name, claims_count) VALUES (%s, 0) ON CONFLICT DO NOTHING", (insurer,))


async def on_claim_opened(claim_id: str, insurer: str | None) -> None:
    if not insurer:
        return
    async with db.pool.connection() as conn:
        if await _mark(conn, claim_id, "opened"):
            await _ensure(conn, insurer)
            await conn.execute("UPDATE insurer_profiles SET claims_count = claims_count + 1, updated_at = now() WHERE insurer_name = %s", (insurer,))
        await conn.commit()


async def on_first_insurer_reply(claim_id: str, insurer: str | None) -> None:
    """Hours between the first outbound email to the insurer and the first inbound reply."""
    if not insurer:
        return
    async with db.pool.connection() as conn:
        row = await (await conn.execute(
            """SELECT EXTRACT(EPOCH FROM (min(i.created_at) - min(o.created_at))) / 3600.0
               FROM communications o JOIN communications i ON i.claim_id = o.claim_id
               WHERE o.claim_id = %s AND o.channel = 'email' AND o.direction = 'outbound'
                 AND i.channel = 'email' AND i.direction = 'inbound'""", (claim_id,))).fetchone()
        hours = float(row[0]) if row and row[0] is not None else None
        if hours is not None and hours >= 0 and await _mark(conn, claim_id, "first_reply"):
            await _ensure(conn, insurer)
            await conn.execute(
                "UPDATE insurer_profiles SET first_reply_hours_sum = first_reply_hours_sum + %s, first_reply_count = first_reply_count + 1, updated_at = now() WHERE insurer_name = %s",
                (hours, insurer))
        await conn.commit()


async def on_first_offer(claim_id: str, insurer: str | None, offer_total: float | None, documented_total: float | None, has_release: bool) -> None:
    if not insurer:
        return
    async with db.pool.connection() as conn:
        if await _mark(conn, claim_id, "first_offer"):
            await _ensure(conn, insurer)
            if offer_total is not None and documented_total:
                await conn.execute(
                    "UPDATE insurer_profiles SET first_offer_ratio_sum = first_offer_ratio_sum + %s, first_offer_count = first_offer_count + 1 WHERE insurer_name = %s",
                    (offer_total / documented_total, insurer))
            if has_release:
                await conn.execute("UPDATE insurer_profiles SET release_language_count = release_language_count + 1 WHERE insurer_name = %s", (insurer,))
            await conn.execute("UPDATE insurer_profiles SET updated_at = now() WHERE insurer_name = %s", (insurer,))
        await conn.commit()


async def on_documents_requested(claim_id: str, insurer: str | None, kinds: list[str]) -> None:
    if not insurer or not kinds:
        return
    async with db.pool.connection() as conn:
        await _ensure(conn, insurer)
        for k in kinds:
            await conn.execute(
                """UPDATE insurer_profiles SET documents_requested = jsonb_set(documents_requested, ARRAY[%s], to_jsonb(coalesce((documents_requested->>%s)::int, 0) + 1)), updated_at = now()
                   WHERE insurer_name = %s""", (k, k, insurer))
        await conn.commit()


def describe(p: dict[str, Any] | None) -> str | None:
    """One factual sentence for the client, or None if there is nothing observed yet."""
    if not p or p.get("claims_count", 0) < 2:
        return None
    parts = [f"Across {p['claims_count']} files handled with {p['insurer_name']}"]
    if p.get("avg_first_reply_hours") is not None:
        parts.append(f"the first written reply took on average {p['avg_first_reply_hours']} h")
    if p.get("avg_first_offer_ratio") is not None:
        parts.append(f"the first offer averaged {round(100 * p['avg_first_offer_ratio'])}% of the documented statement")
    docs = sorted((p.get("documents_requested") or {}).items(), key=lambda kv: -kv[1])[:3]
    if docs:
        parts.append("documents most often requested: " + ", ".join(k.replace("_", " ") for k, _ in docs))
    return "; ".join(parts) + "."
