"""Deterministic rule tables for the review gate (PRD 2.7).

Everything here is data, not I/O. The French entries are the words to detect in outbound
French text; the English entries cover drafts written to the client.
"""

from __future__ import annotations

import re

# --- 7. Banned words toward insurer / police / prefect (PRD 2.7, research 08c §4.3) --------
# Any of these in a description of the event can forfeit the State recourse (L211-10 CSI):
# the Conseil d'État excludes acts of an "organised group". Rewrite as plain facts.
BANNED_EVENT_WORDS: dict[str, list[str]] = {
    "fr": ["organisé", "organisés", "organisée", "organisées", "bande", "bandes", "venus exprès",
           "casseur", "casseurs", "émeutier", "émeutiers", "prémédité", "préméditée", "prémédités"],
    "en": ["organised", "organized", "gang", "gangs", "came on purpose", "rioter", "rioters",
           "looter", "looters", "premeditated"],
}

# --- 5. Promise / acceptance language (the agent never accepts, agrees, waives, settles) ----
PROMISE_PATTERNS: dict[str, list[str]] = {
    "fr": [r"\bnous acceptons\b", r"\bj'accepte\b", r"\bnous renon[cç]ons\b", r"\bpour solde de tout compte\b",
           r"\bnous nous engageons\b", r"\bnous confirmons (?:notre )?accord\b", r"\baccord d[ée]finitif\b",
           r"\bbon pour accord\b", r"\bnous donnons quittance\b"],
    "en": [r"\bwe accept\b", r"\bI accept\b", r"\bwe agree(?:d)? to\b", r"\bwe waive\b", r"\bfull and final\b",
           r"\bwe (?:hereby )?settle\b", r"\bwe commit to\b", r"\bagreed\b(?! amounts)", r"\bwe confirm (?:our )?acceptance\b"],
}

# --- 6. Personalised advice (regulated legal advice — loi 71-1130; Cass. 2015 / CA Nîmes 2023) ---
ADVICE_PATTERNS: dict[str, list[str]] = {
    "fr": [r"\bvous devriez\b", r"\bnous (?:vous )?recommandons\b", r"\bje (?:vous )?recommande\b", r"\bnous (?:vous )?conseillons\b",
           r"\bil (?:vaut|vaudrait) mieux\b", r"\bvos chances\b", r"\bjuridiquement insuffisant", r"\bn'acceptez pas\b",
           r"\brefusez\b", r"\bacceptez cette offre\b", r"\bà votre place\b"],
    "en": [r"\byou should\b", r"\bwe recommend\b", r"\bI recommend\b", r"\bwe advise\b", r"\bI advise\b", r"\byour chances\b",
           r"\blegally insufficient\b", r"\bdon'?t accept\b", r"\byou ought to\b", r"\bbest (?:option|course) (?:is|would be)\b",
           r"\bif I were you\b", r"\byou'?d be better off\b", r"\bin (?:my|our) opinion\b", r"\bI think you should\b"],
}

# Phrasings that are explicitly allowed (factual comparison, enumerated options). Listed so the
# LLM judge is calibrated and so tests document the boundary. Not used to bypass the regexes.
ALLOWED_PHRASINGS: list[str] = [
    "The offer covers {x} of the {y} documented in your loss statement",
    "Your policy provides {cover} up to {cap} (p. {page})",
    "You can accept, ask for details, or contest",
    "Options that exist: a written complaint to the insurer, the insurance ombudsman (if eligible), a loss assessor of your choice, a lawyer",
    "This document extinguishes further claims on this loss (art. 2052 C. civ.)",
    "The contractual deadline for {x} was {date}",
    "Applied: {n}% depreciation on {item} (policy formula p. {page})",
]

# --- 9. Release-language detection on insurer documents (PRD 2.9 step 3) -------------------
RELEASE_TERMS: list[str] = [
    "quittance", "solde de tout compte", "pour solde", "renonciation", "renonce à", "transaction",
    "définitif", "définitive", "irrévocable", "décharge", "sans réserve",
    "full and final", "release", "waiver", "discharge",
]


def _compile(patterns: dict[str, list[str]]) -> dict[str, list[re.Pattern[str]]]:
    return {lang: [re.compile(p, re.IGNORECASE) for p in pats] for lang, pats in patterns.items()}


PROMISE_RE = _compile(PROMISE_PATTERNS)
ADVICE_RE = _compile(ADVICE_PATTERNS)
BANNED_RE: dict[str, list[re.Pattern[str]]] = {
    lang: [re.compile(r"\b" + re.escape(w) + r"\b", re.IGNORECASE) for w in words]
    for lang, words in BANNED_EVENT_WORDS.items()
}
RELEASE_RE = [re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE) for t in RELEASE_TERMS]


def find_all(text: str, regexes: list[re.Pattern[str]]) -> list[str]:
    """Return the distinct matched spans, in order of first appearance."""
    seen: dict[str, None] = {}
    for rx in regexes:
        for m in rx.finditer(text):
            seen.setdefault(m.group(0), None)
    return list(seen)


def has_release_language(text: str) -> list[str]:
    return find_all(text, RELEASE_RE)
