"""Telegram ↔ account linking (README "Database handoffs": B creates `link_codes`, C consumes them).

Never link on a phone number alone: the only path is a one-time code from the website,
consumed within its expiry window.
"""

from __future__ import annotations

from psycopg.rows import dict_row

from app import db


def parse_start_code(text: str | None) -> str | None:
    """`/start ABC123` → `ABC123`; `/start` alone → None."""
    if not text:
        return None
    parts = text.strip().split(maxsplit=1)
    if not parts or parts[0].split("@")[0] != "/start" or len(parts) < 2:
        return None
    code = parts[1].strip()
    return code or None


async def account_for_chat(chat_id: int) -> str | None:
    async with db.pool.connection() as conn:
        row = await (await conn.execute("SELECT account_id FROM telegram_links WHERE chat_id = %s", (chat_id,))).fetchone()
    return str(row[0]) if row else None


async def chat_for_account(account_id: str) -> int | None:
    async with db.pool.connection() as conn:
        row = await (await conn.execute("SELECT chat_id FROM telegram_links WHERE account_id = %s ORDER BY linked_at DESC LIMIT 1", (account_id,))).fetchone()
    return int(row[0]) if row else None


async def consume_link_code(code: str, chat_id: int, username: str | None) -> str | None:
    """Mark the code used and link the chat. Returns account_id, or None if the code is invalid/expired/used."""
    async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            """UPDATE link_codes SET used_at = now()
               WHERE code = %s AND used_at IS NULL AND (expires_at IS NULL OR expires_at > now())
               RETURNING account_id""",
            (code,),
        )
        row = await cur.fetchone()
        if not row:
            await conn.rollback()
            return None
        account_id = str(row["account_id"])
        await cur.execute(
            """INSERT INTO telegram_links (chat_id, account_id, username, linked_at) VALUES (%s, %s, %s, now())
               ON CONFLICT (chat_id) DO UPDATE SET account_id = EXCLUDED.account_id, username = EXCLUDED.username, linked_at = now()""",
            (chat_id, account_id, username),
        )
        await conn.commit()
    return account_id
