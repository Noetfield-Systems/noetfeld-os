"""Tests for sandbox fleet registry reconcile."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_sandbox_registry_reconcile_v1 as reconcile


def test_reconcile_eight_sandboxes():
    row = reconcile.reconcile()
    assert row["sandbox_count"] == 8
    assert row["expected_count"] == 8
    ids = {sb["sandbox_id"] for sb in row["sandboxes"]}
    assert ids == reconcile.EXPECTED_SANDBOX_IDS
    assert row["ok"] is True


def test_reconcile_write_receipt(tmp_path, monkeypatch):
    receipt = tmp_path / "proof" / "sandbox-registry.json"
    monkeypatch.setattr(reconcile, "RECEIPT", receipt)
    row = reconcile.reconcile()
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    assert receipt.is_file()
