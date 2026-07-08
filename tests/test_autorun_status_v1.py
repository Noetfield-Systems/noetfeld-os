"""Tests for read-only autorun status dashboard v1.1."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import autorun_status_v1 as dash  # noqa: E402


def test_stale_wrap_marks_blocked():
    recent = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    row = dash.stale_wrap(
        {"status": "RUNNING", "evidence": {}},
        observed_at=recent,
        stale_minutes=30,
        source="test",
    )
    assert row["data_freshness"] == "STALE_DATA"
    assert row["status"] == "BLOCKED_WITH_REASON"
    assert row["reason"] == "stale_supabase_row"


def test_stale_wrap_fresh():
    recent = datetime.now(timezone.utc).isoformat()
    row = dash.stale_wrap(
        {"status": "RUNNING"},
        observed_at=recent,
        stale_minutes=30,
        source="test",
    )
    assert row["data_freshness"] == "FRESH"


def test_apply_triage_overrides_status():
    row = dash.apply_triage({"status": "RUNNING"}, triage=True, dirty_total=250, threshold=200)
    assert row["status"] == "TRIAGE_REQUIRED"
    assert "dirty_total=250" in row["triage_reason"]


def test_apply_triage_preserves_failed():
    row = dash.apply_triage({"status": "FAILED_WITH_RECEIPT"}, triage=True, dirty_total=250, threshold=200)
    assert row["status"] == "FAILED_WITH_RECEIPT"


def test_reconciler_authority_one():
    wf_doc = {"control_authority": {"sole_reconciler": "SourceA/scripts/phase_reconciler_v1.py"}}
    auth = dash.reconciler_authority_check(wf_doc)
    assert auth["result"] == "ONE"
    assert auth["sourcea_disk_checked"] is False
    assert "phase_reconciler" in auth["sole_authority_path"]


def test_workflow_registry_ids():
    doc = json.loads((ROOT / "data/autorun-workflows-v1.json").read_text())
    ids = [wf["id"] for wf in doc["workflows"]]
    assert ids == [
        "sourcea_cloud_queue",
        "sourcea_buyer_proof_verify",
        "sourcea_recipe_queue_builder",
        "noos_factory_autorun",
        "noos_worker_inbox",
        "noos_factory_autorun_tick",
        "noos_schedule_canary",
        "noos_loop_fleet_tick",
        "noos_loop_inbox",
        "noos_loop_runtime",
        "noos_loop_surface",
        "noos_loop_chain",
        "noos_loop_self_heal",
        "noos_loop_agent_nerve",
        "noos_loop_sourcea_observe",
        "noos_deadman",
        "noos_loop_liveness_registry",
        "sandbox_health_sweep",
        "noos_gha_integrator_daily_witness",
        "noos_gha_autorun_witness",
        "noos_gha_motor_sustain_witness",
        "noos_gha_health_witness",
        "noos_stack_health_receipt",
    "noos_trustfield_observe_witness",
    "noos_sourcea_spine_witness",
    "noos_machine_audit_witness",
    "noos_liveness_registry_witness",
    "noos_sandbox_url_sweep_witness",
    ]


def test_dashboard_findings_flags_blocked_and_slo_miss():
    dash_row = {
        "triage_required": False,
        "workflows": [
            {
                "id": "wf-1",
                "status": "BLOCKED_WITH_REASON",
                "reason": "supabase_not_configured",
                "evidence": {},
                "slo": {"ok": False, "misses": ["success_rate_miss"]},
            }
        ],
    }

    findings = dash.dashboard_findings(dash_row)
    assert len(findings) == 1
    assert any(f["summary"].startswith("Workflow is not healthy") for f in findings)


def test_probe_cf_schedule_canary_complete_when_motor_and_a1_ok(monkeypatch):
    wf = {
        "probe": {
            "type": "cf_schedule_canary",
            "github_workflow": "noos-schedule-canary.yml",
        }
    }

    class Resp:
        status = 200

        def read(self):
            return b'{"ok": true, "service": "noos-loop-fleet-tick-v1"}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(dash.urllib.request, "urlopen", lambda *a, **k: Resp())
    row = dash.probe_cf_schedule_canary(wf)
    assert row["status"] == "COMPLETE"
    assert row["classification"] == "cf_motor_canary_retired_gha_schedule"


def test_sandboxes_no_sourcea_dirty():
    doc = json.loads((ROOT / "data/autorun-sandboxes-v1.json").read_text())
    sourcea = next(sb for sb in doc["sandboxes"] if sb["id"] == "sourcea")
    assert sourcea["counts_toward_dirty_total"] is False
    assert sourcea["git"] is False


def test_portfolio_spine_profile_reads_gha_env(monkeypatch):
    wf_doc = json.loads((ROOT / "data/autorun-workflows-v1.json").read_text())
    monkeypatch.setattr(dash, "load_env_file", lambda _p: {})
    monkeypatch.setenv("PORTFOLIO_SPINE_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("PORTFOLIO_SPINE_SERVICE_ROLE_KEY", "gha-service-role-key")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    cfg = dash.supabase_profile_config("portfolio_spine", wf_doc)
    assert cfg == ("https://example.supabase.co", "gha-service-role-key")


def test_portfolio_spine_profile_rejects_generic_supabase_env(monkeypatch):
    wf_doc = json.loads((ROOT / "data/autorun-workflows-v1.json").read_text())
    monkeypatch.setattr(dash, "load_env_file", lambda _p: {})
    monkeypatch.delenv("PORTFOLIO_SPINE_SUPABASE_URL", raising=False)
    monkeypatch.delenv("PORTFOLIO_SPINE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://bleed.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "bleed-key")
    cfg = dash.supabase_profile_config("portfolio_spine", wf_doc)
    assert cfg is None


def test_portfolio_spine_profile_reads_local_file_only(monkeypatch):
    wf_doc = json.loads((ROOT / "data/autorun-workflows-v1.json").read_text())
    monkeypatch.setattr(
        dash,
        "load_env_file",
        lambda _p: {"SUPABASE_URL": "https://local.supabase.co", "SUPABASE_SERVICE_ROLE_KEY": "local-key"},
    )
    monkeypatch.delenv("PORTFOLIO_SPINE_SUPABASE_URL", raising=False)
    monkeypatch.delenv("PORTFOLIO_SPINE_SERVICE_ROLE_KEY", raising=False)
    cfg = dash.supabase_profile_config("portfolio_spine", wf_doc)
    assert cfg == ("https://local.supabase.co", "local-key")
