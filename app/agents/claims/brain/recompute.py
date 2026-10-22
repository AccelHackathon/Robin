"""AC-13: when supplier invoices arrive, recompute client-stated items at purchase price.

A client who says "180 phones, 220 € each" has stated a value; a client who says "120 000 €
at retail" has stated the wrong basis (policies indemnify stock at purchase price — MAAF p. 79,
AXA p. 57, Generali p. 50). Either way the item stays `unsupported` until invoices land. This
module attaches each new invoice to the item it documents and writes a new item version whose
amount is the sum of invoice amounts — HT when the business recovers VAT (MAAF p. 80), TTC
otherwise. The agent never picks the number: the invoices do.
"""

from __future__ import annotations

import re
from typing import Any

from app.agents.claims import tools_impl as T
from app.contracts import LossItemInput

_STOP = {"the", "and", "les", "des", "de", "du", "la", "le", "en", "of", "in", "stolen", "damaged", "volé", "volés", "units", "unit", "x"}
INVOICE_TYPES = {"invoice", "quote"}
RECOMPUTABLE_BASES = {None, "client_instruction"}
RECOMPUTABLE_VALUE_BASES = {"retail", "estimate", "unknown", "purchase", None}


def _tokens(*texts: str | None) -> set[str]:
    out: set[str] = set()
    for t in texts:
        for w in re.findall(r"[a-zà-ÿ0-9]{3,}", (t or "").lower()):
            if w not in _STOP:
                out.add(w.rstrip("s"))
    return out


def select_document_amount(rows: list[dict[str, Any]], vat_recoverable: bool | None) -> float | None:
    """One amount per invoice document: 'total HT' if VAT is recovered, 'total TTC' otherwise, else the largest."""
    amounts = [(r.get("description") or "", float(r["amount_eur"])) for r in rows if r.get("amount_eur") is not None]
    if not amounts:
        return None
    want = "ht" if vat_recoverable else "ttc"
    for label, a in amounts:
        if re.search(rf"\b{want}\b", label.lower()) and "total" in label.lower():
            return a
    for label, a in amounts:
        if re.search(rf"\b{want}\b", label.lower()):
            return a
    return max(a for _, a in amounts)


# Bilingual cues per catalog key so a French quote ("rideau métallique") finds the English-labelled item ("Metal shutter").
CUES: dict[str, set[str]] = {
    "stock": {"stock", "marchandise", "matières premières", "matiere", "production", "denrées", "smartphone", "téléphone", "telephone", "phone", "article", "produit", "monture", "lunette", "appareil"},
    "spare_parts": {"pièce", "piece", "accessoire", "accessory", "part", "écran", "batterie"},
    "equipment": {"matériel", "equipment", "machine", "station", "microscope", "caisse", "till", "ordinateur", "computer", "tpe", "four", "vitrine réfrigérée"},
    "shutter": {"rideau", "volet", "shutter", "grille"},
    "shopfront_glass": {"vitrine", "vitrage", "verre", "glass", "window", "glace", "porte vitrée"},
    "signage_lettering": {"vitrophanie", "lettrage", "lettering", "adhésif"},
    "sign_awning": {"enseigne", "store", "banne", "awning", "sign"},
    "locks": {"serrure", "lock", "cylindre", "badge"},
    "tenant_fit_out": {"agencement", "aménagement", "fit-out", "mobilier", "présentoir", "comptoir", "faux plafond", "peinture"},
    "guarding_boarding": {"gardiennage", "vigile", "guard", "clôture", "boarding", "contreplaqué", "panneau"},
    "debris_cleaning": {"nettoyage", "déblais", "cleaning", "débarras", "décontamination", "benne"},
    "graffiti": {"tag", "graffiti", "nettoyage tag"},
    "cash": {"espèces", "cash", "caisse"},
    "bailed_goods": {"client", "customer", "confié", "réparation", "repair"},
    "archives": {"archive", "document", "reconstitution"},
    "storage_relocation": {"garde-meuble", "storage", "déménagement", "transport"},
    "temporary_premises": {"local provisoire", "loyer", "temporary", "premises"},
    "architect_fees": {"architecte", "architect", "décorateur", "bureau d'études"},
    "compliance_upgrades": {"mise en conformité", "conformité", "compliance"},
}


def _cue_score(ev_text: str, key: str | None) -> int:
    return sum(1 for cue in CUES.get(key or "", ()) if cue in ev_text)


