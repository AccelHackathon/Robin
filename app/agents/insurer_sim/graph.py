"""Insurer Simulator Agent (workstream A, PRD 2.11) — a LangGraph that plays the insurer by email.

Nodes: load_thread -> classify -> choose_step -> compose -> gate -> send -> persist.
Input: one inbound email on the simulated_insurer mailbox. It never reads the Claims Agent's
memory: the only tables it touches are `insurer_sim_threads`, `communications` (its own) and
`documents` (to attach the release PDF). Everything it knows about the claim comes from the
email text itself.
"""

import asyncio
import hashlib
import json
import logging
import re
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from psycopg.rows import dict_row

from app import db
from app.agents.audit import record_action
from app.agents.checkpointer import get_checkpointer
from app.agents.insurer_sim.release_pdf import build_release_pdf
from app.agents.insurer_sim.scenarios import SCENARIOS, SIGNATURE, Step, classify, make_reference, pick_step
from app.channels.email.send import send_email
from app.contracts import OutboundDraft, ReviewContext

log = logging.getLogger(__name__)

BANNED = re.compile(r"\b(organis[ée]s?|bande|venus expr[èe]s|casseurs|[ée]meutiers|pr[ée]m[ée]dit[ée]e?s?|organi[sz]ed|gang|rioters|looters|premeditated)\b", re.I)


class SimState(TypedDict, total=False):
    inbound: dict            # event payload from the AgentMail webhook
    thread: dict             # insurer_sim_threads row
    intent: str
    step_key: str | None
    subject: str
    body: str
    attach_release: bool
    delay: int
    gate_passed: bool
    gate_violations: list
    communication_id: str | None


def _extract(body: str, pattern: str, default: str) -> str:
    m = re.search(pattern, body, re.I | re.S)
    return m.group(1).strip() if m else default


async def load_thread(state: SimState) -> SimState:
    inbound = state["inbound"]
    thread_ref = inbound.get("thread_ref") or hashlib.sha1((inbound.get("subject") or "").encode()).hexdigest()
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT * FROM insurer_sim_threads WHERE thread_ref = %s", (thread_ref,))
            row = await cur.fetchone()
            if not row:
                await cur.execute("SELECT count(*) AS n FROM insurer_sim_threads")
                n = (await cur.fetchone())["n"]
                await cur.execute(
                    "INSERT INTO insurer_sim_threads (thread_ref, claim_tag, scenario, insurer_reference) VALUES (%s, %s, 'karim_default', %s) RETURNING *",
                    (thread_ref, inbound.get("claim_tag"), make_reference(int(n) + 1)),
                )
                row = await cur.fetchone()
            await conn.commit()
    return {"thread": dict(row)}


async def classify_node(state: SimState) -> SimState:
    inbound = state["inbound"]
    return {"intent": classify(inbound.get("subject") or "", inbound.get("body_text") or "")}


async def choose_step(state: SimState) -> SimState:
    scenario = SCENARIOS[state["thread"]["scenario"]]
    played = {h.get("step") for h in (state["thread"].get("history") or []) if h.get("step")}
    step = pick_step(scenario, state["intent"], played)
    return {"step_key": step.key if step else None}


def _claim_context(inbound: dict, thread: dict) -> dict:
    """Everything the simulator knows comes from the email itself (subject + body), never from Robin's memory."""
    text = f"{inbound.get('subject') or ''}\n{inbound.get('body_text') or ''}"
    business = _extract(text, r"pour le compte de ([^(\n,–-]+)", "") or _extract(text, r"mandataire de ([^(\n,–-]+)", "") \
        or _extract(text, r"sinistre\s*[–-]\s*([^–\-\n]+?)\s*[–-]\s*contrat", "votre client")
    return {
        "subject": re.sub(r"^(re|tr|fwd?)\s*:\s*", "", inbound.get("subject") or "", flags=re.I),
        "ref": thread["insurer_reference"],
        "business_name": business.strip(),
        "policy_number": _extract(text, r"contrat n°\s*([A-Z0-9][A-Z0-9\-/]+)", "non communiqué"),
    }


def _render(step: Step | None, state: SimState) -> tuple[str, str, bool, int]:
    ctx = _claim_context(state["inbound"], state["thread"])
    scenario = SCENARIOS[state["thread"]["scenario"]]
    if step is None:
        return scenario.fallback_subject.format(**ctx), scenario.fallback_body.format(**ctx) + SIGNATURE, False, 15
    return step.subject.format(**ctx), step.body.format(**ctx) + SIGNATURE, step.attach_release_pdf, step.delay_seconds


async def compose(state: SimState) -> SimState:
    scenario = SCENARIOS[state["thread"]["scenario"]]
    step = next((s for s in scenario.steps if s.key == state.get("step_key")), None)
    subject, body, attach, delay = _render(step, state)
    return {"subject": subject, "body": body, "attach_release": attach, "delay": delay}


