import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import db, worker
from app.agents.claims import handlers as claims_handlers  # noqa: F401  (registers worker handlers)
from app.agents.insurer_sim import handlers as insurer_sim_handlers  # noqa: F401
from app.agents.intake import handlers as intake_handlers  # noqa: F401
from app.channels.email import handlers as email_handlers  # noqa: F401
from app.channels.email import routes as email_routes
from app.channels.telegram import handlers as telegram_handlers  # noqa: F401
from app.channels.telegram import routes as telegram_routes
from app.channels.voice import handlers as voice_handlers  # noqa: F401
from app.channels.voice import routes as voice_routes
from app.config import settings
from app.routes import health
from app.web import routes as web_routes

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
app.include_router(web_routes.router)          # workstream B
app.include_router(telegram_routes.router)     # workstream C
app.include_router(email_routes.router)        # workstream A
app.include_router(voice_routes.router)        # workstream A


@app.get("/")
async def root():
    return {"service": "robin", "docs": "/docs", "health": "/health"}
