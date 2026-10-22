"""Evidence-driven items: an invoice, quote or inventory the client sends documents a loss even if
the client never described it. Amounts come from the document (HT/TTC per VAT status), the catalog
key from the bilingual cues, the clause from the cover match. Deterministic — no model involved.

Business interruption is computed only when every input is on file: monthly turnover and gross
margin rate from an accounting document, closure period stated by the client, deductible from the
policy. The formula and its inputs are recorded; the agent never estimates a figure.
"""

from __future__ import annotations

import re
from typing import Any

from app.agents.claims import tools_impl as T
from app.agents.claims.brain import covers
from app.agents.claims.brain.recompute import CUES, INVOICE_TYPES, select_document_amount
from app.contracts import LossItemInput

ITEM_TYPES = INVOICE_TYPES | {"inventory"}
LABELS = {"stock": "Stock (goods for resale)", "spare_parts": "Spare parts and accessories", "equipment": "Professional equipment", "shutter": "Metal shutter",
          "shopfront_glass": "Shop window and glazing", "signage_lettering": "Window lettering", "sign_awning": "Sign / awning", "locks": "Locks",
          "tenant_fit_out": "Tenant fit-out and furniture", "guarding_boarding": "Guarding and boarding-up", "debris_cleaning": "Cleaning and debris removal",
          "graffiti": "Graffiti removal", "cash": "Cash", "bailed_goods": "Customers' goods held in the shop", "archives": "Archives reconstitution",
          "storage_relocation": "Storage and relocation", "temporary_premises": "Temporary premises", "architect_fees": "Architect / designer fees",
          "compliance_upgrades": "Compliance upgrades", "extra_operating_costs": "Extra operating costs"}
_CA_RE = re.compile(r"(?:CA|chiffre d'affaires|turnover)[^0-9]{0,30}(\d[\d\s\u202f\u00a0.,]*\d)\s?(?:€|EUR)?", re.I)
_MARGIN_RE = re.compile(r"(?:marge brute|gross margin)[^0-9]{0,30}(\d{1,2}(?:[.,]\d+)?)\s?%", re.I)


def _key_for(evidence: dict[str, Any]) -> str | None:
    text = " ".join(filter(None, [evidence.get("description"), evidence.get("vendor"), " ".join((evidence.get("extracted") or {}).get("facts") or [])])).lower()
    if any(w in text for w in ("réassort", "restock", "prêt de matériel", "dépôt de pain", "signalétique", "frais supplémentaires", "local provisoire")):
        return "extra_operating_costs"
    if any(w in text for w in ("client", "customer", "prêts à livrer", "en réparation", "confié")):
        return "bailed_goods"
    # Service invoices (cleaning, guarding, fees) name the equipment they act on; check them before contents keys.
    order = ["debris_cleaning", "guarding_boarding", "graffiti", "architect_fees", "compliance_upgrades", "storage_relocation", "temporary_premises",
             "signage_lettering", "sign_awning", "shutter", "shopfront_glass", "locks", "tenant_fit_out", "spare_parts", "equipment", "stock", "cash", "archives"]
    best, best_score = None, 0
    for key in order:
        s = sum(1 for c in CUES.get(key, ()) if c in text)
        if s > best_score:
            best, best_score = key, s
    return best


def _num(s: str) -> float:
    s = s.replace("\u202f", "").replace("\u00a0", "").replace(" ", "")
    if re.search(r"[.,]\d{1,2}$", s):
        s = s[:-3].replace(".", "").replace(",", "") + "." + s[-2:]
    else:
        s = s.replace(".", "").replace(",", "")
    return float(s)


def parse_accounting(description: str) -> tuple[float | None, float | None]:
    text = re.sub(r"\bN[-−]\s?\d\b", "", description or "")  # "N-1", "N-2" are year labels, not digits of the amount
    ca = _CA_RE.search(text)
    mg = _MARGIN_RE.search(text)
    return (_num(ca.group(1)) if ca else None), (float(mg.group(1).replace(",", ".")) / 100 if mg else None)


