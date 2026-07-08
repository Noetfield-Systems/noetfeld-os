"""Tests for stack automation health rollup."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_stack_automation_health_v1 as stack  # noqa: E402


def test_rollup_schema(monkeypatch):
    def fake_run_json(cmd, **kwargs):
        script = cmd[1]
        if script.endswith("noos_integrator_status_v1.py"):
            return {"ok": True, "surfaces": {"vault": True}, "machine_audit_line": "chain_ok=True"}
        if script.endswith("autorun_status_v1.py"):
            return {"critique": {"overall_ok": True, "findings": []}}
        if script.endswith("observe_trustfield_parallel_layers_v1.py"):
            return {"overall_status": "yellow", "summary": {"green": 10, "yellow": 1, "red": 0}}
        if script.endswith("observe_trustfield_loop_registry_v1.py"):
            return {"overall_status": "green", "summary": {"red": 0, "deadman_status": "green"}}
        return {"ok": True}

    monkeypatch.setattr(stack, "run_json", fake_run_json)
    monkeypatch.setattr(
        stack,
        "run_gha_health",
        lambda: {"ok": True, "overall_status": "green", "checks": {}},
    )
    monkeypatch.setattr(
        stack,
        "http_json",
        lambda url, **_: {
            "ok": True,
            "body": {"ok": True, "status": "healthy", "lane_ok": {}, "lanes_run": []},
        },
    )

    row = stack.rollup()
    assert row["schema"] == "noos-stack-automation-health-v1"
    assert row["replaces_workflow"] == "noos-cross-repo-orchestrator.yml"
    assert "integrator_status" in row
    assert "gha_health" in row
    assert row["closure_token"].startswith("NOOS_STACK_AUTOMATION:")
