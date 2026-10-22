"""Typed state of the Claims Agent graph (PRD 2.3). One thread per claim (thread_id = claim_id)."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from app.contracts import WaitType

TriageDecision = Literal["respond", "update", "act", "wait", "present_offer"]


class Draft(TypedDict, total=False):
    """An outbound text waiting for the gate. Mirrors contracts.OutboundDraft plus routing data."""

    channel: str                 # telegram | email | phone_brief | prefect_letter
    language: str                # en | fr
    recipient_role: str          # client | insurer | broker | expert | prefect | accountant
    to: str | None
    subject: str | None
    body: str
    attachment_ids: list[str]
    amounts_eur: list[float]
    loss_item_ids: list[str]
    quotes: list[tuple[int, str]]
    fact_ids_used: list[str]
    purpose: str                 # initial_declaration | ask_client | loss_statement | followup | offer_summary | document_request | confirmation_request
    requested_items: list[str]
    next_wait: WaitType | None   # wait type after this is sent


class ClaimState(TypedDict, total=False):
    claim_id: str
    account_id: str
    event: dict[str, Any]                    # the inbound event being processed (contracts.InboundEvent as dict)
    memory: dict[str, Any]                   # snapshot from memory.get_claim_memory
    triage: dict[str, Any]                   # {"decision": TriageDecision, "reasons": [...], "is_new_claim": bool, "offer_id": str|None}
    analysis: dict[str, Any]                 # what analyze produced this turn: new facts, evidence, loss items, duplicates, missing
    drafts: list[Draft]                      # produced by act, validated by review, sent by dispatch
    review_failures: int                     # consecutive gate failures on this turn
    violations: list[dict[str, Any]]         # last gate violations (fed back to analyze/act)
    wait_type: WaitType | None
    trace: list[str]                         # human-readable log of this turn, for the tracking page and the demo
