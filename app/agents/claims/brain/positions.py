"""Insurer position ledger (public-adjuster discipline, research 09b §5).

Every position the insurer takes — in an email or on the phone — is captured verbatim, dated,
attributed and stored twice: on the communication row (`insurer_position_verbatim`) and in the
claim digest (`insurer_positions`). The agent reads the ledger back when it writes to the
insurer and when it presents an offer ("on 22/10 by phone you stated X; your written offer says Y").
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from app import db
from app.agents.claims.brain import digest as D

log = logging.getLogger(__name__)

POSITION_SYSTEM = """From this message written or spoken by an insurer's claims department, extract every *position* it takes:
a statement about cover, a cap, a deductible, a refusal, a condition, a document it requires, a deadline, or an amount.
Return ONLY JSON: {"positions": [{"topic": "cover|cap|deductible|refusal|condition|document_request|deadline|amount|other",
"position_verbatim": "exact words, in the original language", "summary_en": "one line", "who": "name/role if stated or null"}]}
Do not add anything the message does not say."""

_FALLBACK_RE = re.compile(r"([^.\n]*(?:plafond|franchise|garantie|exclu|refus|sous réserve|pièce|justificatif|délai|indemnit|offre|cap|deductible|cover|excluded)[^.\n]*[.\n])", re.IGNORECASE)


async def _extract(text: str, claim_id: str) -> list[dict[str, Any]]:
    try:
        from app.agents.claims.nodes import llm

        if llm.provider():
            res = await llm.complete_json(POSITION_SYSTEM, [{"type": "text", "text": text[:8000]}], claim_id=claim_id, tool="extract_positions")
            if res and isinstance(res.get("positions"), list):
                return [p for p in res["positions"] if p.get("position_verbatim")]
    except Exception:
        log.exception("position extraction failed; regex fallback")
    return [{"topic": "other", "position_verbatim": m.group(1).strip(), "summary_en": None, "who": None} for m in _FALLBACK_RE.finditer(text)][:8]


async def record(claim_id: str, *, channel: str, text: str, communication_id: str | None = None, who: str | None = None,
                 at: datetime | None = None) -> list[dict[str, Any]]:
    at = at or datetime.now(timezone.utc)
    positions = await _extract(text, claim_id)
    if not positions:
        return []
    entries = [{"at": at.isoformat(), "channel": channel, "who": p.get("who") or who, "topic": p.get("topic"),
                "position_verbatim": p["position_verbatim"], "summary_en": p.get("summary_en"), "communication_id": communication_id,
                "status": "oral_to_confirm" if channel == "phone" else "written"} for p in positions]
    d = await D.load(claim_id)
    d.setdefault("insurer_positions", []).extend(entries)
    await D.save(d)
    if communication_id:
        async with db.pool.connection() as conn:
            await conn.execute("UPDATE communications SET insurer_position_verbatim = %s WHERE id = %s",
                               (" | ".join(p["position_verbatim"] for p in positions), communication_id))
            await conn.commit()
    return entries


def contradictions(positions: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Pairs (oral, written) on the same topic — surfaced factually when presenting an offer."""
    out = []
    oral = [p for p in positions if p.get("status") == "oral_to_confirm"]
    written = [p for p in positions if p.get("status") == "written"]
    for o in oral:
        for w in written:
            if o.get("topic") == w.get("topic") and o.get("topic") in ("cover", "cap", "deductible", "refusal", "amount") \
                    and o.get("position_verbatim", "").strip().lower() != w.get("position_verbatim", "").strip().lower():
                out.append((o, w))
    return out[:5]
