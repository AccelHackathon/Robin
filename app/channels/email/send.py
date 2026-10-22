"""`send_email` adapter (workstream A). Called by the Claims Agent's `send_email` tool
and by the simulated insurer. The caller is responsible for having passed `review()`.
"""

import asyncio
import base64
import html
import logging

from psycopg.rows import dict_row

from app import db
from app.agents.audit import record_action
from app.channels.email.client import agentmail, claim_tag
from app.channels.email.mailboxes import ensure_account_mailbox, get_mailbox

log = logging.getLogger(__name__)


async def _attachments(document_ids: list[str]) -> list[dict]:
    if not document_ids:
        return []
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT id, filename, mime_type, content FROM documents WHERE id = ANY(%s::uuid[])", (document_ids,))
            rows = await cur.fetchall()
    out = []
    for r in rows:
        if r["content"] is None:
            log.warning("document %s has no stored content; skipped as attachment", r["id"])
            continue
        out.append({
            "filename": r["filename"] or f"{r['id']}.bin",
            "content_type": r["mime_type"] or "application/octet-stream",
            "content": base64.b64encode(bytes(r["content"])).decode(),
        })
    return out


def _text_to_html(text: str) -> str:
    return "<div style=\"font-family:system-ui,Arial,sans-serif;white-space:pre-wrap\">" + html.escape(text) + "</div>"


async def send_email(
    *,
    account_id: str | None,
    claim_id: str | None,
    to: str,
    subject: str,
    body: str,
    attachment_document_ids: list[str] = (),
    language: str = "fr",
    from_mailbox_address: str | None = None,
    in_reply_to: str | None = None,
    thread_ref: str | None = None,
    agent: str = "claims",
) -> str:
    """Send from the account's agent mailbox (or an explicit mailbox). Returns communication_id.

    Retries 3 times on provider errors; on final failure the communication is stored with
    `failed_reason` and the id is still returned so the caller can tell the client.
    """
    if from_mailbox_address:
        mailbox = await get_mailbox(address=from_mailbox_address)
        if not mailbox:
            raise RuntimeError(f"unknown mailbox {from_mailbox_address}")
    else:
        if not account_id:
            raise RuntimeError("account_id is required to pick the agent mailbox")
        mailbox = await ensure_account_mailbox(account_id)

    tag = claim_tag(claim_id)
    full_subject = subject if (not tag or tag in subject) else f"{subject} {tag}"
    attachments = await _attachments(list(attachment_document_ids))

    async with db.pool.connection() as conn:
        comm_id = (
            await (
                await conn.execute(
                    """
                    INSERT INTO communications (account_id, claim_id, channel, direction, counterpart, subject, body, attachments,
                                                delivery_status, language, mailbox_id, from_address, to_addresses, in_reply_to, thread_ref)
                    VALUES (%s, %s, 'email', 'outbound', %s, %s, %s, %s::uuid[], 'sending', %s, %s, %s, %s, %s, %s) RETURNING id
                    """,
                    (account_id, claim_id, to, full_subject, body, list(attachment_document_ids), language, mailbox["id"],
                     mailbox["address"], [to], in_reply_to, thread_ref),
                )
            ).fetchone()
        )[0]
        await conn.commit()

    last_error: Exception | None = None
    response = None
    for attempt in range(3):
        try:
            client = agentmail()
            kwargs = dict(to=[to], text=body, html=_text_to_html(body), attachments=attachments or None,
                          labels=[f"claim:{str(claim_id)[:8]}"] if claim_id else None, idempotency_key=str(comm_id))
            if in_reply_to:
                response = await client.inboxes.messages.reply(mailbox["address"], in_reply_to, **kwargs)
            else:
                response = await client.inboxes.messages.send(mailbox["address"], subject=full_subject, **kwargs)
            last_error = None
            break
        except Exception as exc:  # provider errors, network
            last_error = exc
            log.warning("send_email attempt %d failed: %r", attempt + 1, exc)
            await asyncio.sleep(1.5 * (attempt + 1))

    async with db.pool.connection() as conn:
        if last_error is None and response is not None:
            await conn.execute(
                "UPDATE communications SET delivery_status = 'sent', provider_ref = %s, thread_ref = coalesce(%s, thread_ref) WHERE id = %s",
                (response.message_id, getattr(response, "thread_id", None), comm_id),
            )
        else:
            await conn.execute(
                "UPDATE communications SET delivery_status = 'failed', failed_reason = %s WHERE id = %s",
                (repr(last_error)[:500], comm_id),
            )
        await conn.commit()

    await record_action(agent, "send_email", {"to": to, "subject": full_subject, "attachments": len(attachments), "claim_id": claim_id},
                        {"communication_id": str(comm_id), "ok": last_error is None, "error": repr(last_error) if last_error else None},
                        ok=last_error is None, claim_id=claim_id, account_id=account_id)
    return str(comm_id)
