"""Tests for noos_gha_run_health_v1 billing gate classification."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_gha_run_health_v1 as gha  # noqa: E402


def test_classify_runs_billing_gate_on_short_failure():
    rows = [
        {
            "workflowName": "GEL CI",
            "displayTitle": "billing gate",
            "conclusion": "failure",
            "createdAt": "2026-07-08T00:00:00Z",
            "updatedAt": "2026-07-08T00:00:03Z",
        }
    ]
    out = gha.classify_runs(rows)
    assert out["latest_is_billing_gate"] is True
    assert out["latest_real_failure"] is False
    assert out["billing_gate_failures_12s"] == 1


def test_classify_runs_real_ci_on_long_failure():
    rows = [
        {
            "workflowName": "GEL CI",
            "displayTitle": "pytest fail",
            "conclusion": "failure",
            "createdAt": "2026-07-08T00:00:00Z",
            "updatedAt": "2026-07-08T00:00:45Z",
        }
    ]
    out = gha.classify_runs(rows)
    assert out["latest_is_billing_gate"] is False
    assert out["latest_real_failure"] is True
    assert out["real_failures"]


def test_run_gha_health_schema(monkeypatch):
    def fake_repo(repo: str, *, limit: int = 8):
        return {
            "ok": True,
            "repo": repo,
            "billing_gate_failures_12s": 0,
            "latest_is_billing_gate": False,
            "latest_real_failure": False,
            "real_failures": [],
            "latest_conclusion": "success",
            "latest_duration_s": 30.0,
            "recent_count": 1,
        }

    monkeypatch.setattr(gha, "gh_repo_health", fake_repo)
    monkeypatch.setattr(
        gha,
        "org_plan_row",
        lambda *, billing_gate_clear: {"ok": True, "plan": "team", "billing_gate_clear": True},
    )
    monkeypatch.setattr(
        gha,
        "witness_early_warning",
        lambda **_: {"ok": True, "warnings": [], "billing_gate_precursors": []},
    )
    row = gha.run_gha_health()
    assert row["schema"] == "noos-gha-run-health-v1"
    assert "ICL-D10" in row["checks"]
    assert row["overall_status"] == "green"
