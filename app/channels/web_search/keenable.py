"""Keenable web search and page fetch (workstream D). HTTP API, authenticated with X-API-Key.

    hits = await search("vigilance orange grêle Bouches-du-Rhône", published_after="48h")
    page = await fetch(url, prompt="Extract date, time, place and perimeter of the event")

Every call is recorded in `actions` (agent "sentinel") with the Keenable usage block so the cost
of monitoring is measurable per account.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import httpx

from app.agents.audit import record_action
from app.config import settings

log = logging.getLogger(__name__)

BASE = "https://api.keenable.ai/v1"


@dataclass
class Hit:
    url: str
    title: str
    snippet: str
    published_at: str | None
    site: str | None


def available() -> bool:
    return bool(settings.keenable_api_key)


def _headers() -> dict[str, str]:
    if not settings.keenable_api_key:
        raise RuntimeError("KEENABLE_API_KEY is not set")
    return {"X-API-Key": settings.keenable_api_key, "Content-Type": "application/json"}


def _hit(r: dict) -> Hit:
    return Hit(
        url=r.get("url", ""),
        title=r.get("title") or "",
        snippet=r.get("description") or r.get("snippet") or "",
        published_at=r.get("published_at") or r.get("published") or None,
        site=r.get("site") or (r.get("url", "").split("/")[2] if "://" in r.get("url", "") else None),
    )


async def search(query: str, *, published_after: str | None = None, site: str | None = None,
                 max_results: int = 8, mode: str | None = None, account_id: str | None = None) -> list[Hit]:
    body: dict = {"query": query, "mode": mode or settings.keenable_search_mode, "max_results": max_results,
                  "snippet_max_length": 600}
    if published_after:
        body["published_after"] = published_after
    if site:
        body["site"] = site
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=40) as http:
            r = await http.post(f"{BASE}/search", headers=_headers(), json=body)
            r.raise_for_status()
            data = r.json()
    except Exception as exc:
        await record_action("sentinel", "search_web", body, {"error": repr(exc)}, ok=False, account_id=account_id,
                            latency_ms=int((time.perf_counter() - started) * 1000))
        raise
    hits = [_hit(x) for x in data.get("results", [])]
    await record_action("sentinel", "search_web", body, {"results": len(hits), "usage": data.get("usage")},
                        account_id=account_id, latency_ms=int((time.perf_counter() - started) * 1000), model="keenable")
    return hits


async def fetch(url: str, *, prompt: str | None = None, max_chars: int = 12000, live: bool = False,
                account_id: str | None = None) -> dict:
    params: dict = {"url": url, "max_chars": max_chars}
    if prompt:
        params["prompt"] = prompt[:2000]
    if live:
        params["live"] = "true"
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=60) as http:
            r = await http.get(f"{BASE}/fetch", headers=_headers(), params=params)
            if r.status_code == 404 and not live:
                params["live"] = "true"
                r = await http.get(f"{BASE}/fetch", headers=_headers(), params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as exc:
        await record_action("sentinel", "fetch_page", {"url": url, "prompt": bool(prompt)}, {"error": repr(exc)}, ok=False,
                            account_id=account_id, latency_ms=int((time.perf_counter() - started) * 1000))
        return {"url": url, "title": None, "content": None, "error": repr(exc)}
    await record_action("sentinel", "fetch_page", {"url": url, "prompt": bool(prompt)},
                        {"chars": len(data.get("content") or ""), "usage": data.get("usage")},
                        account_id=account_id, latency_ms=int((time.perf_counter() - started) * 1000), model="keenable")
    return {"url": data.get("url") or url, "title": data.get("title"), "content": data.get("content")}
