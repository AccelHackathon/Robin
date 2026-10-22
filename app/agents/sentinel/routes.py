"""Workstream D — operator endpoints for the Sentinel (bearer INTERNAL_API_TOKEN) and the alerts feed."""

from fastapi import APIRouter, Header, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

from app import db
from app.agents.sentinel.graph import sweep
from app.agents.sentinel.handlers import arm
from app.config import settings

router = APIRouter(prefix="/internal/sentinel", tags=["sentinel"])


def _auth(authorization: str | None) -> None:
    if not settings.internal_api_token or authorization != f"Bearer {settings.internal_api_token}":
        raise HTTPException(status_code=401)


class SweepRequest(BaseModel):
    account_id: str


@router.post("/sweep")
async def run_sweep(body: SweepRequest, authorization: str | None = Header(default=None)):
    """Run one sweep now (rehearsal / demo). Returns stats and the alerts produced."""
    _auth(authorization)
    await arm(body.account_id, delay_minutes=settings.sentinel_interval_minutes)
    state = await sweep(body.account_id)
    return {
        "stats": state.get("stats"),
        "notified": state.get("notified", 0),
        "alerts": [{k: a.get(k) for k in ("title", "severity", "place", "event_starts_at", "guarantee", "review_passed", "notify", "message_en")}
                   | {"source": a["source"]["url"]} for a in state.get("alerts", [])],
    }


@router.get("/alerts")
async def list_alerts(account_id: str, authorization: str | None = Header(default=None), limit: int = 20):
    _auth(authorization)
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT a.id, a.created_at, a.risk_key, a.severity, a.status, a.title, a.place, a.event_starts_at, a.guarantee, a.clause_page,
                       a.message_en, a.claim_id,
                       (SELECT json_agg(json_build_object('url', s.url, 'title', s.title, 'official', s.official, 'published_at', s.published_at))
                          FROM alert_sources s WHERE s.alert_id = a.id) AS sources
                FROM alerts a WHERE a.account_id = %s ORDER BY a.created_at DESC LIMIT %s
                """,
                (account_id, limit),
            )
            alerts = await cur.fetchall()
            await cur.execute("SELECT * FROM risk_profiles WHERE account_id = %s", (account_id,))
            profile = await cur.fetchone()
            await cur.execute("SELECT * FROM sentinel_sweeps WHERE account_id = %s ORDER BY started_at DESC LIMIT 5", (account_id,))
            sweeps = await cur.fetchall()
    return {"profile": profile, "alerts": alerts, "recent_sweeps": sweeps}
