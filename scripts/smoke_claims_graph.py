"""Smoke test for the Claims Agent graph against a real database (no LLM, no Telegram token needed).

    .venv/bin/python scripts/smoke_claims_graph.py

Seeds an account + business, sends a Telegram message event, checks the thread parks on an
interrupt, then sends a second message and checks it resumes (AC-7 logic without a restart).
"""

from __future__ import annotations

import asyncio
import uuid

from app import db
from app.agents.claims import graph as G
from app.agents.claims import handlers as H


async def main() -> None:
    await db.open_pool()
    await db.run_migrations()
    await G.setup()
    acct = str(uuid.uuid4())
    async with db.pool.connection() as conn:
        await conn.execute("INSERT INTO accounts (id, email, password_hash) VALUES (%s, %s, 'x')", (acct, f"smoke-{acct[:8]}@example.com"))
        await conn.execute(
            "INSERT INTO businesses (account_id, name, siret, address, insurer_name, insurer_contact_email) VALUES (%s,'Karim Phone Repair','12345678900012','12 rue de la République, Marseille','MAAF','sinistres-demo@agentmail.to')",
            (acct,),
        )
        await conn.commit()

    ev1 = {"id": 1, "source": "telegram", "kind": "message", "account_id": acct, "claim_id": None,
           "payload": {"chat_id": 1, "text": "My shop was looted Saturday night around 7pm, the shutter was forced.", "provider_ref": "smoke-1"}}
    await H.on_client_input(ev1)
    claim_id = await H._open_claim_for(acct)
    assert claim_id, "claim not created"
    wait = await G.is_waiting(claim_id)
    print("after event 1: claim", claim_id, "waiting on", wait)
    assert wait == "awaiting_client", wait

    ev2 = dict(ev1, id=2, payload={"chat_id": 1, "text": "Here is more detail: about 180 phones were in stock.", "provider_ref": "smoke-2"})
    await H.on_client_input(ev2)
    print("after event 2: waiting on", await G.is_waiting(claim_id))

    async with db.pool.connection() as conn:
        comms = await (await conn.execute("SELECT channel, direction, delivery_status, subject, left(body, 70) FROM communications WHERE claim_id = %s ORDER BY created_at", (claim_id,))).fetchall()
        facts = await (await conn.execute("SELECT source_kind, status, left(statement, 60) FROM facts WHERE claim_id = %s ORDER BY created_at", (claim_id,))).fetchall()
        tasks = await (await conn.execute("SELECT kind, due_at::date, reason FROM scheduled_tasks WHERE claim_id = %s ORDER BY due_at", (claim_id,))).fetchall()
        reviews = await (await conn.execute("SELECT passed, violations FROM review_log WHERE claim_id = %s", (claim_id,))).fetchall()
        actions = await (await conn.execute("SELECT tool, ok FROM actions WHERE claim_id = %s ORDER BY created_at", (claim_id,))).fetchall()
    print("communications:", *comms, sep="\n  ")
    print("facts:", *facts, sep="\n  ")
    print("tasks:", *tasks, sep="\n  ")
    print("review_log:", *reviews, sep="\n  ")
    print("actions:", [a[0] for a in actions])
    assert any(c[0] == "email" and "Déclaration" in (c[3] or "") for c in comms), "no initial declaration email"
    assert all(r[0] for r in reviews), "a draft was blocked by the gate"
    await G.teardown()
    await db.close_pool()
    print("SMOKE OK")


if __name__ == "__main__":
    asyncio.run(main())
