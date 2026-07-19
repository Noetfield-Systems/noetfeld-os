"""Tests for plan motor dequeue, kernel bridge, and wiring verify."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cloud_inbox_worker_v1 as worker
import noos_plan_motor_v1 as plan_motor
from cloud_inbox_constants_v1 import FOUNDER_BLOCKED_STATUS
from noos_plan_motor_kernel_bridge_v1 import kernel_classify, kernel_triage_finding
from verify_noos_plan_motor_wiring_v1 import verify


def test_select_next_step_dry_run():
    row = plan_motor.try_execute_next_step(dry_run=True)
    if row is None:
        pytest.skip("no open machine_safe plan steps in fixture")
    assert row["status"] == "DRY_RUN"
    assert row["action"] == "plan_motor_dequeue"
    assert row.get("verify_cmd")


def test_burn_down_summary_shape():
    summary = plan_motor.burn_down_summary()
    assert "open_machine_safe_steps" in summary
    assert "submitted_ok_count" in summary


def test_kernel_bridge_classify():
    row = kernel_classify(text="integration timeout on supabase sink", labels=["systematic", "integration"])
    assert "routing" in row or "ok" in row


def test_kernel_triage_finding():
    row = kernel_triage_finding({"id": "f-1", "severity": "high", "metadata": {"lane": "inbox"}})
    assert isinstance(row, dict)


def test_wiring_verify_passes():
    row = verify(write_receipt=False)
    assert row["lock_state"] == "LOCKED_v1"
    assert row["ok"] is True, json.dumps(row["checks"], indent=2)


def test_empty_inbox_falls_through_to_plan_motor_idle():
    store = {"pending": [], "founder_blocked": []}

    def fake_request(method: str, path: str, *, body: dict | None = None):
        if method == "GET" and "status=eq.pending" in path:
            return list(store["pending"])
        if method == "GET" and f"status=eq.{FOUNDER_BLOCKED_STATUS}" in path:
            return list(store["founder_blocked"])
        raise AssertionError(f"unexpected request: {method} {path}")

    worker._request_fn = fake_request
    with patch.object(plan_motor, "try_execute_next_step", return_value=None):
        result = worker.process_cycle()
    worker._request_fn = None
    assert result["status"] == "IDLE_NO_WORK"
    assert result.get("plan_motor_checked") is True


def test_empty_inbox_executes_plan_motor_when_available():
    store = {"pending": [], "founder_blocked": []}
    plan_result = {
        "ok": True,
        "status": "completed",
        "item_id": "PLAN-A-A10",
        "action": "plan_motor_executed",
        "plan_motor": True,
    }

    def fake_request(method: str, path: str, *, body: dict | None = None):
        if method == "GET" and "status=eq.pending" in path:
            return list(store["pending"])
        if method == "GET" and f"status=eq.{FOUNDER_BLOCKED_STATUS}" in path:
            return list(store["founder_blocked"])
        raise AssertionError(f"unexpected request: {method} {path}")

    worker._request_fn = fake_request
    with patch.object(plan_motor, "try_execute_next_step", return_value=plan_result):
        result = worker.process_cycle()
    worker._request_fn = None
    assert result["action"] == "plan_motor_executed"
    assert result.get("plan_motor") is True
