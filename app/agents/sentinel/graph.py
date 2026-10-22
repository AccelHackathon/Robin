"""Risk Sentinel Agent (workstream D) — continuous monitoring of external risks for each account.

Graph (one run = one sweep for one account):
  load_profile -> plan_queries -> search -> triage -> fetch -> assess -> dedupe -> compose -> gate -> notify -> persist

Principles (same as the rest of Robin): every alert has at least one source URL; everything said
about the contract comes from `coverage_profile` / `deadline_rules` with page references; the
message passes the review gate; practical precautions are labelled as general, never as advice
on the claim. If a loss is later declared in the event window, the alert's sources become
evidence of the external event (see `link_alerts_to_claim`).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from psycopg.rows import dict_row

from app import db
from app.agents.audit import record_action
from app.agents.checkpointer import get_checkpointer
from app.agents.sentinel.profile import build_profile
from app.agents.sentinel.risks import RISKS, SEVERITY_ORDER
from app.channels.web_search import keenable
from app.config import settings
from app.contracts import OutboundDraft, ReviewContext
from app.llm import chat_model, llm_available

log = logging.getLogger(__name__)

MAX_QUERIES_PER_SWEEP = 10
MAX_QUERIES_PER_RISK = 2
MAX_CANDIDATES = 4


class SentinelState(TypedDict, total=False):
    account_id: str
    sweep_id: int
    profile: dict
    queries: list[dict]            # {risk_key, query, site}
    hits: list[dict]               # {risk_key, url, title, snippet, published_at, site}
    candidates: list[dict]         # triaged hits with {reason}
    pages: dict                    # url -> extracted content
    assessments: list[dict]        # structured events
    alerts: list[dict]             # new alerts to create (after dedupe)
    notified: int
    stats: dict


# --- helpers ----------------------------------------------------------------------------------

def _json(text: str) -> Any:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t[t.find("\n") + 1:] if "\n" in t else t
    for opener, closer in (("[", "]"), ("{", "}")):
        s, e = t.find(opener), t.rfind(closer)
        if s >= 0 and e > s:
            try:
                return json.loads(t[s:e + 1])
            except json.JSONDecodeError:
                continue
    return None


async def _llm_json(system: str, user: str, *, account_id: str, tool: str, max_tokens: int = 1500) -> Any:
    model = chat_model(max_tokens=max_tokens)
    import time
    started = time.perf_counter()
    msg = await model.ainvoke([SystemMessage(content=system), HumanMessage(content=user)])
    u = getattr(msg, "usage_metadata", None) or {}
    await record_action("sentinel", tool, {"chars": len(user)}, {"ok": True}, account_id=account_id,
                        tokens_in=u.get("input_tokens"), tokens_out=u.get("output_tokens"),
                        latency_ms=int((time.perf_counter() - started) * 1000), model=settings.openai_model)
    return _json(msg.content if isinstance(msg.content, str) else "")


def _fingerprint(risk_key: str, place: str | None, date: str | None) -> str:
    import unicodedata
    ascii_place = unicodedata.normalize("NFKD", place or "").encode("ascii", "ignore").decode()
    norm = re.sub(r"[^a-z0-9]+", " ", ascii_place.lower()).strip()
    return hashlib.sha1(f"{risk_key}|{norm}|{(date or '')[:10]}".encode()).hexdigest()


def _fill(template: str, profile: dict) -> str:
    return " ".join(template.format(city=profile.get("city") or "", department=profile.get("department") or "",
                                    street=profile.get("street") or "").split())


# --- nodes ------------------------------------------------------------------------------------

async def load_profile(state: SentinelState) -> SentinelState:
    profile = await build_profile(state["account_id"])
    async with db.pool.connection() as conn:
        row = await (await conn.execute("INSERT INTO sentinel_sweeps (account_id) VALUES (%s) RETURNING id", (state["account_id"],))).fetchone()
        await conn.commit()
    return {"profile": profile, "sweep_id": row[0], "stats": {}}


async def plan_queries(state: SentinelState) -> SentinelState:
    profile = state["profile"]
    queries: list[dict] = []
    for key in profile["risk_keys"]:
        risk = RISKS[key]
        for template in risk.queries[:MAX_QUERIES_PER_RISK]:
            q = _fill(template, profile)
            if len(q) > 8:
                queries.append({"risk_key": key, "query": q, "site": None})
    queries = queries[:MAX_QUERIES_PER_SWEEP]
    async with db.pool.connection() as conn:
        for q in queries:
            await conn.execute(
                """
                INSERT INTO watch_queries (account_id, risk_key, query, published_after) VALUES (%s, %s, %s, %s)
                ON CONFLICT (account_id, risk_key, query) DO NOTHING
                """,
                (state["account_id"], q["risk_key"], q["query"], f"{settings.sentinel_lookback_hours}h"),
            )
        await conn.commit()
    return {"queries": queries}


async def search(state: SentinelState) -> SentinelState:
    if not keenable.available():
        log.warning("sentinel: KEENABLE_API_KEY not set; sweep has no sources")
        return {"hits": [], "stats": {**state.get("stats", {}), "queries_run": 0}}
    hits: dict[str, dict] = {}
    window = f"{settings.sentinel_lookback_hours}h"

    async def run(q: dict):
        try:
            found = await keenable.search(q["query"], published_after=window, max_results=6, account_id=state["account_id"])
        except Exception:
            log.exception("sentinel search failed: %s", q["query"])
            found = []
        async with db.pool.connection() as conn:
            await conn.execute("UPDATE watch_queries SET last_run_at = now(), last_hits = %s WHERE account_id = %s AND query = %s",
                               (len(found), state["account_id"], q["query"]))
            await conn.commit()
        return q, found

    results = await asyncio.gather(*(run(q) for q in state["queries"]))
    for q, found in results:
        for h in found:
            if h.url and h.url not in hits:
                hits[h.url] = {"risk_key": q["risk_key"], "url": h.url, "title": h.title, "snippet": h.snippet,
                               "published_at": h.published_at, "site": h.site}
    return {"hits": list(hits.values()), "stats": {**state.get("stats", {}), "queries_run": len(state["queries"]), "hits": len(hits)}}


TRIAGE_SYSTEM = """You triage web search results for a monitoring agent that protects one small business.
Keep only results describing a CONCRETE, DATED external event or official measure that could affect THIS business in the coming days
(or started in the last 48 hours): protest routes or bans, curfews, riots, weather vigilance (hail, storm, flood), nearby fires,
strikes blocking access, burglary waves, insurer or government measures changing claim deadlines or deductibles.
Discard: opinion pieces, national politics without local effect, events in other cities, anything older than 3 days unless it is a measure still in force.
Return ONLY a JSON array of at most {max} objects: [{"url": "...", "risk_key": "...", "reason": "one line", "likely_relevant": true}]"""


async def triage(state: SentinelState) -> SentinelState:
    hits = state["hits"]
    if not hits:
        return {"candidates": []}
    if not llm_available():
        return {"candidates": hits[:MAX_CANDIDATES]}
    p = state["profile"]
    listing = "\n".join(
        f"- url: {h['url']}\n  risk_key: {h['risk_key']} | published: {h['published_at'] or '?'} | site: {h['site']}\n  title: {h['title']}\n  snippet: {h['snippet'][:400]}"
        for h in hits[:40]
    )
    user = (f"Business: {p.get('business_name')} — {p.get('activity') or 'shop'} — {p.get('address')} ({p.get('city')}, {p.get('department')}).\n"
            f"Today: {datetime.now(timezone.utc).date().isoformat()}.\nResults:\n{listing}")
    picked = await _llm_json(TRIAGE_SYSTEM.replace("{max}", str(MAX_CANDIDATES)), user, account_id=state["account_id"], tool="triage_hits") or []
    by_url = {h["url"]: h for h in hits}
    candidates = []
    for c in picked if isinstance(picked, list) else []:
        h = by_url.get(c.get("url"))
        if h and c.get("likely_relevant", True):
            candidates.append({**h, "risk_key": c.get("risk_key") or h["risk_key"], "reason": c.get("reason")})
    return {"candidates": candidates[:MAX_CANDIDATES], "stats": {**state["stats"], "candidates": len(candidates)}}


FETCH_PROMPT = ("Extract, as plain facts and in English: what the event or measure is; the exact place(s), streets or perimeter; "
                "the date and time window (start/end); who issued it (prefecture, Météo-France, ministry, insurer, press); "
                "and any instruction given to shops or residents. Quote the key sentence verbatim in French. If the page is not about a concrete event, say so.")


async def fetch(state: SentinelState) -> SentinelState:
    pages: dict[str, dict] = {}

    async def one(c: dict):
        pages[c["url"]] = await keenable.fetch(c["url"], prompt=FETCH_PROMPT, max_chars=6000, account_id=state["account_id"])

    if state["candidates"] and keenable.available():
        await asyncio.gather(*(one(c) for c in state["candidates"]))
    return {"pages": pages, "stats": {**state["stats"], "pages_fetched": len(pages)}}


ASSESS_SYSTEM = """You assess one external event for a monitoring agent protecting a small business. You are a procedural layer:
you state facts and the business's own policy terms; you never give legal advice, never estimate claim outcomes, never qualify people
(never use words like organised, gang, rioters, looters, premeditated).
Return ONLY a JSON object:
{
  "relevant": true|false,
  "title": "short English title",
  "event_summary": "plain facts in English: what, where (streets/perimeter), when (dates, hours), issued by whom",
  "place": "most specific place name (street / district / city)",
  "distance_hint": "same_street|same_district|same_city|same_department|other",
  "event_starts_at": "ISO 8601 or null", "event_ends_at": "ISO 8601 or null",
  "severity": "low|medium|high|critical",
  "event_phase": "upcoming|ongoing|past",
  "risk_key": "the best matching risk key among: {risk_keys}",
  "official": true|false,
  "guarantee": "one of the cover keys provided or null",
  "excerpt_fr": "the key sentence quoted verbatim from the source, in French",
  "why_it_matters": "one factual sentence linking the event to the business's situation"
}
Severity: critical = ban/curfew/riot or red weather vigilance covering the business's street or district within 72 h; high = same city within 72 h or orange vigilance for the department;
medium = department-level or 3-7 days out; low = weak link. A PAST event (ended more than 12 hours ago) in the business's city or department stays relevant for 7 days: the business may have suffered damage and
the declaration deadline is running — set event_phase "past". Mark relevant=false if the place is another city/department."""


async def assess(state: SentinelState) -> SentinelState:
    if not state.get("candidates") or not llm_available():
        return {"assessments": []}
    p = state["profile"]
    cover_keys = ", ".join(sorted(p["covers"].keys())) or "none extracted yet"
    out: list[dict] = []

    async def one(c: dict):
        page = state["pages"].get(c["url"]) or {}
        user = (f"Business: {p.get('business_name')} — {p.get('activity') or 'shop'} — address: {p.get('address')} "
                f"(city {p.get('city')}, department {p.get('department')}). Covers extracted from its policy: {cover_keys}.\n"
                f"Today: {datetime.now(timezone.utc).isoformat(timespec='minutes')}.\n"
                f"Risk type: {c['risk_key']} ({RISKS[c['risk_key']].label_en}). Source: {c['url']} ({c.get('site')}), published {c.get('published_at')}.\n"
                f"Title: {c['title']}\nSnippet: {c['snippet']}\nExtracted content:\n{(page.get('content') or '')[:5000]}")
        system = ASSESS_SYSTEM.replace("{risk_keys}", ", ".join(RISKS.keys()))
        a = await _llm_json(system, user, account_id=state["account_id"], tool="assess_event")
        if isinstance(a, dict):
            risk_key = a.get("risk_key") if a.get("risk_key") in RISKS else c["risk_key"]
            a.update({"risk_key": risk_key, "source": {"url": c["url"], "title": page.get("title") or c["title"], "site": c.get("site"),
                                                             "published_at": c.get("published_at"), "excerpt": a.get("excerpt_fr")}})
            out.append(a)

    await asyncio.gather(*(one(c) for c in state["candidates"]))
    return {"assessments": [a for a in out if a.get("relevant")]}


async def dedupe(state: SentinelState) -> SentinelState:
    alerts: list[dict] = []
    seen: set[str] = set()
    async with db.pool.connection() as conn:
        for a in state.get("assessments", []):
            fp = _fingerprint(a["risk_key"], a.get("place"), a.get("event_starts_at") or a["source"].get("published_at"))
            if fp in seen:
                continue
            seen.add(fp)
            existing = await (await conn.execute("SELECT id FROM alerts WHERE account_id = %s AND fingerprint = %s", (state["account_id"], fp))).fetchone()
            if existing:
                await conn.execute("INSERT INTO alert_sources (alert_id, url, title, site, published_at, excerpt, official) VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                                   (existing[0], a["source"]["url"], a["source"]["title"], a["source"]["site"], a["source"]["published_at"], a["source"]["excerpt"], bool(a.get("official"))))
                continue
            alerts.append({**a, "fingerprint": fp})
        await conn.commit()
    return {"alerts": alerts}


def _cover_lines(profile: dict, guarantee: str | None, risk_key: str) -> tuple[list[str], list[dict], str | None, int | None, int | None]:
    """Policy facts for the message: cover status + contractual conditions (with pages), deadline."""
    covers = profile["covers"]
    keys = [g for g in RISKS[risk_key].guarantees if g in covers]
    if guarantee and guarantee in covers:
        keys = [guarantee] + [g for g in keys if g != guarantee]
    lines, prevention = [], []
    clause_id = page = None
    for g in keys[:2]:
        c = covers[g]
        status = {"yes": "covered", "no": "not covered according to your schedule", "unknown": "cover not confirmed yet (schedule page missing)"}[c["subscribed"]]
        where = f" (policy p. {c['page']})" if c.get("page") else ""
        cap = c.get("ceiling") or {}
        cap_txt = f", cap {cap.get('amount'):,.0f} €".replace(",", " ") if isinstance(cap, dict) and isinstance(cap.get("amount"), (int, float)) else ""
        lines.append(f"{g.replace('_', ' ')}: {status}{cap_txt}{where}")
        if clause_id is None:
            clause_id, page = c.get("clause_id"), c.get("page")
        for cond in (c.get("conditions") or [])[:3]:
            prevention.append({"text": str(cond), "kind": "contractual", "page": c.get("page"), "clause_id": c.get("clause_id")})
    deadline = None
    for d in profile.get("deadlines", []):
        if d["kind"] in ("declaration_theft", "declaration", "declaration_other", "police_report"):
            rule = d["rule"] if isinstance(d["rule"], dict) else {}
            deadline = f"{d['kind'].replace('_', ' ')}: {rule.get('text') or rule.get('value') or json.dumps(rule)} (policy p. {d['page']})"
            break
    if not deadline:
        deadline = "declaration within 2 working days for theft/vandalism, 5 working days otherwise (art. L113-2 Code des assurances); 30 days announced by France Assureurs for the 17–18 Oct events"
    return lines, prevention, deadline, clause_id, page


def compose_message(profile: dict, a: dict) -> tuple[str, list[dict], str, int | None, int | None]:
    risk = RISKS[a["risk_key"]]
    cover_lines, prevention, deadline, clause_id, page = _cover_lines(profile, a.get("guarantee"), a["risk_key"])
    when = ""
    if a.get("event_starts_at"):
        when = f" Window: {a['event_starts_at'][:16].replace('T', ' ')}" + (f" → {a['event_ends_at'][:16].replace('T', ' ')}" if a.get("event_ends_at") else "") + "."
    past = a.get("event_phase") == "past"
    practical = [] if past else [{"text": m, "kind": "general"} for m in risk.practical_measures[:3]]
    head = "ℹ️ Recent event near you" if past else "⚠️ Heads-up"
    parts = [
        f"{head}: {risk.label_en} — {a['severity'].upper()} — {a.get('place') or profile.get('city')}",
        a["event_summary"].strip() + when,
        f"Source: {a['source']['title'] or a['source']['url']} — {a['source']['url']}" + (" (official)" if a.get("official") else ""),
    ]
    if cover_lines:
        parts.append("Your policy: " + "; ".join(cover_lines) + ".")
    if prevention and not past:
        parts.append("Conditions in your policy: " + " ".join(f"{p_['text']} (p. {p_['page']})." if p_.get("page") else f"{p_['text']}." for p_ in prevention[:3]))
    if practical:
        parts.append("General precautions (not contractual, not advice on a claim): " + " ".join(m["text"] for m in practical))
    if past:
        parts.append("Did your premises, stock or vehicles suffer any damage from this event? If yes, reply here with photos: "
                     f"I will declare it the same day. The declaration deadline runs from the day of the loss. Deadline rule: {deadline}.")
    else:
        parts.append(f"If damage occurs: photograph everything before any clean-up, keep invoices, and tell me here — I will declare it the same day. Deadline rule: {deadline}.")
    return "\n\n".join(parts), prevention + practical, deadline, clause_id, page


async def compose(state: SentinelState) -> SentinelState:
    out = []
    threshold = SEVERITY_ORDER.get(settings.sentinel_min_severity_to_notify, 1)
    for a in state.get("alerts", []):
        text, prevention, deadline, clause_id, page = compose_message(state["profile"], a)
        out.append({**a, "message_en": text, "prevention_items": prevention, "deadline_note": deadline, "clause_id": clause_id, "clause_page": page,
                    "notify": SEVERITY_ORDER.get(a.get("severity", "low"), 0) >= threshold})
    return {"alerts": out}


async def gate(state: SentinelState) -> SentinelState:
    """Every alert text passes the shared review gate (banned words, no advice, no promises)."""
    try:
        from app.agents.review.gate import review
    except ImportError:
        review = None
    out = []
    for a in state.get("alerts", []):
        passed, text = True, a["message_en"]
        if review is not None:
            try:
                draft = OutboundDraft(channel="telegram", language="en", recipient_role="client", body=text)
                ctx = ReviewContext(claim_id=None, evidence_amounts_eur=[], derived_amounts_eur=[],
                                    client_instruction_amounts_eur=[], confirmed_fact_ids=[], cited_clause_ids=[a["clause_id"]] if a.get("clause_id") else [])
                result = await review(draft, ctx, use_judge=False)
                passed = result.passed
                if not passed and result.rewrite:
                    text, passed = result.rewrite, True
                if not passed:
                    log.warning("sentinel alert blocked by review: %s", [v.type for v in result.violations])
            except Exception:
                log.exception("review() failed for sentinel alert; sending deterministic text")
        out.append({**a, "message_en": text, "review_passed": passed})
    return {"alerts": out}


async def notify(state: SentinelState) -> SentinelState:
    notified = 0
    try:
        from app.channels.telegram.send import send_telegram
    except ImportError:
        send_telegram = None
    for a in state.get("alerts", []):
        a["communication_id"] = None
        if not (a.get("notify") and a.get("review_passed") and send_telegram and state["profile"].get("telegram_linked")):
            continue
        try:
            a["communication_id"] = await send_telegram(account_id=state["account_id"], text=a["message_en"])
            notified += 1
        except Exception as exc:
            log.warning("sentinel: telegram send failed: %r", exc)
    return {"notified": notified}


async def persist(state: SentinelState) -> SentinelState:
    created = 0
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            for a in state.get("alerts", []):
                status = ("notified" if a.get("communication_id") else "review_blocked" if not a.get("review_passed")
                          else "below_threshold" if not a.get("notify") else "new")
                await cur.execute(
                    """
                    INSERT INTO alerts (account_id, risk_key, fingerprint, severity, title, event_summary, event_starts_at, event_ends_at, place,
                                        distance_hint, guarantee, clause_id, clause_page, prevention_items, deadline_note, assessment, message_en,
                                        review_passed, communication_id, status, notified_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, CASE WHEN %s THEN now() END)
                    ON CONFLICT (account_id, fingerprint) DO NOTHING RETURNING id
                    """,
                    (state["account_id"], a["risk_key"], a["fingerprint"], a.get("severity", "low"), a.get("title") or RISKS[a["risk_key"]].label_en,
                     a["event_summary"], a.get("event_starts_at"), a.get("event_ends_at"), a.get("place"), a.get("distance_hint"), a.get("guarantee"),
                     a.get("clause_id"), a.get("clause_page"), json.dumps(a.get("prevention_items") or []), a.get("deadline_note"),
                     json.dumps({k: v for k, v in a.items() if k not in ("source", "prevention_items")}, default=str), a["message_en"],
                     a.get("review_passed"), a.get("communication_id"), status, bool(a.get("communication_id"))),
                )
                row = await cur.fetchone()
                if row:
                    created += 1
                    s = a["source"]
                    await cur.execute("INSERT INTO alert_sources (alert_id, url, title, site, published_at, excerpt, official) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                      (row["id"], s["url"], s["title"], s["site"], s["published_at"], s["excerpt"], bool(a.get("official"))))
            stats = state.get("stats", {})
            await cur.execute(
                """
                UPDATE sentinel_sweeps SET finished_at = now(), queries_run = %s, hits = %s, pages_fetched = %s, candidates = %s,
                       alerts_created = %s, alerts_notified = %s WHERE id = %s
                """,
                (stats.get("queries_run", 0), stats.get("hits", 0), stats.get("pages_fetched", 0), stats.get("candidates", 0), created,
                 state.get("notified", 0), state["sweep_id"]),
            )
            await cur.execute(
                "UPDATE risk_profiles SET last_sweep_at = now(), next_sweep_at = now() + make_interval(mins => sweep_interval_minutes) WHERE account_id = %s",
                (state["account_id"],),
            )
        await conn.commit()
    # Claims already open for this account: attach alerts whose window covers the loss date (evidence of the external event).
    linked = 0
    if created:
        async with db.pool.connection() as conn:
            claims = await (await conn.execute(
                "SELECT id, coalesce(loss_date::timestamptz, created_at) FROM claims WHERE account_id = %s AND status NOT IN ('closed')", (state["account_id"],)
            )).fetchall()
        for claim_id, loss_date in claims:
            linked += await link_alerts_to_claim(str(claim_id), state["account_id"], loss_date)
    await record_action("sentinel", "sweep", {"sweep_id": state["sweep_id"], **state.get("stats", {})},
                        {"alerts_created": created, "notified": state.get("notified", 0), "linked_to_claims": linked}, account_id=state["account_id"])
    return {"stats": {**state.get("stats", {}), "alerts_created": created, "linked_to_claims": linked}}


def build_graph():
    g = StateGraph(SentinelState)
    for name, fn in [("load_profile", load_profile), ("plan_queries", plan_queries), ("search", search), ("triage", triage),
                     ("fetch", fetch), ("assess", assess), ("dedupe", dedupe), ("compose", compose), ("gate", gate),
                     ("notify", notify), ("persist", persist)]:
        g.add_node(name, fn)
    order = ["load_profile", "plan_queries", "search", "triage", "fetch", "assess", "dedupe", "compose", "gate", "notify", "persist"]
    g.add_edge(START, order[0])
    for a, b in zip(order, order[1:]):
        g.add_edge(a, b)
    g.add_edge(order[-1], END)
    return g


_compiled = None


async def sweep(account_id: str) -> dict:
    """Run one sweep for an account. Returns the final state (alerts + stats)."""
    global _compiled
    if _compiled is None:
        _compiled = build_graph().compile(checkpointer=await get_checkpointer())
    config = {"configurable": {"thread_id": f"sentinel:{account_id}:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"}}
    try:
        return await _compiled.ainvoke({"account_id": str(account_id)}, config=config)
    except Exception as exc:
        async with db.pool.connection() as conn:
            await conn.execute("UPDATE sentinel_sweeps SET finished_at = now(), error = %s WHERE account_id = %s AND finished_at IS NULL", (repr(exc)[:500], account_id))
            await conn.execute("UPDATE risk_profiles SET next_sweep_at = now() + interval '15 minutes' WHERE account_id = %s", (account_id,))
            await conn.commit()
        raise


async def link_alerts_to_claim(claim_id: str, account_id: str, loss_date) -> int:
    """When a claim is opened, attach the alerts whose event window covers the loss date: their
    sources become dated, third-party evidence of the external event (cause, riot_event match)."""
    async with db.pool.connection() as conn:
        res = await conn.execute(
            """
            UPDATE alerts SET claim_id = %s WHERE account_id = %s AND claim_id IS NULL
              AND coalesce(event_starts_at, created_at) - interval '2 days' <= %s::timestamptz
              AND coalesce(event_ends_at, event_starts_at, created_at) + interval '2 days' >= %s::timestamptz
            """,
            (claim_id, account_id, loss_date, loss_date),
        )
        await conn.commit()
        return res.rowcount
