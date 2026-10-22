import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import db, worker
from app.config import settings
from app.routes import health

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("robin")


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = asyncio.Event()
    worker_task = None
    if await db.open_pool():
        applied = await db.run_migrations()
        log.info("migrations applied: %s", applied or "none")
        if settings.worker_enabled:
            worker_task = asyncio.create_task(worker.run_forever(stop))
    log.info("robin up, commit=%s", settings.git_commit)
    try:
        yield
    finally:
        stop.set()
        if worker_task:
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
        await db.close_pool()


app = FastAPI(title="Robin", version="0.1.0", lifespan=lifespan)
app.include_router(health.router)


@app.get("/")
async def root():
    return {"service": "robin", "docs": "/docs", "health": "/health"}
