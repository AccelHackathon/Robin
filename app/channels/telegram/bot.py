"""Telegram bot (python-telegram-bot). Handlers only enqueue; the worker does the work.

Dev: long polling (`TELEGRAM_MODE=polling`), started from the app lifespan.
Prod: webhook `POST /webhooks/telegram/<token>` (routes.py), set via `setWebhook` at startup
when `PUBLIC_BASE_URL` is set.
"""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from app import db
from app.channels.telegram import links, media, transcribe
from app.config import settings
from app.worker import enqueue

log = logging.getLogger(__name__)

_application: Application | None = None

NOT_LINKED = ("This chat is not linked to a Robin account yet. Please finish the onboarding on the website and tap "
              "\"Open Telegram\" there — the link carries a one-time code that connects this chat to your file.")
LINK_INVALID = "This link code is invalid, already used or expired. Please generate a new one from the website."


def application() -> Application:
    if _application is None:
        raise RuntimeError("telegram application not built (TELEGRAM_BOT_TOKEN missing?)")
    return _application


def build() -> Application | None:
    global _application
    if not settings.telegram_bot_token:
        log.warning("TELEGRAM_BOT_TOKEN not set; Telegram channel disabled")
        return None
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r"^/start"), on_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL | filters.VOICE | filters.AUDIO | filters.VIDEO, on_media))
    _application = app
    return app


async def start_polling() -> None:
    app = application()
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=False)
    log.info("telegram long polling started")


async def start_webhook() -> None:
    app = application()
    await app.initialize()
    await app.start()
    url = f"{settings.public_base_url.rstrip('/')}/webhooks/telegram/{settings.telegram_bot_token}"
    await app.bot.set_webhook(url=url, drop_pending_updates=False, allowed_updates=["message"])
    log.info("telegram webhook set")


async def stop() -> None:
    if _application is None:
        return
    try:
        if _application.updater and _application.updater.running:
            await _application.updater.stop()
        if _application.running:
            await _application.stop()
        await _application.shutdown()
    except Exception:
        log.exception("telegram shutdown error")


# --- update handlers ----------------------------------------------------------------------------

def _ref(update: Update) -> str:
    return f"tg:{update.effective_chat.id}:{update.effective_message.message_id}"


async def _welcome_text(account_id: str) -> str:
    try:
        from app.agents.intake.brief import write_welcome_brief  # workstream B

        text = await write_welcome_brief(account_id)
        if text:
            return text
    except Exception:
        pass
    # Fallback until B's brief exists: a short factual welcome built from what is already in the profile.
    async with db.pool.connection() as conn:
        rows = await (
            await conn.execute(
                """SELECT guarantee, subscribed, page FROM coverage_profile cp WHERE account_id = %s
                   AND NOT EXISTS (SELECT 1 FROM coverage_profile n WHERE n.supersedes = cp.id) AND subscribed = 'yes' ORDER BY guarantee LIMIT 12""",
                (account_id,),
            )
        ).fetchall()
    covers = ", ".join(f"{g.replace('_', ' ')}{f' (p. {p})' if p else ''}" for g, _, p in rows)
    lines = ["Hi! Your account is linked. You can message me here whenever you need help, and send photos or documents about your claim."]
    if covers:
        lines.append(f"From your policy documents, covers I found as subscribed: {covers}.")
    lines.append("If something happens: tell me what happened, when and where, and send photos — I will declare it the same day.")
    return "\n".join(lines)


async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    chat_id = update.effective_chat.id
    code = links.parse_start_code(msg.text)
    if not code:
        linked = await links.account_for_chat(chat_id)
        await msg.reply_text("You're linked — just write to me." if linked else NOT_LINKED)
        return
    account_id = await links.consume_link_code(code, chat_id, update.effective_user.username if update.effective_user else None)
    if not account_id:
        await msg.reply_text(LINK_INVALID)
        return
    text = await _welcome_text(account_id)
    sent = await msg.reply_text(text)
    async with db.pool.connection() as conn:
        await conn.execute(
            "INSERT INTO communications (account_id, channel, direction, counterpart, body, provider_ref, delivery_status, language) VALUES (%s,'telegram','outbound',%s,%s,%s,'sent','en')",
            (account_id, str(chat_id), text, f"tg:{chat_id}:{sent.message_id}"),
        )
        await conn.commit()
    log.info("telegram chat %s linked to account %s", chat_id, account_id)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg, chat_id = update.effective_message, update.effective_chat.id
    account_id = await links.account_for_chat(chat_id)
    if not account_id:
        await msg.reply_text(NOT_LINKED)
        return
    await enqueue("telegram", "message", {"account_id": account_id, "chat_id": chat_id, "text": msg.text, "provider_ref": _ref(update)}, account_id=account_id)


async def on_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg, chat_id = update.effective_message, update.effective_chat.id
    account_id = await links.account_for_chat(chat_id)
    if not account_id:
        await msg.reply_text(NOT_LINKED)
        return
    stored = await media.store_document(context.bot, msg, account_id)
    if not stored:
        return
    if msg.voice or msg.audio:
        async with db.pool.connection() as conn:
            row = await (await conn.execute("SELECT content FROM documents WHERE id = %s", (stored["document_id"],))).fetchone()
        text = await transcribe.transcribe(bytes(row[0]), stored["filename"] or "voice.oga", stored["mime_type"] or "audio/ogg")
        if text:
            await media.set_extracted_text(stored["document_id"], text)
            await enqueue("telegram", "message", {"account_id": account_id, "chat_id": chat_id, "text": text, "document_id": stored["document_id"],
                                                  "provider_ref": _ref(update)}, account_id=account_id)
        else:
            await msg.reply_text("I received your voice note but couldn't transcribe it. Could you type the key points?")
        return
    await enqueue("telegram", "document", {"account_id": account_id, "chat_id": chat_id, "document_id": stored["document_id"], "mime_type": stored["mime_type"],
                                           "caption": msg.caption, "provider_ref": _ref(update)}, account_id=account_id)
