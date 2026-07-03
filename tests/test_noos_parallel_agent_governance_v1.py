"""Tests for parallel agent conflict check."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_agent_conflict_check_v1 as conflict  # noqa: E402


def test_registry_loads():
    reg = conflict.load_json(conflict.REGISTRY_PATH)
    assert reg.get("schema") == "noos-parallel-agent-registry-v1"
    workers = reg.get("workers") or []
    assert len(workers) >= 20
    ids = {w["worker_id"] for w in workers if isinstance(w, dict)}
    assert "cursor-daily-autorun-status" in ids
    assert "gha-noos-surface-loop" in ids


def test_clean_when_no_integrator_state():
    reg = conflict.load_json(conflict.REGISTRY_PATH)
    row = conflict.check_conflicts(registry=reg, integrator={})
    assert row["ok"] is True
    assert row["active_claims"] == 0


def test_scope_overlap_detected():
    reg = conflict.load_json(conflict.REGISTRY_PATH)
    integrator = {
        "tasks": [
            {
                "task_id": "A",
                "agent_id": "agent-a",
                "status": "in_progress",
                "scope_files": ["scripts/foo.py"],
                "heartbeat_at": conflict.utc_now(),
            },
            {
                "task_id": "B",
                "agent_id": "agent-b",
                "status": "claimed",
                "scope_files": ["scripts/foo.py"],
                "heartbeat_at": conflict.utc_now(),
            },
        ]
    }
    row = conflict.check_conflicts(registry=reg, integrator=integrator)
    assert row["ok"] is False
    kinds = [c["kind"] for c in row["conflicts"]]
    assert "integrator_scope_overlap" in kinds


def test_mutex_groups_defined():
    reg = conflict.load_json(conflict.REGISTRY_PATH)
    groups = {g["id"] for g in reg.get("mutex_groups") or [] if isinstance(g, dict)}
    assert "public-health-nerve" in groups
    assert "self-heal-pipeline" in groups
