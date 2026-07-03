"""Tests for Cursor Local Mac T2 Phase 2 tooling."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_agent_conflict_check_v1 as conflict  # noqa: E402
import noos_local_boot_receipt_v1 as boot_receipt  # noqa: E402
import verify_living_system_governance_v1 as gov  # noqa: E402


def test_claim_lane_script_executable():
    path = ROOT / "scripts/noos_local_claim_lane_v1.sh"
    assert path.is_file()
    mode = path.stat().st_mode
    assert mode & stat.S_IXUSR


def test_mac_worktree_sync_script_executable():
    path = ROOT / "scripts/noos_mac_worktree_sync_v1.sh"
    assert path.is_file()
    mode = path.stat().st_mode
    assert mode & stat.S_IXUSR


def test_session_boot_hook_exits_zero():
    hook = ROOT / ".cursor/hooks/noos-local-boot.sh"
    assert hook.is_file()
    proc = subprocess.run([str(hook)], cwd=ROOT, capture_output=True, text=True, check=False)
    assert proc.returncode == 0


def test_claim_reminder_hook_exits_zero_without_block():
    hook = ROOT / ".cursor/hooks/noos-claim-reminder.sh"
    assert hook.is_file()
    payload = json.dumps({"file_path": "scripts/noos_integrator_sync_v1.py"})
    proc = subprocess.run(
        [str(hook)],
        input=payload,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0


def test_governance_includes_cursor_local_mac():
    registry = gov.load_json(gov.PARALLEL_REGISTRY)
    row = gov.check_cursor_local_mac(registry)
    assert row["ok"] is True
    assert row["worker_id"] == "cursor-local-mac"


def test_full_governance_verify_still_passes():
    row = gov.run_verify(write_receipt=False)
    assert row["ok"] is True
    assert row["checks"]["cursor_local_mac"] is True


def test_claim_overlap_fails_closed():
    reg = conflict.load_json(conflict.REGISTRY_PATH)
    integrator = {
        "tasks": [
            {
                "task_id": "A",
                "agent_id": "agent-a",
                "status": "in_progress",
                "scope_files": ["Makefile"],
                "heartbeat_at": conflict.utc_now(),
            },
            {
                "task_id": "B",
                "agent_id": "agent-b",
                "status": "claimed",
                "scope_files": ["Makefile"],
                "heartbeat_at": conflict.utc_now(),
            },
        ]
    }
    row = conflict.check_conflicts(registry=reg, integrator=integrator)
    assert row["ok"] is False


def test_local_boot_receipt_schema_no_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(ROOT)
    row = boot_receipt.build_receipt(write_file=False)
    assert row["schema"] == "noos-local-boot-v1"
    assert "governance_checks" in row
    assert "cursor_local_mac" in (row.get("governance_checks") or {})
