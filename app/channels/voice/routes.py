"""Workstream A — ElevenLabs post-call webhook and voice endpoints. Owned by A."""
from fastapi import APIRouter

router = APIRouter(prefix="/webhooks", tags=["voice"])
