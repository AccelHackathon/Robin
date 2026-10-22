"""`start_call` adapter (workstream A). Called by the Claims Agent's `start_call` tool.

Starts an ElevenLabs outbound call through the imported Twilio number, records the call and
the outbound communication. The result arrives later via the post-call webhook as an
("elevenlabs", "call_ended") event consumed by workstream C.
"""

import json
import logging

from app import db
from app.agents.audit import record_action
from app.channels.voice import elevenlabs
from app.config import settings

log = logging.getLogger(__name__)


def build_dynamic_variables(*, brief: dict, goal: str, questions: list[str]) -> dict:
    """Everything the agent prompt references. Values must be strings for the ElevenLabs API."""
    numbered = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions))
    return {
        "business_name": str(brief.get("business_name") or "the policyholder"),
        "policy_number": str(brief.get("policy_number") or "unknown"),
        "insurer_name": str(brief.get("insurer_name") or "the insurer"),
        "claim_ref": str(brief.get("claim_ref") or ""),
        "insurer_reference": str(brief.get("insurer_reference") or "not yet assigned"),
        "loss_date": str(brief.get("loss_date") or ""),
        "loss_summary": str(brief.get("loss_summary") or ""),
        "call_goal": goal,
        "questions": numbered,
        "question_count": str(len(questions)),
        "language": str(brief.get("language") or "en"),
    }


async def start_call(*, account_id: str, claim_id: str, to_number: str, goal: str, questions: list[str], brief: dict) -> str:
    agent_id = settings.elevenlabs_agent_id
    phone_number_id = settings.elevenlabs_phone_number_id
    if not agent_id or not phone_number_id:
        raise RuntimeError("ELEVENLABS_AGENT_ID / ELEVENLABS_PHONE_NUMBER_ID are not set")

    variables = build_dynamic_variables(brief=brief, goal=goal, questions=questions)

    async with db.pool.connection() as conn:
        call_id = (
            await (
                await conn.execute(
                    """
                    INSERT INTO calls (claim_id, account_id, goal, questions, to_number, from_number, brief, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'requested') RETURNING id
                    """,
                    (claim_id, account_id, goal, json.dumps(questions), to_number, settings.twilio_phone_number, json.dumps(brief, default=str)),
                )
            ).fetchone()
        )[0]
        await conn.commit()

    try:
        result = await elevenlabs.outbound_call(
            agent_id=agent_id, phone_number_id=phone_number_id, to_number=to_number, dynamic_variables=variables
        )
    except Exception as exc:
        log.exception("outbound call failed to start")
        async with db.pool.connection() as conn:
            await conn.execute(
                "UPDATE calls SET status = 'failed', failure_reason = %s, ended_at = now() WHERE id = %s",
                (f"start_error: {exc!r}"[:500], call_id),
            )
            await conn.commit()
        await record_action("claims", "start_call", {"claim_id": claim_id, "to": to_number, "goal": goal},
                            {"call_id": str(call_id), "error": repr(exc)}, ok=False, claim_id=claim_id, account_id=account_id)
        raise

    conversation_id = result.get("conversation_id")
    twilio_sid = result.get("callSid")
    async with db.pool.connection() as conn:
        await conn.execute(
            "UPDATE calls SET provider_ref = %s, twilio_call_sid = %s, status = 'in_progress' WHERE id = %s",
            (conversation_id, twilio_sid, call_id),
        )
        await conn.execute(
            """
            INSERT INTO communications (account_id, claim_id, channel, direction, counterpart, subject, body, provider_ref, delivery_status, language)
            VALUES (%s, %s, 'phone', 'outbound', %s, %s, %s, %s, 'started', %s)
            """,
            (account_id, claim_id, to_number, goal, variables["questions"], conversation_id, variables["language"]),
        )
        await conn.commit()

    await record_action("claims", "start_call", {"claim_id": claim_id, "to": to_number, "goal": goal, "questions": questions},
                        {"call_id": str(call_id), "conversation_id": conversation_id, "twilio_call_sid": twilio_sid},
                        claim_id=claim_id, account_id=account_id)
    return str(call_id)
