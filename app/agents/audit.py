import json
import time
from contextlib import asynccontextmanager
from typing import Any

from app import db


async def record_action(
    agent: str,
    tool: str,
    arguments: dict[str, Any],
    result: Any = None,
    ok: bool = True,
    *,
    claim_id: str | None = None,
    account_id: str | None = None,
    trigger_event_id: int | None = None,
    tokens_in: int | None = None,
    tokens_out: int | None = None,
    latency_ms: int | None = None,
    model: str | None = None,
) -> int:
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                """
                INSERT INTO actions (agent, tool, arguments, result, ok, claim_id, account_id, trigger_event_id,
                                     tokens_in, tokens_out, latency_ms, model)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (agent, tool, json.dumps(arguments, default=str), json.dumps(result, default=str) if result is not None else None,
                 ok, claim_id, account_id, trigger_event_id, tokens_in, tokens_out, latency_ms, model),
            )
        ).fetchone()
        await conn.commit()
    return row[0]


@asynccontextmanager
async def timed_action(agent: str, tool: str, arguments: dict[str, Any], **ids):
    """Usage: async with timed_action("claims", "search_clauses", {...}, claim_id=cid) as a: a["result"] = ..."""
    started = time.perf_counter()
    holder: dict[str, Any] = {"result": None, "ok": True}
    try:
        yield holder
    except Exception as exc:
        holder["ok"], holder["result"] = False, {"error": repr(exc)}
        raise
    finally:
        await record_action(agent, tool, arguments, holder["result"], holder["ok"],
                            latency_ms=int((time.perf_counter() - started) * 1000), **ids)
