from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import autorun_status_v1 as dash  # noqa: E402
import noos_loop_heartbeat_v1 as hb  # noqa: E402
import noos_slo_v1 as slo  # noqa: E402


def test_score_slo_flags_miss() -> None:
    result = slo.score_slo(
        freshness_minutes=90,
        success_rate=0.5,
        latency_minutes=90,
        targets={
            "freshness_target_minutes": 30,
            "success_rate_target": 0.98,
            "latency_target_minutes": 60,
        },
    )

    assert result["ok"] is False
    assert "freshness_miss" in result["misses"]
    assert "success_rate_miss" in result["misses"]
    assert "latency_miss" in result["misses"]


def test_autofile_kaizen_receipt_writes_file(tmp_path: Path) -> None:
    rel_path = slo.autofile_kaizen_receipt(
        root=tmp_path,
        source="unit-test",
        loop_id="loop-a",
        score_row={"score": 62.5, "ok": False, "misses": ["success_rate_miss"]},
        evidence={"status": "RUNNING"},
    )

    out = tmp_path / rel_path
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "improvement-receipt-v2"
    assert data["source_ref"] == "unit-test"
    assert data["loop_id"] == "loop-a"


def test_workflow_slo_attaches_receipt_on_miss(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(dash, "ROOT", tmp_path)
    row = {"status": "BLOCKED_WITH_REASON", "evidence": {"observed_at": datetime.now(timezone.utc).isoformat()}}
    wf = {"id": "wf-1", "title": "Workflow 1", "plane": "NOETFELD-OS"}
    wf_doc = {"slo_defaults": {"freshness_target_minutes": 30, "success_rate_target": 0.98, "latency_target_minutes": 60}}

    slo_row, receipt_path = dash.workflow_slo(row, wf, wf_doc)

    assert slo_row["ok"] is False
    assert receipt_path is not None
    assert (tmp_path / receipt_path).is_file()


def test_heartbeat_emits_slo_and_kaizen_receipt(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(hb, "ROOT", tmp_path)
    monkeypatch.setattr(hb, "REGISTRY", tmp_path / "registry.json")
    monkeypatch.setattr(
        hb,
        "load_registry",
        lambda: {
            "slo_defaults": {"freshness_target_minutes": 30, "success_rate_target": 0.98, "latency_target_minutes": 60},
            "loops": [
                {
                    "id": "loop-a",
                    "github_workflow": "loop-a.yml",
                    "interval_minutes": 5,
                    "lane": "noos",
                    "value_class": "hygiene",
                }
            ],
        },
    )
    monkeypatch.setattr(hb, "loop_state", lambda loop_id: {"last_state": "BLOCKED_WITH_REASON", "last_finished_at": datetime.now(timezone.utc).isoformat()})
    monkeypatch.setattr(hb, "recent_cycles", lambda loop_id, limit=20: [])
    monkeypatch.setattr(hb, "trigger_registry_sweep", lambda: {"ok": True, "drift": False, "registry_path": "data/trigger-registry-v1.json", "report_line": "trigger_sweep_clean"})
    monkeypatch.setattr(hb, "deployed_cron", lambda workflow_file: "*/5 * * * *")

    row = hb.build_heartbeat()

    loop = row["loops"][0]
    assert loop["slo"]["ok"] is False
    assert loop["slo"]["kaizen_receipt"]
    assert row["founder_gated_improvements"]


def test_heartbeat_findings_flags_slo_miss(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(hb, "ROOT", tmp_path)
    report = {
        "drift": {"mismatches": []},
        "loops": [
            {
                "workflow_id": "wf-1",
                "last_run_at": datetime.now(timezone.utc).isoformat(),
                "cycles_observed": 1,
                "throttled_roi": False,
                "slo": {"ok": False, "misses": ["freshness_miss"]},
            }
        ],
    }

    findings = hb.heartbeat_findings(report)
    assert len(findings) == 1
    assert findings[0]["summary"] == "Loop SLO miss"


def test_loop_registry_includes_workflow_audit() -> None:
    doc = json.loads((ROOT / "data/noos-24-7-loops-v1.json").read_text())
    ids = [loop["id"] for loop in doc["loops"]]
    assert "workflow_audit" in ids
