"""Tests for deploy baseline audit."""

from __future__ import annotations

import json
from pathlib import Path

import scripts.noos_deploy_baseline_audit_v1 as baseline


def test_build_baseline_schema() -> None:
    row = baseline.build_baseline()
    assert row["schema"] == "noos-deploy-baseline-audit-v1"
    assert "motor_matrix" in row
    assert "scopes" in row


def test_deploy_scopes_file_exists() -> None:
    path = Path("data/noos-deploy-scopes-v1.json")
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "fly-inbox" in data["scopes"]
