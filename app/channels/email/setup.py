"""One-off provisioning for the email channel (workstream A).

    .venv/bin/python -m app.channels.email.setup

- creates the simulated insurer inbox (role simulated_insurer) if missing
- registers the AgentMail webhook pointing at PUBLIC_BASE_URL/webhooks/agentmail (message.received)
- prints the values to set: SIMULATED_INSURER_EMAIL, AGENTMAIL_WEBHOOK_SECRET
"""

import asyncio
import json
import sys

from app import db
from app.channels.email.client import agentmail
from app.channels.email.mailboxes import ensure_simulated_insurer_mailbox
from app.config import settings


async def main() -> None:
    if not settings.public_base_url:
        sys.exit("PUBLIC_BASE_URL is required")
    await db.open_pool()
    await db.run_migrations()
    try:
        sim = await ensure_simulated_insurer_mailbox()
        client = agentmail()
        url = f"{settings.public_base_url.rstrip('/')}/webhooks/agentmail"
        existing = await client.webhooks.list()
        hook = next((w for w in (existing.webhooks or []) if w.url == url), None)
        if hook is None:
            hook = await client.webhooks.create(url=url, event_types=["message.received"], client_id="robin-inbound")
        print(json.dumps({
            "SIMULATED_INSURER_EMAIL": sim["address"],
            "AGENTMAIL_WEBHOOK_ID": hook.webhook_id,
            "AGENTMAIL_WEBHOOK_SECRET": getattr(hook, "secret", None),
            "webhook_url": url,
        }, indent=2))
    finally:
        await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
