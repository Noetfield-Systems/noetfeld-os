from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_workflow_audit_v1 as audit  # noqa: E402


def test_audit_report_is_clean_when_helpers_are_clean(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "WORKFLOW_DIR", tmp_path / ".github/workflows")
    monkeypatch.setattr(audit, "LOOP_REGISTRY", tmp_path / "data/noos-24-7-loops-v1.json")
    monkeypatch.setattr(audit.dash, "build_dashboard", lambda: {"triage_required": False, "workflows": []})
    monkeypatch.setattr(audit.dash, "dashboard_findings", lambda dash: [])
    monkeypatch.setattr(audit.hb, "build_heartbeat", lambda: {"drift": {"mismatches": []}, "loops": []})
    monkeypatch.setattr(audit.hb, "heartbeat_findings", lambda hb: [])
    monkeypatch.setattr(audit, "scan_continue_on_error", lambda: [])

    report = audit.audit_report()

    assert report["overall_ok"] is True
    assert report["findings_count"] == 0


def test_audit_report_flags_findings(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "WORKFLOW_DIR", tmp_path / ".github/workflows")
    monkeypatch.setattr(audit, "LOOP_REGISTRY", tmp_path / "data/noos-24-7-loops-v1.json")
    monkeypatch.setattr(audit.dash, "build_dashboard", lambda: {"triage_required": True, "dirty_total": 250, "triage_threshold": 200, "workflows": []})
    monkeypatch.setattr(audit.dash, "dashboard_findings", lambda dash: [{"scope": "sandbox_triage", "severity": "high", "summary": "Dirty workspace total exceeds triage threshold", "detail": "dirty_total=250 threshold=200"}])
    monkeypatch.setattr(audit.hb, "build_heartbeat", lambda: {"drift": {"mismatches": [{"loop_id": "x", "surface": "cron", "committed_truth": "a", "deployed_truth": "b"}]}, "loops": []})
    monkeypatch.setattr(audit.hb, "heartbeat_findings", lambda hb: [{"scope": "x", "severity": "high", "summary": "Drift mismatch on cron", "detail": "committed=a deployed=b"}])
    monkeypatch.setattr(audit, "scan_continue_on_error", lambda: [{"scope": "f.yml", "severity": "high", "line": 1, "summary": "Workflow step masks failures with continue-on-error", "detail": "continue-on-error: true"}])

    report = audit.audit_report()

    assert report["overall_ok"] is False
    assert report["findings_count"] == 3


def test_write_findings_file_shape(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    report = {
        "schema": "noos-workflow-audit-v1",
        "generated_at": "2026-07-06T10:00:00Z",
        "overall_ok": False,
        "findings_count": 2,
        "findings": [
            {"scope": "a.yml", "severity": "high", "summary": "Workflow step masks failures with continue-on-error", "detail": "x"},
            {"scope": "b.yml", "severity": "medium", "summary": "Workflow SLO miss", "detail": "freshness_missing"},
        ],
    }
    out = audit.write_findings_file(report, path=tmp_path / "data" / "noos-audit-findings-v1.json")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema"] == "noos-audit-findings-v1"
    assert len(payload["blocking"]) == 1
    assert len(payload["dependencies"]) == 1
