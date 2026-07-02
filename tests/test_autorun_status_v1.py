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
        "sandbox_health_sweep",
    ]


def test_sandboxes_no_sourcea_dirty():
    doc = json.loads((ROOT / "data/autorun-sandboxes-v1.json").read_text())
    sourcea = next(sb for sb in doc["sandboxes"] if sb["id"] == "sourcea")
    assert sourcea["counts_toward_dirty_total"] is False
    assert sourcea["git"] is False
