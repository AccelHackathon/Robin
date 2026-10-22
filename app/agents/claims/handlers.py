"""Workstream C — worker handlers that route events into the Claims Agent graph. Owned by C.

Handles ("scheduler", "followup_due") and dispatches resumes for threads waiting on
client / insurer / call events (see docs/workstreams/README.md, "Event routing").
"""
from app.worker import handles  # noqa: F401
