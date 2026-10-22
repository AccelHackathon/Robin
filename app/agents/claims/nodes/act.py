"""`act` node: decide what leaves the system this turn and build the drafts (PRD 2.3).

Robin is a procedural layer. Drafts here state facts, cite the policy, ask for documents,
follow up and explain. They never recommend, accept or originate an amount — the review gate
enforces it, these templates respect it.
"""

from __future__ import annotations

from typing import Any

from app.agents.claims.state import Draft
from app.config import settings

DAY0_CHECKLIST_EN = (
    "Here is what to do today to protect your claim:\n"
    "1. File a police complaint (plainte) and keep the receipt — your policy sets a short deadline after a theft or vandalism.\n"
    "2. Take photos of all damage before any repair or clean-up.\n"
    "3. Secure the premises (temporary boarding, guarding) and keep every invoice — these costs are usually claimable.\n"
    "4. Do not start repairs beyond emergency measures without the insurer's written approval.\n"
    "5. Gather: supplier invoices for stock, your last inventory, till/sales export, equipment invoices, and a list of customer items held in the shop.\n"
    "I have sent the initial declaration to your insurer today. Send me documents here as you find them."
)


def _short(claim_id: str) -> str:
    return claim_id.split("-")[0][:8].upper()


def _insurer_email(memory: dict[str, Any]) -> str | None:
    b = memory.get("business") or {}
    return b.get("insurer_contact_email") or settings.simulated_insurer_email


def _business_line(memory: dict[str, Any]) -> str:
    b = memory.get("business") or {}
    parts = [b.get("name"), f"SIRET {b['siret']}" if b.get("siret") else None, b.get("address")]
    return ", ".join(x for x in parts if x) or "l'entreprise assurée"


def declaration_email(memory: dict[str, Any], claim_id: str) -> Draft:
    c = memory["claim"]
    b = memory.get("business") or {}
    loss_date = c.get("loss_date").isoformat() if c.get("loss_date") else "à confirmer"
    nature = c.get("loss_type") or "dommages aux biens professionnels"
    body = (
        f"Madame, Monsieur,\n\n"
        f"Agissant en vertu du mandat écrit qui nous a été confié par {_business_line(memory)}, nous vous déclarons par la présente un sinistre "
        f"survenu le {loss_date} dans les locaux professionnels situés {b.get('address') or 'à l’adresse assurée'}.\n\n"
        f"Nature du sinistre : {nature}.\n"
        f"Référence de votre dossier chez nous : RB-{_short(claim_id)}.\n\n"
        f"Un état des pertes détaillé, accompagné des justificatifs, vous sera transmis dès que possible, sous réserve de compléments. "
        f"Nous vous remercions de nous confirmer l’ouverture du dossier et de nous indiquer la référence attribuée ainsi que les pièces attendues.\n\n"
        f"Nous vous prions d’agréer, Madame, Monsieur, l’expression de nos salutations distinguées.\n\n"
        f"Robin — assistant de gestion de sinistre, pour le compte de {b.get('name') or 'l’assuré'}"
    )
    return Draft(channel="email", language="fr", recipient_role="insurer", to=_insurer_email(memory),
                 subject=f"Déclaration de sinistre — {b.get('name') or 'assuré'} — [RB-{_short(claim_id)}]", body=body,
                 attachment_ids=[], amounts_eur=[], loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="initial_declaration",
                 requested_items=[], next_wait=None)


def _deadline_lines(memory: dict[str, Any]) -> str:
    rows = [t for t in memory.get("deadlines", []) if t.get("status") == "pending" and t.get("kind") in ("police_report", "declaration", "loss_statement")]
    if not rows:
        return ""
    labels = {"police_report": "police complaint", "declaration": "declaration to the insurer", "loss_statement": "detailed statement of loss"}
    return "\nDates that apply to your file:\n" + "\n".join(
        f"• {labels[t['kind']]}: by {t['due_at'].date().isoformat()}" + (f" (policy p. {t['page']})" if t.get("page") else (f" ({t['legal_basis'].split(';')[0]})" if t.get("legal_basis") else ""))
        for t in sorted(rows, key=lambda t: t["due_at"]))


