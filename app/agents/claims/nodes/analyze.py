"""`analyze` node: turn the inbound event into facts, evidence and loss items (PRD 2.3, 2.4, 2.6).

Deterministic part. Document reading and narrative extraction call `llm.py` when a model is
configured; without one, documents are still registered as evidence (with dedup) and the client
text is still logged as a fact, so the flow is demonstrable end to end.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from psycopg.rows import dict_row

from app import db
from app.agents.claims import tools_impl as T
from app.agents.claims.brain import covers, positions, profiles
from app.contracts import LossItemInput
from app.agents.review.amounts import extract_amounts_eur
from app.agents.review.rules import has_release_language

_OFFER_RE = re.compile(r"\b(offre|proposition d'indemnisation|indemnit[ée]|r[èe]glement|quittance|settlement|offer)\b", re.IGNORECASE)


def looks_like_offer(text: str) -> bool:
    return bool(_OFFER_RE.search(text or "")) and bool(extract_amounts_eur(text or ""))


def _evidence_type(mime: str | None, caption: str | None) -> str:
    c = (caption or "").lower()
    if any(w in c for w in ("facture", "invoice", "devis", "quote")):
        return "invoice"
    if any(w in c for w in ("plainte", "police", "récépissé")):
        return "police_report"
    if any(w in c for w in ("inventaire", "inventory", "stock")):
        return "inventory"
    if (mime or "").startswith("image/"):
        return "photo"
    return "document"


async def _document(doc_id: str) -> dict[str, Any] | None:
    async with db.pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT id, sha256, mime_type, filename, doc_type, extracted_text FROM documents WHERE id = %s", (doc_id,))
        r = await cur.fetchone()
        return dict(r) if r else None


async def _attach_document_to_claim(doc_id: str, claim_id: str) -> None:
    async with db.pool.connection() as conn:
        await conn.execute("UPDATE documents SET claim_id = %s WHERE id = %s AND claim_id IS NULL", (claim_id, doc_id))
        await conn.commit()


async def _structure_narrative(state: dict[str, Any], text: str, out: dict[str, Any]) -> None:
    """Model-backed: dates, nature, neutral description and items the client mentions (never amounts the agent invents)."""
    try:
        from app.agents.claims.nodes import llm
    except ImportError:
        return
    claim_id, memory = state["claim_id"], state["memory"]
    catalog_keys = [c["key"] for c in memory.get("catalog", [])]
    try:
        n = await llm.extract_narrative(text, claim_id=claim_id, today=datetime.now(timezone.utc).date().isoformat(), catalog_keys=catalog_keys)
    except Exception:
        return
    if not n:
        return
    out["narrative"] = n
    claim = memory["claim"]
    updates, params = [], []
    if n.get("loss_date") and not claim.get("loss_date"):
        updates.append("loss_date = %s"); params.append(n["loss_date"])
    if n.get("loss_type") and not claim.get("loss_type"):
        updates.append("loss_type = %s"); params.append(n["loss_type"])
    if n.get("neutral_description"):
        updates.append("summary = %s"); params.append(n["neutral_description"][:500])
    if updates:
        async with db.pool.connection() as conn:
            await conn.execute(f"UPDATE claims SET {', '.join(updates)}, updated_at = now() WHERE id = %s", (*params, claim_id))
            if n.get("loss_date") and not claim.get("riot_event_id"):
                await conn.execute(
                    """UPDATE claims SET riot_event_id = r.id FROM riot_events r
                       WHERE claims.id = %s AND r.started_at::date <= %s AND coalesce(r.ended_at, r.started_at + interval '2 days')::date >= %s""",
                    (claim_id, n["loss_date"], n["loss_date"]),
                )
            await conn.commit()
    if n.get("neutral_description"):
        f = await T.log_fact(claim_id, f"Event (neutral restatement): {n['neutral_description']}", "agent_inference", "medium", status="to_confirm")
        out["new_fact_ids"].append(f.fact_id)

    items: list[LossItemInput] = []
    existing = {(li.get("label") or "").lower() for li in memory["loss_items"]}
    for it in n.get("items_mentioned") or []:
        label = (it.get("label") or "").strip()
        if not label or label.lower() in existing:
            continue
        total = it.get("total_value_eur")
        if total is None and it.get("quantity") is not None and it.get("unit_value_eur") is not None:
            total = round(float(it["quantity"]) * float(it["unit_value_eur"]), 2)
        note, clause_id, page, quote = None, None, None, None
        if it.get("value_basis") == "retail":
            note = "Stated at retail price. Stock is indemnified at purchase price under the policy; to be recomputed from supplier invoices."
            clause = await _find_clause(memory, "marchandises prix d'achat valeur")
            if clause:
                clause_id, page, quote = clause.id, clause.page, clause.body[:200]
        elif it.get("value_basis") in ("estimate", "unknown") and total is not None:
            note = "Client estimate; supporting invoices or inventory needed before it can be claimed."
        if it.get("is_customer_property"):
            note = ((note + " ") if note else "") + "Customer property held in the shop (goods in custody / bailee cover to verify)."
        items.append(LossItemInput(
            catalog_key=it.get("catalog_key") if it.get("catalog_key") in catalog_keys else None, label=label,
            category="customer_property" if it.get("is_customer_property") else "contents",
            amount_claimed_eur=total, amount_basis="client_instruction" if total is not None else None,
            computation=(f"{it.get('quantity')} × {it.get('unit_value_eur')} € as stated by the client" if it.get("quantity") and it.get("unit_value_eur") else None),
            computation_detail={"stated_by": "client", "value_basis": it.get("value_basis"), "quantity": it.get("quantity"), "unit_value_eur": it.get("unit_value_eur")},
            evidence_ids=[], clause_id=clause_id, clause_page=page, clause_quote=quote, condition_note=note, status="unsupported",
        ))
    if n.get("closure_days"):
        out["closure_days"] = n["closure_days"]
        bi = covers.ensure_bi_item(memory, n["closure_days"])
        if bi:
            items.append(LossItemInput(**bi))
    if items:
        stored = await T.update_loss_statement(claim_id, items)
        out["items_created"] = [str(r["id"]) for r in stored]


async def _find_clause(memory: dict[str, Any], query: str):
    for c in memory.get("contracts", []):
        if c.get("doc_type") in ("general_conditions", "particular_conditions"):
            try:
                hits = await T.search_clauses(str(c["id"]), query, 1)
            except Exception:
                hits = []
            if hits:
                return hits[0]
    return None


async def run(state: dict[str, Any]) -> dict[str, Any]:
    claim_id, ev = state["claim_id"], state["event"]
    kind, p = ev.get("kind"), ev.get("payload", {}) or {}
    out: dict[str, Any] = {"new_fact_ids": [], "new_evidence": [], "duplicates": [], "offer_id": None, "missing": [], "summary": ""}

    if kind == "message":
        text = (p.get("text") or "").strip()
        if text:
            f = await T.log_fact(claim_id, text, "client", "medium")
            out["new_fact_ids"].append(f.fact_id)
            amounts = extract_amounts_eur(text)
            if amounts:
                out["client_amounts_mentioned"] = amounts
            await _structure_narrative(state, text, out)
        out["summary"] = f"client message logged as fact{' with amounts ' + str(out.get('client_amounts_mentioned')) if out.get('client_amounts_mentioned') else ''}" \
            + (f"; {len(out.get('items_created', []))} loss item(s) drafted from the narrative" if out.get("items_created") else "")

    elif kind == "document":
        doc = await _document(p["document_id"]) if p.get("document_id") else None
        if doc:
            await _attach_document_to_claim(str(doc["id"]), claim_id)
            extract = None
            try:
                from app.agents.claims.nodes.llm import read_document  # optional model-backed extraction

                extract = await read_document(str(doc["id"]), claim_id=claim_id)
            except ImportError:
                extract = None
            except Exception:  # model unavailable or failed: register the document without amounts
                extract = None
            amounts = (extract or {}).get("amounts") or []
            etype = (extract or {}).get("doc_type") or _evidence_type(doc.get("mime_type"), p.get("caption"))
            if amounts:
                for a in amounts:
                    row = await T.add_evidence(claim_id, document_id=str(doc["id"]), evidence_type=etype, amount_eur=a.get("amount_eur"),
                                               issued_on=(extract or {}).get("document_date"), vendor=(extract or {}).get("vendor"),
                                               description=a.get("label"), extracted=extract, sha256=doc.get("sha256"))
                    (out["duplicates"] if row.get("duplicate_of") else out["new_evidence"]).append(str(row["id"]))
            else:
                row = await T.add_evidence(claim_id, document_id=str(doc["id"]), evidence_type=etype, amount_eur=None, issued_on=None,
                                           vendor=None, description=p.get("caption") or doc.get("filename"), extracted=extract, sha256=doc.get("sha256"))
                (out["duplicates"] if row.get("duplicate_of") else out["new_evidence"]).append(str(row["id"]))
            out["summary"] = f"document {doc.get('filename') or doc['id']}: {len(out['new_evidence'])} evidence, {len(out['duplicates'])} duplicate(s)"
            if out["new_evidence"]:
                from app.agents.claims.brain import recompute

                fresh = await T.get_claim_memory(claim_id)
                rows = await recompute.recompute_from_evidence(claim_id, fresh, out["new_evidence"])
                if rows:
                    out["items_recomputed"] = [{"id": str(r["id"]), "label": r["label"], "amount_eur": float(r["amount_claimed_eur"]), "version": r["version"]} for r in rows]
                    out["summary"] += f"; {len(rows)} item(s) recomputed from invoices"
        else:
            out["summary"] = "document event without a stored document"

    elif kind == "call_ended":
        sr = p.get("structured_result") or {}
        answers = sr.get("answers") or sr.get("questions") or []
        for q in answers:
            stmt = f"Insurer (by phone): Q: {q.get('question')} — A: {q.get('answer_verbatim') or q.get('answer_summary')}"
            f = await T.log_fact(claim_id, stmt, "insurer_oral", q.get("confidence") or "medium")
            out["new_fact_ids"].append(f.fact_id)
        spoken = "\n".join(f"{q.get('question')}: {q.get('answer_verbatim') or q.get('answer_summary')}" for q in answers) or (p.get("transcript") or "")
        if spoken.strip():
            out["positions"] = await positions.record(claim_id, channel="phone", text=spoken, who=sr.get("insurer_reference"))
        if not answers and p.get("transcript"):
            f = await T.log_fact(claim_id, f"Insurer call transcript (unstructured): {p['transcript'][:2000]}", "insurer_oral", "low")
            out["new_fact_ids"].append(f.fact_id)
        out["reached_human"] = sr.get("reached_human", bool(answers))
        out["summary"] = f"call result → {len(out['new_fact_ids'])} oral fact(s) to confirm in writing"

    elif kind == "email_received":
        body, subject = p.get("body_text") or "", p.get("subject") or ""
        f = await T.log_fact(claim_id, f"Insurer email « {subject} »: {body[:3000]}", "insurer_email", "high")
        out["new_fact_ids"].append(f.fact_id)
        insurer = (state["memory"].get("business") or {}).get("insurer_name")
        out["positions"] = await positions.record(claim_id, channel="email", text=f"{subject}\n{body}", communication_id=p.get("communication_id"), who=p.get("from"))
        await profiles.on_first_insurer_reply(claim_id, insurer)
        doc_kinds = [x["topic"] for x in out["positions"] if x.get("topic") == "document_request"]
        if doc_kinds:
            await profiles.on_documents_requested(claim_id, insurer, [(x.get("summary_en") or "document")[:40] for x in out["positions"] if x.get("topic") == "document_request"])
        if state.get("triage", {}).get("decision") == "present_offer":
            amounts = extract_amounts_eur(body)
            total = max(amounts) if amounts else None
            release = has_release_language(body + " " + subject)
            async with db.pool.connection() as conn:
                row = await (
                    await conn.execute(
                        """INSERT INTO offers (claim_id, source_communication_id, total_eur, breakdown, received_at, nature, has_release_language, release_terms)
                           VALUES (%s,%s,%s,%s,now(),%s,%s,%s) RETURNING id""",
                        (claim_id, p.get("communication_id"), total, json.dumps([{"amount_eur": a} for a in amounts]),
                         "final" if release else "provisional", bool(release), ", ".join(release) or None),
                    )
                ).fetchone()
                await conn.commit()
            out["offer_id"] = str(row[0])
            out["offer_total"] = total
            out["release_terms"] = release
            documented = sum(float(li["amount_claimed_eur"]) for li in state["memory"]["loss_items"] if li.get("amount_claimed_eur") is not None)
            await profiles.on_first_offer(claim_id, insurer, total, documented or None, bool(release))
        out["summary"] = "insurer email logged" + (f"; offer {out['offer_id']} total {out.get('offer_total')}" if out["offer_id"] else "")

    else:
        out["summary"] = f"no analysis for event kind {kind}"

    # Cover matching on the current loss statement whenever it may have changed.
    if out.get("items_created") or out.get("new_evidence") or kind == "message":
        fresh = await T.get_claim_memory(claim_id)
        if fresh["loss_items"]:
            out["cover_matches"] = await covers.match_claim(claim_id, fresh)
            statuses = {}
            for m in out["cover_matches"]:
                statuses[m["status"]] = statuses.get(m["status"], 0) + 1
            out["summary"] += f"; covers: {statuses}"
    return out
