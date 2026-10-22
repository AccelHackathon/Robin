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


class InboxLimitReached(Exception):
    pass


async def _create_inbox(username: str, display_name: str) -> dict:
    """Create the inbox, or reuse it if it already exists at AgentMail (e.g. DB was reset).
    Raises InboxLimitReached when the plan has no slot left."""
    address = f"{username}@{settings.agentmail_domain}"
    try:
        inbox = await agentmail().inboxes.create(
            request=CreateInboxRequest(username=username, domain=settings.agentmail_domain, display_name=display_name, client_id=username)
        )
    except Exception as exc:
        body = str(getattr(exc, "body", exc))
        try:
            inbox = await agentmail().inboxes.get(address)
            log.info("reusing existing inbox %s", address)
        except Exception:
            if "limit" in body.lower():
                raise InboxLimitReached(address) from exc
            raise
    return {"inbox_id": inbox.inbox_id, "display_name": getattr(inbox, "display_name", None) or display_name}


async def ensure_shared_mailbox() -> dict:
    """The shared agent inbox used when the plan's inbox limit is reached. Replies are routed by the
    [RB-xxxxxxxx] subject tag instead of the mailbox's account."""
    existing = await get_mailbox(address=settings.agentmail_shared_inbox)
    if existing:
        return existing
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                INSERT INTO mailboxes (account_id, address, provider_id, role, display_name, metadata)
                VALUES (NULL, %s, %s, 'agent', 'Robin (shared)', '{"shared": true}'::jsonb)
                ON CONFLICT (address) DO UPDATE SET role = 'agent' RETURNING *
                """,
                (settings.agentmail_shared_inbox, settings.agentmail_shared_inbox),
            )
            row = await cur.fetchone()
        await conn.commit()
    return row


async def bootstrap() -> None:
    """Startup hook: make sure the simulated insurer inbox exists and is known in this database."""
    if not settings.agentmail_api_key:
        return
    try:
        sim = await ensure_simulated_insurer_mailbox()
        shared = await ensure_shared_mailbox()
        log.info("simulated insurer mailbox: %s; shared agent mailbox: %s", sim["address"], shared["address"])
    except Exception:
        log.exception("could not bootstrap the email mailboxes")


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
    try:
        created = await _create_inbox(username, display)
    except InboxLimitReached:
        shared = await ensure_shared_mailbox()
        log.warning("inbox limit reached; account %s will use the shared mailbox %s", account_id, shared["address"])
        return shared
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
