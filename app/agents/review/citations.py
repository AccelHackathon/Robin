"""Citation verification (PRD 2.7 control 2).

A quote attributed to a clause must actually appear in that clause's body. Workstream B owns
`app.ingestion.search.verify_quote`; until it lands we use the same contract here so the gate
is testable. Whitespace-normalised, case-insensitive similarity >= 0.9.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from app import db

SIMILARITY_THRESHOLD = 0.9


def normalise(s: str) -> str:
    s = s.replace("’", "'").replace("œ", "oe")
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_in_body(quote: str, body: str) -> bool:
    q, b = normalise(quote), normalise(body)
    if not q:
        return False
    if q in b:
        return True
    # Tolerate OCR / line-break noise: best window of the same length.
    if len(q) > len(b):
        return SequenceMatcher(None, q, b).ratio() >= SIMILARITY_THRESHOLD
    best = 0.0
    step = max(1, len(q) // 4)
    for i in range(0, len(b) - len(q) + 1, step):
        r = SequenceMatcher(None, q, b[i : i + len(q)]).ratio()
        if r > best:
            best = r
            if best >= SIMILARITY_THRESHOLD:
                return True
    return best >= SIMILARITY_THRESHOLD


async def verify_quote(clause_id: int, quote: str) -> bool:
    try:
        from app.ingestion.search import verify_quote as _b_verify  # workstream B, when available

        return await _b_verify(clause_id, quote)
    except (ImportError, AttributeError):
        pass
    if db.pool is None:
        return False
    async with db.pool.connection() as conn:
        row = await (await conn.execute("SELECT body FROM clauses WHERE id = %s", (clause_id,))).fetchone()
    return bool(row) and quote_in_body(quote, row[0])


async def clause_exists(clause_id: int) -> bool:
    if db.pool is None:
        return False
    async with db.pool.connection() as conn:
        row = await (await conn.execute("SELECT 1 FROM clauses WHERE id = %s", (clause_id,))).fetchone()
    return row is not None
