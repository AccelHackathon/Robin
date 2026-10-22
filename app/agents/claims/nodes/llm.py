"""Model-backed steps of the Claims Agent, isolated so the rest of the graph stays deterministic.

Provider: OpenAI (`OPENAI_API_KEY`, see `app.llm`); without a key callers degrade gracefully. Every call records tokens and latency in
`actions`. Document extractions are cached by (sha256, task) so the benchmark is cheap.
"""

from __future__ import annotations

import base64
import json
import logging
import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app import db
from app.agents.audit import record_action
from app.config import settings
from app.llm import chat_model, llm_available

log = logging.getLogger(__name__)

def provider() -> str | None:
    return "openai" if llm_available() else None


def get_model(*, temperature: float = 0.0):
    if not llm_available():
        raise RuntimeError("no model configured (set OPENAI_API_KEY)")
    return chat_model(temperature=temperature, max_tokens=4096), settings.openai_model


def _usage(msg) -> tuple[int | None, int | None]:
    u = getattr(msg, "usage_metadata", None) or {}
    return u.get("input_tokens"), u.get("output_tokens")


def _json(text: str) -> dict[str, Any]:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t[t.find("{"):]
    start, end = t.find("{"), t.rfind("}")
    return json.loads(t[start : end + 1]) if start >= 0 else {}


async def _cached(sha256: str | None, task: str) -> dict[str, Any] | None:
    if not sha256 or db.pool is None:
        return None
    async with db.pool.connection() as conn:
        row = await (await conn.execute("SELECT result FROM llm_extraction_cache WHERE sha256 = %s AND task = %s", (sha256, task))).fetchone()
    return row[0] if row else None


async def _store(sha256: str | None, task: str, model: str, result: dict[str, Any]) -> None:
    if not sha256 or db.pool is None:
        return
    async with db.pool.connection() as conn:
        await conn.execute(
            "INSERT INTO llm_extraction_cache (sha256, task, model, result) VALUES (%s,%s,%s,%s) ON CONFLICT (sha256, task) DO UPDATE SET model = EXCLUDED.model, result = EXCLUDED.result",
            (sha256, task, model, json.dumps(result)),
        )
        await conn.commit()


async def complete_json(system: str, user_parts: list[dict[str, Any]], *, claim_id: str | None, tool: str, cache_key: str | None = None) -> dict[str, Any]:
    cached = await _cached(cache_key, tool)
    if cached is not None:
        await record_action("claims", tool, {"cache": "hit", "sha256": cache_key}, {"keys": list(cached)}, claim_id=claim_id)
        return cached
    model, name = get_model()
    started = time.perf_counter()
    try:
        msg = await model.ainvoke([SystemMessage(content=system), HumanMessage(content=user_parts)])
        result = _json(msg.content if isinstance(msg.content, str) else "".join(p.get("text", "") for p in msg.content if isinstance(p, dict)))
        tin, tout = _usage(msg)
        await record_action("claims", tool, {"cache": "miss", "sha256": cache_key}, {"keys": list(result)}, claim_id=claim_id,
                            tokens_in=tin, tokens_out=tout, latency_ms=int((time.perf_counter() - started) * 1000), model=name)
        await _store(cache_key, tool, name, result)
        return result
    except Exception as exc:
        await record_action("claims", tool, {"cache": "miss", "sha256": cache_key}, {"error": repr(exc)}, ok=False, claim_id=claim_id,
                            latency_ms=int((time.perf_counter() - started) * 1000), model=name)
        raise


# --- read_document ------------------------------------------------------------------------------

