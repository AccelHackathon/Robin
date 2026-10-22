"""Inbound Telegram media → `documents` rows (origin = telegram, sha256 set)."""

from __future__ import annotations

import hashlib
import logging

from telegram import Bot, Message

from app import db

log = logging.getLogger(__name__)


def _pick(message: Message) -> tuple[str | None, str | None, str | None]:
    """(file_id, mime_type, filename) for the richest attachment on the message."""
    if message.document:
        return message.document.file_id, message.document.mime_type, message.document.file_name
    if message.photo:
        best = max(message.photo, key=lambda p: (p.width or 0) * (p.height or 0))
        return best.file_id, "image/jpeg", f"photo_{best.file_unique_id}.jpg"
    if message.voice:
        return message.voice.file_id, message.voice.mime_type or "audio/ogg", f"voice_{message.voice.file_unique_id}.oga"
    if message.audio:
        return message.audio.file_id, message.audio.mime_type, message.audio.file_name or f"audio_{message.audio.file_unique_id}"
    if message.video:
        return message.video.file_id, message.video.mime_type, message.video.file_name or f"video_{message.video.file_unique_id}.mp4"
    return None, None, None


async def store_document(bot: Bot, message: Message, account_id: str, *, doc_type: str = "other") -> dict | None:
    file_id, mime, filename = _pick(message)
    if not file_id:
        return None
    tg_file = await bot.get_file(file_id)
    data = bytes(await tg_file.download_as_bytearray())
    sha = hashlib.sha256(data).hexdigest()
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                """INSERT INTO documents (account_id, doc_type, origin, filename, mime_type, sha256, content, metadata)
                   VALUES (%s, %s, 'telegram', %s, %s, %s, %s, %s::jsonb) RETURNING id""",
                (account_id, doc_type, filename, mime, sha, data,
                 f'{{"telegram_file_id": "{file_id}", "message_id": {message.message_id}, "caption": {_json_str(message.caption)}}}'),
            )
        ).fetchone()
        await conn.commit()
    return {"document_id": str(row[0]), "mime_type": mime, "filename": filename, "sha256": sha, "size": len(data)}


def _json_str(s: str | None) -> str:
    import json

    return json.dumps(s)


async def set_extracted_text(document_id: str, text: str) -> None:
    async with db.pool.connection() as conn:
        await conn.execute("UPDATE documents SET extracted_text = %s WHERE id = %s", (text, document_id))
        await conn.commit()
