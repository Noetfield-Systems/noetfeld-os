"""Unified Motor Event API client — signing + idempotency."""

from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import unified_motor_event_client_v1 as client  # noqa: E402


def test_sign_motor_event_body_matches_gateway_contract() -> None:
    secret = "api-secret"
    raw = json.dumps({"event_id": "evt_api_1", "source": "api.motor"})
    ts = "1700000000"
    expected = (
        "sha256="
        + hmac.new(secret.encode(), f"{ts}.{raw}".encode(), hashlib.sha256).hexdigest()
    )
    assert client.sign_motor_event_body(secret=secret, timestamp=ts, raw_body=raw) == expected


def test_idempotency_key_stable_for_same_cycle() -> None:
    key_a = client.build_idempotency_key(loop_id="inbox", cycle_number=42, op_key="wf:inbox:42")
    key_b = client.build_idempotency_key(loop_id="inbox", cycle_number=42, op_key="wf:inbox:42")
    assert key_a == key_b
    assert key_a.startswith("noos.portfolio:")


def test_idempotency_key_differs_across_cycles() -> None:
    a = client.build_idempotency_key(loop_id="inbox", cycle_number=1)
    b = client.build_idempotency_key(loop_id="inbox", cycle_number=2)
    assert a != b


def test_build_motor_event_payload_required_fields() -> None:
    event = client.build_motor_event_payload(
        loop_id="inbox",
        cycle_number=7,
        event_type="noos_inbox_loop_tick",
        state_after="COMPLETE",
        op_key="wf:inbox:7",
    )
    assert event["schema_version"] == "motor.event.v1"
    assert event["role_id"] == "noetfield:noos.portfolio-owner"
    assert event["source"] == "api.motor"
    assert event["payload"]["noos_source_id"] == "noos.portfolio"
    assert event["route"] == "noos.portfolio.inbox_observe"


def test_verify_timestamp_fresh_within_skew() -> None:
    now = 1_700_000_000
    assert client.verify_timestamp_fresh(str(now), now_sec=now) is True
    assert client.verify_timestamp_fresh(str(now - 299), now_sec=now) is True
    assert client.verify_timestamp_fresh(str(now - 301), now_sec=now) is False


def test_maybe_emit_skipped_when_bridge_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NOOS_UNIFIED_MOTOR_EVENT_BRIDGE", raising=False)
    result = client.maybe_emit_loop_cycle_event(
        {"loop_id": "inbox", "cycle_number": 1, "state_after": "COMPLETE"}
    )
    assert result.get("skipped") is True
    assert result.get("reason") == "bridge_disabled"


def test_maybe_emit_skipped_for_non_complete_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOOS_UNIFIED_MOTOR_EVENT_BRIDGE", "1")
    result = client.maybe_emit_loop_cycle_event(
        {"loop_id": "inbox", "cycle_number": 1, "state_after": "BLOCKED_WITH_REASON"}
    )
    assert result.get("skipped") is True
    assert "state_not_emittable" in str(result.get("reason"))
