"""Full-text lookup; private clauses require explicit account context."""

import re
from difflib import SequenceMatcher
from psycopg.rows import dict_row
from app import db
from app.contracts import Clause


def quote_matches(body: str, quote: str) -> bool:
    body, quote = " ".join(body.split()), " ".join(quote.split())
    if len(quote) < 12:
        return False
    if quote in body:
        return True
    # Fuzzy matching is restricted to a similarly-sized source window, not a whole page.
    words, target = body.split(), quote.split()
    for i in range(max(0, len(words) - len(target) + 1)):
        candidate = " ".join(words[i : i + len(target)])
        if re.findall(r"\d+", candidate) != re.findall(r"\d+", quote):
            continue
        if SequenceMatcher(None, candidate, quote).ratio() >= 0.9:
            return True
    return False


async def search_clauses(
    document_id: str, query: str, k: int = 8, *, account_id: str | None = None
) -> list[Clause]:
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """SELECT c.id,c.document_id,c.page,c.heading,c.body FROM clauses c
                JOIN documents d ON d.id=c.document_id
                WHERE c.document_id=%s AND (d.account_id IS NULL OR d.account_id=%s)
                AND c.tsv @@ websearch_to_tsquery('french', %s)
                ORDER BY ts_rank(c.tsv,websearch_to_tsquery('french',%s)) DESC,c.page,c.id LIMIT %s""",
                (document_id, account_id, query, query, max(1, min(k, 30))),
            )
            return [
                Clause(**{**r, "document_id": str(r["document_id"])})
                for r in await cur.fetchall()
            ]


async def verify_quote(
    clause_id: int, quote: str, *, account_id: str | None = None
) -> bool:
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                """SELECT c.body FROM clauses c JOIN documents d ON d.id=c.document_id
            WHERE c.id=%s AND (d.account_id IS NULL OR d.account_id=%s)""",
                (clause_id, account_id),
            )
        ).fetchone()
    return bool(row and quote_matches(row[0], quote))
