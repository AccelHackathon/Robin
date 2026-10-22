"""Claims Agent tool signatures (PRD §5).

Each tool must write one row to `actions` (tool, arguments, result, tokens, latency) via
`app.agents.audit.record_action`. Outbound text (ask_client, send_email, request_insurer_document,
present_offer) MUST go through `app.agents.review.gate.review` before leaving the system.

Implementations live next to this file; this module is the stable contract other workstreams
(Telegram, email, voice, web) code against.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from app.contracts import CallId, Clause, CommId, DocExtract, FactId, FactSource, LossItemInput, TaskId

InsurerDocumentKind = Literal["CG_signed", "CP_signed", "delivery_proof", "expert_report"]


async def get_claim_memory(claim_id: str) -> dict:
    """Business profile, coverage profile, claim, facts, evidence, loss items, actions, communications, deadlines."""
    raise NotImplementedError


async def search_clauses(contract_id: str, query: str, k: int = 8) -> list[Clause]:
    """Full-text search (french dictionary) over the clauses of one contract document."""
    raise NotImplementedError


async def read_document(doc_id: str) -> DocExtract:
    """Vision/text extraction of a client document into structured facts and amounts. Cached by sha256."""
    raise NotImplementedError


async def update_loss_statement(claim_id: str, items: list[LossItemInput]) -> list[dict]:
    """Insert new versions of loss items (never overwrite). Returns the stored rows."""
    raise NotImplementedError


async def ask_client(claim_id: str, text_en: str, requested_items: list[str]) -> CommId:
    """Send a Telegram message to the client (through review) and move the thread to awaiting_client."""
    raise NotImplementedError


async def send_email(claim_id: str, to: str, subject: str, body: str, attachment_ids: list[str], language: str = "fr") -> CommId:
    """Send an email from the account's AgentMail mailbox (through review). Records the provider message id."""
    raise NotImplementedError


async def start_call(claim_id: str, goal: str, questions: list[str]) -> CallId:
    """Start an ElevenLabs outbound call with the claim brief as dynamic variables. Result arrives as an event."""
    raise NotImplementedError


async def schedule_followup(claim_id: str, when: datetime, reason: str, source_clause_id: int | None = None) -> TaskId:
    raise NotImplementedError


async def register_deadline(claim_id: str, kind: str, due_at: datetime, source_clause_id: int | None, legal_basis: str | None = None) -> TaskId:
    raise NotImplementedError


async def log_fact(claim_id: str, text: str, source: FactSource, confidence: str, supersedes: str | None = None) -> FactId:
    raise NotImplementedError


async def request_insurer_document(claim_id: str, kind: InsurerDocumentKind) -> CommId:
    """Email the insurer asking for signed policy documents, proof of delivery or the expert report."""
    raise NotImplementedError


async def present_offer(claim_id: str, offer_id: str) -> None:
    """Compare the offer with the loss statement, detect release language, interrupt with awaiting_signature_decision."""
    raise NotImplementedError