def candidate_items(evidence: dict[str, Any], items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Items this invoice can document, best first. Only client-stated, still-unsupported contents items qualify."""
    if evidence.get("evidence_type") not in INVOICE_TYPES or evidence.get("duplicate_of"):
        return []
    pool = [li for li in items if li.get("status") == "unsupported" and li.get("amount_basis") in RECOMPUTABLE_BASES
            and ((li.get("computation_detail") or {}).get("value_basis") in RECOMPUTABLE_VALUE_BASES)
            and li.get("catalog_key") not in ("business_interruption", "extra_operating_costs", "state_recourse_remainder")]
    if not pool:
        return []
    ev_text = " ".join(filter(None, [evidence.get("description"), evidence.get("vendor"), " ".join((evidence.get("extracted") or {}).get("facts") or [])])).lower()
    ev_tokens = _tokens(ev_text)
    scored = []
    for li in pool:
        score = len(ev_tokens & _tokens(li.get("label"), li.get("catalog_key"))) + 2 * _cue_score(ev_text, li.get("catalog_key"))
        scored.append((score, li))
    scored.sort(key=lambda x: -x[0])
    if scored[0][0] > 0:
        return [li for s, li in scored if s == scored[0][0]]
    # No cue at all: a plain supplier *invoice* (not a quote) documents the stock item if exactly one exists.
    if evidence.get("evidence_type") != "invoice":
        return []
    stock = [li for li in pool if li.get("catalog_key") in ("stock", "spare_parts", "equipment")]
    return stock if len(stock) == 1 else []


def build_recomputed(item: dict[str, Any], linked_evidence: list[dict[str, Any]], vat_recoverable: bool | None,
                     clause: dict[str, Any] | None) -> LossItemInput | None:
    """New version of `item` whose amount is the sum of one selected amount per linked invoice document."""
    by_doc: dict[str, list[dict[str, Any]]] = {}
    for e in linked_evidence:
        by_doc.setdefault(str(e.get("document_id") or e["id"]), []).append(e)
    per_doc = {d: select_document_amount(rows, vat_recoverable) for d, rows in by_doc.items()}
    per_doc = {d: a for d, a in per_doc.items() if a is not None}
    if not per_doc:
        return None
    total = round(sum(per_doc.values()), 2)
    prior = item.get("amount_claimed_eur")
    basis_note = "HT (VAT recovered by the business)" if vat_recoverable else "TTC (VAT not recovered)"
    stated = (item.get("computation_detail") or {}).get("value_basis")
    note = f"Recomputed from {len(per_doc)} supplier invoice(s) at purchase price, {basis_note}."
    if stated == "retail" and prior is not None:
        note += f" The client's retail-price statement ({float(prior):,.0f} €) is replaced: stock is indemnified at purchase price.".replace(",", " ")
    if clause:
        note += f" Clause p. {clause.get('page')}."
    detail = dict(item.get("computation_detail") or {})
    detail.update({"recomputed_from_invoices": per_doc, "vat_basis": "HT" if vat_recoverable else "TTC", "previous_amount_eur": prior})
    return LossItemInput(
        catalog_key=item.get("catalog_key"), label=item["label"], category=item.get("category"), amount_claimed_eur=total, amount_basis="invoice",
        computation=" + ".join(f"{a:,.2f} €".replace(",", " ") for a in per_doc.values()) + f" = {total:,.2f} €".replace(",", " "),
        computation_detail=detail, evidence_ids=[str(e["id"]) for e in linked_evidence],
        clause_id=item.get("clause_id") or (clause or {}).get("id"), clause_page=item.get("clause_page") or (clause or {}).get("page"),
        clause_quote=item.get("clause_quote") or ((clause or {}).get("body") or "")[:200] or None, condition_note=note, status="supported",
    )


async def recompute_from_evidence(claim_id: str, memory: dict[str, Any], new_evidence_ids: list[str]) -> list[dict[str, Any]]:
    """Attach each new invoice to the item it documents and write the recomputed version. Returns the new rows."""
    evidence_by_id = {str(e["id"]): e for e in memory.get("evidence", [])}
    vat = (memory.get("business") or {}).get("vat_recoverable")
    clause = None
    updates: dict[str, tuple[dict[str, Any], list[dict[str, Any]]]] = {}
    for eid in new_evidence_ids:
        e = evidence_by_id.get(eid)
        if not e:
            continue
        targets = candidate_items(e, memory.get("loss_items", []))
        if len(targets) != 1:
            continue  # ambiguous: leave it to the client question path rather than guess
        item = targets[0]
        key = str(item["id"])
        if key not in updates:
            linked = [evidence_by_id[x] for x in (item.get("evidence_ids") or []) if str(x) in evidence_by_id]
            updates[key] = (item, linked)
        updates[key][1].append(e)
    if not updates:
        return []
    if any((it.get("computation_detail") or {}).get("value_basis") == "retail" and not it.get("clause_id") for it, _ in updates.values()):
        from app.agents.claims.nodes.analyze import _find_clause

        c = await _find_clause(memory, "marchandises prix d'achat valeur")
        clause = {"id": c.id, "page": c.page, "body": c.body} if c else None
    inputs = [build_recomputed(it, linked, vat, clause) for it, linked in updates.values()]
    inputs = [i for i in inputs if i]
    return await T.update_loss_statement(claim_id, inputs) if inputs else []
