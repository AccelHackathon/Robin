"""Workstream A — voice result handling (no network)."""

import hashlib
import hmac
import time

from app.channels.voice import elevenlabs
from app.channels.voice.call import build_dynamic_variables
from app.channels.voice.results import structured_result_from_payload


def _sig(secret: str, body: bytes, ts: int | None = None) -> str:
    ts = ts or int(time.time())
    mac = hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={ts},v0={mac}"


def test_hmac_accepts_valid_and_rejects_tampered():
    body = b'{"type":"post_call_transcription"}'
    assert elevenlabs.verify_signature(body, _sig("s3cret", body), "s3cret")
    assert not elevenlabs.verify_signature(body + b" ", _sig("s3cret", body), "s3cret")
    assert not elevenlabs.verify_signature(body, _sig("other", body), "s3cret")


def test_hmac_rejects_stale_timestamp():
    body = b"{}"
    assert not elevenlabs.verify_signature(body, _sig("s", body, ts=int(time.time()) - 3600), "s")


def test_structured_result_marks_oral_answers_and_reached_human():
    data = {
        "transcript": [
            {"role": "agent", "message": "Hello"},
            {"role": "user", "message": "Yes, riot extension applies to stock."},
            {"role": "agent", "message": "Thanks. Second question..."},
            {"role": "user", "message": "Send supplier invoices and the inventory."},
        ],
        "analysis": {
            "transcript_summary": "Insurer confirmed riot extension; asked for invoices.",
            "data_collection_results": {
                "reached_human": {"value": True},
                "answer_1": {"value": "Riot extension applies to stock."},
                "answer_2": {"value": "Supplier invoices and last inventory."},
                "insurer_reference": {"value": "SIN-2026-104201"},
            },
        },
    }
    r = structured_result_from_payload(data)
    assert r["reached_human"] is True
    assert [a["question_index"] for a in r["answers"]] == [1, 2]
    assert r["answers"][0]["answer_verbatim"] == "Yes, riot extension applies to stock."
    assert r["insurer_reference"] == "SIN-2026-104201"


def test_structured_result_no_human():
    r = structured_result_from_payload({"transcript": [{"role": "agent", "message": "Hello?"}], "analysis": {}})
    assert r["reached_human"] is False and r["answers"] == []


def test_dynamic_variables_are_strings_and_numbered():
    v = build_dynamic_variables(brief={"business_name": "Karim", "language": "en"}, goal="g", questions=["a", "b"])
    assert all(isinstance(x, str) for x in v.values())
    assert v["questions"] == "1. a\n2. b" and v["question_count"] == "2"
