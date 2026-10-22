"""Workstream A — worker handlers for the email channel.

- ("web", "onboarding_done"): create the account's agent mailbox (runs alongside B's Intake handler).
"""

import logging

from app.channels.email.mailboxes import ensure_account_mailbox
from app.worker import handles

log = logging.getLogger(__name__)


@handles("web", "onboarding_done")
async def create_mailbox_on_onboarding(event: dict) -> None:
    account_id = event.get("account_id") or (event.get("payload") or {}).get("account_id")
    if not account_id:
        log.warning("onboarding_done without account_id; no mailbox created")
        return
    mailbox = await ensure_account_mailbox(str(account_id))
    log.info("account %s mailbox ready: %s", account_id, mailbox["address"])
