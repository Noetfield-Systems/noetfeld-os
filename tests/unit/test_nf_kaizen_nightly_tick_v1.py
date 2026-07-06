"""Unit tests for nf_kaizen_nightly_tick_v1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import nf_kaizen_nightly_tick_v1 as kz  # noqa: E402


def test_kaizen_dry_run_no_candidates(monkeypatch):
    monkeypatch.setattr(kz, "fetch_open_machine_safe", lambda **_: [])
    monkeypatch.setattr(sys, "argv", ["nf_kaizen_nightly_tick_v1.py", "--dry-run"])
    assert kz.main() == 0


def test_kaizen_dry_run_with_recipe(monkeypatch):
    row = {
        "id": "00000000-0000-4000-8000-000000000001",
        "finding": "greeting drift",
        "source": "probe:greeting_coupling",
        "expected_roi": "greeting_coupling",
        "machine_safe": True,
        "status": "open",
        "metadata": {"kaizen_recipe": "greeting_coupling"},
        "created_at": "2026-07-05T00:00:00Z",
    }
    monkeypatch.setattr(kz, "fetch_open_machine_safe", lambda **_: [row])
    monkeypatch.setattr(sys, "argv", ["nf_kaizen_nightly_tick_v1.py", "--dry-run"])
    assert kz.main() == 0


def test_copilot_scheduled_disabled_manifest():
    manifest = json.loads(
        (ROOT / "governance" / "COPILOT_SCHEDULED_AUTOMATIONS_LOCKED.json").read_text(encoding="utf-8")
    )
    assert manifest["policy"] == "all_disabled"
    assert all(a["enabled"] is False for a in manifest["automations"])
