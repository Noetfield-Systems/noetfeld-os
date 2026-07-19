"""Tests for the hourly NOOS role-circle tick."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_role_circle_tick_v1 as circle  # noqa: E402


def test_circle_registry_covers_all_categories():
    doc = circle.load_circle()
    roles = {r["category"] for r in doc["roles"]}
    for cat in doc["category_coverage"]:
        assert cat in roles


def test_role_circle_wired_into_24_7_loops():
    loops = json.loads((ROOT / "data/noos-24-7-loops-v1.json").read_text())
    row = next(l for l in loops["loops"] if l["id"] == "role_circle")
    assert row["event_type"] == "noos_role_circle_tick"
    assert row["interval_minutes"] == 60
    assert any("noos_role_circle_tick_v1.py" in " ".join(s.get("cmd") or []) for s in row["steps"])


def test_role_circle_in_cf_dispatch_table():
    table = json.loads((ROOT / "data/noos-cf-dispatch-table-v1.json").read_text())
    hit = next(t for t in table["targets"] if t["dispatch_id"] == "role_circle")
    assert hit["interval_minutes"] == 60
    assert hit["event_type"] == "noos_role_circle_tick"
    # Worker copy must stay in sync
    worker = json.loads(
        (ROOT / "cloud/workers/noos-loop-fleet-tick-v1/src/dispatch-table.json").read_text()
    )
    assert any(t["dispatch_id"] == "role_circle" for t in worker["targets"])


def test_observer_probes_live_apis(monkeypatch):
    calls = []

    def fake_http(url, **_):
        calls.append(url)
        return {"ok": True, "status": 200, "body": {"ok": True}}

    monkeypatch.setattr(circle, "http_json", fake_http)
    doc = circle.load_circle()
    row = circle.role_observer(doc)
    assert row["ok"] is True
    assert row["live_api_count"] == 3
    assert row["live_api_ok_count"] == 3
    assert len(calls) == 3


def test_observer_soft_ok_when_partial_probes(monkeypatch):
    def fake_http(url, **_):
        if "deadman" in url:
            return {"ok": False, "error": "timeout"}
        return {"ok": True, "status": 200, "body": {"ok": True}}

    monkeypatch.setattr(circle, "http_json", fake_http)
    row = circle.role_observer(circle.load_circle())
    assert row["ok"] is True
    assert row["degraded"] is True
    assert row["live_api_ok_count"] == 2


def test_run_circle_writes_receipt(monkeypatch, tmp_path):
    monkeypatch.setattr(circle, "PROOF_DIR", tmp_path)
    monkeypatch.setattr(
        circle,
        "http_json",
        lambda url, **_: {"ok": True, "status": 200, "body": {"ok": True}},
    )
    monkeypatch.setattr(
        circle,
        "run_cli",
        lambda cmd, **_: {"ok": True, "exit_code": 0, "cmd": cmd, "stdout_json": {"ok": True}},
    )
    monkeypatch.setattr(
        circle,
        "role_route_health_incidents",
        lambda: {"ok": True, "skipped": True, "reason": "test"},
    )
    monkeypatch.setattr(
        circle,
        "role_runway_preflight",
        lambda: {"ok": True, "runway_live": False, "preflight": {"verdict": "BLOCKED_RUNWAY_API_NOT_LIVE"}},
    )
    # Rebind hooks after monkeypatch of functions used by HOOKS values
    circle.HOOKS["route_health_incidents"] = circle.role_route_health_incidents
    circle.HOOKS["runway_preflight"] = circle.role_runway_preflight

    row = circle.run_circle(write_receipt=True)
    assert row["ok"] is True
    assert row["coverage_ok"] is True
    assert (tmp_path / "noos-role-circle-latest.json").is_file()
    assert row["cost"] == "NO_EXTERNAL_MODEL_CALL"


def test_workflow_is_not_primary_motor():
    text = (ROOT / ".github/workflows/noos-role-circle.yml").read_text()
    assert "Primary live trigger is CF fleet cron" in text
    assert "workflow_dispatch" in text
