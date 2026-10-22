"""Thin async client for the ElevenLabs Agents endpoints we use."""

import hashlib
import hmac
import time

import httpx

from app.config import settings

BASE = "https://api.elevenlabs.io"


def _headers() -> dict[str, str]:
    if not settings.elevenlabs_api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")
    return {"xi-api-key": settings.elevenlabs_api_key}


async def outbound_call(*, agent_id: str, phone_number_id: str, to_number: str, dynamic_variables: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as http:
        r = await http.post(
            f"{BASE}/v1/convai/twilio/outbound-call",
            headers=_headers(),
            json={
                "agent_id": agent_id,
                "agent_phone_number_id": phone_number_id,
                "to_number": to_number,
                "conversation_initiation_client_data": {"dynamic_variables": dynamic_variables},
            },
        )
        r.raise_for_status()
        return r.json()


async def get_conversation(conversation_id: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as http:
        r = await http.get(f"{BASE}/v1/convai/conversations/{conversation_id}", headers=_headers())
        r.raise_for_status()
        return r.json()


async def create_agent(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=60) as http:
        r = await http.post(f"{BASE}/v1/convai/agents/create", headers=_headers(), json=payload)
        r.raise_for_status()
        return r.json()


async def update_agent(agent_id: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=60) as http:
        r = await http.patch(f"{BASE}/v1/convai/agents/{agent_id}", headers=_headers(), json=payload)
        r.raise_for_status()
        return r.json()


def verify_signature(raw_body: bytes, header: str | None, secret: str, tolerance_secs: int = 30 * 60) -> bool:
    """ElevenLabs-Signature: "t=<unix>,v0=<hex hmac-sha256(secret, f'{t}.{body}')>"."""
    if not header or not secret:
        return False
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    ts, sig = parts.get("t"), parts.get("v0")
    if not ts or not sig:
        return False
    try:
        if abs(time.time() - int(ts)) > tolerance_secs:
            return False
    except ValueError:
        return False
    expected = hmac.new(secret.encode(), f"{ts}.".encode() + raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)
