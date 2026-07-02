"""Tests for noetfield-gate chain tool."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from noetfield_gate.boot import run_gate_checks, write_gate_report
from noetfield_gate.decide import SAMPLE_BLOCK_INTENT, build_receipt


def test_gate_pass_in_repo(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    report = run_gate_checks(root=root, api_url=None)
    assert report["outcome"] == "PASS"
    assert any(c["name"] == "policy_pack_present" and c["ok"] for c in report["checks"])


def test_gate_block_missing_policy(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    report = run_gate_checks(root=empty)
    assert report["outcome"] == "BLOCK"
    assert report["block_reasons"]


def test_gate_pass_portable_bundled(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    report = run_gate_checks(api_url=None)
    assert report["outcome"] == "PASS"
    assert any(c["name"] == "policy_pack_present" and c["ok"] for c in report["checks"])


def test_gate_report_writes_md_and_json(tmp_path):
    report = {
        "schema": "noetfield-gate-report-v1",
        "outcome": "PASS",
        "checked_at": "2026-06-15T00:00:00Z",
        "checks": [{"id": "G1", "name": "test", "ok": True, "reason": "ok"}],
        "block_reasons": [],
    }
    out = write_gate_report(report, tmp_path / "gate.json")
    assert out.is_file()
    assert out.with_suffix(".md").is_file()


def test_build_receipt_shape():
    api = {
        "request_id": "r1",
        "decision": "APPROVE",
        "composite_score": 80.0,
        "audit_id": 1,
        "rule_set_version": "1.0.0",
        "policy_hashes": {"base": "a", "corridor": "b", "combined": "c"},
    }
    receipt = build_receipt(api, intent={"applicant_id": "x"})
    assert receipt["decision"] == "APPROVE"
    assert receipt["schema"] == "noetfield-decision-receipt-v1"


def test_gate_strict_fails_on_skipped_checks(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    report = run_gate_checks(root=root, api_url=None, strict=True)
    assert report["outcome"] == "BLOCK"
    assert any("strict mode" in reason for reason in report["block_reasons"])


def test_gate_json_stdout(tmp_path, monkeypatch, capsys):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    from noetfield_gate.cli import main

    code = main(["gate", "--json"])
    assert code == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["schema"] == "noetfield-gate-report-v1"
    assert payload["outcome"] == "PASS"


def test_sample_block_intent_extreme_dti():
    dti = SAMPLE_BLOCK_INTENT["monthly_debt"] / SAMPLE_BLOCK_INTENT["monthly_income"]
    assert dti > 0.60


def test_intent_validate_approve_fixture():
    from noetfield_gate.intent_validate import validate_intent_file

    root = Path(__file__).resolve().parents[1]
    result = validate_intent_file(root / "fixtures/demo_intents/approve.json")
    assert result["ok"]
    assert result["applicant_id"] == "gate-demo-001"


def test_verify_chain_passes_in_repo(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    from noetfield_gate.verify import verify_chain

    report = verify_chain(root=root)
    assert report["outcome"] == "PASS"


def test_dated_receipt_dirs():
    from noetfield_gate.boot import dated_receipt_dir

    gate = dated_receipt_dir("gate")
    decide = dated_receipt_dir("decide")
    assert gate.parent == decide.parent
    assert "receipts" in str(gate)


def test_decide_validate_only_cli(capsys):
    root = Path(__file__).resolve().parents[1]
    from noetfield_gate.cli import main

    code = main(
        ["decide", "--file", str(root / "fixtures/demo_intents/approve.json"), "--validate-only"]
    )
    assert code == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["ok"]


def test_verify_cli_json(monkeypatch, capsys):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    from noetfield_gate.cli import main

    code = main(["verify", "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["outcome"] == "PASS"
