import pytest


@pytest.fixture(autouse=True)
def _no_db(monkeypatch):
    """Unit tests run without a database: gate paths that need `db.pool` short-circuit on None."""
    from app import db

    monkeypatch.setattr(db, "pool", None)