def day0_checklist(claim_id: str, memory: dict[str, Any] | None = None) -> Draft:
    return Draft(channel="telegram", language="en", recipient_role="client", to=None, subject=None, body=DAY0_CHECKLIST_EN + _deadline_lines(memory or {}),
                 attachment_ids=[], amounts_eur=[], loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="ask_client",
                 requested_items=["police complaint receipt", "photos", "supplier invoices", "last inventory", "till export", "customer items list"],
                 next_wait="awaiting_client")


def ack_document(analysis: dict[str, Any], memory: dict[str, Any]) -> Draft:
    if analysis.get("duplicates") and not analysis.get("new_evidence"):
        body = "I already have this document on file — I have not counted it twice. Anything else you can send?"
    else:
        n = len(analysis.get("new_evidence", []))
        body = f"Received and filed ({n} item{'s' if n != 1 else ''}). " + _still_needed(memory)
        cl = _cover_lines(memory)
        if cl:
            body += "\nHow this maps to your policy so far:\n" + "\n".join(cl)
    return Draft(channel="telegram", language="en", recipient_role="client", to=None, subject=None, body=body, attachment_ids=[],
                 amounts_eur=[], loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="ask_client", requested_items=[], next_wait="awaiting_client")


def ack_message(memory: dict[str, Any], analysis: dict[str, Any] | None = None) -> Draft:
    body = "Noted and added to your file. " + _still_needed(memory)
    created = (analysis or {}).get("items_created") or []
    if created:
        labels = [li["label"] for li in memory.get("loss_items", []) if str(li["id"]) in set(created)]
        if labels:
            body += "\nI have added to your loss statement, pending supporting documents: " + ", ".join(labels) + "."
    cl = _cover_lines(memory)
    if cl:
        body += "\nHow this maps to your policy so far:\n" + "\n".join(cl)
    return Draft(channel="telegram", language="en", recipient_role="client", to=None, subject=None, body=body, attachment_ids=[],
                 amounts_eur=[], loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="ask_client", requested_items=[], next_wait="awaiting_client")


def _still_needed(memory: dict[str, Any]) -> str:
    """Reads the digest: never re-list what is already on file; say how long an ask has been open."""
    have = {e.get("evidence_type") for e in memory.get("evidence", []) if not e.get("duplicate_of")}
    digest = memory.get("digest") or {}
    open_asks = [a for a in (digest.get("open_asks") or []) if not a.get("satisfied_at")]
    wanted = [("police_report", "the police complaint receipt"), ("invoice", "supplier invoices"), ("inventory", "your last inventory"),
              ("photo", "photos of the damage")]
    missing = [label for key, label in wanted if key not in have]
    # BI inputs become an ask only once the BI item exists (cover subscribed) and is still unsupported.
    if any(li.get("catalog_key") == "business_interruption" and li.get("status") == "unsupported" for li in memory.get("loss_items", [])):
        missing.append("monthly turnover N-1/N-2 and your gross margin rate (your accountant can export these)")
    if not missing:
        return "Your file has the core documents; I am preparing the loss statement."
    reminders = {a["item"].lower(): a for a in open_asks}
    parts = []
    for label in missing:
        prior = next((a for k, a in reminders.items() if any(w in k for w in label.lower().split()[:2])), None)
        parts.append(f"{label} (asked {prior['times']}× since {prior['asked_at'][:10]})" if prior and prior.get("times", 1) > 1 else label)
    return "Still useful: " + "; ".join(parts) + "."


def _cover_lines(memory: dict[str, Any]) -> list[str]:
    """Factual lines about how the current items map to the policy — caps and gaps, with pages."""
    lines = []
    for li in memory.get("loss_items", []):
        cov = ((li.get("computation_detail") or {}).get("cover") or {})
        st = cov.get("status")
        page = f" (p. {cov['page']})" if cov.get("page") else ""
        if st == "capped":
            lines.append(f"• {li['label']}: exceeds the {cov.get('cap')} cap of the {cov.get('guarantee', '').replace('_', ' ')} cover{page}.")
        elif st == "no_cover_found":
            lines.append(f"• {li['label']}: no matching cover found in your policy documents — {cov.get('note')}.")
        elif st == "unknown":
            lines.append(f"• {li['label']}: cover not established yet — {cov.get('note')}.")
        elif st == "not_insurance":
            lines.append(f"• {li['label']}: not an insurance cover; {cov.get('note')}.")
    return lines[:6]


