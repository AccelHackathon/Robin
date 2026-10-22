"""Shared interface contracts (PRD §5).

Every workstream imports from here instead of redefining shapes. Changing a type here is a
cross-team change: announce it. Keep this module free of I/O and framework imports.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field

# --- Events ---------------------------------------------------------------------------------

EventSource = Literal["telegram", "agentmail", "elevenlabs", "scheduler", "web"]
EventKind = Literal[
    "message",          # text from the client
    "document",         # photo / file from the client
    "email_received",   # inbound email on an agent mailbox
    "call_ended",       # ElevenLabs post-call webhook
    "followup_due",     # scheduler fired a scheduled_task
    "onboarding_done",  # web onboarding completed -> run Intake Agent
    "document_added",   # new contract document uploaded on the web -> re-run Intake
]

WaitType = Literal[
    "awaiting_client",
    "awaiting_insurer_email",
    "awaiting_call_result",
    "awaiting_followup",
    "awaiting_signature_decision",
]


class InboundEvent(TypedDict):
    source: EventSource
    kind: EventKind
    account_id: str | None
    claim_id: str | None
    payload: dict[str, Any]
    received_at: datetime


# --- Documents and clauses -------------------------------------------------------------------

DocType = Literal[
    "general_conditions", "particular_conditions", "endorsement", "ipid",
    "report", "police_report", "correspondence", "invoice", "quote", "photo",
    "inventory", "bank_statement", "accounting", "other",
]


class Clause(BaseModel):
    id: int
    document_id: str
    page: int
    heading: str | None = None
    body: str


class DocExtract(BaseModel):
    doc_type: DocType
    facts: list[str] = Field(default_factory=list)
    amounts: list[ExtractedAmount] = Field(default_factory=list)
    document_date: str | None = None
    vendor: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"
    unreadable_pages: list[int] = Field(default_factory=list)


class ExtractedAmount(BaseModel):
    label: str
    amount_eur: float
    currency: str = "EUR"
    vat_included: bool | None = None
    page: int | None = None


# --- Coverage profile (Intake Agent output, PRD 2.2) -----------------------------------------

Subscribed = Literal["yes", "no", "unknown"]


class CoverageFact(BaseModel):
    guarantee: str                       # canonical key: theft, riot, glass, business_interruption, bailed_goods...
    subscribed: Subscribed = "unknown"
    ceiling: dict[str, Any] | None = None       # {"amount": 15000, "unit": "EUR", "basis": "per claim"}
    deductible: dict[str, Any] | None = None    # {"amount": 3, "unit": "days"}
    conditions: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    quote: str                           # verbatim excerpt (<= 200 chars) from the cited clause
    clause_id: int
    page: int
    confidence: Literal["high", "medium", "low"] = "medium"


# --- Facts, evidence, loss statement -------------------------------------------------------

FactSource = Literal["document", "client", "client_instruction", "insurer_email", "insurer_oral", "agent_inference"]
FactStatus = Literal["confirmed", "to_confirm", "contradicted", "superseded"]
LossItemStatus = Literal["supported", "unsupported", "no_cover_found", "sent", "accepted", "refused", "partial"]
AmountBasis = Literal["purchase_price", "replacement_value", "invoice", "formula", "client_instruction"]


class LossItemInput(BaseModel):
    catalog_key: str | None = None
    label: str
    category: str | None = None
    amount_claimed_eur: float | None = None
    amount_basis: AmountBasis | None = None
    computation: str | None = None       # human-readable; every input must be an evidence or a client instruction
    computation_detail: dict[str, Any] | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    clause_id: int | None = None
    clause_page: int | None = None
    clause_quote: str | None = None
    condition_note: str | None = None
    status: LossItemStatus = "unsupported"


# --- Review gate (PRD 2.7) -----------------------------------------------------------------

Channel = Literal["telegram", "email", "phone_brief", "prefect_letter"]


class OutboundDraft(BaseModel):
    channel: Channel
    language: Literal["en", "fr"]
    recipient_role: Literal["client", "insurer", "broker", "expert", "prefect", "accountant"]
    subject: str | None = None
    body: str
    attachment_ids: list[str] = Field(default_factory=list)
    amounts_eur: list[float] = Field(default_factory=list)   # every amount mentioned in the body


class ReviewContext(BaseModel):
    claim_id: str
    evidence_amounts_eur: list[float]
    derived_amounts_eur: list[float]      # computed from evidence with a cited formula (e.g. business interruption)
    client_instruction_amounts_eur: list[float]
    confirmed_fact_ids: list[str]
    cited_clause_ids: list[int]
    # Additive (C): what the draft actually relies on, so the gate can verify it.
    loss_item_ids: list[str] = Field(default_factory=list)       # loss items referenced by the draft
    quotes: list[tuple[int, str]] = Field(default_factory=list)  # (clause_id, verbatim quote) pairs used
    fact_ids_used: list[str] = Field(default_factory=list)       # facts the draft states


class ReviewViolation(BaseModel):
    type: Literal[
        "missing_evidence", "bad_citation", "duplicate_counted", "untraceable_amount",
        "promise_or_acceptance", "personalised_advice", "banned_word", "unconfirmed_fact", "wrong_language",
    ]
    span: str
    fix: str | None = None


class ReviewResult(BaseModel):
    passed: bool
    violations: list[ReviewViolation] = Field(default_factory=list)
    rewrite: str | None = None


# --- Tool result handles -------------------------------------------------------------------

class CommId(BaseModel):
    communication_id: str


class CallId(BaseModel):
    call_id: str


class TaskId(BaseModel):
    task_id: str


class FactId(BaseModel):
    fact_id: str
