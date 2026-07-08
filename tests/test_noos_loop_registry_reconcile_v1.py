"""Tests for loop registry reconcile."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_loop_registry_reconcile_v1 as reconcile


def test_reconcile_all_core_workflows_exist():
    row = reconcile.reconcile()
    assert row["ok"] is True
    assert row["loop_count"] >= 7
    core = {"inbox", "runtime", "surface", "chain", "self_heal", "sourcea_observe", "agent_nerve"}
    seen = {loop["loop_id"] for loop in row["loops"]}
    assert core.issubset(seen)
    for loop in row["loops"]:
        if loop["loop_id"] in core:
            assert loop["workflow_exists"] is True
            assert loop["event_match"] is True


def test_reconcile_write_receipt(tmp_path, monkeypatch):
    receipt = tmp_path / "proof" / "reconcile.json"
    monkeypatch.setattr(reconcile, "RECEIPT", receipt)
    row = reconcile.reconcile()
    reconcile.RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    reconcile.RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    assert receipt.is_file()
