"""Tests for NOOS role-circle v2 — full input→valuable-output portfolio."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_role_circle_tick_v1 as circle  # noqa: E402


def test_required_loops_cover_24_7_operational_set():
    doc = circle.load_circle()
    loops = {l["id"] for l in circle.load_loops()}
    required = set(doc["required_loop_ids"])
    assert required.issubset(loops)
    assert "role_circle" not in required
    assert "improve_kaizen_daily" not in required
    # Core value loops must be present
    for must in ("inbox", "runtime", "surface", "chain", "self_heal", "workflow_audit"):
        assert must in required


def test_every_required_loop_has_io_contract():
    doc = circle.load_circle()
    io = doc["loop_io"]
    for lid in doc["required_loop_ids"]:
        assert lid in io, f"missing IO for {lid}"
        for key in ("role_id", "input", "process", "valuable_output", "value_class"):
            assert io[lid].get(key), f"{lid} missing {key}"


def test_extract_valuable_output_requires_identity_and_state():
    io = {"valuable_output": "x", "value_class": "risk_reduction"}
    good = circle.extract_valuable_output(
        {
            "loop_id": "inbox",
            "event_type": "noos_inbox_loop_tick",
            "cycle_number": 3,
            "state_after": "COMPLETE",
            "value_class": "revenue_path",
            "runner_output": {"steps": [{"name": "cloud_worker", "ok": True, "exit_code": 0}]},
            "evidence": [{"command": "x"}],
        },
        io=io,
    )
    assert good["valuable"] is True
    bad = circle.extract_valuable_output({"loop_id": "inbox", "state_after": ""}, io=io)
    assert bad["valuable"] is False


def test_run_circle_executes_all_required_loops(monkeypatch, tmp_path):
    doc = circle.load_circle()
    required = list(doc["required_loop_ids"])

    def fake_execute(loop, self_heal=True):
        return {
            "loop_id": loop["id"],
            "event_type": loop["event_type"],
            "cycle_number": 1,
            "op_key": f"op-{loop['id']}",
            "state_after": "COMPLETE",
            "value_class": loop.get("value_class"),
            "status": "ok",
            "mission_id": "M2",
            "runner_output": {"steps": [{"name": "step", "ok": True, "exit_code": 0, "stdout_tail": "done"}]},
            "evidence": [{"command": "step"}],
            "liveness_upsert": {"ok": True},
        }

    monkeypatch.setattr(circle.loop_runner, "execute_loop", fake_execute)
    monkeypatch.setattr(circle, "PROOF_DIR", tmp_path)
    monkeypatch.setattr(
        circle,
        "http_json",
        lambda url, **_: {"ok": True, "status": 200, "body": {"ok": True}},
    )
    monkeypatch.setattr(
        circle,
        "run_cli",
        lambda cmd, **_: {
            "ok": True,
            "exit_code": 0,
            "cmd": cmd,
            "stdout_json": {"ok": True, "schema": "noos-machine-dispatch-queue-v1", "report_line": "ok"},
        },
    )
    monkeypatch.setattr(
        circle,
        "role_route_health_incidents",
        lambda: {
            "ok": True,
            "valuable_output": {"valuable": True, "artifact": {"kind": "incident_dispatch", "created": []}},
        },
    )
    monkeypatch.setattr(
        circle,
        "role_runway_preflight",
        lambda: {
            "ok": True,
            "valuable_output": {
                "valuable": True,
                "artifact": {"kind": "runway_preflight", "verdict": "BLOCKED_RUNWAY_API_NOT_LIVE"},
            },
        },
    )
    circle.HOOKS["route_health_incidents"] = circle.role_route_health_incidents
    circle.HOOKS["runway_preflight"] = circle.role_runway_preflight

    row = circle.run_circle(write_receipt=True)
    assert row["schema"] == "noos-role-circle-cycle-v2"
    assert row["loop_count"] == len(required)
    assert row["loops_valuable"] == len(required)
    assert row["loops_productive"] == len(required)
    assert row["value_ledger"]["real_valuable_output"] is True
    assert row["portfolio_productive"] is True
    assert row["ok"] is True
    assert (tmp_path / "noos-role-circle-latest.json").is_file()
    assert list(tmp_path.glob("noos-role-circle-value-ledger-*.json"))


def test_value_ledger_marks_missing_outputs():
    loop_rows = [
        {
            "loop_id": "inbox",
            "ok": True,
            "productive": True,
            "value_class": "revenue_path",
            "valuable_output": {"valuable": True, "artifact": {"kind": "loop_cycle_receipt"}},
            "state_after": "COMPLETE",
            "cycle_number": 1,
            "op_key": "a",
            "role_id": "noos.inbox_worker",
            "evidence": [{"command": "x"}],
            "steps_summary": [{"name": "s", "ok": True}],
        },
        {
            "loop_id": "runtime",
            "ok": False,
            "productive": False,
            "value_class": "risk_reduction",
            "valuable_output": {"valuable": False},
            "role_id": "noos.runtime_gate",
        },
    ]
    ledger = circle.build_value_ledger(loop_rows, [])
    assert ledger["valuable_loops"] == 1
    assert ledger["productive_loops"] == 1
    assert ledger["missing_valuable"] == ["runtime"]
    assert ledger["not_productive"] == ["runtime"]
    assert ledger["real_valuable_output"] is False
    assert ledger["portfolio_productive"] is False


def test_fake_execute_marks_productive_from_state(monkeypatch, tmp_path):
    def fake_execute(loop, self_heal=True):
        return {
            "loop_id": loop["id"],
            "event_type": loop["event_type"],
            "cycle_number": 1,
            "op_key": f"op-{loop['id']}",
            "state_after": "BLOCKED_WITH_REASON",
            "blocker_reason": "sink_unacked",
            "value_class": loop.get("value_class"),
            "status": "degraded",
            "runner_output": {"steps": [{"name": "step", "ok": True, "exit_code": 0, "stdout_tail": "done"}]},
            "evidence": [{"command": "step"}],
            "supabase_sink": {"ok": False, "reason": "supabase_not_configured"},
            "liveness_upsert": {"ok": False, "skipped": True},
        }

    monkeypatch.setattr(circle.loop_runner, "execute_loop", fake_execute)
    monkeypatch.setattr(circle, "PROOF_DIR", tmp_path)
    monkeypatch.setattr(circle, "http_json", lambda url, **_: {"ok": True, "status": 200, "body": {"ok": True}})
    monkeypatch.setattr(
        circle,
        "run_cli",
        lambda cmd, **_: {
            "ok": True,
            "exit_code": 0,
            "cmd": cmd,
            "stdout_json": {"ok": True, "schema": "noos-machine-dispatch-queue-v1"},
        },
    )
    monkeypatch.setattr(
        circle,
        "role_route_health_incidents",
        lambda: {"ok": True, "valuable_output": {"valuable": True, "artifact": {"kind": "incident_dispatch"}}},
    )
    monkeypatch.setattr(
        circle,
        "role_runway_preflight",
        lambda: {
            "ok": True,
            "valuable_output": {"valuable": True, "artifact": {"kind": "runway_preflight", "verdict": "BLOCKED"}},
        },
    )
    circle.HOOKS["route_health_incidents"] = circle.role_route_health_incidents
    circle.HOOKS["runway_preflight"] = circle.role_runway_preflight
    row = circle.run_circle(write_receipt=True)
    assert row["value_ledger"]["real_valuable_output"] is True
    assert row["portfolio_productive"] is False
    assert all(r.get("blocker_reason") == "sink_unacked" for r in row["loops"])
    assert all(r.get("productive") is False for r in row["loops"])


def test_cf_and_24_7_still_wire_role_circle():
    loops = json.loads((ROOT / "data/noos-24-7-loops-v1.json").read_text())
    row = next(l for l in loops["loops"] if l["id"] == "role_circle")
    assert row["interval_minutes"] == 60
    table = json.loads((ROOT / "data/noos-cf-dispatch-table-v1.json").read_text())
    assert any(t["dispatch_id"] == "role_circle" for t in table["targets"])
