import asyncio
import json
import logging
from typing import Any

from psycopg.rows import dict_row

from app import db
from app.config import settings

log = logging.getLogger(__name__)

HANDLERS: dict[str, Any] = {}


def handles(source: str, kind: str):
    """Register an async handler(event: dict) for a (source, kind) pair."""

    def deco(fn):
        HANDLERS[(source, kind)] = fn
        return fn

    return deco


async def enqueue(source: str, kind: str, payload: dict, account_id=None, claim_id=None) -> int:
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                "INSERT INTO events (source, kind, account_id, claim_id, payload) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (source, kind, account_id, claim_id, json.dumps(payload)),
            )
        ).fetchone()
        await conn.commit()
    return row[0]


async def _claim_one() -> dict | None:
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                UPDATE events SET status = 'processing', attempts = attempts + 1
                WHERE id = (
                    SELECT id FROM events WHERE status = 'pending'
                    ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1
                )
                RETURNING *
                """
            )
            row = await cur.fetchone()
        await conn.commit()
    return row


async def _finish(event_id: int, ok: bool, error: str | None = None) -> None:
    async with db.pool.connection() as conn:
        await conn.execute(
            "UPDATE events SET status = %s, error = %s, processed_at = now() WHERE id = %s",
            ("done" if ok else "failed", error, event_id),
        )
        await conn.commit()


async def _fire_due_tasks() -> None:
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "UPDATE scheduled_tasks SET status = 'fired' WHERE status = 'pending' AND due_at <= now() RETURNING id, claim_id, reason"
            )
            rows = await cur.fetchall()
        await conn.commit()
    for t in rows:
        await enqueue("scheduler", "followup_due", {"task_id": str(t["id"]), "reason": t["reason"]}, claim_id=t["claim_id"])


async def run_forever(stop: asyncio.Event) -> None:
    log.info("worker started (%d handlers)", len(HANDLERS))
    while not stop.is_set():
        try:
            await _fire_due_tasks()
            event = await _claim_one()
            if not event:
                await asyncio.sleep(settings.worker_poll_seconds)
                continue
            handler = HANDLERS.get((event["source"], event["kind"]))
            if not handler:
                await _finish(event["id"], False, f"no handler for {event['source']}/{event['kind']}")
                continue
            try:
                await handler(event)
                await _finish(event["id"], True)
            except Exception as exc:
                log.exception("event %s failed", event["id"])
                await _finish(event["id"], False, repr(exc))
        except asyncio.CancelledError:
            break
        except Exception:
            log.exception("worker loop error")
            await asyncio.sleep(2)
    log.info("worker stopped")