def confirmation_request_email(memory: dict[str, Any], claim_id: str, fact_ids: list[str]) -> Draft:
    facts = [f for f in memory["facts"] if str(f["id"]) in fact_ids]
    lines = "\n".join(f"- {f['statement']}" for f in facts) or "- (voir transcription de l’appel)"
    b = memory.get("business") or {}
    body = (
        f"Madame, Monsieur,\n\nÀ la suite de notre échange téléphonique de ce jour concernant le dossier RB-{_short(claim_id)} ({b.get('name') or 'assuré'}), "
        f"nous vous remercions de bien vouloir nous confirmer par écrit les éléments suivants :\n{lines}\n\n"
        f"Dans l’attente de votre confirmation, nous vous prions d’agréer, Madame, Monsieur, nos salutations distinguées.\n\nRobin — pour le compte de {b.get('name') or 'l’assuré'}"
    )
    return Draft(channel="email", language="fr", recipient_role="insurer", to=_insurer_email(memory),
                 subject=f"Demande de confirmation écrite — [RB-{_short(claim_id)}]", body=body, attachment_ids=[], amounts_eur=[],
                 loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="confirmation_request", requested_items=[], next_wait="awaiting_insurer_email")


def call_summary_to_client(fact_ids: list[str], memory: dict[str, Any]) -> Draft:
    facts = [f for f in memory["facts"] if str(f["id"]) in fact_ids]
    lines = "\n".join(f"• {f['statement'].replace('Insurer (by phone): ', '')}" for f in facts)
    body = ("I spoke with your insurer. What they said on the phone (recorded as oral, to be confirmed — it does not change your policy terms until written):\n"
            f"{lines}\n\nI have asked them to confirm in writing.")
    return Draft(channel="telegram", language="en", recipient_role="client", to=None, subject=None, body=body, attachment_ids=[], amounts_eur=[],
                 loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="call_summary", requested_items=[], next_wait=None)


def followup_email(memory: dict[str, Any], claim_id: str, reason: str) -> Draft:
    b = memory.get("business") or {}
    body = (
        f"Madame, Monsieur,\n\nSauf erreur de notre part, nous restons dans l’attente de votre retour concernant le dossier RB-{_short(claim_id)} ({b.get('name') or 'assuré'}) : {reason}.\n\n"
        f"Nous vous remercions de nous indiquer l’état d’avancement du dossier et, le cas échéant, les pièces complémentaires attendues.\n\n"
        f"Nous vous prions d’agréer, Madame, Monsieur, nos salutations distinguées.\n\nRobin — pour le compte de {b.get('name') or 'l’assuré'}"
    )
    return Draft(channel="email", language="fr", recipient_role="insurer", to=_insurer_email(memory), subject=f"Relance — [RB-{_short(claim_id)}]",
                 body=body, attachment_ids=[], amounts_eur=[], loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="followup", requested_items=[],
                 next_wait="awaiting_insurer_email")


