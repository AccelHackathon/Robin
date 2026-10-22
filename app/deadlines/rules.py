"""Deadline machine, pure part (PRD 2.5): turn contract rules and legal articles into dated tasks.

Every task carries its source: `source_clause_id` when it comes from the policy (B's
`deadline_rules` candidates, quote + page), else `legal_basis`. Never a universal clock — the
contract may lengthen a legal minimum but never shorten it (L113-2), so the later of the two wins.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

# Legal floors / defaults (Code des assurances unless stated). Contract rules may only lengthen these.
LEGAL: dict[str, dict[str, Any]] = {
    "declaration_theft":        {"days": 2, "business_days": True,  "basis": "art. L113-2 4° C. assur. (2 business days, theft)"},
    "declaration_other":        {"days": 5, "business_days": True,  "basis": "art. L113-2 4° C. assur. (5 business days)"},
    "police_report":            {"hours": 48,                       "basis": "usual policy condition; file as soon as possible"},
    "loss_statement":           {"days": 30,                        "basis": "usual policy term (e.g. MMA 30 days); send 'subject to completion' before"},
    "payment":                  {"days": 30,                        "basis": "usual policy term: payment within 30 days of agreement (L113-5 refers to the agreed term)"},
    "replacement_value_top_up": {"days": 700,                       "basis": "policy: replacement within 2 years for the depreciation top-up; reminder at D+700"},
    "prescription_alert":       {"days": 730 - 90,                  "basis": "art. L114-1 C. assur. two-year limitation; alert 90 days before"},
    "prescription":             {"days": 730,                       "basis": "art. L114-1 C. assur. (interrupted by registered letter on settlement or appointment of an expert, L114-2)"},
    "state_recourse":           {"fixed": None,                     "basis": "art. L211-10 CSI — four-year limitation, prior claim to the prefect (R421-1 CJA)"},
}

_NUM = {"un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "dix": 10, "quinze": 15, "vingt": 20, "trente": 30, "soixante": 60}
_DUR = re.compile(r"\b(\d+|un|une|deux|trois|quatre|cinq|dix|quinze|vingt|trente|soixante)\s+(heures?|jours?\s+ouvr[ée]s?|jours?|mois|ans?|ann[ée]es?)\b", re.I)


@dataclass
class Rule:
    kind: str
    hours: int | None = None
    days: int | None = None
    months: int | None = None
    business_days: bool = False
    source_clause_id: int | None = None
    page: int | None = None
    quote: str | None = None
    legal_basis: str | None = None


@dataclass
class Task:
    kind: str
    due_at: datetime
    reason: str
    source_clause_id: int | None = None
    legal_basis: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)


def parse_duration(quote: str) -> Rule | None:
    """'dans les 2 jours ouvrés' → Rule(days=2, business_days=True); 'au plus vite' → None (use legal/default)."""
    m = _DUR.search(quote or "")
    if not m:
        return None
    n = int(m.group(1)) if m.group(1).isdigit() else _NUM[m.group(1).lower()]
    unit = m.group(2).lower()
    if unit.startswith("heure"):
        return Rule(kind="", hours=n)
    if "ouvr" in unit:
        return Rule(kind="", days=n, business_days=True)
    if unit.startswith("jour"):
        return Rule(kind="", days=n)
    if unit.startswith("mois"):
        return Rule(kind="", months=n)
    return Rule(kind="", days=365 * n)


def add_business_days(d: date, n: int) -> date:
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def _due(start: datetime, r: Rule) -> datetime:
    if r.hours is not None:
        return start + timedelta(hours=r.hours)
    if r.months is not None:
        return start + timedelta(days=30 * r.months)
    if r.business_days and r.days is not None:
        return datetime.combine(add_business_days(start.date(), r.days), time(18, 0), tzinfo=timezone.utc)
    return start + timedelta(days=r.days or 0)


def _later(a: datetime, b: datetime) -> datetime:
    return a if a >= b else b


def plan(*, loss_at: datetime, loss_type: str | None, contract_rules: list[dict[str, Any]], riot_event: dict[str, Any] | None,
         declared_at: datetime | None = None, agreement_at: datetime | None = None, now: datetime | None = None) -> list[Task]:
    """Build the dated task list for a claim. Contract rules (B's candidates) only lengthen legal floors."""
    now = now or datetime.now(timezone.utc)
    by_kind: dict[str, dict[str, Any]] = {}
    for r in contract_rules:
        if r.get("kind") and r["kind"] not in by_kind:
            by_kind[r["kind"]] = r
    tasks: list[Task] = []

    def contract(kind: str) -> tuple[Rule | None, dict[str, Any] | None]:
        r = by_kind.get(kind)
        if not r:
            return None, None
        parsed = parse_duration(r.get("quote") or (r.get("rule") or {}).get("text") or "")
        if parsed:
            parsed.kind, parsed.source_clause_id, parsed.page, parsed.quote = kind, r.get("source_clause_id"), r.get("page"), r.get("quote")
        return parsed, r

    # 1. Police report
    c, src = contract("police_report")
    legal = Rule(kind="police_report", **{k: v for k, v in LEGAL["police_report"].items() if k in ("hours", "days")})
    due = _due(loss_at, c) if c else _due(loss_at, legal)
    tasks.append(Task("police_report", due, "file the police complaint and keep the receipt", c.source_clause_id if c else None,
                      None if c else LEGAL["police_report"]["basis"], {"page": c.page if c else None}))

    # 2. Declaration — legal floor by nature; riot event may extend (France Assureurs 30 days for 17-18/10/2026)
    key = "declaration_theft" if loss_type in ("theft", "vandalism", "riot_damage") else "declaration_other"
    legal = Rule(kind="declaration", days=LEGAL[key]["days"], business_days=True, legal_basis=LEGAL[key]["basis"])
    due = _due(loss_at, legal)
    basis = LEGAL[key]["basis"]
    c, _ = contract("declaration")
    if c:
        due = _later(due, _due(loss_at, c))
    if riot_event and riot_event.get("declaration_deadline_days"):
        ext = loss_at + timedelta(days=int(riot_event["declaration_deadline_days"]))
        if ext > due:
            due, basis = ext, f"{basis}; extended to {riot_event['declaration_deadline_days']} days for « {riot_event.get('name')} » (France Assureurs)"
    tasks.append(Task("declaration", due, "declare the loss to the insurer (sent on Day 0 regardless)", c.source_clause_id if c else None, basis))

    # 3. Loss statement
    c, _ = contract("loss_statement")
    due = _due(loss_at, c) if c else _due(loss_at, Rule(kind="", days=LEGAL["loss_statement"]["days"]))
    tasks.append(Task("loss_statement", due, "send the detailed statement of loss (subject to completion)", c.source_clause_id if c else None,
                      None if c else LEGAL["loss_statement"]["basis"]))

    # 4. Payment after agreement (only once there is an agreement)
    if agreement_at:
        c, _ = contract("payment")
        due = _due(agreement_at, c) if c else _due(agreement_at, Rule(kind="", days=LEGAL["payment"]["days"]))
        tasks.append(Task("payment", due, "payment expected after agreement; follow up if not received", c.source_clause_id if c else None,
                          None if c else LEGAL["payment"]["basis"]))

    # 5. Replacement-value top-up (2 years, reminder at D+700)
    c, _ = contract("replacement_value_top_up")
    tasks.append(Task("replacement_value_top_up", loss_at + timedelta(days=LEGAL["replacement_value_top_up"]["days"]),
                      "depreciation top-up: send replacement invoices before the 2-year window closes", c.source_clause_id if c else None,
                      None if c else LEGAL["replacement_value_top_up"]["basis"]))

    # 6. Prescription (2 years) — alert at D-90 and the date itself
    c, _ = contract("prescription")
    tasks.append(Task("prescription_alert", loss_at + timedelta(days=LEGAL["prescription_alert"]["days"]),
                      "two-year limitation in 90 days: a registered letter on settlement or an expert appointment interrupts it",
                      c.source_clause_id if c else None, LEGAL["prescription_alert"]["basis"]))
    tasks.append(Task("prescription", loss_at + timedelta(days=LEGAL["prescription"]["days"]), "two-year limitation against the insurer",
                      c.source_clause_id if c else None, LEGAL["prescription"]["basis"]))

    # 7. State recourse (riot events only)
    if riot_event and riot_event.get("state_claim_deadline"):
        d = riot_event["state_claim_deadline"]
        d = d if isinstance(d, date) else date.fromisoformat(str(d))
        tasks.append(Task("state_recourse", datetime.combine(d - timedelta(days=90), time(9, 0), tzinfo=timezone.utc),
                          "State liability claim (L211-10 CSI) for the remainder not paid by the insurer: prior claim to the prefect before the deadline",
                          None, LEGAL["state_recourse"]["basis"], {"deadline": d.isoformat()}))

    return tasks


def missed(tasks: list[dict[str, Any]], now: datetime) -> list[dict[str, Any]]:
    """Tasks whose due date passed while still pending (informational: the agent continues and states it)."""
    return [t for t in tasks if t.get("status") == "pending" and t.get("due_at") and t["due_at"] < now]
