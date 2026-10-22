"""Running claim digest: the agent's own summary, read back every turn.

Deterministic core (open asks, next steps from scheduled tasks) + an optional model-written
narrative. The digest is what lets the agent say "I already have your invoice from Monday;
still missing the inventory you were asked for twice" instead of re-listing everything.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from psycopg.rows import dict_row

from app import db

log = logging.getLogger(__name__)

# What kind of evidence satisfies which requested item (lower-cased substrings).
SATISFIERS: dict[str, list[str]] = {
    "police_report": ["police", "plainte", "complaint", "récépissé"],
    "invoice": ["invoice", "facture", "supplier"],
    "inventory": ["inventory", "inventaire", "stock list"],
    "photo": ["photo", "picture"],
    "accounting": ["turnover", "tax return", "liasse", "accountant", "chiffre d'affaires", "margin"],
    "customer_items_list": ["customer", "client items", "devices in repair", "biens confiés"],
}


async def load(claim_id: str) -> dict[str, Any]:
    async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT * FROM claim_digest WHERE claim_id = %s", (claim_id,))
        row = await cur.fetchone()
    return dict(row) if row else {"claim_id": claim_id, "narrative": None, "open_asks": [], "insurer_positions": [], "next_steps": [], "turn_count": 0}


async def save(d: dict[str, Any]) -> None:
    async with db.pool.connection() as conn:
        await conn.execute(
            """INSERT INTO claim_digest (claim_id, narrative, open_asks, insurer_positions, next_steps, turn_count, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,now())
               ON CONFLICT (claim_id) DO UPDATE SET narrative = EXCLUDED.narrative, open_asks = EXCLUDED.open_asks,
                 insurer_positions = EXCLUDED.insurer_positions, next_steps = EXCLUDED.next_steps, turn_count = EXCLUDED.turn_count, updated_at = now()""",
            (d["claim_id"], d.get("narrative"), json.dumps(d.get("open_asks") or [], default=str), json.dumps(d.get("insurer_positions") or [], default=str),
             json.dumps(d.get("next_steps") or [], default=str), d.get("turn_count", 0)),
        )
        await conn.commit()


def record_asks(d: dict[str, Any], requested_items: list[str], now: datetime) -> None:
    asks = d.setdefault("open_asks", [])
    for item in requested_items:
        key = item.strip().lower()
        if not key:
            continue
        hit = next((a for a in asks if a["item"].lower() == key and not a.get("satisfied_at")), None)
        if hit:
            hit["times"] = int(hit.get("times", 1)) + 1
            hit["last_asked_at"] = now.isoformat()
        else:
            asks.append({"item": item.strip(), "asked_at": now.isoformat(), "last_asked_at": now.isoformat(), "times": 1, "satisfied_at": None})


def mark_satisfied(d: dict[str, Any], evidence_types: set[str], now: datetime) -> list[str]:
    """Close open asks that the evidence on file now satisfies. Returns the items closed this turn."""
    closed = []
    for a in d.get("open_asks", []):
        if a.get("satisfied_at"):
            continue
        needle = a["item"].lower()
        for etype, words in SATISFIERS.items():
            if etype in evidence_types and any(w in needle for w in words):
                a["satisfied_at"] = now.isoformat()
                closed.append(a["item"])
                break
    return closed


def open_asks(d: dict[str, Any]) -> list[dict[str, Any]]:
    return [a for a in d.get("open_asks", []) if not a.get("satisfied_at")]


def next_steps_from_tasks(deadlines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for t in deadlines:
        if t.get("status") in ("pending", "fired"):
            out.append({"step": t.get("reason") or t.get("kind"), "due": t["due_at"].isoformat() if t.get("due_at") else None,
                        "source": t.get("legal_basis") or (f"clause {t['source_clause_id']}" if t.get("source_clause_id") else "agent")})
    return out[:10]


def deterministic_narrative(memory: dict[str, Any], d: dict[str, Any]) -> str:
    c = memory["claim"]
    b = memory.get("business") or {}
    ev_types = sorted({e.get("evidence_type") for e in memory.get("evidence", []) if not e.get("duplicate_of")})
    items = [li for li in memory.get("loss_items", [])]
    supported = [li for li in items if li.get("status") in ("supported", "sent", "accepted", "partial")]
    total = sum(float(li["amount_claimed_eur"]) for li in items if li.get("amount_claimed_eur") is not None)
    offers = memory.get("offers", [])
    lines = [
        f"{b.get('name') or 'The business'} — {c.get('loss_type') or 'loss'} on {c.get('loss_date') or 'date to confirm'}. Status: {c.get('status')}.",
        f"Evidence on file: {', '.join(ev_types) if ev_types else 'none yet'}. Loss statement: {len(items)} item(s), {len(supported)} supported, total stated {total:,.0f} €.".replace(",", " "),
    ]
    oa = open_asks(d)
    if oa:
        lines.append("Still waiting from the client: " + "; ".join(f"{a['item']} (asked {a['times']}×)" for a in oa) + ".")
    if d.get("insurer_positions"):
        last = d["insurer_positions"][-1]
        lines.append(f"Last insurer position ({last.get('at', '')[:10]}, {last.get('channel')}): {last.get('position_verbatim', '')[:160]}")
    if offers:
        o = offers[0]
        lines.append(f"Offer on file: {o.get('total_eur')} € ({o.get('nature')}), release language: {o.get('has_release_language')}, decision: {o.get('client_decision') or 'pending'}.")
    return "\n".join(lines)


async def update_after_turn(claim_id: str, memory: dict[str, Any], drafts: list[dict[str, Any]], analysis: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    d = await load(claim_id)
    for dr in drafts:
        if dr.get("requested_items"):
            record_asks(d, dr["requested_items"], now)
    ev_types = {e.get("evidence_type") for e in memory.get("evidence", []) if not e.get("duplicate_of")}
    d["closed_this_turn"] = mark_satisfied(d, ev_types, now)
    d["next_steps"] = next_steps_from_tasks(memory.get("deadlines", []))
    d["turn_count"] = int(d.get("turn_count", 0)) + 1
    narrative = None
    try:
        from app.agents.claims.nodes import llm

        if llm.provider():
            narrative = await _llm_narrative(claim_id, memory, d, analysis)
    except Exception:
        log.exception("digest narrative failed; deterministic fallback")
    d["narrative"] = narrative or deterministic_narrative(memory, d)
    d.pop("closed_this_turn", None)
    await save(d)
    return d


DIGEST_SYSTEM = """You maintain the running digest of an insurance claim handled by a procedural assistant.
Write 5-8 short lines of plain facts: what happened, what documents are on file, what has been sent to the insurer and when,
what the insurer has stated (verbatim where available), what is still awaited from the client (with how many times it was asked),
and the next dated steps. No advice, no recommendations, no evaluation of chances, no qualifying words about people.
Return ONLY JSON: {"narrative": "..."}"""


async def _llm_narrative(claim_id: str, memory: dict[str, Any], d: dict[str, Any], analysis: dict[str, Any]) -> str | None:
    from app.agents.claims.nodes import llm

    snapshot = {
        "claim": {k: str(v) for k, v in memory["claim"].items() if k in ("loss_date", "loss_type", "status", "summary")},
        "business": (memory.get("business") or {}).get("name"),
        "evidence": [{"type": e.get("evidence_type"), "amount": float(e["amount_eur"]) if e.get("amount_eur") is not None else None, "vendor": e.get("vendor")}
                     for e in memory.get("evidence", []) if not e.get("duplicate_of")][:30],
        "loss_items": [{"label": li["label"], "amount": float(li["amount_claimed_eur"]) if li.get("amount_claimed_eur") is not None else None, "status": li.get("status"),
                        "cover": ((li.get("computation_detail") or {}).get("cover") or {}).get("status")} for li in memory.get("loss_items", [])][:40],
        "sent": [{"at": str(c.get("created_at"))[:16], "channel": c.get("channel"), "subject": c.get("subject"), "to": c.get("counterpart")}
                 for c in memory.get("communications", []) if c.get("direction") == "outbound"][:20],
        "open_asks": open_asks(d), "insurer_positions": d.get("insurer_positions", [])[-5:], "next_steps": d.get("next_steps", []),
        "this_turn": analysis.get("summary"), "previous_narrative": d.get("narrative"),
    }
    res = await llm.complete_json(DIGEST_SYSTEM, [{"type": "text", "text": json.dumps(snapshot, default=str)}], claim_id=claim_id, tool="claim_digest")
    return (res or {}).get("narrative")
