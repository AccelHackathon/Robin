from fastapi import APIRouter

from app import db
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health():
    db_ok = await db.ping()
    return {
        "status": "ok",
        "db": "ok" if db_ok else "unavailable",
        "commit": settings.git_commit,
        "integrations": {
            "anthropic": bool(settings.anthropic_api_key),
            "telegram": bool(settings.telegram_bot_token),
            "agentmail": bool(settings.agentmail_api_key),
            "elevenlabs": bool(settings.elevenlabs_api_key),
        },
    }
