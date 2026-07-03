"""Tests for the NOOS integrator coordination layer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_integrator_sync_v1 as integrator


def _state(tmp_path: Path, monkeypatch):
    runtime_dir = tmp_path / "runtime"
    home_mirror = tmp_path / "home" / "noos-integrator-state-v1.json"
    monkeypatch.setenv("NOOS_INTEGRATOR_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("NOOS_INTEGRATOR_HOME_MIRROR", str(home_mirror))
    monkeypatch.delenv("NOOS_INTEGRATOR_SUPABASE_SYNC", raising=False)
    return runtime_dir, home_mirror


def test_claim_writes_home_mirror(tmp_path, monkeypatch):
    _, home_mirror = _state(tmp_path, monkeypatch)

    assert integrator.main(["init"]) == 0
    assert integrator.main(["register-agent", "--agent-id", "copilot", "--ide", "copilot-cli"]) == 0
    assert (
        integrator.main(
            [
                "claim",
                "--agent-id",
                "copilot",
                "--ide",
                "copilot-cli",
                "--task-id",
                "TASK-1",
                "--title",
                "Implement integrator",
                "--scope-file",
                "scripts/noos_integrator_sync_v1.py",
            ]
        )
        == 0
    )

    state = integrator.read_state()
    task = state["tasks"][0]
    assert task["task_id"] == "TASK-1"
    assert task["claimed_by"] == "copilot"
    assert task["status"] == "in_progress"
    assert home_mirror.is_file()

    mirrored = json.loads(home_mirror.read_text(encoding="utf-8"))
    assert mirrored["summary"]["in_progress"] == 1


def test_scope_conflict_blocks_other_agent(tmp_path, monkeypatch):
    _state(tmp_path, monkeypatch)
    integrator.main(["init"])
    integrator.main(["register-agent", "--agent-id", "copilot", "--ide", "copilot-cli"])
    integrator.main(["register-agent", "--agent-id", "cursor", "--ide", "cursor"])
    integrator.main(
        [
            "claim",
            "--agent-id",
            "copilot",
            "--ide",
            "copilot-cli",
            "--task-id",
            "TASK-1",
            "--title",
            "Task one",
            "--scope-file",
            "scripts/noos_integrator_sync_v1.py",
        ]
    )

    result = integrator.main(
        [
            "claim",
            "--agent-id",
            "cursor",
            "--ide",
            "cursor",
            "--task-id",
            "TASK-2",
            "--title",
            "Task two",
            "--scope-file",
            "scripts/noos_integrator_sync_v1.py",
        ]
    )

    state = integrator.read_state()
    assert result == 2
    assert len(state["tasks"]) == 1
    assert state["tasks"][0]["task_id"] == "TASK-1"


def test_complete_releases_claim(tmp_path, monkeypatch):
    _state(tmp_path, monkeypatch)
    integrator.main(["init"])
    integrator.main(["register-agent", "--agent-id", "copilot", "--ide", "copilot-cli"])
    integrator.main(
        [
            "claim",
            "--agent-id",
            "copilot",
            "--ide",
            "copilot-cli",
            "--task-id",
            "TASK-1",
            "--title",
            "Task one",
        ]
    )

    assert (
        integrator.main(
            [
                "complete",
                "--agent-id",
                "copilot",
                "--ide",
                "copilot-cli",
                "--task-id",
                "TASK-1",
                "--note",
                "done",
            ]
        )
        == 0
    )

    state = integrator.read_state()
    task = state["tasks"][0]
    agent = state["agents"][0]
    assert task["status"] == "done"
    assert task["claimed_by"] is None
    assert agent["current_task_ids"] == []


def test_sweep_stale_releases_expired_claim(tmp_path, monkeypatch):
    _state(tmp_path, monkeypatch)
    integrator.main(["init"])
    integrator.main(["register-agent", "--agent-id", "copilot", "--ide", "copilot-cli"])
    integrator.main(
        [
            "claim",
            "--agent-id",
            "copilot",
            "--ide",
            "copilot-cli",
            "--task-id",
            "TASK-STALE",
            "--title",
            "Stale task",
        ]
    )

    monkeypatch.setattr(integrator, "_is_stale_task", lambda task, protocol, now=None: True)
    assert integrator.main(["sweep-stale"]) == 0

    state = integrator.read_state()
    task = state["tasks"][0]
    assert task["status"] == "released"
    assert task["claimed_by"] is None
