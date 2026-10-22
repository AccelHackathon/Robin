"""Review gate (PRD 2.7). Every outbound text passes here before leaving the system.

Deterministic controls run first and are authoritative. The LLM judge (control 6 nuance and
rewrites) is layered on top in `judge.py` when an OpenAI key is configured; without it the
gate is still safe because the regex controls block the unambiguous cases.

Controls:
 1. evidence        each loss item in the send has >= 1 evidence and an existing clause
 2. citation        every (clause_id, quote) pair is verbatim in the clause body (>= 0.9)
 3. duplicates      no evidence counted twice
 4. traceable €     every amount in the text is an evidence / derived / client-instruction amount
 5. promise         no acceptance, agreement, waiver, settlement language
 6. advice          no personalised recommendation (regex here; judge refines)
 7. banned words    no "organised / gang / looters…" toward insurer, police, prefect
 8. unconfirmed     no fact with status != confirmed in an external send
"""

from __future__ import annotations

import json
import logging

from app import db
from app.agents.review import amounts as amt
from app.agents.review import citations
from app.agents.review.rules import ADVICE_RE, BANNED_RE, PROMISE_RE, find_all
from app.contracts import OutboundDraft, ReviewContext, ReviewResult, ReviewViolation

log = logging.getLogger(__name__)

EXTERNAL_ROLES = {"insurer", "broker", "expert", "prefect", "accountant"}


async def _loss_item_checks(ctx: ReviewContext) -> list[ReviewViolation]:
    out: list[ReviewViolation] = []
    if not ctx.loss_item_ids or db.pool is None:
        return out
    async with db.pool.connection() as conn:
        rows = await (
            await conn.execute(
                "SELECT id, label, evidence_ids, clause_id FROM loss_items WHERE id = ANY(%s::uuid[])",
                (ctx.loss_item_ids,),
            )
        ).fetchall()
        seen_evidence: set[str] = set()
        for item_id, label, evidence_ids, clause_id in rows:
            ev = [str(e) for e in (evidence_ids or [])]
            if not ev:
                out.append(ReviewViolation(type="missing_evidence", span=label, fix="attach at least one evidence row"))
            if clause_id is None or not await citations.clause_exists(int(clause_id)):
                out.append(ReviewViolation(type="missing_evidence", span=label, fix="cite an existing clause"))
            for e in ev:
                if e in seen_evidence:
                    out.append(ReviewViolation(type="duplicate_counted", span=f"{label}: evidence {e}", fix="count each evidence once"))
                seen_evidence.add(e)
            if ev:
                dup = await (
                    await conn.execute(
                        "SELECT id FROM evidence WHERE id = ANY(%s::uuid[]) AND duplicate_of IS NOT NULL", (ev,)
                    )
                ).fetchall()
                for (d,) in dup:
                    out.append(ReviewViolation(type="duplicate_counted", span=f"{label}: evidence {d} is a duplicate", fix="use the original evidence"))
    return out


async def _citation_checks(ctx: ReviewContext) -> list[ReviewViolation]:
    out: list[ReviewViolation] = []
    for clause_id, quote in ctx.quotes:
        if not await citations.verify_quote(clause_id, quote):
            out.append(ReviewViolation(type="bad_citation", span=quote[:120], fix=f"quote is not in clause {clause_id}"))
    return out


def _text_checks(draft: OutboundDraft, ctx: ReviewContext) -> list[ReviewViolation]:
    out: list[ReviewViolation] = []
    text = ((draft.subject or "") + "\n" + draft.body)
    langs = [draft.language, "fr" if draft.language == "en" else "en"]  # check both; mixed drafts happen

    mentioned = list(draft.amounts_eur) + amt.extract_amounts_eur(text)
    allowed = ctx.evidence_amounts_eur + ctx.derived_amounts_eur + ctx.client_instruction_amounts_eur
    for a in sorted(set(amt.untraceable(mentioned, allowed))):
        out.append(ReviewViolation(type="untraceable_amount", span=f"{a:,.2f} €", fix="only evidence, derived or client-instructed amounts"))

    for lang in langs:
        for span in find_all(text, PROMISE_RE[lang]):
            out.append(ReviewViolation(type="promise_or_acceptance", span=span, fix="Robin transmits; it never accepts, agrees or waives"))
        for span in find_all(text, ADVICE_RE[lang]):
            out.append(ReviewViolation(type="personalised_advice", span=span, fix="state the facts and list the options; do not recommend"))
        if draft.recipient_role in EXTERNAL_ROLES or draft.channel in ("prefect_letter", "phone_brief"):
            for span in find_all(text, BANNED_RE[lang]):
                out.append(ReviewViolation(type="banned_word", span=span, fix="describe time, place, number of people; do not qualify"))

    if draft.recipient_role in EXTERNAL_ROLES:
        unconfirmed = [f for f in ctx.fact_ids_used if f not in ctx.confirmed_fact_ids]
        for f in unconfirmed:
            out.append(ReviewViolation(type="unconfirmed_fact", span=f, fix="confirm with the client before sending externally"))
    return out


async def _log(draft: OutboundDraft, ctx: ReviewContext, result: ReviewResult) -> None:
    if db.pool is None:
        return
    try:
        async with db.pool.connection() as conn:
            acct = await (await conn.execute("SELECT account_id FROM claims WHERE id = %s", (ctx.claim_id,))).fetchone()
            await conn.execute(
                "INSERT INTO review_log (account_id, claim_id, channel, draft, passed, violations, rewrite) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (acct[0] if acct else None, ctx.claim_id, draft.channel, draft.body, result.passed,
                 json.dumps([v.model_dump() for v in result.violations]), result.rewrite),
            )
            await conn.commit()
    except Exception:
        log.exception("review_log insert failed")


async def review(draft: OutboundDraft, ctx: ReviewContext, *, use_judge: bool = True) -> ReviewResult:
    violations = _text_checks(draft, ctx)
    violations += await _citation_checks(ctx)
    violations += await _loss_item_checks(ctx)

    rewrite: str | None = None
    if use_judge:
        try:
            from app.agents.review.judge import judge  # optional LLM layer

            judged = await judge(draft, ctx, violations)
            if judged:
                violations += judged.violations
                rewrite = judged.rewrite
        except ImportError:
            pass
        except Exception:
            log.exception("review judge failed; deterministic result kept")

    result = ReviewResult(passed=not violations, violations=violations, rewrite=rewrite)
    await _log(draft, ctx, result)
    return result
