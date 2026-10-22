"""Voice note transcription. ElevenLabs Scribe if its key is set, else OpenAI Whisper, else None."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

log = logging.getLogger(__name__)


async def transcribe(data: bytes, filename: str, mime: str) -> str | None:
    if settings.elevenlabs_api_key:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    "https://api.elevenlabs.io/v1/speech-to-text",
                    headers={"xi-api-key": settings.elevenlabs_api_key},
                    data={"model_id": "scribe_v1"},
                    files={"file": (filename, data, mime)},
                )
                r.raise_for_status()
                return (r.json().get("text") or "").strip() or None
        except Exception:
            log.exception("ElevenLabs transcription failed")
    if settings.openai_api_key:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    data={"model": "whisper-1"},
                    files={"file": (filename, data, mime)},
                )
                r.raise_for_status()
                return (r.json().get("text") or "").strip() or None
        except Exception:
            log.exception("OpenAI transcription failed")
    return None
