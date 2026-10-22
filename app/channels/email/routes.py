"""Workstream A — AgentMail inbound webhook.

Verifies the Svix signature, stores the message as an inbound `communications` row and its
attachments as `documents`, then enqueues ("agentmail", "email_received") carrying the mailbox
role so the worker routes it to the Claims Agent (role `agent`) or to the simulated insurer
(role `simulated_insurer`). Replies to the client's claim are matched through the subject tag
[RB-xxxxxxxx] that every outbound email carries.
"""

import hashlib
import json
import logging
import re
import subprocess
import tempfile

import httpx
from fastapi import APIRouter, HTTPException, Request
from psycopg.rows import dict_row
from svix.webhooks import Webhook, WebhookVerificationError

from app import db
from app.channels.email.client import agentmail
from app.channels.email.mailboxes import get_mailbox
from app.config import settings
from app.worker import enqueue

log = logging.getLogger(__name__)
router = APIRouter(tags=["email"])

TAG_RE = re.compile(r"\[RB-([0-9a-fA-F]{8})\]")
RECEIVED_EVENTS = {"message.received", "message.received.unauthenticated"}


def parse_claim_tag(subject: str | None) -> str | None:
    m = TAG_RE.search(subject or "")
    return m.group(1).lower() if m else None


async def resolve_claim(tag: str | None, mailbox: dict) -> tuple[str | None, str | None]:
    """Returns (claim_id, account_id) for a subject tag, scoped to the mailbox account when known."""
    account_id = mailbox.get("account_id")
    if not tag:
        return None, account_id
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            if account_id:
                await cur.execute("SELECT id, account_id FROM claims WHERE account_id = %s AND left(id::text, 8) = %s", (account_id, tag))
            else:
                await cur.execute("SELECT id, account_id FROM claims WHERE left(id::text, 8) = %s", (tag,))
            row = await cur.fetchone()
    return (str(row["id"]), str(row["account_id"])) if row else (None, account_id)


def _pdf_text(content: bytes) -> str | None:
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(content)
            f.flush()
            out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, timeout=60)
            return out.stdout.decode("utf-8", "ignore") if out.returncode == 0 else None
    except Exception:
        return None


async def store_attachments(mailbox: dict, message: dict, account_id: str | None, claim_id: str | None) -> list[str]:
    ids: list[str] = []
    attachments = message.get("attachments") or []
    if not attachments:
        return ids
    client = agentmail()
    async with httpx.AsyncClient(timeout=60) as http:
        for att in attachments:
            att_id = att.get("attachment_id")
            try:
                meta = await client.inboxes.messages.get_attachment(mailbox["address"], message["message_id"], att_id)
                content = (await http.get(meta.download_url)).content
                text = None
                text_url = getattr(meta, "text_url", None)
                if text_url:
                    text = (await http.get(text_url)).text
                elif (att.get("content_type") or "").startswith("application/pdf"):
                    text = _pdf_text(content)
            except Exception:
                log.exception("failed to download attachment %s", att_id)
                continue
            sha = hashlib.sha256(content).hexdigest()
            mime = att.get("content_type") or getattr(meta, "content_type", None) or "application/octet-stream"
            doc_type = "correspondence" if mime.startswith("application/pdf") else ("photo" if mime.startswith("image/") else "other")
            async with db.pool.connection() as conn:
                row = await (
                    await conn.execute(
                        """
                        INSERT INTO documents (account_id, claim_id, doc_type, origin, filename, mime_type, sha256, content, extracted_text, metadata)
                        VALUES (%s, %s, %s, 'email', %s, %s, %s, %s, %s, %s) RETURNING id
                        """,
                        (account_id, claim_id, doc_type, att.get("filename"), mime, sha, content, text,
                         json.dumps({"from": message.get("from"), "subject": message.get("subject"), "attachment_id": att_id})),
                    )
                ).fetchone()
                await conn.commit()
            ids.append(str(row[0]))
    return ids


@router.post("/webhooks/agentmail")
async def agentmail_webhook(request: Request):
    raw = await request.body()
    if settings.agentmail_webhook_secret:
        try:
            Webhook(settings.agentmail_webhook_secret).verify(raw, dict(request.headers))
        except WebhookVerificationError:
            raise HTTPException(status_code=401, detail="invalid signature")
    else:
        log.warning("AGENTMAIL_WEBHOOK_SECRET not set; accepting unsigned webhook")

    payload = json.loads(raw)
    event_type = payload.get("event_type")
    if event_type not in RECEIVED_EVENTS:
        return {"received": True, "ignored": event_type}

    message = payload.get("message") or {}
    inbox_address = message.get("inbox_id")
    mailbox = await get_mailbox(address=inbox_address)
    if not mailbox:
        log.warning("email for unknown mailbox %s", inbox_address)
        return {"received": True, "ignored": "unknown mailbox"}

    provider_ref = message.get("message_id")
    async with db.pool.connection() as conn:
        dup = await (await conn.execute(
            "SELECT 1 FROM communications WHERE channel = 'email' AND direction = 'inbound' AND mailbox_id = %s AND provider_ref = %s",
            (mailbox["id"], provider_ref),
        )).fetchone()
    if dup:
        return {"received": True, "ignored": "duplicate"}

    tag = parse_claim_tag(message.get("subject"))
    claim_id, account_id = await resolve_claim(tag, mailbox)
    body_text = message.get("extracted_text") or message.get("text") or ""
    attachment_ids = await store_attachments(mailbox, message, account_id, claim_id)

    async with db.pool.connection() as conn:
        comm_id = (
            await (
                await conn.execute(
                    """
                    INSERT INTO communications (account_id, claim_id, channel, direction, counterpart, subject, body, attachments,
                                                provider_ref, delivery_status, mailbox_id, thread_ref, from_address, to_addresses)
                    VALUES (%s, %s, 'email', 'inbound', %s, %s, %s, %s::uuid[], %s, 'received', %s, %s, %s, %s) RETURNING id
                    """,
                    (account_id, claim_id, message.get("from"), message.get("subject"), body_text, attachment_ids,
                     provider_ref, mailbox["id"], message.get("thread_id"), message.get("from"), message.get("to") or []),
                )
            ).fetchone()
        )[0]
        await conn.commit()

    await enqueue(
        "agentmail", "email_received",
        {
            "mailbox_id": str(mailbox["id"]),
            "mailbox_role": mailbox["role"],
            "mailbox_address": mailbox["address"],
            "communication_id": str(comm_id),
            "from": message.get("from"),
            "subject": message.get("subject"),
            "body_text": body_text,
            "attachment_document_ids": attachment_ids,
            "thread_ref": message.get("thread_id"),
            "message_id": provider_ref,
            "claim_tag": tag,
            "provider_ref": f"agentmail:{payload.get('event_id') or provider_ref}",
        },
        account_id=account_id, claim_id=claim_id,
    )
    return {"received": True}
