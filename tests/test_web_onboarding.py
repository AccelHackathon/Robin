"""Integration tests use a dedicated database selected by ROBIN_TEST_DATABASE_URL."""

import os
import re
from pathlib import Path
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app import db
from app.main import app
from app.config import settings
from app.ingestion.load_corpus import load_corpus
from app.agents.intake.graph import run_intake, rows
from app.ingestion.search import search_clauses, verify_quote


@pytest.fixture(autouse=True)
def _no_db():
    """Override the unit-suite fixture: these tests require the real dedicated pool."""
    yield


@pytest.fixture(scope="module")
def client():
    url = os.getenv("ROBIN_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set ROBIN_TEST_DATABASE_URL to a dedicated PostgreSQL database.")
    previous = (
        settings.database_url,
        settings.worker_enabled,
        settings.openai_api_key,
        settings.telegram_bot_username,
    )
    settings.database_url = url
    settings.worker_enabled = False
    settings.openai_api_key = None
    settings.telegram_bot_username = "RobinTestBot"
    with TestClient(app) as c:
        c.portal.call(load_corpus)
        yield c
    (
        settings.database_url,
        settings.worker_enabled,
        settings.openai_api_key,
        settings.telegram_bot_username,
    ) = previous


def csrf(response):
    return re.search(r'name="csrf" value="([^"]+)"', response.text)[1]


def signup(c):
    c.cookies.clear()
    email = f"test-{uuid4().hex}@example.com"
    token = csrf(c.get("/signup"))
    response = c.post(
        "/signup",
        data={"csrf": token, "email": email, "password": "A-long-test-password-123"},
    )
    assert response.status_code == 200
    aid = c.portal.call(rows, "SELECT id FROM accounts WHERE email=%s", (email,))[0][
        "id"
    ]
    return aid


def business(c):
    token = csrf(c.get("/onboarding/business"))
    response = c.post(
        "/onboarding/business",
        data={
            "csrf": token,
            "name": "Karim Mobile",
            "representative_name": "Karim Benali",
            "tenant_or_owner": "tenant",
            "vat_recoverable": "yes",
            "insurer_name": "MAAF",
        },
    )
    assert response.status_code == 200


async def attach_maaf(aid):
    async with db.pool.connection() as conn:
        await conn.execute(
            "INSERT INTO account_contracts(account_id,document_id) SELECT %s,id FROM documents WHERE account_id IS NULL AND insurer_name='MAAF' ON CONFLICT DO NOTHING",
            (aid,),
        )


def test_auth_resume_csrf_and_logout(client):
    c = client
    signup(c)
    assert c.post("/onboarding/business", data={"name": "bad"}).status_code == 403
    business(c)
    assert "Karim Mobile" in c.get("/onboarding/business").text
    assert c.get("/onboarding/resume").url.path == "/onboarding/documents"
    cookie = c.cookies.get("robin_session")
    assert cookie and len(cookie) > 32
    response = c.post("/logout", data={"csrf": csrf(c.get("/onboarding/documents"))})
    assert response.status_code == 200
    assert c.get("/onboarding/profile.json", follow_redirects=False).status_code == 303
    c.cookies.set("robin_session", cookie)
    assert c.get("/onboarding/profile.json", follow_redirects=False).status_code == 303


def test_upload_analysis_versioning_and_isolation(client):
    c = client
    aid = signup(c)
    business(c)
    c.portal.call(attach_maaf, aid)
    source = Path("data/fixtures/karim_particular_conditions.pdf").read_bytes()
    for _ in range(2):
        response = c.post(
            "/onboarding/documents",
            data={"csrf": csrf(c.get("/onboarding/documents"))},
            files={"files": ("schedule.pdf", source, "application/pdf")},
        )
        assert response.status_code == 200
    docs = c.portal.call(rows, "SELECT id FROM documents WHERE account_id=%s", (aid,))
    assert len(docs) == 1
    c.portal.call(run_intake, str(aid))
    profile = c.get("/onboarding/profile.json").json()
    assert len(profile["guarantees"]) >= 15
    theft = next(
        f for f in profile["guarantees"] if f["guarantee"] == "theft_vandalism"
    )
    bi = next(
        f for f in profile["guarantees"] if f["guarantee"] == "business_interruption"
    )
    assert theft["subscribed"] == "yes" and theft["ceiling"]["amount"] == 15000
    assert bi["subscribed"] == "yes" and bi["deductible_detail"]["amount"] == 3
    assert c.get(f"/clauses/{theft['source_clause_id']}").status_code == 200
    c.portal.call(run_intake, str(aid))
    assert (
        next(
            f
            for f in c.get("/onboarding/profile.json").json()["guarantees"]
            if f["guarantee"] == "theft_vandalism"
        )["version"]
        == theft["version"]
    )
    endorsement = Path("data/fixtures/karim_endorsement.pdf").read_bytes()
    c.post(
        "/onboarding/documents",
        data={"csrf": csrf(c.get("/onboarding/documents"))},
        files={"files": ("endorsement.pdf", endorsement, "application/pdf")},
    )
    c.portal.call(run_intake, str(aid))
    updated = next(
        f
        for f in c.get("/onboarding/profile.json").json()["guarantees"]
        if f["guarantee"] == "theft_vandalism"
    )
    assert (
        updated["ceiling"]["amount"] == 30000
        and updated["version"] == theft["version"] + 1
    )
    versions = c.portal.call(
        rows,
        "SELECT supersedes FROM coverage_profile WHERE account_id=%s AND guarantee='theft_vandalism' ORDER BY version DESC",
        (aid,),
    )
    assert versions[0]["supersedes"]
    signup(c)
    assert c.get(f"/documents/{docs[0]['id']}").status_code == 404
    assert c.get(f"/clauses/{theft['source_clause_id']}").status_code == 404
    assert not c.get("/onboarding/profile.json").json()["guarantees"]


