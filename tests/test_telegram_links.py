"""Telegram linking — pure helpers (no DB)."""

import pytest

from app.channels.telegram.links import parse_start_code


@pytest.mark.parametrize("text,expected", [
    ("/start ABC123", "ABC123"),
    ("/start@RobinClaimsBot ABC123", "ABC123"),
    ("/start", None),
    ("/start   ", None),
    ("hello", None),
    (None, None),
    ("/start  code-with-dash ", "code-with-dash"),
])
def test_parse_start_code(text, expected):
    assert parse_start_code(text) == expected


def test_webhook_rejects_wrong_token():
    from fastapi.testclient import TestClient

    from app.config import settings
    from app.main import app

    settings.telegram_bot_token = "secret-token"
    try:
        # No `with`: the lifespan (DB, polling) must not run; only the route is under test.
        client = TestClient(app, raise_server_exceptions=False)
        assert client.post("/webhooks/telegram/not-the-token", json={}).status_code == 404
        assert client.post("/webhooks/telegram/secret-token", json={}).status_code == 503  # token ok, bot not built
    finally:
        settings.telegram_bot_token = None
