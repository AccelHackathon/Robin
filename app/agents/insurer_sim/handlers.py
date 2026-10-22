"""Workstream A — route inbound emails on the simulated_insurer mailbox into the simulator graph."""

import logging

from app.agents.insurer_sim.graph import run as run_simulator
from app.worker import handles

log = logging.getLogger(__name__)


@handles("agentmail", "email_received")
async def simulated_insurer_reply(event: dict) -> None:
    payload = event.get("payload") or {}
    if payload.get("mailbox_role") != "simulated_insurer":
        return  # the agent mailbox is handled by workstream C
    await run_simulator(payload)
