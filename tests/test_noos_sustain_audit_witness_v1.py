"""Tests for Phase-4 sustain/audit witnesses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_liveness_registry_witness_v1 as liveness  # noqa: E402
import noos_machine_audit_witness_v1 as machine  # noqa: E402
import noos_sandbox_url_sweep_witness_v1 as sandbox  # noqa: E402


def test_machine_audit_witness_schema(monkeypatch):
    monkeypatch.setattr(
        machine,
        "run_outside_audit",
        lambda **_: {"ok": True, "chain": {"ok": True}, "receipts_scanned": 10},
    )
    row = machine.witness(write_receipt=False)
    assert row["schema"] == "noos-machine-audit-witness-v1"
    assert row["chain_ok"] is True


def test_liveness_registry_witness_readonly(monkeypatch):
    wf_doc = json.loads((ROOT / "data/autorun-workflows-v1.json").read_text(encoding="utf-8"))

    monkeypatch.setattr(liveness, "WORKFLOWS", ROOT / "data/autorun-workflows-v1.json")
    monkeypatch.setattr(
        liveness,
        "probe_supabase_noos_liveness_registry",
        lambda wf, doc, stale: {
            "status": "RUNNING",
            "stale_count": 0,
            "registry_rows": 14,
            "stale_loops": [],
        },
    )
    row = liveness.witness(write_receipt=False)
    assert row["mutates_registry"] is False
    assert row["stale_count"] == 0


def test_sandbox_url_sweep_witness(monkeypatch):
    monkeypatch.setattr(
        sandbox,
        "probe_url_sweep_readonly",
        lambda wf: {"status": "COMPLETE", "evidence": {"checked": 6, "oks": ["OK"]}},
    )
    monkeypatch.setattr(
        sandbox,
        "run_sweep",
        lambda **_: {"ok": True, "report_line": "trigger_sweep_clean · registry matches live"},
    )
    row = sandbox.witness(write_receipt=False)
    assert row["schema"] == "noos-sandbox-url-sweep-witness-v1"
    assert row["overall_status"] == "green"