READ_DOCUMENT_SYSTEM = """You extract facts from documents sent by a French small-business owner after an insured loss
(invoices, receipts, inventories, photos of damage, police reports, insurer letters).
Return ONLY a JSON object:
{
  "doc_type": "invoice|quote|inventory|police_report|photo|correspondence|bank_statement|accounting|other",
  "document_date": "YYYY-MM-DD or null",
  "vendor": "issuer / supplier name or null",
  "amounts": [{"label": "what the amount is", "amount_eur": number, "vat_included": true|false|null, "page": int|null}],
  "facts": ["short factual statements visible in the document"],
  "description": "one line: what this document shows",
  "confidence": "high|medium|low",
  "unreadable_pages": [int]
}
Rules: report only what is written or visible. For an invoice, give the total excluding VAT if shown (label it "total HT") and the total including VAT ("total TTC").
For a photo, amounts is [] and facts describe the visible damage (what, where, extent) without guessing causes or qualifying people.
Never invent an amount. Never add commentary."""


async def read_document(doc_id: str, *, claim_id: str | None = None) -> dict[str, Any] | None:
    if provider() is None or db.pool is None:
        return None
    async with db.pool.connection() as conn:
        row = await (await conn.execute("SELECT sha256, mime_type, filename, content, extracted_text FROM documents WHERE id = %s", (doc_id,))).fetchone()
    if not row:
        return None
    sha, mime, filename, content, extracted_text = row
    parts: list[dict[str, Any]] = [{"type": "text", "text": f"Document: {filename or doc_id} ({mime or 'unknown type'})."}]
    if (mime or "").startswith("image/") and content:
        b64 = base64.b64encode(bytes(content)).decode()
        parts.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
    elif extracted_text:
        parts.append({"type": "text", "text": extracted_text[:20000]})
    elif content and (mime or "") == "application/pdf":
        text = _pdf_text(bytes(content))
        if text:
            parts.append({"type": "text", "text": text[:20000]})
        else:
            parts.append({"type": "text", "text": "(PDF without extractable text)"})
    else:
        return {"doc_type": "other", "amounts": [], "facts": [], "confidence": "low", "unreadable_pages": [], "description": "unsupported content"}
    return await complete_json(READ_DOCUMENT_SYSTEM, parts, claim_id=claim_id, tool="read_document", cache_key=sha)


def _pdf_text(data: bytes) -> str | None:
    import subprocess
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(data)
            f.flush()
            out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, timeout=60)
            return out.stdout.decode(errors="replace") if out.returncode == 0 else None
    except Exception:
        return None


# --- narrative extraction -------------------------------------------------------------------

NARRATIVE_SYSTEM = """You structure what a French small-business owner tells a claims assistant about a loss event.
Return ONLY a JSON object:
{
  "is_loss_report": true|false,
  "loss_date": "YYYY-MM-DD or null",
  "loss_time": "HH:MM or null",
  "loss_type": "theft|vandalism|riot_damage|fire|water_damage|glass_breakage|other|null",
  "place": "address or place as stated, or null",
  "neutral_description": "the event restated as plain facts: date, time, place, what was damaged or taken, how entry happened. No qualification of the people involved (never: organised, gang, rioters, looters, premeditated, came on purpose).",
  "items_mentioned": [{"label": "item or category", "catalog_key": "one of {catalog_keys} or null", "quantity": number|null, "unit_value_eur": number|null, "total_value_eur": number|null, "value_basis": "purchase|retail|estimate|unknown", "is_customer_property": true|false}],
  "closure_days": number|null,
  "questions": ["what the owner asked, if anything"],
  "answers_to_requests": ["information the owner is providing in response to an earlier request"]
}
Rules: copy amounts exactly as stated; never compute or estimate. If the owner gives retail prices for stock, keep value_basis "retail" — do not convert.
Today's date is {today}; resolve relative dates (e.g. "Saturday night") against it only when unambiguous, otherwise null."""


async def extract_narrative(text: str, *, claim_id: str | None, today: str, catalog_keys: list[str] = ()) -> dict[str, Any] | None:
    if provider() is None or not text.strip():
        return None
    system = NARRATIVE_SYSTEM.replace("{today}", today).replace("{catalog_keys}", ", ".join(catalog_keys) or "stock, equipment, glass, other")
    return await complete_json(system, [{"type": "text", "text": text}], claim_id=claim_id, tool="extract_narrative")
