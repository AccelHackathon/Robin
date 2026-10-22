"""One AgentMail inbox per account (role `agent`) plus the demo `simulated_insurer` inbox."""

import logging
import re
import unicodedata

from agentmail.inboxes.types import CreateInboxRequest
from psycopg.rows import dict_row

from app import db
from app.channels.email.client import agentmail
from app.config import settings

log = logging.getLogger(__name__)


def slugify(value: str, max_len: int = 24) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:max_len] or "client"


async def get_mailbox(*, account_id: str | None = None, role: str = "agent", address: str | None = None) -> dict | None:
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            if address:
                await cur.execute("SELECT * FROM mailboxes WHERE address = %s", (address,))
            elif account_id:
                await cur.execute("SELECT * FROM mailboxes WHERE account_id = %s AND role = %s ORDER BY created_at LIMIT 1", (account_id, role))
            else:
                await cur.execute("SELECT * FROM mailboxes WHERE role = %s ORDER BY created_at LIMIT 1", (role,))
            return await cur.fetchone()


async def _create_inbox(username: str, display_name: str) -> dict:
    """Create the inbox, or reuse it if it already exists at AgentMail (e.g. DB was reset)."""
    address = f"{username}@{settings.agentmail_domain}"
    try:
        inbox = await agentmail().inboxes.create(
            request=CreateInboxRequest(username=username, domain=settings.agentmail_domain, display_name=display_name, client_id=username)
        )
    except Exception as exc:
        log.warning("inbox create failed for %s (%r); trying to reuse", address, exc)
        inbox = await agentmail().inboxes.get(address)
    return {"inbox_id": inbox.inbox_id, "display_name": getattr(inbox, "display_name", None) or display_name}


async def bootstrap() -> None:
    """Startup hook: make sure the simulated insurer inbox exists and is known in this database."""
    if not settings.agentmail_api_key:
        return
    try:
        sim = await ensure_simulated_insurer_mailbox()
        log.info("simulated insurer mailbox: %s", sim["address"])
    except Exception:
        log.exception("could not bootstrap the simulated insurer mailbox")


async def ensure_account_mailbox(account_id: str) -> dict:
    """Idempotent: returns the existing agent mailbox of the account or creates it."""
    existing = await get_mailbox(account_id=account_id, role="agent")
    if existing:
        return existing
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT name FROM businesses WHERE account_id = %s ORDER BY created_at LIMIT 1", (account_id,))
            biz = await cur.fetchone()
    base = slugify(biz["name"] if biz else "client")
    username = f"robin-{base}-{str(account_id)[:6]}"
    display = f"Robin for {biz['name']}" if biz else "Robin"
    created = await _create_inbox(username, display)
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO mailboxes (account_id, address, provider_id, role, display_name)
                VALUES (%s, %s, %s, 'agent', %s)
                ON CONFLICT (address) DO UPDATE SET account_id = EXCLUDED.account_id
                RETURNING *
                """,
                (account_id, created["inbox_id"], created["inbox_id"], display),
            )
            row = await cur.fetchone()
        await conn.commit()
    log.info("created agent mailbox %s for account %s", row["address"], account_id)
    return row


async def ensure_simulated_insurer_mailbox() -> dict:
    """The demo insurer inbox. Always labelled as simulated."""
    existing = await get_mailbox(role="simulated_insurer")
    if existing:
        return existing
    created = await _create_inbox("sinistres-demo-assureur", "Service Indemnisation - SIMULATED INSURER")
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO mailboxes (account_id, address, provider_id, role, display_name)
                VALUES (NULL, %s, %s, 'simulated_insurer', %s)
                ON CONFLICT (address) DO UPDATE SET role = 'simulated_insurer'
                RETURNING *
                """,
                (created["inbox_id"], created["inbox_id"], created["display_name"]),
            )
            row = await cur.fetchone()
        await conn.commit()
    return row
