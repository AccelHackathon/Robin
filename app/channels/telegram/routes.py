"""Workstream C — Telegram webhook (production) ; long polling in dev lives in bot.py. Owned by C."""
from fastapi import APIRouter

router = APIRouter(prefix="/webhooks", tags=["telegram"])
