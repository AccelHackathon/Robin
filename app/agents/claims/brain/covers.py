"""Loss item ↔ cover matching (PRD 2.4; research 08a/08b §5, 09a).

For each current loss item, find the cover(s) in the account's coverage_profile that can
indemnify it given the nature of the loss, then record: subscribed (yes/no/unknown), cap,
deductible, the clause and page, and a status. The agent never invents a cap — every figure
comes from a coverage_profile row that itself cites a clause.

Ventilation rule (08a: AXA excludes theft from the riot cover; MAAF routes riot damage through
the subscribed covers): *stolen* contents go to theft_vandalism; *damaged* property goes to
the damage cover (riot / glass / fire); fees follow the cover that triggered them.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app import db
from app.agents.audit import record_action

log = logging.getLogger(__name__)

# catalog_key → ordered list of candidate coverage guarantees (first subscribed wins).
# Keys on the right are workstream B's canonical guarantee keys (app/agents/intake/guarantees.py).
CANDIDATES: dict[str, dict[str, list[str]]] = {
    # contents: stolen → theft; damaged → riot / fire
    "stock":          {"stolen": ["theft_vandalism"], "damaged": ["riot_civil_commotion", "fire", "theft_vandalism"]},
    "spare_parts":    {"stolen": ["theft_vandalism"], "damaged": ["riot_civil_commotion", "fire", "theft_vandalism"]},
    "equipment":      {"stolen": ["theft_vandalism"], "damaged": ["riot_civil_commotion", "equipment_replacement_value", "fire", "theft_vandalism"]},
    "cash":           {"stolen": ["cash", "theft_vandalism"], "damaged": ["cash"]},
    "bailed_goods":   {"stolen": ["bailed_goods", "theft_vandalism"], "damaged": ["bailed_goods", "riot_civil_commotion"]},
    # property
    "shopfront_glass":   {"*": ["glass", "riot_civil_commotion"]},
    "shutter":           {"*": ["glass", "theft_vandalism", "riot_civil_commotion"]},
    "signage_lettering": {"*": ["glass", "riot_civil_commotion"]},
    "sign_awning":       {"*": ["glass", "riot_civil_commotion"]},
    "locks":             {"*": ["locks", "theft_vandalism"]},
    "tenant_fit_out":    {"*": ["tenant_fit_out", "riot_civil_commotion", "theft_vandalism"]},
    # fees
    "guarding_boarding":    {"*": ["guarding_boarding", "glass", "theft_vandalism"]},
    "debris_cleaning":      {"*": ["debris", "riot_civil_commotion"]},
    "graffiti":             {"*": ["graffiti", "theft_vandalism"]},
    "indirect_losses":      {"*": ["indirect_losses"]},
    "assessor_fees":        {"*": ["assessor_fees"]},
    "archives":             {"*": ["riot_civil_commotion", "theft_vandalism"]},
    "storage_relocation":   {"*": ["riot_civil_commotion", "fire"]},
    "temporary_premises":   {"*": ["business_interruption", "riot_civil_commotion"]},
    "architect_fees":       {"*": ["riot_civil_commotion", "fire"]},
    "compliance_upgrades":  {"*": ["riot_civil_commotion", "fire"]},
    "deferred_depreciation": {"*": ["equipment_replacement_value", "riot_civil_commotion"]},
    "outstanding_leasing":  {"*": ["equipment_replacement_value"]},
    # business interruption
    "business_interruption": {"*": ["business_interruption"]},
    "extra_operating_costs": {"*": ["business_interruption"]},
    "seals_prolonging_bi":   {"*": ["business_interruption"]},
    "goodwill_loss":         {"*": ["business_interruption"]},
    # recourse (not an insurance cover)
    "state_recourse_remainder": {"*": []},
}

STOLEN_TYPES = {"theft", "riot_damage", "vandalism"}  # looting = theft during riot damage


def _mode(item: dict[str, Any], loss_type: str | None) -> str:
    detail = item.get("computation_detail") or {}
    if detail.get("damage_mode") in ("stolen", "damaged"):
        return detail["damage_mode"]
    label = (item.get("label") or "").lower()
    if any(w in label for w in ("stolen", "volé", "looted", "taken", "missing")):
        return "stolen"
    if any(w in label for w in ("broken", "damaged", "cassé", "brisé", "endommag", "destroyed")):
        return "damaged"
    return "stolen" if (loss_type in STOLEN_TYPES) else "damaged"


def _cap_text(cov: dict[str, Any]) -> tuple[str | None, float | None]:
    c = cov.get("ceiling") if isinstance(cov.get("ceiling"), dict) else None
    if not c and cov.get("ceiling_eur") is not None:
        c = {"amount": float(cov["ceiling_eur"]), "unit": "EUR"}
    if not c or c.get("amount") is None:
        return None, None
    unit = c.get("unit", "EUR")
    amt = float(c["amount"])
    if unit == "EUR":
        return f"{amt:,.0f} €".replace(",", " "), amt
    return f"{amt:g} {unit.replace('_', ' ')}", None


def match_item(item: dict[str, Any], coverage: list[dict[str, Any]], loss_type: str | None) -> dict[str, Any]:
    key = item.get("catalog_key")
    if not key or key not in CANDIDATES:
        return {"status": "unmapped", "guarantee": None}
    table = CANDIDATES[key]
    mode = _mode(item, loss_type)
    candidates = table.get(mode) or table.get("*") or []
    if not candidates:
        return {"status": "not_insurance", "guarantee": None, "note": "claimable from the State under L211-10 CSI, not from the insurer"}
    by_key = {c["guarantee"]: c for c in coverage}
    chosen, first_unknown = None, None
    for g in candidates:
        cov = by_key.get(g)
        if not cov:
            continue
        if cov.get("subscribed") == "yes":
            chosen = cov
            break
        if cov.get("subscribed") == "unknown" and first_unknown is None:
            first_unknown = cov
    if chosen is None and first_unknown is not None:
        cov = first_unknown
        return {"status": "unknown", "guarantee": cov["guarantee"], "mode": mode, "clause_id": cov.get("clause_id") or cov.get("source_clause_id"),
                "page": cov.get("page"), "quote": cov.get("quote"), "note": "cover not established from the documents received (policy schedule missing?)"}
    if chosen is None:
        known_no = [g for g in candidates if by_key.get(g, {}).get("subscribed") == "no"]
        return {"status": "no_cover_found", "guarantee": None, "mode": mode,
                "note": f"candidate covers not subscribed: {', '.join(known_no)}" if known_no else "no matching cover in the profile"}
    cap_text, cap_eur = _cap_text(chosen)
    ded = chosen.get("deductible_detail") if isinstance(chosen.get("deductible_detail"), dict) else None
    amount = float(item["amount_claimed_eur"]) if item.get("amount_claimed_eur") is not None else None
    capped = cap_eur is not None and amount is not None and amount > cap_eur
    notes = []
    if capped:
        notes.append(f"amount exceeds the {cap_text} cap of the {chosen['guarantee']} cover")
    # A more specific cover listed before the chosen one is still unknown: say so, never assume it is absent.
    if first_unknown is not None and candidates.index(first_unknown["guarantee"]) < candidates.index(chosen["guarantee"]):
        notes.append(f"specific cover {first_unknown['guarantee']} not established from the documents received; "
                     f"falls under {chosen['guarantee']} only if its definition of insured contents includes these goods")
    return {
        "status": "capped" if capped else "covered", "guarantee": chosen["guarantee"], "mode": mode,
        "cap": cap_text, "cap_eur": cap_eur, "deductible": ded, "conditions": chosen.get("conditions") or [],
        "clause_id": chosen.get("clause_id") or chosen.get("source_clause_id"), "page": chosen.get("page"), "quote": chosen.get("quote"),
        "note": "; ".join(notes) or None, "specific_cover_unknown": first_unknown["guarantee"] if first_unknown is not None else None,
    }


async def match_claim(claim_id: str, memory: dict[str, Any]) -> list[dict[str, Any]]:
    """Match every current loss item; persist the result in computation_detail.cover and the status."""
    loss_type = (memory.get("claim") or {}).get("loss_type")
    results = []
    async with db.pool.connection() as conn:
        for item in memory.get("loss_items", []):
            m = match_item(item, memory.get("coverage", []), loss_type)
            detail = dict(item.get("computation_detail") or {})
            detail["cover"] = m
            new_status = item.get("status")
            if m["status"] == "no_cover_found" and item.get("status") in ("unsupported", "supported"):
                new_status = "no_cover_found"
            clause_id = item.get("clause_id") or m.get("clause_id")
            page = item.get("clause_page") or m.get("page")
            quote = item.get("clause_quote") or m.get("quote")
            await conn.execute(
                "UPDATE loss_items SET computation_detail = %s, status = %s, clause_id = %s, clause_page = %s, clause_quote = %s WHERE id = %s",
                (json.dumps(detail, default=str), new_status, clause_id, page, quote, item["id"]),
            )
            results.append({"item": item.get("label"), **m})
        await conn.commit()
    await record_action("claims", "match_covers", {"claim_id": claim_id, "items": len(results)},
                        {"statuses": {r["status"]: sum(1 for x in results if x["status"] == r["status"]) for r in results}}, claim_id=claim_id)
    return results


def ensure_bi_item(memory: dict[str, Any], closure_days: float | None) -> dict[str, Any] | None:
    """If business interruption is subscribed and the shop closed, make the BI item exist as *unsupported*
    with the inputs it needs — never with a number the agent made up."""
    cov = next((c for c in memory.get("coverage", []) if c["guarantee"] == "business_interruption"), None)
    if not cov or cov.get("subscribed") != "yes":
        return None
    if any(li.get("catalog_key") == "business_interruption" for li in memory.get("loss_items", [])):
        return None
    ded = cov.get("deductible_detail") if isinstance(cov.get("deductible_detail"), dict) else None
    need = ["monthly turnover N-1 and N-2 (tax returns or accountant export)", "gross margin rate (turnover minus variable costs)",
            "exact closure period (reopening date)"]
    note = ("Business interruption is subscribed" + (f" (p. {cov['page']})" if cov.get("page") else "") +
            (f", deductible {ded.get('amount')} {ded.get('unit', '')}" if ded and ded.get("amount") is not None else "") +
            ". Indemnity = loss of gross margin over the closure period, minus saved costs, plus extra operating costs. Needed: " + "; ".join(need) + ".")
    return {"catalog_key": "business_interruption", "label": "Business interruption (loss of gross margin)", "category": "business_interruption",
            "amount_claimed_eur": None, "amount_basis": None, "computation": None,
            "computation_detail": {"inputs_needed": need, "closure_days_stated": closure_days, "formula": "perte de CA × taux de marge brute − charges économisées + frais supplémentaires"},
            "evidence_ids": [], "clause_id": cov.get("clause_id") or cov.get("source_clause_id"), "clause_page": cov.get("page"), "clause_quote": cov.get("quote"),
            "condition_note": note, "status": "unsupported"}
