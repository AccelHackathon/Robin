"""Claims brain — pure logic (no DB): cover matching, digest asks, position contradictions."""

from datetime import datetime, timezone

from app.agents.claims.brain import covers, digest, positions, profiles

COVERAGE = [
    {"guarantee": "theft_vandalism", "subscribed": "yes", "ceiling": {"amount": 15000, "unit": "EUR"}, "page": 19, "clause_id": 1, "quote": "vol"},
    {"guarantee": "riot_civil_commotion", "subscribed": "yes", "ceiling": None, "page": 15, "clause_id": 2, "quote": "émeutes"},
    {"guarantee": "glass", "subscribed": "yes", "ceiling": None, "page": 14, "clause_id": 3, "quote": "vitrines"},
    {"guarantee": "business_interruption", "subscribed": "yes", "deductible_detail": {"amount": 3, "unit": "days"}, "page": 41, "clause_id": 4, "quote": "marge brute"},
    {"guarantee": "bailed_goods", "subscribed": "unknown", "page": 22, "clause_id": 5},
    {"guarantee": "assessor_fees", "subscribed": "no"},
]


def item(key, label, amount=None, **detail):
    return {"id": "x", "catalog_key": key, "label": label, "amount_claimed_eur": amount, "computation_detail": detail}


def test_stolen_stock_goes_to_theft_and_is_capped():
    m = covers.match_item(item("stock", "Smartphones stolen", 39600), COVERAGE, "riot_damage")
    assert m["status"] == "capped" and m["guarantee"] == "theft_vandalism" and m["cap_eur"] == 15000 and m["page"] == 19


def test_damaged_stock_goes_to_riot_cover_not_theft():
    m = covers.match_item(item("stock", "Smartphones damaged by glass", 2000), COVERAGE, "riot_damage")
    assert m["status"] == "covered" and m["guarantee"] == "riot_civil_commotion"


def test_shopfront_uses_glass_cover():
    m = covers.match_item(item("shopfront_glass", "Shop window", 3600), COVERAGE, "riot_damage")
    assert m["guarantee"] == "glass" and m["status"] == "covered"


def test_unknown_specific_cover_falls_back_but_is_flagged():
    m = covers.match_item(item("bailed_goods", "Customer phones in repair", 7500), COVERAGE, "theft")
    assert m["status"] == "covered" and m["guarantee"] == "theft_vandalism"
    assert m["specific_cover_unknown"] == "bailed_goods" and "not established" in m["note"]


def test_unknown_only_candidate_stays_unknown_never_no():
    cov = [{"guarantee": "bailed_goods", "subscribed": "unknown", "page": 22, "clause_id": 5}]
    m = covers.match_item(item("bailed_goods", "Customer phones in repair", 7500), cov, "theft")
    assert m["status"] == "unknown" and m["guarantee"] == "bailed_goods"


def test_not_subscribed_is_no_cover_found():
    m = covers.match_item(item("assessor_fees", "Loss assessor fees", 2000), COVERAGE, "theft")
    assert m["status"] == "no_cover_found" and "assessor_fees" in m["note"]


def test_state_recourse_is_not_insurance():
    m = covers.match_item(item("state_recourse_remainder", "Remainder from the State", 10000), COVERAGE, "riot_damage")
    assert m["status"] == "not_insurance" and "L211-10" in m["note"]


def test_bi_item_created_without_amount_when_subscribed():
    bi = covers.ensure_bi_item({"coverage": COVERAGE, "loss_items": []}, 28)
    assert bi and bi["amount_claimed_eur"] is None and bi["status"] == "unsupported" and bi["clause_page"] == 41
    assert "3 days" in bi["condition_note"]
    assert covers.ensure_bi_item({"coverage": COVERAGE, "loss_items": [{"catalog_key": "business_interruption"}]}, 28) is None


def test_digest_asks_count_and_satisfy():
    now = datetime(2026, 10, 22, tzinfo=timezone.utc)
    d = {"claim_id": "c", "open_asks": []}
    digest.record_asks(d, ["police complaint receipt", "supplier invoices"], now)
    digest.record_asks(d, ["police complaint receipt"], now)
    assert [a["times"] for a in d["open_asks"]] == [2, 1]
    closed = digest.mark_satisfied(d, {"invoice"}, now)
    assert closed == ["supplier invoices"]
    assert [a["item"] for a in digest.open_asks(d)] == ["police complaint receipt"]


def test_contradiction_oral_vs_written_same_topic():
    ps = [
        {"status": "oral_to_confirm", "topic": "cap", "position_verbatim": "the riot extension applies to stock", "at": "2026-10-22T10:00"},
        {"status": "written", "topic": "cap", "position_verbatim": "stock under theft cover, 15 000 € cap", "at": "2026-10-23T09:00"},
        {"status": "written", "topic": "document_request", "position_verbatim": "merci de transmettre la plainte", "at": "2026-10-23T09:00"},
    ]
    pairs = positions.contradictions(ps)
    assert len(pairs) == 1 and pairs[0][0]["status"] == "oral_to_confirm"


def test_profile_description_needs_two_claims():
    assert profiles.describe({"claims_count": 1, "insurer_name": "MAAF"}) is None
    s = profiles.describe({"claims_count": 3, "insurer_name": "MAAF", "avg_first_reply_hours": 26.5, "avg_first_offer_ratio": 0.23, "documents_requested": {"police_report": 3}})
    assert "3 files" in s and "26.5 h" in s and "23%" in s and "police report" in s
