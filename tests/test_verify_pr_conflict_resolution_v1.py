"""Tests for PR conflict resolution machine gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_pr_conflict_resolution_v1 as vpr  # noqa: E402


def test_lock_manifest_present():
    assert (ROOT / "data/noos-pr-conflict-skill-lock-v1.json").is_file()


def test_skill_stub_and_rule_exist():
    assert (ROOT / ".cursor/skills/pr-conflict-resolver/SKILL.md").is_file()
    assert (ROOT / ".cursor/rules/noos-pr-conflict-resolver-mandatory.mdc").is_file()
    assert (ROOT / ".cursor/hooks/noos-pr-conflict-guard.py").is_file()


def test_verify_passes_on_clean_tree():
    row = vpr.verify(require_sg=False, mac_desktop=False)
    assert row["ok"] is True
    assert row.get("issues") == []


def test_lock_manifest_is_locked():
    lock = json.loads((ROOT / "data/noos-pr-conflict-skill-lock-v1.json").read_text(encoding="utf-8"))
    assert lock.get("status") == "LOCKED"
    assert lock.get("sg_canonical", {}).get("skill_sha256_prefix")
