"""Workstream A — route inbound emails on the simulated_insurer mailbox into the simulator graph."""

import asyncio
import logging

from app.agents.insurer_sim.graph import run as run_simulator
from app.worker import handles

log = logging.getLogger(__name__)
_tasks: set[asyncio.Task] = set()


@handles("agentmail", "email_received")
async def simulated_insurer_reply(event: dict) -> None:
    payload = event.get("payload") or {}
    if payload.get("mailbox_role") != "simulated_insurer":
        return  # the agent mailbox is handled by workstream C

    async def _run():
        try:
            await run_simulator(payload)
        except Exception:
            log.exception("simulated insurer failed on event %s", event.get("id"))

    # The scripted reply delay (15-30 s) must not stall the worker for everyone else.
    task = asyncio.create_task(_run())
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
