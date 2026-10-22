"""Workstream D — Sentinel event handlers.

- ("sentinel", "sweep_due")        : run one sweep for the account (background task, never blocks the worker)
- ("web", "onboarding_done")       : arm monitoring for the new account (first sweep 3 minutes later, after Intake)
- ("telegram", "message"|"document"): when a new claim appears for the account, link matching alerts as evidence
"""

import asyncio
import logging

from app import db
from app.agents.sentinel.graph import link_alerts_to_claim, sweep
from app.config import settings
from app.worker import handles

log = logging.getLogger(__name__)
_tasks: set[asyncio.Task] = set()


def _background(coro):
    task = asyncio.create_task(coro)
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


async def arm(account_id: str, delay_minutes: int = 3) -> None:
    async with db.pool.connection() as conn:
        await conn.execute(
            """
            INSERT INTO risk_profiles (account_id, sweep_interval_minutes, next_sweep_at)
            VALUES (%s, %s, now() + make_interval(mins => %s))
            ON CONFLICT (account_id) DO UPDATE SET watch_enabled = true, next_sweep_at = LEAST(risk_profiles.next_sweep_at, EXCLUDED.next_sweep_at)
            """,
            (account_id, settings.sentinel_interval_minutes, delay_minutes),
        )
        await conn.commit()


@handles("web", "onboarding_done")
async def arm_on_onboarding(event: dict) -> None:
    if not settings.sentinel_enabled:
        return
    account_id = event.get("account_id") or (event.get("payload") or {}).get("account_id")
    if account_id:
        await arm(str(account_id))
        log.info("sentinel armed for account %s", account_id)


@handles("sentinel", "sweep_due")
async def on_sweep_due(event: dict) -> None:
    account_id = event.get("account_id") or (event.get("payload") or {}).get("account_id")
    if not account_id:
        return

    async def _run():
        try:
            state = await sweep(str(account_id))
            log.info("sentinel sweep for %s: %s", account_id, state.get("stats"))
        except Exception:
            log.exception("sentinel sweep failed for %s", account_id)

    _background(_run())


@handles("telegram", "message")
@handles("telegram", "document")
async def link_alerts_on_new_claim(event: dict) -> None:
    """Runs after C's handler (registration order): if the account now has a claim without linked alerts,
    attach the alerts whose window covers the loss date."""
    account_id = event.get("account_id")
    if not account_id:
        return
    async with db.pool.connection() as conn:
        rows = await (await conn.execute(
            "SELECT id, coalesce(loss_date::timestamptz, created_at) FROM claims WHERE account_id = %s ORDER BY created_at DESC LIMIT 1", (account_id,)
        )).fetchall()
    for claim_id, loss_date in rows:
        n = await link_alerts_to_claim(str(claim_id), str(account_id), loss_date)
        if n:
            log.info("linked %d sentinel alerts to claim %s as external-event evidence", n, claim_id)
