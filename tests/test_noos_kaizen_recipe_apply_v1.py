"""Phase D — kaizen recipe matcher and dry-run."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_kaizen_recipe_apply_v1 as kaizen  # noqa: E402


def test_match_cloud_motor_401() -> None:
    recipe = kaizen.match_recipe("CF motor returned 401 unauthorized", kaizen.load_recipes())
    assert recipe is not None
    assert recipe["id"] == "cloud-motor-401-resync"


def test_match_stale_loops() -> None:
    recipe = kaizen.match_recipe("deadman stale_count=12 never_fired", kaizen.load_recipes())
    assert recipe is not None
    assert recipe["id"] == "seed-all-loop-ticks"


def test_dry_run_apply() -> None:
    recipes = kaizen.load_recipes()
    row = kaizen.apply_recipe(recipes[0], dry_run=True)
    assert row["ok"] is True
    assert row["dry_run"] is True


def test_at_least_five_recipes() -> None:
    assert len(kaizen.load_recipes()) >= 5
