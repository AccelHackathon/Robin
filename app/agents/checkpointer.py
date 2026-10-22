"""Shared LangGraph Postgres checkpointer on the application database.

Usage:
    saver = await get_checkpointer()
    graph = builder.compile(checkpointer=saver)

A small dedicated autocommit pool (the checkpointer requires autocommit + dict rows); tables are created on first
use. Workstreams A and C both compile their graphs against this saver; thread ids are namespaced
by the caller (e.g. "claim:<uuid>", "insurer_sim:<thread_ref>").
"""

import asyncio
import logging

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config import settings

log = logging.getLogger(__name__)

_saver: AsyncPostgresSaver | None = None
_lock = asyncio.Lock()


async def get_checkpointer() -> AsyncPostgresSaver:
    global _saver
    if _saver is not None:
        return _saver
    async with _lock:
        if _saver is None:
            if not settings.database_url:
                raise RuntimeError("DATABASE_URL is not set")
            pool = AsyncConnectionPool(settings.database_url, min_size=1, max_size=2, open=False,
                                       kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row})
            await pool.open()
            saver = AsyncPostgresSaver(pool)
            await saver.setup()
            _saver = saver
            log.info("langgraph checkpointer ready")
    return _saver
