"""Claims Agent graph (PRD 2.3): load_memory → triage → analyze → act → review → dispatch → wait.

One LangGraph thread per claim (thread_id = claim_id), checkpointed in Postgres. The thread
lives as long as the claim: each run ends in `wait` with a typed interrupt and is resumed by
the worker with `Command(resume={"event": ...})` when the next event arrives.

This module holds the graph wiring and the deterministic node logic. LLM-backed steps
(document reading, narrative extraction, judge rewrites) are called through `nodes/` helpers
and degrade gracefully when no model key is configured.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app import db
from app.agents.claims import outbound
from app.agents.claims import tools_impl as T
from app.agents.claims.nodes import act as act_rules
from app.agents.claims.nodes import analyze as analyze_rules
from app.agents.claims.state import ClaimState
from app.agents.review.rules import has_release_language
from app.config import settings

log = logging.getLogger(__name__)

_saver_pool: AsyncConnectionPool | None = None
_saver: AsyncPostgresSaver | None = None
_graph = None


# --- nodes -----------------------------------------------------------------------------------

async def load_memory(state: ClaimState) -> dict[str, Any]:
    memory = await T.get_claim_memory(state["claim_id"])
    return {"memory": memory, "account_id": memory["account_id"], "drafts": [], "violations": [], "review_failures": 0,
            "trace": [f"loaded memory: {len(memory['facts'])} facts, {len(memory['evidence'])} evidence, {len(memory['loss_items'])} items"]}


async def triage(state: ClaimState) -> dict[str, Any]:
    ev, memory = state["event"], state["memory"]
    kind = ev.get("kind")
    sent_purposes = {c.get("subject", "") for c in memory["communications"] if c.get("direction") == "outbound"}
    declared = any(a.get("tool") == "send_email" and (a.get("arguments") or {}).get("purpose") == "initial_declaration" and a.get("ok") for a in memory["actions"]) \
        or any("Déclaration de sinistre" in (s or "") for s in sent_purposes)
    t: dict[str, Any] = {"kind": kind, "is_new_claim": not declared, "offer_id": None, "reasons": []}

    if kind == "followup_due":
        t["decision"] = "act"
        t["reasons"].append(f"scheduled task fired: {ev.get('payload', {}).get('reason')}")
    elif kind == "call_ended":
        t["decision"] = "update"
        t["reasons"].append("call result → oral facts to confirm in writing")
    elif kind == "email_received":
        body = (ev.get("payload", {}).get("body_text") or "") + " " + (ev.get("payload", {}).get("subject") or "")
        looks_like_offer = analyze_rules.looks_like_offer(body)
        t["decision"] = "present_offer" if looks_like_offer else "update"
        t["reasons"].append("insurer email looks like an offer" if looks_like_offer else "insurer email → fact")
        if has_release_language(body):
            t["reasons"].append("release language detected in email body")
    else:  # telegram message / document
        t["decision"] = "update"
        t["reasons"].append("client input → analyze")
    if t["is_new_claim"]:
        t["reasons"].append("no initial declaration sent yet → declare today (L113-2)")
    return {"triage": t, "trace": state.get("trace", []) + [f"triage: {t['decision']} ({'; '.join(t['reasons'])})"]}


async def analyze(state: ClaimState) -> dict[str, Any]:
    analysis = await analyze_rules.run(state)
    return {"analysis": analysis, "memory": await T.get_claim_memory(state["claim_id"]),
            "trace": state.get("trace", []) + [f"analyze: {analysis.get('summary', '')}"]}


async def act(state: ClaimState) -> dict[str, Any]:
    drafts = await act_rules.build_drafts(state)
    return {"drafts": drafts, "trace": state.get("trace", []) + [f"act: {len(drafts)} draft(s): {', '.join(d.get('purpose', '?') for d in drafts)}"]}


async def review(state: ClaimState) -> dict[str, Any]:
    approved, violations = [], []
    for d in state.get("drafts", []):
        r = await outbound.gate(state["claim_id"], state["memory"], d)
        if r.passed:
            approved.append(d)
        elif r.rewrite:
            d2 = dict(d, body=r.rewrite)
            r2 = await outbound.gate(state["claim_id"], state["memory"], d2)
            (approved if r2.passed else violations).append(d2 if r2.passed else {"purpose": d.get("purpose"), "violations": [v.model_dump() for v in r2.violations]})
        else:
            violations.append({"purpose": d.get("purpose"), "violations": [v.model_dump() for v in r.violations]})
    failures = state.get("review_failures", 0) + (1 if violations else 0)
    trace = state.get("trace", []) + [f"review: {len(approved)} approved, {len(violations)} blocked"]
    return {"drafts": approved, "violations": violations, "review_failures": failures, "trace": trace}


async def dispatch(state: ClaimState) -> dict[str, Any]:
    wait_type = None
    now = datetime.now(timezone.utc)
    for d in state.get("drafts", []):
        await outbound.dispatch(state["claim_id"], state["memory"], d)
        if d["channel"] == "email" and d.get("recipient_role") == "insurer":
            await T.schedule_followup(state["claim_id"], now + timedelta(days=7), f"follow up insurer on: {d.get('purpose')}")
        if d.get("purpose") == "offer_summary":
            await T.register_deadline(state["claim_id"], "client_reminder", now + timedelta(days=3), None, None, reason="offer decision reminder D+3")
            await T.register_deadline(state["claim_id"], "client_reminder", now + timedelta(days=7), None, None, reason="offer decision reminder D+7")
        if d.get("next_wait"):
            wait_type = d["next_wait"]
    if not wait_type:
        wait_type = "awaiting_signature_decision" if state.get("triage", {}).get("decision") == "present_offer" else "awaiting_client"
    return {"wait_type": wait_type, "trace": state.get("trace", []) + [f"dispatch: sent {len(state.get('drafts', []))}, now {wait_type}"]}


async def wait(state: ClaimState) -> dict[str, Any]:
    wait_type = state.get("wait_type") or "awaiting_client"
    async with db.pool.connection() as conn:
        await conn.execute("UPDATE claims SET status = %s, updated_at = now() WHERE id = %s", (wait_type, state["claim_id"]))
        await conn.commit()
    resume = interrupt({"wait_type": wait_type, "claim_id": state["claim_id"]})
    # Resumed: the worker passed the next inbound event.
    return {"event": resume["event"], "wait_type": None, "drafts": [], "violations": [], "review_failures": 0, "trace": []}


def _after_triage(state: ClaimState) -> str:
    return {"act": "act", "present_offer": "analyze"}.get(state["triage"]["decision"], "analyze")


def _after_review(state: ClaimState) -> str:
    if state.get("violations") and not state.get("drafts") and state.get("review_failures", 0) < 3:
        return "act"  # retry: act sees the violations and produces a corrected draft (or asks the client)
    return "dispatch"


def build() -> StateGraph:
    g = StateGraph(ClaimState)
    g.add_node("load_memory", load_memory)
    g.add_node("triage", triage)
    g.add_node("analyze", analyze)
    g.add_node("act", act)
    g.add_node("review", review)
    g.add_node("dispatch", dispatch)
    g.add_node("wait", wait)
    g.add_edge(START, "load_memory")
    g.add_edge("load_memory", "triage")
    g.add_conditional_edges("triage", _after_triage, {"act": "act", "analyze": "analyze"})
    g.add_edge("analyze", "act")
    g.add_edge("act", "review")
    g.add_conditional_edges("review", _after_review, {"act": "act", "dispatch": "dispatch"})
    g.add_edge("dispatch", "wait")
    g.add_edge("wait", "load_memory")
    return g


# --- lifecycle --------------------------------------------------------------------------------

async def setup() -> None:
    """Create the checkpointer (own small pool: autocommit + dict_row as the saver requires) and compile."""
    global _saver_pool, _saver, _graph
    if not settings.database_url:
        log.warning("claims graph: no DATABASE_URL, graph not compiled")
        return
    _saver_pool = AsyncConnectionPool(settings.database_url, min_size=1, max_size=2, open=False,
                                      kwargs={"autocommit": True, "row_factory": dict_row, "prepare_threshold": 0})
    await _saver_pool.open()
    _saver = AsyncPostgresSaver(_saver_pool)
    await _saver.setup()
    _graph = build().compile(checkpointer=_saver)
    log.info("claims graph compiled with Postgres checkpointer")


async def teardown() -> None:
    global _saver_pool, _saver, _graph
    _graph = _saver = None
    if _saver_pool:
        await _saver_pool.close()
        _saver_pool = None


def graph():
    if _graph is None:
        raise RuntimeError("claims graph not set up; call app.agents.claims.graph.setup() at startup")
    return _graph


def _config(claim_id: str) -> dict:
    return {"configurable": {"thread_id": claim_id}}


async def is_waiting(claim_id: str) -> str | None:
    """Return the wait_type if the claim's thread is parked on an interrupt, else None."""
    snap = await graph().aget_state(_config(claim_id))
    for task in snap.tasks or ():
        for it in getattr(task, "interrupts", ()) or ():
            v = getattr(it, "value", None)
            if isinstance(v, dict) and v.get("wait_type"):
                return v["wait_type"]
    return None


async def run_event(claim_id: str, event: dict[str, Any]) -> dict[str, Any]:
    """Start the thread on its first event, or resume it with the next one. Returns the final state."""
    cfg = _config(claim_id)
    if await is_waiting(claim_id):
        result = await graph().ainvoke(Command(resume={"event": event}), cfg)
    else:
        result = await graph().ainvoke({"claim_id": claim_id, "event": event}, cfg)
    return result
