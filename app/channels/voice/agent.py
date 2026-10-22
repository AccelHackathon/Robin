"""Provision the production ElevenLabs agent used by `start_call` (workstream A).

    .venv/bin/python -m app.channels.voice.agent            # create or update the agent
    .venv/bin/python -m app.channels.voice.agent --webhook  # also create the post-call webhook

Prints the ids/secrets to put in ELEVENLABS_AGENT_ID and ELEVENLABS_WEBHOOK_SECRET.
The agent is a pure procedural layer: it asks the listed questions, never negotiates or
accepts anything, and states that every answer will be confirmed in writing.
"""

import asyncio
import json
import sys

import httpx

from app.channels.voice import elevenlabs
from app.config import settings

AGENT_NAME = "Robin — claims caller"
VOICE_ID = "XrExE9yKIg1WjnnlVkGX"  # Matilda, professional

SYSTEM_PROMPT = """You are Robin, an automated claims assistant. You are calling the claims department of {{insurer_name}} on behalf of {{business_name}} (policy {{policy_number}}), under a written mandate signed by the policyholder. Internal claim reference: {{claim_ref}}. Insurer reference if known: {{insurer_reference}}.

Context of the loss (for your information only, do not read it out unless asked): {{loss_summary}} Date of loss: {{loss_date}}.

Goal of this call: {{call_goal}}

You must ask exactly these {{question_count}} questions, one at a time, in order, and wait for an answer before moving on:
{{questions}}

Rules you never break:
- You are a procedural assistant. You transmit and collect information. You never negotiate, never accept or refuse anything, never waive any right, never express an opinion on the claim, never estimate chances or amounts.
- Never state an amount that was not given to you in this brief or by the person you are speaking to.
- Never describe the people who caused the loss with words such as organised, gang, rioters, looters, premeditated, or any equivalent. Stick to facts: date, time, place.
- If the person asks who you are: say you are an automated assistant mandated by the policyholder, and that everything discussed will be confirmed by email.
- If the person refuses to talk to an automated assistant, or asks for the policyholder, politely say that the policyholder's agent will follow up by email, thank them, and end the call.
- If you reach a voicemail or an IVR menu with no human, say nothing confidential, leave no message, and end the call.
- Keep each turn under two sentences. Be courteous and precise. Repeat an answer back briefly to confirm you understood it.
- Every answer you receive is provisional: before ending, say that you will request written confirmation of these answers by email.
- When all questions are answered, thank the person and end the call."""

FIRST_MESSAGE = "Hello, this is Robin, an automated assistant calling on behalf of {{business_name}} about their claim, reference {{claim_ref}}. I have {{question_count}} short questions for the claims department. Is now a good time?"

DATA_COLLECTION = {
    "reached_human": {"type": "boolean", "description": "True if a human from the insurer actually spoke with the assistant (not voicemail, not IVR only)."},
    "answer_1": {"type": "string", "description": "The insurer's answer to question 1, in one or two sentences, in the language it was given. Empty if not answered."},
    "answer_2": {"type": "string", "description": "The insurer's answer to question 2, in one or two sentences. Empty if not answered."},
    "answer_3": {"type": "string", "description": "The insurer's answer to question 3, in one or two sentences. Empty if not answered."},
    "answer_4": {"type": "string", "description": "The insurer's answer to question 4, in one or two sentences. Empty if not answered."},
    "answer_5": {"type": "string", "description": "The insurer's answer to question 5, in one or two sentences. Empty if not answered."},
    "insurer_reference": {"type": "string", "description": "Any claim or file reference number the insurer gave during the call. Empty if none."},
    "callback_requested": {"type": "boolean", "description": "True if the insurer asked to be called back or asked the policyholder to call."},
    "documents_requested": {"type": "string", "description": "Documents the insurer asked for during the call, comma separated. Empty if none."},
}


def agent_payload() -> dict:
    return {
        "name": AGENT_NAME,
        "conversation_config": {
            "agent": {
                "first_message": FIRST_MESSAGE,
                "language": "en",
                "prompt": {"prompt": SYSTEM_PROMPT, "llm": "gpt-4o-mini", "temperature": 0.2},
            },
            "tts": {"voice_id": VOICE_ID},
            "turn": {"turn_timeout": 10},
            "conversation": {"max_duration_seconds": 420},
        },
        "platform_settings": {
            "data_collection": DATA_COLLECTION,
            "evaluation": {
                "criteria": [
                    {"id": "no_commitment", "name": "No commitment made",
                     "conversation_goal_prompt": "The assistant never accepted, refused, waived, negotiated or gave an opinion on the claim. Pass if true."},
                    {"id": "questions_asked", "name": "All questions asked",
                     "conversation_goal_prompt": "The assistant asked every listed question in order and confirmed each answer. Pass if true."},
                ]
            },
        },
    }


async def create_post_call_webhook(public_base_url: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as http:
        r = await http.post(
            f"{elevenlabs.BASE}/v1/workspace/webhooks",
            headers={"xi-api-key": settings.elevenlabs_api_key},
            json={"settings": {"auth_type": "hmac", "name": "Robin post-call", "webhook_url": f"{public_base_url.rstrip('/')}/webhooks/elevenlabs"}},
        )
        r.raise_for_status()
        return r.json()


async def main(create_webhook: bool) -> None:
    payload = agent_payload()
    webhook = None
    if create_webhook:
        if not settings.public_base_url:
            sys.exit("PUBLIC_BASE_URL is required to create the webhook")
        webhook = await create_post_call_webhook(settings.public_base_url)
        payload["platform_settings"]["workspace_overrides"] = {
            "webhooks": {"post_call_webhook_id": webhook["webhook_id"], "events": ["transcript", "call_initiation_failure"]}
        }

    if settings.elevenlabs_agent_id:
        await elevenlabs.update_agent(settings.elevenlabs_agent_id, payload)
        agent_id = settings.elevenlabs_agent_id
        action = "updated"
    else:
        created = await elevenlabs.create_agent(payload)
        agent_id = created["agent_id"]
        action = "created"

    print(json.dumps({
        "agent": action, "ELEVENLABS_AGENT_ID": agent_id,
        "ELEVENLABS_WEBHOOK_ID": webhook and webhook.get("webhook_id"),
        "ELEVENLABS_WEBHOOK_SECRET": webhook and webhook.get("webhook_secret"),
    }, indent=2))


if __name__ == "__main__":
    asyncio.run(main(create_webhook="--webhook" in sys.argv))