async def gate(state: SimState) -> SimState:
    """The simulator's emails obey the same rules as Robin's: no banned words. Uses C's review() when available."""
    violations: list = []
    if BANNED.search(state["body"]):
        violations.append({"type": "banned_word", "span": BANNED.search(state["body"]).group(0)})
    try:
        from app.agents.review.gate import review  # workstream C; optional at this stage
        draft = OutboundDraft(channel="email", language="fr", recipient_role="client", subject=state["subject"], body=state["body"])
        ctx = ReviewContext(claim_id=None, evidence_amounts_eur=[], derived_amounts_eur=[], client_instruction_amounts_eur=[],
                            confirmed_fact_ids=[], cited_clause_ids=[])
        result = await review(draft, ctx)
        if not result.passed:
            violations.extend(v.model_dump() for v in result.violations if v.type == "banned_word")
    except ImportError:
        pass
    except Exception:
        log.exception("review() failed for simulator draft; continuing with local checks only")
    return {"gate_passed": not violations, "gate_violations": violations}


async def send(state: SimState) -> SimState:
    if not state.get("gate_passed", True):
        log.error("simulator draft blocked: %s", state.get("gate_violations"))
        return {"communication_id": None}
    inbound, thread = state["inbound"], state["thread"]
    attachment_ids: list[str] = []
    if state.get("attach_release"):
        ctx = _claim_context(inbound, thread)
        pdf = build_release_pdf(
            business_name=ctx["business_name"] or "l'assuré", signer="le représentant légal", amount=20750.0,
            loss_date="17/10/2026", ref=thread["insurer_reference"], policy_number=ctx["policy_number"],
        )
        async with db.pool.connection() as conn:
            row = await (
                await conn.execute(
                    """
                    INSERT INTO documents (account_id, claim_id, doc_type, origin, filename, mime_type, sha256, content, metadata)
                    VALUES (NULL, NULL, 'correspondence', 'email', %s, 'application/pdf', %s, %s, %s) RETURNING id
                    """,
                    (f"quittance_{thread['insurer_reference']}.pdf", hashlib.sha256(pdf).hexdigest(), pdf,
                     json.dumps({"generated_by": "insurer_sim", "label": "SIMULATED INSURER"})),
                )
            ).fetchone()
            await conn.commit()
        attachment_ids.append(str(row[0]))

    await asyncio.sleep(state.get("delay", 15))
    to = inbound.get("from") or ""
    to_addr = re.search(r"<([^>]+)>", to).group(1) if "<" in to else to
    comm_id = await send_email(
        account_id=None, claim_id=None, to=to_addr, subject=state["subject"], body=state["body"],
        attachment_document_ids=attachment_ids, language="fr",
        from_mailbox_address=inbound["mailbox_address"], in_reply_to=inbound.get("message_id"),
        thread_ref=inbound.get("thread_ref"), agent="insurer_sim",
    )
    return {"communication_id": comm_id}


async def persist(state: SimState) -> SimState:
    thread = state["thread"]
    history = list(thread.get("history") or [])
    history.append({"intent": state["intent"], "step": state.get("step_key"), "communication_id": state.get("communication_id"),
                    "blocked": not state.get("gate_passed", True)})
    async with db.pool.connection() as conn:
        await conn.execute(
            "UPDATE insurer_sim_threads SET step = step + 1, history = %s, updated_at = now() WHERE id = %s",
            (json.dumps(history), thread["id"]),
        )
        await conn.commit()
    await record_action("insurer_sim", "reply", {"intent": state["intent"], "step": state.get("step_key"), "thread_ref": thread["thread_ref"]},
                        {"communication_id": state.get("communication_id"), "violations": state.get("gate_violations")},
                        ok=state.get("gate_passed", True))
    return {}


def build_graph():
    g = StateGraph(SimState)
    g.add_node("load_thread", load_thread)
    g.add_node("classify", classify_node)
    g.add_node("choose_step", choose_step)
    g.add_node("compose", compose)
    g.add_node("gate", gate)
    g.add_node("send", send)
    g.add_node("persist", persist)
    g.add_edge(START, "load_thread")
    g.add_edge("load_thread", "classify")
    g.add_edge("classify", "choose_step")
    g.add_edge("choose_step", "compose")
    g.add_edge("compose", "gate")
    g.add_edge("gate", "send")
    g.add_edge("send", "persist")
    g.add_edge("persist", END)
    return g


_compiled = None


async def run(inbound: dict) -> None:
    global _compiled
    if _compiled is None:
        _compiled = build_graph().compile(checkpointer=await get_checkpointer())
    thread_ref = inbound.get("thread_ref") or inbound.get("message_id") or "unknown"
    config = {"configurable": {"thread_id": f"insurer_sim:{thread_ref}"}}
    await _compiled.ainvoke({"inbound": inbound}, config=config)