async def create_items_from_evidence(claim_id: str, memory: dict[str, Any], new_evidence_ids: list[str]) -> list[dict[str, Any]]:
    ev_by_id = {str(e["id"]): e for e in memory.get("evidence", [])}
    vat = (memory.get("business") or {}).get("vat_recoverable")
    already = {str(x) for li in memory.get("loss_items", []) for x in (li.get("evidence_ids") or [])}
    existing_keys = {li.get("catalog_key") for li in memory.get("loss_items", [])}
    groups: dict[str, list[dict[str, Any]]] = {}
    for eid in new_evidence_ids:
        e = ev_by_id.get(eid)
        if not e or e.get("duplicate_of") or e.get("evidence_type") not in ITEM_TYPES or eid in already or e.get("amount_eur") is None:
            continue
        key = _key_for(e)
        if key and key not in existing_keys:
            groups.setdefault(key, []).append(e)
    loss_type = (memory.get("claim") or {}).get("loss_type")
    inputs = []
    for key, evs in groups.items():
        by_doc: dict[str, list[dict[str, Any]]] = {}
        for e in evs:
            by_doc.setdefault(str(e.get("document_id") or e["id"]), []).append(e)
        per_doc = {d: a for d, a in ((d, select_document_amount(rows, vat)) for d, rows in by_doc.items()) if a is not None}
        if not per_doc:
            continue
        total = round(sum(per_doc.values()), 2)
        m = covers.match_item({"catalog_key": key, "label": LABELS.get(key, key), "amount_claimed_eur": total, "computation_detail": {}}, memory.get("coverage", []), loss_type)
        inputs.append(LossItemInput(
            catalog_key=key, label=LABELS.get(key, key), category="contents" if key in ("stock", "spare_parts", "equipment", "cash", "bailed_goods") else "property",
            amount_claimed_eur=total, amount_basis="invoice" if any(e.get("evidence_type") in INVOICE_TYPES for e in evs) else "client_instruction",
            computation=" + ".join(f"{a:,.2f} €".replace(",", " ") for a in per_doc.values()) + (f" = {total:,.2f} €".replace(",", " ") if len(per_doc) > 1 else ""),
            computation_detail={"from_documents": per_doc, "vat_basis": "HT" if vat else "TTC", "cover": m},
            evidence_ids=[str(e["id"]) for e in evs], clause_id=m.get("clause_id"), clause_page=m.get("page"), clause_quote=m.get("quote"),
            condition_note=m.get("note"), status="supported" if m.get("status") in ("covered", "capped", "unknown") else ("no_cover_found" if m.get("status") == "no_cover_found" else "supported"),
        ))
    return await T.update_loss_statement(claim_id, inputs) if inputs else []


async def compute_business_interruption(claim_id: str, memory: dict[str, Any], closure_days: float | None) -> dict[str, Any] | None:
    """BI = (closure days − deductible days) / 30 × monthly turnover × gross margin rate. All inputs must be on file."""
    cov = next((c for c in memory.get("coverage", []) if c["guarantee"] == "business_interruption" and c.get("subscribed") == "yes"), None)
    if not cov or not closure_days:
        return None
    acct = [e for e in memory.get("evidence", []) if e.get("evidence_type") == "accounting" and not e.get("duplicate_of")]
    ca = margin = None
    for e in acct:
        c, mg = parse_accounting(e.get("description") or "")
        ca, margin = ca or c, margin or mg
    if ca is None or margin is None:
        return None
    ded = cov.get("deductible_detail") if isinstance(cov.get("deductible_detail"), dict) else None
    ded_days = float(ded["amount"]) if ded and ded.get("unit", "").startswith("day") and ded.get("amount") is not None else 0.0
    months = max(0.0, float(closure_days) - ded_days) / 30.0
    total = round(months * ca * margin, 2)
    bi = LossItemInput(
        catalog_key="business_interruption", label="Business interruption (loss of gross margin)", category="business_interruption", amount_claimed_eur=total,
        amount_basis="formula", computation=f"({closure_days:g} − {ded_days:g} days) / 30 × {ca:,.0f} € × {margin:.0%} = {total:,.2f} €".replace(",", " "),
        computation_detail={"closure_days": closure_days, "deductible_days": ded_days, "monthly_turnover_eur": ca, "gross_margin_rate": margin,
                            "inputs": {"turnover_and_margin": [str(e["id"]) for e in acct], "closure_days": "client statement"}},
        evidence_ids=[str(e["id"]) for e in acct], clause_id=cov.get("clause_id") or cov.get("source_clause_id"), clause_page=cov.get("page"), clause_quote=cov.get("quote"),
        condition_note="Loss of gross margin over the closure period, net of the policy's day deductible; saved costs and short-time work compensation to be deducted when known.",
        status="supported",
    )
    rows = await T.update_loss_statement(claim_id, [bi])
    return rows[0] if rows else None
