"""Outbound Telegram adapter (README signature). Writes `communications`, returns its id.

Rate limit: 30 messages per chat per 10 minutes (PRD §9).
"""

from __future__ import annotations

import io

from app import db
from app.channels.telegram import bot as tg
from app.channels.telegram import links

RATE_LIMIT = 30
RATE_WINDOW_MINUTES = 10


class RateLimited(RuntimeError):
    pass


async def _recent_count(account_id: str) -> int:
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                "SELECT count(*) FROM communications WHERE account_id = %s AND channel = 'telegram' AND direction = 'outbound' AND created_at > now() - make_interval(mins => %s)",
                (account_id, RATE_WINDOW_MINUTES),
            )
        ).fetchone()
    return int(row[0])


async def send_telegram(*, account_id: str, text: str, document_ids: list[str] = (), claim_id: str | None = None) -> str:
    chat_id = await links.chat_for_account(account_id)
    if chat_id is None:
        raise RuntimeError(f"account {account_id} has no linked Telegram chat")
    if await _recent_count(account_id) >= RATE_LIMIT:
        raise RateLimited(f"more than {RATE_LIMIT} messages in {RATE_WINDOW_MINUTES} minutes for account {account_id}")
    bot = tg.application().bot
    sent = await bot.send_message(chat_id=chat_id, text=text)
    for doc_id in document_ids:
        async with db.pool.connection() as conn:
            row = await (await conn.execute("SELECT filename, content FROM documents WHERE id = %s AND account_id = %s", (doc_id, account_id))).fetchone()
        if row:
            await bot.send_document(chat_id=chat_id, document=io.BytesIO(bytes(row[1])), filename=row[0] or "document")
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                """INSERT INTO communications (account_id, claim_id, channel, direction, counterpart, body, attachments, provider_ref, delivery_status, language)
                   VALUES (%s,%s,'telegram','outbound',%s,%s,%s::uuid[],%s,'sent','en') RETURNING id""",
                (account_id, claim_id, str(chat_id), text, list(document_ids), f"tg:{chat_id}:{sent.message_id}"),
            )
        ).fetchone()
        await conn.commit()
    return str(row[0])
