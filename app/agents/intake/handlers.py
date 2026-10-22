"""B consumes upload events and the transactional onboarding fan-out (migration 200).
A retains the sole web/onboarding_done handler for mailbox creation.
"""

from app.worker import handles
from app.agents.intake.graph import run_intake


@handles("web", "document_added")
async def document_added(event):
    account_id = event.get("account_id")
    if not account_id:
        raise ValueError("Intake requires account_id on the event.")
    await run_intake(str(account_id))
