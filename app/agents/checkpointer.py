"""Shared LangGraph Postgres checkpointer on the application database.

Usage:
    saver = await get_checkpointer()
    graph = builder.compile(checkpointer=saver)

One dedicated autocommit connection (the checkpointer requires it); tables are created on first
use. Workstreams A and C both compile their graphs against this saver; thread ids are namespaced
by the caller (e.g. "claim:<uuid>", "insurer_sim:<thread_ref>").
"""

import asyncio
import logging

import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row

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
            conn = await psycopg.AsyncConnection.connect(
                settings.database_url, autocommit=True, prepare_threshold=0, row_factory=dict_row
            )
            saver = AsyncPostgresSaver(conn)
            await saver.setup()
            _saver = saver
            log.info("langgraph checkpointer ready")
    return _saver
