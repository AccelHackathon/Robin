"""Review gate — deterministic controls (PRD 2.7; AC-10, AC-11, AC-12). No database needed."""

import pytest

from app.agents.review import amounts, citations
from app.agents.review.gate import review
from app.agents.review.rules import has_release_language
from app.contracts import OutboundDraft, ReviewContext

CLAIM = "00000000-0000-0000-0000-000000000001"


def ctx(**kw) -> ReviewContext:
    base = dict(claim_id=CLAIM, evidence_amounts_eur=[], derived_amounts_eur=[], client_instruction_amounts_eur=[],
                confirmed_fact_ids=[], cited_clause_ids=[])
    base.update(kw)
    return ReviewContext(**base)


def draft(body: str, *, role="client", channel="telegram", lang="en", **kw) -> OutboundDraft:
    return OutboundDraft(channel=channel, language=lang, recipient_role=role, body=body, **kw)


async def gate(d, c):
    return await review(d, c, use_judge=False)


# --- amounts -------------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("The offer is 20 750 €.", [20750.0]),
    ("Stock: €39,600 and spare parts 6 000,00 EUR", [39600.0, 6000.0]),
    ("Plafond 15.000 € ; franchise 1 000 euros", [15000.0, 1000.0]),
    ("No amounts here", []),
    ("3 600 € pour la vitrine", [3600.0]),
])
def test_extract_amounts(text, expected):
    assert amounts.extract_amounts_eur(text) == expected


def test_untraceable_tolerance():
    assert amounts.untraceable([100.0, 100.4, 250.0], [100.0]) == [250.0]


@pytest.mark.asyncio
async def test_ac12_untraceable_amount_blocks():
    r = await gate(draft("The offer covers €20,750 of the €89,700 documented."), ctx(evidence_amounts_eur=[20750.0]))
    assert not r.passed
    assert [v.type for v in r.violations] == ["untraceable_amount"]
    assert "89,700" in r.violations[0].span


@pytest.mark.asyncio
async def test_traceable_amounts_pass():
    r = await gate(draft("The offer covers €20,750 of the €89,700 documented."),
                   ctx(evidence_amounts_eur=[20750.0], derived_amounts_eur=[89700.0]))
    assert r.passed


@pytest.mark.asyncio
async def test_client_instruction_amount_is_traceable():
    r = await gate(draft("Per your instruction we transmit a counter-figure of 60 000 €.", role="insurer", channel="email", lang="fr"),
                   ctx(client_instruction_amounts_eur=[60000.0]))
    assert r.passed


# --- advice / promise -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac11_advice_blocks():
    r = await gate(draft("We recommend you refuse this offer; you should contest."), ctx())
    types = {v.type for v in r.violations}
    assert types == {"personalised_advice"}
    assert not r.passed


@pytest.mark.asyncio
async def test_allowed_factual_comparison_passes():
    body = ("The offer covers €20,750 of the €89,700 documented in your loss statement (23%). "
            "Not covered: stock above the theft cap, customer devices, business interruption. "
            "You can accept, ask for details, or contest. Options that exist: a written complaint, "
            "the insurance ombudsman if eligible, a loss assessor of your choice, a lawyer.")
    r = await gate(draft(body), ctx(evidence_amounts_eur=[20750.0], derived_amounts_eur=[89700.0]))
    assert r.passed, r.violations


@pytest.mark.asyncio
async def test_promise_blocks_in_french_email():
    r = await gate(draft("Nous acceptons votre proposition pour solde de tout compte.", role="insurer", channel="email", lang="fr"), ctx())
    assert {v.type for v in r.violations} == {"promise_or_acceptance"}


# --- banned words ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ac10_banned_words_toward_insurer():
    body = "Le 17 octobre vers 19 h, des casseurs organisés ont forcé le rideau."
    r = await gate(draft(body, role="insurer", channel="email", lang="fr"), ctx())
    spans = {v.span.lower() for v in r.violations if v.type == "banned_word"}
    assert spans == {"casseurs", "organisés"}


@pytest.mark.asyncio
async def test_banned_words_allowed_toward_client():
    # The client may describe events freely; the gate only guards external sends.
    r = await gate(draft("You mentioned organised looters — I will describe the facts neutrally to the insurer."), ctx())
    assert r.passed


@pytest.mark.asyncio
async def test_factual_event_description_passes():
    body = "Le 17 octobre 2026 vers 19 h, rue de la République à Marseille, une trentaine de personnes ont forcé le rideau métallique."
    r = await gate(draft(body, role="insurer", channel="email", lang="fr"), ctx())
    assert r.passed


# --- unconfirmed facts -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unconfirmed_fact_blocks_external_send():
    r = await gate(draft("Stock of 180 devices.", role="insurer", channel="email", lang="fr"),
                   ctx(confirmed_fact_ids=["f1"], fact_ids_used=["f1", "f2"]))
    assert [v.type for v in r.violations] == ["unconfirmed_fact"]
    assert r.violations[0].span == "f2"


# --- citations (pure helper) ------------------------------------------------------------------

def test_quote_in_body_exact_and_noisy():
    body = "les frais de clôture et de gardiennage engagés avec notre accord — plafond 6 600 €"
    assert citations.quote_in_body("frais de clôture et de gardiennage engagés avec notre accord", body)
    assert citations.quote_in_body("frais  de clôture\net de gardiennage", body)
    assert not citations.quote_in_body("honoraires d'expert pris en charge", body)


# --- release language (AC-9 input) -------------------------------------------------------------

def test_release_language_detection():
    assert has_release_language("Veuillez signer la quittance d'indemnité pour solde de tout compte.") == ["quittance", "solde de tout compte", "pour solde"]
    assert has_release_language("Accusé de réception de votre déclaration.") == []
