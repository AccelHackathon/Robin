"""AC-13 — retail-stated stock is recomputed at purchase price from supplier invoices (pure logic)."""

from app.agents.claims.brain import recompute as R

STOCK_RETAIL = {"id": "i1", "label": "Smartphones stolen", "catalog_key": "stock", "status": "unsupported", "amount_basis": "client_instruction",
                "amount_claimed_eur": 120000.0, "computation_detail": {"value_basis": "retail"}, "evidence_ids": [], "clause_id": None}
SHUTTER = {"id": "i2", "label": "Metal shutter", "catalog_key": "shutter", "status": "unsupported", "amount_basis": "client_instruction",
           "amount_claimed_eur": 3500.0, "computation_detail": {"value_basis": "estimate"}, "evidence_ids": []}
BI = {"id": "i3", "label": "Business interruption", "catalog_key": "business_interruption", "status": "unsupported", "amount_basis": None,
      "amount_claimed_eur": None, "computation_detail": {}, "evidence_ids": []}

INV_HT = {"id": "e1", "document_id": "d1", "evidence_type": "invoice", "description": "total HT", "amount_eur": 33000.0, "vendor": "TechDistrib SAS", "extracted": {"facts": ["smartphones reconditionnés"]}}
INV_TTC = {"id": "e2", "document_id": "d1", "evidence_type": "invoice", "description": "total TTC", "amount_eur": 39600.0, "vendor": "TechDistrib SAS"}
INV2_HT = {"id": "e3", "document_id": "d2", "evidence_type": "invoice", "description": "total HT", "amount_eur": 6600.0, "vendor": "PhoneParts"}
PHOTO = {"id": "e4", "document_id": "d3", "evidence_type": "photo", "description": "broken window", "amount_eur": None}
SHUTTER_QUOTE = {"id": "e5", "document_id": "d4", "evidence_type": "quote", "description": "devis rideau métallique motorisé — total HT", "amount_eur": 3200.0, "vendor": "Fermetures Sud"}


def test_amount_selection_prefers_vat_basis():
    assert R.select_document_amount([INV_HT, INV_TTC], True) == 33000.0
    assert R.select_document_amount([INV_HT, INV_TTC], False) == 39600.0
    assert R.select_document_amount([{"description": "montant", "amount_eur": 10.0}], True) == 10.0


def test_invoice_matches_stock_by_tokens_or_uniqueness():
    assert [li["id"] for li in R.candidate_items(INV_HT, [STOCK_RETAIL, SHUTTER, BI])] == ["i1"]      # "smartphones" overlap
    assert [li["id"] for li in R.candidate_items(INV2_HT, [STOCK_RETAIL, SHUTTER, BI])] == ["i1"]     # no overlap → unique stock item
    assert [li["id"] for li in R.candidate_items(SHUTTER_QUOTE, [STOCK_RETAIL, SHUTTER, BI])] == ["i2"]  # French "rideau" → shutter via cues, never the stock fallback
    unmatched_quote = {"id": "e9", "document_id": "d9", "evidence_type": "quote", "description": "devis divers", "amount_eur": 500.0}
    assert R.candidate_items(unmatched_quote, [STOCK_RETAIL, SHUTTER]) == []  # a quote with no cue is never guessed
    assert R.candidate_items(PHOTO, [STOCK_RETAIL]) == []
    assert R.candidate_items(INV_HT, [BI]) == []  # BI is never recomputed from invoices


def test_ac13_retail_replaced_by_invoice_purchase_price():
    out = R.build_recomputed(STOCK_RETAIL, [INV_HT, INV_TTC, INV2_HT], True, {"id": 77, "page": 79, "body": "évaluées au prix d'achat calculé au cours du jour"})
    assert out.amount_claimed_eur == 39600.0            # 33 000 HT (doc 1) + 6 600 HT (doc 2), TTC row ignored
    assert out.amount_basis == "invoice" and out.status == "supported"
    assert out.evidence_ids == ["e1", "e2", "e3"] and out.clause_page == 79
    assert "120 000 €" in out.condition_note and "purchase price" in out.condition_note
    assert out.computation_detail["previous_amount_eur"] == 120000.0 and out.computation_detail["vat_basis"] == "HT"


def test_ttc_when_vat_not_recovered():
    out = R.build_recomputed(STOCK_RETAIL, [INV_HT, INV_TTC], False, None)
    assert out.amount_claimed_eur == 39600.0 and out.computation_detail["vat_basis"] == "TTC"