def test_missing_schedule_never_means_unsubscribed(client):
    c = client
    aid = signup(c)
    business(c)
    c.portal.call(attach_maaf, aid)
    c.portal.call(run_intake, str(aid))
    profile = c.get("/onboarding/profile.json").json()
    assert all(f["subscribed"] == "unknown" for f in profile["guarantees"])
    assert any("policy schedule" in t for t in profile["tasks"])


def test_mandate_atomic_fanout_and_link_expiry(client):
    c = client
    aid = signup(c)
    business(c)
    form = {
        "csrf": csrf(c.get("/onboarding/mandate")),
        "mandate": "on",
        "data_processing": "on",
        "telegram": "on",
        "signer_name": "Karim Benali",
        "signer_role": "Owner",
    }
    response = c.post("/onboarding/mandate", data=form)
    assert (
        response.status_code == 200
        and "https://t.me/RobinTestBot?start=" in response.text
    )
    c.post("/onboarding/mandate", data=form)
    assert (
        len(c.portal.call(rows, "SELECT id FROM mandates WHERE account_id=%s", (aid,)))
        == 1
    )
    assert (
        len(c.portal.call(rows, "SELECT id FROM consents WHERE account_id=%s", (aid,)))
        == 3
    )
    events = c.portal.call(
        rows, "SELECT kind,payload FROM events WHERE account_id=%s", (aid,)
    )
    assert {e["kind"] for e in events} == {"onboarding_done", "document_added"}
    codes = c.portal.call(
        rows,
        "SELECT extract(epoch from (expires_at-created_at)) AS seconds FROM link_codes WHERE account_id=%s",
        (aid,),
    )
    assert 899 <= codes[0]["seconds"] <= 901


def test_public_corpus_search_and_private_quote_boundary(client):
    c = client
    maaf = c.portal.call(
        rows,
        "SELECT id FROM documents WHERE account_id IS NULL AND insurer_name='MAAF'",
    )[0]["id"]
    hits = c.portal.call(search_clauses, str(maaf), "gardiennage", 30)
    assert any(c.page == 58 and "72 heures" in c.body for c in hits)
    initial = c.portal.call(
        rows, "SELECT count(*) AS count FROM documents WHERE account_id IS NULL"
    )[0]["count"]
    c.portal.call(load_corpus)
    assert (
        c.portal.call(
            rows, "SELECT count(*) AS count FROM documents WHERE account_id IS NULL"
        )[0]["count"]
        == initial
        == 12
    )


def test_upload_rejects_masquerading_file(client):
    c = client
    signup(c)
    business(c)
    response = c.post(
        "/onboarding/documents",
        data={"csrf": csrf(c.get("/onboarding/documents"))},
        files={"files": ("fake.pdf", b"not a PDF", "application/pdf")},
    )
    assert "Choose a PDF" in response.text


def test_tracking_links_are_scoped_and_revocable(client):
    c = client
    aid = signup(c)
    business(c)

    async def create_claim():
        async with db.pool.connection() as conn:
            return str(
                (
                    await (
                        await conn.execute(
                            "INSERT INTO claims(account_id,summary) VALUES (%s,'Fictional test claim') RETURNING id",
                            (aid,),
                        )
                    ).fetchone()
                )[0]
            )

    claim = c.portal.call(create_claim)
    response = c.post(
        f"/claims/{claim}/tracking-link",
        data={"csrf": csrf(c.get("/onboarding/business"))},
        follow_redirects=False,
    )
    link = response.headers["location"]
    assert "token=" in link
    signup(c)
    assert c.get(f"/claims/{claim}/track").status_code == 404
    assert (
        c.post(
            f"/claims/{claim}/tracking-link",
            data={"csrf": csrf(c.get("/onboarding/business"))},
        ).status_code
        == 404
    )
    c.cookies.clear()
    assert c.get(link).status_code == 200
    assert c.get(link + "x").status_code == 404


