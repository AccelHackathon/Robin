"""Workstream A — AgentMail inbound webhook. Owned by A."""
from fastapi import APIRouter

router = APIRouter(prefix="/webhooks", tags=["email"])
