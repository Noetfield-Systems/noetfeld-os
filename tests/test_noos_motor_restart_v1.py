"""Phase C — motor restart recipe dry-run and fail-closed gates."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_motor_restart_v1 as motor  # noqa: E402


def test_dry_run_cf_loop_motor_passes() -> None:
    row = motor.execute_recipe("cf-loop-motor", dry_run=True)
    assert row["ok"] is True
    assert row["dry_run"] is True
    assert row["recipe_id"] == "cf-loop-motor"


def test_founder_gated_fails_closed() -> None:
    row = motor.execute_recipe("fly-inbox-motor", dry_run=True)
    assert row["ok"] is False
    assert row.get("error") == "founder_gated"


def test_unknown_recipe() -> None:
    row = motor.execute_recipe("nonexistent-motor", dry_run=True)
    assert row["ok"] is False
    assert row.get("error") == "recipe_not_found"


def test_recipes_file_has_machine_safe_motors() -> None:
    doc = motor.load_recipes()
    ids = {r["id"] for r in doc.get("recipes") or []}
    assert {"cf-loop-motor", "cf-deadman", "fly-loop-executor"}.issubset(ids)


def test_health_probe_structure() -> None:
    row = motor.probe_health("https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev/health")
    assert "ok" in row
