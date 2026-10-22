"""`analyze` node: turn the inbound event into facts, evidence and loss items (PRD 2.3, 2.4, 2.6).

Deterministic part. Document reading and narrative extraction call `llm.py` when a model is
configured; without one, documents are still registered as evidence (with dedup) and the client
text is still logged as a fact, so the flow is demonstrable end to end.
"""

from __future__ import annotations

import json
import re
from typing import Any

from psycopg.rows import dict_row

from app import db
from app.agents.claims import tools_impl as T
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
        out["summary"] = f"client message logged as fact{' with amounts ' + str(out.get('client_amounts_mentioned')) if out.get('client_amounts_mentioned') else ''}"

    elif kind == "document":
        doc = await _document(p["document_id"]) if p.get("document_id") else None
        if doc:
            await _attach_document_to_claim(str(doc["id"]), claim_id)
            extract = None
            try:
                from app.agents.claims.nodes.llm import read_document  # optional model-backed extraction

                extract = await read_document(str(doc["id"]))
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
        else:
            out["summary"] = "document event without a stored document"

    elif kind == "call_ended":
        sr = p.get("structured_result") or {}
        answers = sr.get("answers") or sr.get("questions") or []
        for q in answers:
            stmt = f"Insurer (by phone): Q: {q.get('question')} — A: {q.get('answer_verbatim') or q.get('answer_summary')}"
            f = await T.log_fact(claim_id, stmt, "insurer_oral", q.get("confidence") or "medium")
            out["new_fact_ids"].append(f.fact_id)
        if not answers and p.get("transcript"):
            f = await T.log_fact(claim_id, f"Insurer call transcript (unstructured): {p['transcript'][:2000]}", "insurer_oral", "low")
            out["new_fact_ids"].append(f.fact_id)
        out["reached_human"] = sr.get("reached_human", bool(answers))
        out["summary"] = f"call result → {len(out['new_fact_ids'])} oral fact(s) to confirm in writing"

    elif kind == "email_received":
        body, subject = p.get("body_text") or "", p.get("subject") or ""
        f = await T.log_fact(claim_id, f"Insurer email « {subject} »: {body[:3000]}", "insurer_email", "high")
        out["new_fact_ids"].append(f.fact_id)
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
        out["summary"] = "insurer email logged" + (f"; offer {out['offer_id']} total {out.get('offer_total')}" if out["offer_id"] else "")

    else:
        out["summary"] = f"no analysis for event kind {kind}"

    return out
