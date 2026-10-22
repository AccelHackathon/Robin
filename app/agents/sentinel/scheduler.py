"""Sentinel scheduler: every minute, enqueue a sweep for each watched account whose next_sweep_at is due.
Runs as a background task in the application lifespan. Bumps next_sweep_at before enqueueing so a
restart or a second instance never double-sweeps the same account.
"""

import asyncio
import logging

from app import db
from app.config import settings
from app.worker import enqueue

log = logging.getLogger(__name__)


async def tick() -> int:
    if db.pool is None:
        return 0
    async with db.pool.connection() as conn:
        rows = await (await conn.execute(
            """
            UPDATE risk_profiles SET next_sweep_at = now() + make_interval(mins => sweep_interval_minutes)
            WHERE watch_enabled AND next_sweep_at <= now() RETURNING account_id
            """
        )).fetchall()
        await conn.commit()
    for (account_id,) in rows:
        await enqueue("sentinel", "sweep_due", {"account_id": str(account_id), "provider_ref": f"sentinel:{account_id}:{int(asyncio.get_event_loop().time())}"},
                      account_id=account_id)
    return len(rows)


async def run_forever(stop: asyncio.Event, interval_seconds: int = 60) -> None:
    if not settings.sentinel_enabled:
        log.info("sentinel scheduler disabled")
        return
    log.info("sentinel scheduler started (interval %ss)", interval_seconds)
    while not stop.is_set():
        try:
            n = await tick()
            if n:
                log.info("sentinel: %d sweep(s) enqueued", n)
        except asyncio.CancelledError:
            break
        except Exception:
            log.exception("sentinel scheduler tick failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            pass
    log.info("sentinel scheduler stopped")
