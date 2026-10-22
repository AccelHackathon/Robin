"""Workstream C — Telegram webhook (production). The bot token is the URL secret."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from telegram import Update

from app.channels.telegram import bot as tg
from app.config import settings

log = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["telegram"])


@router.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request):
    if not settings.telegram_bot_token or token != settings.telegram_bot_token:
        raise HTTPException(status_code=404)
    try:
        app = tg.application()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="telegram not configured")
    data = await request.json()
    update = Update.de_json(data, app.bot)
    # Handlers only enqueue, so processing inline stays well under the 1 s budget.
    await app.process_update(update)
    return {"ok": True}
