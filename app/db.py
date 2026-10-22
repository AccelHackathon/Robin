import logging
from pathlib import Path

from psycopg_pool import AsyncConnectionPool

from app.config import settings

log = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

pool: AsyncConnectionPool | None = None


async def open_pool() -> AsyncConnectionPool | None:
    global pool
    if not settings.database_url:
        log.warning("DATABASE_URL not set; running without a database")
        return None
    pool = AsyncConnectionPool(settings.database_url, min_size=1, max_size=8, open=False)
    await pool.open()
    await pool.wait()
    log.info("database pool ready")
    return pool


async def close_pool() -> None:
    global pool
    if pool:
        await pool.close()
        pool = None


async def ping() -> bool:
    if not pool:
        return False
    try:
        async with pool.connection() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        log.exception("database ping failed")
        return False


async def run_migrations() -> list[str]:
    if not pool:
        return []
    applied: list[str] = []
    async with pool.connection() as conn:
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (name text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"
        )
        await conn.execute("SELECT pg_advisory_lock(727272)")
        try:
            done = {r[0] for r in await (await conn.execute("SELECT name FROM schema_migrations")).fetchall()}
            for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
                if path.name in done:
                    continue
                log.info("applying migration %s", path.name)
                await conn.execute(path.read_text())
                await conn.execute("INSERT INTO schema_migrations (name) VALUES (%s)", (path.name,))
                applied.append(path.name)
            await conn.commit()
        finally:
            await conn.execute("SELECT pg_advisory_unlock(727272)")
    return applied
