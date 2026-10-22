"""Workstream D — Risk Sentinel deterministic parts (no network, no database)."""

from app.agents.sentinel.graph import _fingerprint, _fill, compose_message
from app.agents.sentinel.profile import parse_address
from app.agents.sentinel.risks import RISKS, risks_for


def test_parse_french_address():
    a = parse_address("12 rue de la République, 13001 Marseille")
    assert a["postcode"] == "13001" and a["city"] == "Marseille"
    assert a["department"] == "Bouches-du-Rhône" and a["street"] == "rue de la République"


def test_parse_address_without_postcode_is_safe():
    a = parse_address("")
    assert a["city"] is None and a["department"] is None


def test_risks_never_assume_a_cover_is_absent():
    # No coverage facts at all -> every risk is watched (unknown never means "no").
    keys = {r.key for r in risks_for(has_vehicles=False, has_shopfront=True, covers={})}
    assert {"civil_unrest", "hail", "storm", "flood", "regulatory"} <= keys


def test_risks_drop_when_all_covers_are_explicitly_no():
    covers = {g: {"subscribed": "no"} for g in RISKS["flood"].guarantees}
    keys = {r.key for r in risks_for(has_vehicles=False, has_shopfront=True, covers=covers)}
    assert "flood" not in keys and "regulatory" in keys


def test_query_templates_fill_location():
    q = _fill("vigilance orange orages grêle {department}", {"department": "Bouches-du-Rhône", "city": "Marseille"})
    assert q == "vigilance orange orages grêle Bouches-du-Rhône"


def test_fingerprint_dedupes_same_event_from_different_sources():
    a = _fingerprint("civil_unrest", "Rue de la République, Marseille", "2026-10-25T14:00:00")
    b = _fingerprint("civil_unrest", "rue de la republique marseille", "2026-10-25T16:00:00")
    assert a == b


def _profile():
    return {
        "city": "Marseille", "department": "Bouches-du-Rhône", "covers": {
            "riot_civil_commotion": {"subscribed": "yes", "ceiling": None, "conditions": ["Rideau métallique baissé en dehors des heures d'ouverture."],
                                     "clause_id": 42, "page": 15},
            "theft_vandalism": {"subscribed": "yes", "ceiling": {"amount": 15000}, "conditions": [], "clause_id": 43, "page": 19},
        },
        "deadlines": [{"kind": "declaration", "rule": {"text": "2 jours ouvrés en cas de vol"}, "page": 76, "clause_id": 50}],
    }


def _event(phase="upcoming"):
    return {"risk_key": "civil_unrest", "severity": "high", "title": "Declared protest", "place": "Rue de la République, Marseille",
            "event_summary": "A protest march declared to the prefecture will pass rue de la République on Saturday 25 October from 14:00.",
            "event_starts_at": "2026-10-25T14:00:00", "event_ends_at": None, "official": True, "guarantee": "riot_civil_commotion",
            "event_phase": phase, "source": {"url": "https://example.gouv.fr/arrete", "title": "Arrêté préfectoral", "site": "example.gouv.fr",
                                              "published_at": "2026-10-22", "excerpt": "..."}}


def test_upcoming_alert_cites_policy_pages_and_labels_precautions():
    text, items, deadline, clause_id, page = compose_message(_profile(), _event())
    assert "policy p. 15" in text and "cap 15 000 €" in text
    assert "Rideau métallique" in text and "(p. 15)" in text
    assert "not contractual, not advice" in text
    assert "2 jours ouvrés" in deadline and clause_id == 42 and page == 15
    assert "https://example.gouv.fr/arrete" in text


def test_past_event_asks_about_damage_and_skips_precautions():
    text, items, _, _, _ = compose_message(_profile(), _event(phase="past"))
    assert "Recent event near you" in text and "Did your premises" in text
    assert "General precautions" not in text


def test_alert_text_has_no_banned_words():
    import re
    text, *_ = compose_message(_profile(), _event())
    assert not re.search(r"\b(organised|gang|rioters|looters|premeditated|casseurs|émeutiers)\b", text, re.I)
