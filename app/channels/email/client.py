"""AgentMail client accessor (workstream A)."""

from functools import lru_cache

from agentmail import AsyncAgentMail

from app.config import settings


@lru_cache(maxsize=1)
def agentmail() -> AsyncAgentMail:
    if not settings.agentmail_api_key:
        raise RuntimeError("AGENTMAIL_API_KEY is not set")
    return AsyncAgentMail(api_key=settings.agentmail_api_key)


def claim_tag(claim_id: str | None) -> str:
    """Subject tag that lets the inbound webhook route a reply to its claim."""
    return f"[RB-{str(claim_id)[:8]}]" if claim_id else ""
