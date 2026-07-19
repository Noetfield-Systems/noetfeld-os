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
    # Mission 3: NOOS emits its honest canonical source, not an api.motor masquerade.
    assert event["source"] == "noos.portfolio"
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


def test_health_states_are_emittable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mission 3: FAILED_WITH_RECEIPT and BLOCKED_WITH_REASON now route (not skipped)."""
    monkeypatch.setenv("NOOS_UNIFIED_MOTOR_EVENT_BRIDGE", "1")
    captured: dict[str, object] = {}

    def fake_post(event, **_):
        captured["event"] = event
        return {"ok": True, "status": 200, "event_id": event.get("event_id"), "idempotency_key": "k"}

    monkeypatch.setattr(client, "post_signed_event", fake_post)
    for state, route in (
        ("FAILED_WITH_RECEIPT", "noos.portfolio.health_failed"),
        ("BLOCKED_WITH_REASON", "noos.portfolio.health_blocked"),
    ):
        result = client.maybe_emit_loop_cycle_event(
            {"loop_id": "stack_health", "cycle_number": 3, "state_after": state,
             "event_type": "noos_stack_health_tick"}
        )
        assert result.get("skipped") is not True, f"{state} must be emittable"
        assert captured["event"]["route"] == route
        assert captured["event"]["source"] == "noos.portfolio"


def test_unemittable_state_still_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOOS_UNIFIED_MOTOR_EVENT_BRIDGE", "1")
    result = client.maybe_emit_loop_cycle_event(
        {"loop_id": "inbox", "cycle_number": 1, "state_after": "RUNNING"}
    )
    assert result.get("skipped") is True
    assert "state_not_emittable" in str(result.get("reason"))


def test_preflight_config_blocks_with_exact_missing_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("NOOS_UNIFIED_MOTOR_EVENT_BRIDGE", "MOTOR_EVENT_GATEWAY_URL", "MOTOR_EVENT_API_SECRET"):
        monkeypatch.delenv(var, raising=False)
    row = client.preflight_config(deployment="github-actions:noetfeld-os")
    assert row["ok"] is False
    assert row["verdict"] == "BLOCKED_MOTOR_EVENT_GATEWAY_CONFIGURATION"
    assert set(row["missing"]) == {
        "NOOS_UNIFIED_MOTOR_EVENT_BRIDGE",
        "MOTOR_EVENT_GATEWAY_URL",
        "MOTOR_EVENT_API_SECRET",
    }
    assert row["deployment"] == "github-actions:noetfeld-os"
    assert "unblock_action" in row


def test_preflight_config_ok_when_all_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOOS_UNIFIED_MOTOR_EVENT_BRIDGE", "1")
    monkeypatch.setenv("MOTOR_EVENT_GATEWAY_URL", "https://gw.example/v1")
    monkeypatch.setenv("MOTOR_EVENT_API_SECRET", "shhh")
    row = client.preflight_config()
    assert row["ok"] is True
    assert row["missing"] == []


def test_inbound_signature_valid() -> None:
    secret, ts, raw = "s3cr3t", "1700000000", '{"event_id":"evt_1"}'
    sig = client.sign_motor_event_body(secret=secret, timestamp=ts, raw_body=raw)
    res = client.verify_inbound_signature(
        secret=secret, timestamp=ts, raw_body=raw, signature=sig, now_sec=1700000000
    )
    assert res["ok"] is True


def test_inbound_signature_invalid_rejected() -> None:
    res = client.verify_inbound_signature(
        secret="s3cr3t", timestamp="1700000000", raw_body='{"event_id":"evt_1"}',
        signature="sha256=deadbeef", now_sec=1700000000,
    )
    assert res["ok"] is False
    assert res["reason"] == "invalid_signature"


def test_inbound_replay_rejected() -> None:
    secret, ts, raw = "s3cr3t", "1700000000", '{"event_id":"evt_1"}'
    sig = client.sign_motor_event_body(secret=secret, timestamp=ts, raw_body=raw)
    # now is 10 minutes later than the signed timestamp → outside 300s skew.
    res = client.verify_inbound_signature(
        secret=secret, timestamp=ts, raw_body=raw, signature=sig, now_sec=1700000000 + 600
    )
    assert res["ok"] is False
    assert res["reason"] == "replay_or_stale_timestamp"