def offer_summary(memory: dict[str, Any], analysis: dict[str, Any]) -> Draft:
    total = analysis.get("offer_total")
    documented = round(sum(float(li["amount_claimed_eur"]) for li in memory["loss_items"] if li.get("amount_claimed_eur") is not None), 2)
    release = analysis.get("release_terms") or []
    parts = ["Your insurer has sent an offer."]
    amounts: list[float] = []
    if total is not None:
        parts.append(f"Offer total: {total:,.2f} €.".replace(",", " "))
        amounts.append(total)
    if documented:
        parts.append(f"Your documented loss statement totals {documented:,.2f} €.".replace(",", " "))
        amounts.append(documented)
        if total is not None and documented:
            parts.append(f"The offer covers {round(100 * total / documented)}% of what is documented.")
    if release:
        parts.append("The documents include release language (" + ", ".join(release) + "). Signing such a document extinguishes further claims on this loss "
                     "(art. 2052 C. civ.); for business property there is no withdrawal period after signature.")
    cl = _cover_lines(memory)
    if cl:
        parts.append("Items in your statement and the policy:\n" + "\n".join(cl))
    from app.agents.claims.brain import positions as P, profiles as PR

    for oral, written in P.contradictions((memory.get("digest") or {}).get("insurer_positions") or []):
        amounts_text = f"On {oral['at'][:10]} by phone the insurer stated: « {oral['position_verbatim'][:140]} ». In writing on {written['at'][:10]}: « {written['position_verbatim'][:140]} »."
        parts.append(amounts_text)
    obs = PR.describe(memory.get("insurer_profile"))
    if obs:
        parts.append(obs)
    parts.append("You can accept, ask for details, or contest. Options that exist: a written complaint to the insurer, the insurance ombudsman (if eligible), "
                 "a loss assessor of your choice, a lawyer. Nothing is accepted unless you tell me to.")
    return Draft(channel="telegram", language="en", recipient_role="client", to=None, subject=None, body="\n".join(parts), attachment_ids=[],
                 amounts_eur=amounts, loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="offer_summary", requested_items=["decision: accept / ask / contest"],
                 next_wait="awaiting_signature_decision")


def blocked_notice(violations: list[dict[str, Any]]) -> Draft:
    kinds = sorted({v["type"] for item in violations for v in item.get("violations", [])})
    body = ("I prepared a message for your insurer but held it back: " + ", ".join(k.replace("_", " ") for k in kinds) +
            ". I need your confirmation on the facts and figures involved before anything is sent. Could you confirm or send the supporting document?")
    return Draft(channel="telegram", language="en", recipient_role="client", to=None, subject=None, body=body, attachment_ids=[], amounts_eur=[],
                 loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="ask_client", requested_items=["confirmation"], next_wait="awaiting_client")


async def build_drafts(state: dict[str, Any]) -> list[Draft]:
    memory, triage, analysis = state["memory"], state.get("triage", {}), state.get("analysis", {}) or {}
    kind, claim_id = triage.get("kind"), state["claim_id"]
    drafts: list[Draft] = []

    if state.get("review_failures", 0) > 0 and state.get("violations"):
        return [blocked_notice(state["violations"])]

    if triage.get("is_new_claim"):
        drafts.append(declaration_email(memory, claim_id))
        drafts.append(day0_checklist(claim_id, memory))
        return drafts

    if triage.get("decision") == "present_offer":
        drafts.append(offer_summary(memory, analysis))
    elif kind == "document":
        drafts.append(ack_document(analysis, memory))
    elif kind == "message":
        drafts.append(ack_message(memory, analysis))
    elif kind == "call_ended":
        ids = analysis.get("new_fact_ids", [])
        if ids:
            drafts.append(call_summary_to_client(ids, memory))
            drafts.append(confirmation_request_email(memory, claim_id, ids))
        else:
            drafts.append(Draft(channel="telegram", language="en", recipient_role="client", to=None, subject=None,
                                body="I couldn't reach the insurer by phone. I've sent the same questions by email.", attachment_ids=[], amounts_eur=[],
                                loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="call_summary", requested_items=[], next_wait="awaiting_insurer_email"))
    elif kind == "followup_due":
        drafts.append(followup_email(memory, claim_id, state["event"].get("payload", {}).get("reason") or "notre précédent envoi"))
    elif kind == "email_received":
        drafts.append(Draft(channel="telegram", language="en", recipient_role="client", to=None, subject=None,
                            body=f"Your insurer wrote back: « {state['event'].get('payload', {}).get('subject') or 'message'} ». I have filed it and will act on it.",
                            attachment_ids=[], amounts_eur=[], loss_item_ids=[], quotes=[], fact_ids_used=[], purpose="insurer_update", requested_items=[], next_wait=None))
    return drafts