def test_urgent_path_skips_documents_and_saves_incident(client):
    c = client
    aid = signup(c)
    response = c.post(
        "/onboarding/business",
        data={
            "csrf": csrf(c.get("/onboarding/business")),
            "name": "Test shop",
            "representative_name": "Test person",
            "tenant_or_owner": "unknown",
            "urgent": "1",
            "incident": "Window broken this morning.",
        },
    )
    assert response.url.path == "/onboarding/mandate"
    record = c.portal.call(
        rows, "SELECT urgent,incident FROM onboarding WHERE account_id=%s", (aid,)
    )[0]
    assert record["urgent"] and record["incident"] == "Window broken this morning."


def test_expired_sessions_and_csrf_origin(client):
    c = client
    aid = signup(c)
    token = csrf(c.get("/onboarding/business"))
    assert (
        c.post(
            "/onboarding/business",
            data={"csrf": token},
            headers={"Origin": "https://untrusted.example"},
        ).status_code
        == 403
    )

    async def expire():
        async with db.pool.connection() as conn:
            await conn.execute(
                "UPDATE web_sessions SET expires_at=now()-interval '1 second' WHERE account_id=%s",
                (aid,),
            )

    c.portal.call(expire)
    assert c.get("/onboarding/business", follow_redirects=False).status_code == 303


def test_private_quote_requires_account_context(client):
    c = client
    aid = signup(c)
    business(c)
    c.post(
        "/onboarding/documents",
        data={"csrf": csrf(c.get("/onboarding/documents"))},
        files={
            "files": (
                "private.pdf",
                Path("data/fixtures/karim_particular_conditions.pdf").read_bytes(),
                "application/pdf",
            )
        },
    )
    c.portal.call(run_intake, str(aid))
    fact = next(
        f
        for f in c.get("/onboarding/profile.json").json()["guarantees"]
        if f["guarantee"] == "theft_vandalism"
    )
    assert c.portal.call(verify_quote, fact["source_clause_id"], fact["quote"]) is False

    async def authorized():
        return await verify_quote(
            fact["source_clause_id"], fact["quote"], account_id=str(aid)
        )

    assert c.portal.call(authorized) is True


def test_model_citation_and_amount_validation(client, monkeypatch):
    from types import SimpleNamespace
    from app.agents.intake import graph as module

    c = client
    aid = signup(c)
    clause = {
        "id": 987654321,
        "page": 1,
        "sha256": uuid4().hex,
        "metadata": {},
        "body": "Le plafond stock est fixé à 15 000 EUR par sinistre.",
    }
    result = {
        "subscribed": "yes",
        "ceiling": {"amount": 30000, "unit": "EUR", "basis": "stock"},
        "deductible": None,
        "conditions": [],
        "exclusions": [],
        "quote": clause["body"],
        "confidence": "high",
    }

    class Model:
        def __init__(self, **kwargs):
            pass

        async def ainvoke(self, *args):
            import json

            return SimpleNamespace(content=json.dumps(result), usage_metadata={})

    monkeypatch.setattr(module, "chat_model", lambda **kwargs: Model(**kwargs))
    monkeypatch.setattr(settings, "openai_api_key", "fake-test-key")
    with pytest.raises(ValueError, match="amount"):
        c.portal.call(
            module.extract_fact,
            str(aid),
            "theft_vandalism",
            clause,
            "particular_conditions",
        )
    result["ceiling"]["amount"] = 15000
    result["quote"] = "A completely invented sentence about this insurance policy."
    with pytest.raises(ValueError, match="citation"):
        c.portal.call(
            module.extract_fact,
            str(aid),
            "theft_vandalism",
            clause,
            "particular_conditions",
        )
    result["quote"] = clause["body"]
    extracted = c.portal.call(
        module.extract_fact, str(aid), "theft_vandalism", clause, "general_conditions"
    )
    assert extracted["subscribed"] == "unknown"


def test_telegram_consent_can_be_added_later(client):
    c = client
    aid = signup(c)
    business(c)
    c.post(
        "/onboarding/mandate",
        data={
            "csrf": csrf(c.get("/onboarding/mandate")),
            "mandate": "on",
            "data_processing": "on",
            "signer_name": "Demo",
            "signer_role": "Owner",
        },
    )
    assert not c.portal.call(
        rows, "SELECT code FROM link_codes WHERE account_id=%s", (aid,)
    )
    response = c.post(
        "/onboarding/telegram-consent",
        data={"csrf": csrf(c.get("/onboarding/done")), "telegram": "on"},
    )
    assert "https://t.me/RobinTestBot?start=" in response.text
    assert (
        len(
            c.portal.call(
                rows,
                "SELECT id FROM consents WHERE account_id=%s AND purpose='telegram'",
                (aid,),
            )
        )
        == 1
    )
