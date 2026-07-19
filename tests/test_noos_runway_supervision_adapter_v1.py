"""Tests for the NOOS → NOETFIELD-RUNWAY supervision adapter (Mission 5)."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_runway_supervision_adapter_v1 as rw  # noqa: E402

NOW = datetime(2026, 7, 19, 12, 0, 0, tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_preflight_blocks_when_api_absent(monkeypatch):
    monkeypatch.delenv("NOETFIELD_RUNWAY_API_URL", raising=False)
    pf = rw.preflight()
    assert pf["ok"] is False
    assert pf["verdict"] == "BLOCKED_RUNWAY_API_NOT_LIVE"
    assert pf["required_url_env"] == "NOETFIELD_RUNWAY_API_URL"
    assert pf["auth_interface"].startswith("Authorization: Bearer")
    assert "job_id" in pf["event_schema"]


def test_preflight_ok_when_api_present(monkeypatch):
    monkeypatch.setenv("NOETFIELD_RUNWAY_API_URL", "https://runway.example")
    assert rw.preflight()["ok"] is True


def test_healthy_running_job_no_dispatch():
    ev = {
        "job_id": "j1", "recipe_id": "software_repair", "state": "RUNNING",
        "updated_at": _iso(NOW - timedelta(minutes=5)),
        "budget": {"spent_usd": 1.0, "ceiling_usd": 10.0},
        "provider": {"name": "deepseek", "healthy": True},
    }
    det = rw.supervise(ev, now=NOW)["detection"]
    assert det["dispatch_decision"] == "none"
    assert det["founder_escalation"] is False


def test_stale_job_routes_to_repair():
    ev = {
        "job_id": "j2", "state": "RUNNING",
        "updated_at": _iso(NOW - timedelta(minutes=45)),
        "budget": {"spent_usd": 1.0, "ceiling_usd": 10.0},
        "provider": {"name": "deepseek", "healthy": True},
    }
    det = rw.detect_conditions(rw.observe_job(ev), now=NOW)
    assert det["dispatch_decision"] == "repair"
    assert any(f.startswith("stale:") for f in det["findings"])


def test_provider_unhealthy_routes_to_fallback():
    ev = {
        "job_id": "j3", "state": "RUNNING",
        "updated_at": _iso(NOW - timedelta(minutes=2)),
        "budget": {"spent_usd": 1.0, "ceiling_usd": 10.0},
        "provider": {"name": "kimi", "healthy": False},
    }
    det = rw.detect_conditions(rw.observe_job(ev), now=NOW)
    assert det["dispatch_decision"] == "fallback"
    assert det["founder_escalation"] is False


def test_budget_ceiling_breach_escalates_founder():
    ev = {
        "job_id": "j4", "state": "RUNNING",
        "updated_at": _iso(NOW - timedelta(minutes=2)),
        "budget": {"spent_usd": 12.0, "ceiling_usd": 10.0},
        "provider": {"name": "deepseek", "healthy": True},
    }
    det = rw.detect_conditions(rw.observe_job(ev), now=NOW)
    assert det["dispatch_decision"] == "fallback"
    assert det["founder_escalation"] is True


def test_failed_state_routes_to_repair():
    ev = {
        "job_id": "j5", "state": "FAILED",
        "updated_at": _iso(NOW - timedelta(minutes=1)),
        "budget": {"spent_usd": 1.0, "ceiling_usd": 10.0},
        "provider": {"name": "deepseek", "healthy": True},
    }
    det = rw.detect_conditions(rw.observe_job(ev), now=NOW)
    assert det["dispatch_decision"] == "repair"


def test_complete_job_not_stale_even_if_old():
    ev = {
        "job_id": "j6", "state": "COMPLETE",
        "updated_at": _iso(NOW - timedelta(hours=5)),
        "budget": {"spent_usd": 2.0, "ceiling_usd": 10.0},
        "provider": {"name": "deepseek", "healthy": True},
        "terminal_receipt": "receipts/proof/runway-j6.json",
    }
    det = rw.detect_conditions(rw.observe_job(ev), now=NOW)
    assert det["dispatch_decision"] == "none"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
