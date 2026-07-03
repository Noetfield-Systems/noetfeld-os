"""Tests for living-system governance verifier."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_living_system_governance_v1 as gov  # noqa: E402


def test_full_governance_verify_passes():
    row = gov.run_verify(write_receipt=False)
    assert row["ok"] is True, json.dumps(row.get("checks"), indent=2)
    assert row["checks"]["gha_coverage"] is True
    assert row["checks"]["parallel_conflict"] is True
    assert row["checks"]["trigger_sweep"] is True


def test_gha_workflows_all_mapped():
    registry = gov.load_json(gov.PARALLEL_REGISTRY)
    workflows = gov.discover_gha_workflows()
    gha = gov.check_gha_coverage(registry, workflows)
    assert gha["unmapped_workflows"] == []
    assert gha["orphan_worker_refs"] == []
    assert gha["stale_coverage_keys"] == []


def test_copilot_instructions_markers():
    row = gov.check_copilot_instructions()
    assert row["ok"] is True
    assert row["missing_markers"] == []
