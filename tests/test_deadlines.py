"""Deadline machine — AC-14: a claim dated 17/10/2026 gets every deadline, correctly dated and sourced (no DB)."""

from datetime import date, datetime, timezone

from app.deadlines import rules as R

LOSS = datetime(2026, 10, 17, 19, 0, tzinfo=timezone.utc)  # Saturday
RIOT = {"name": "17–18 October 2026 unrest", "declaration_deadline_days": 30, "state_claim_deadline": date(2030, 12, 31)}
MAAF_RULES = [
    {"kind": "declaration", "source_clause_id": 101, "page": 76, "quote": "dans les 2 jours ouvrés en cas de vol, tentative de vol ou vandalisme"},
    {"kind": "police_report", "source_clause_id": 102, "page": 76, "quote": "Prévenez la police ou la gendarmerie locale au plus vite et déposez plainte."},
    {"kind": "loss_statement", "source_clause_id": 103, "page": 81, "quote": "un état des pertes dans les trente jours"},
    {"kind": "replacement_value_top_up", "source_clause_id": 104, "page": 79, "quote": "dès lors que le remplacement s'effectue dans les deux ans"},
]


def test_parse_durations():
    assert R.parse_duration("dans les 2 jours ouvrés").days == 2 and R.parse_duration("dans les 2 jours ouvrés").business_days
    assert R.parse_duration("déposer plainte dans les 24 heures").hours == 24
    assert R.parse_duration("dans les trente jours").days == 30
    assert R.parse_duration("dans les deux ans").days == 730
    assert R.parse_duration("au plus vite") is None


def test_business_days_skip_weekend():
    # Saturday 17 Oct + 2 business days = Tuesday 20 Oct
    assert R.add_business_days(date(2026, 10, 17), 2) == date(2026, 10, 20)


def test_ac14_full_plan_for_riot_theft():
    tasks = R.plan(loss_at=LOSS, loss_type="riot_damage", contract_rules=MAAF_RULES, riot_event=RIOT, now=LOSS)
    kinds = {t.kind: t for t in tasks}
    assert set(kinds) == {"police_report", "declaration", "loss_statement", "replacement_value_top_up", "prescription_alert", "prescription", "state_recourse"}
    # declaration: legal 2 business days → extended to 30 days by the riot event
    assert kinds["declaration"].due_at.date() == date(2026, 11, 16) and "30 days" in kinds["declaration"].legal_basis
    assert kinds["declaration"].source_clause_id == 101
    # loss statement from the contract (30 days), sourced to the clause
    assert kinds["loss_statement"].due_at.date() == date(2026, 11, 16) and kinds["loss_statement"].source_clause_id == 103
    # police report: contract says "au plus vite" → legal default 48 h, sourced to the article
    assert kinds["police_report"].due_at == LOSS.replace(day=19) and kinds["police_report"].legal_basis
    # 2-year items
    assert kinds["replacement_value_top_up"].due_at.date() == date(2028, 9, 16)
    assert kinds["prescription"].due_at.date() == date(2028, 10, 16)
    assert kinds["prescription_alert"].due_at.date() == date(2028, 7, 18)
    # State recourse: 90 days before 31/12/2030
    assert kinds["state_recourse"].due_at.date() == date(2030, 10, 2)
    # every task is sourced
    assert all(t.source_clause_id or t.legal_basis for t in tasks)


def test_contract_cannot_shorten_legal_minimum():
    rules = [{"kind": "declaration", "source_clause_id": 9, "page": 1, "quote": "déclarer dans les 24 heures"}]  # below L113-2 floor
    tasks = R.plan(loss_at=LOSS, loss_type="theft", contract_rules=rules, riot_event=None, now=LOSS)
    decl = next(t for t in tasks if t.kind == "declaration")
    assert decl.due_at.date() == date(2026, 10, 20)  # legal 2 business days wins over the shorter clause


def test_no_riot_no_state_recourse_and_other_loss_5_days():
    tasks = R.plan(loss_at=LOSS, loss_type="water_damage", contract_rules=[], riot_event=None, now=LOSS)
    kinds = {t.kind: t for t in tasks}
    assert "state_recourse" not in kinds
    assert kinds["declaration"].due_at.date() == date(2026, 10, 23)  # 5 business days from Saturday


def test_payment_task_only_after_agreement():
    agreed = datetime(2026, 12, 1, tzinfo=timezone.utc)
    tasks = R.plan(loss_at=LOSS, loss_type="theft", contract_rules=[], riot_event=None, agreement_at=agreed, now=agreed)
    pay = next(t for t in tasks if t.kind == "payment")
    assert pay.due_at.date() == date(2026, 12, 31)


def test_missed_detection():
    now = datetime(2026, 12, 1, tzinfo=timezone.utc)
    rows = [{"status": "pending", "due_at": LOSS}, {"status": "done", "due_at": LOSS}, {"status": "pending", "due_at": now.replace(year=2027)}]
    assert R.missed(rows, now) == [rows[0]]
