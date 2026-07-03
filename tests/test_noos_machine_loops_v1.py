"""E2E tests for MACHINE_LOOPS v1 + FOUNDER_CANON interface."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_machine_loops_v1 as loops  # noqa: E402
import noos_receipt_chain_v1 as chain  # noqa: E402


def test_dispatch_templates_exist():
    for name in ("worker-execute-v1.json", "repair-lane-v1.json", "critic-pass-v1.json", "research-memo-v1.json"):
        assert (ROOT / ".agent-policy/dispatch-templates" / name).is_file()


def test_founder_trigger_ledger_has_retirement_conditions():
    ledger = loops.load_json(loops.LEDGER_PATH)
    triggers = ledger.get("triggers") or []
    assert len(triggers) >= 6
    for row in triggers:
        assert row.get("retirement_condition")
        assert row.get("trigger_id")


def test_critic_rejects_verifier_edit_in_diff():
    receipt = {"schema": "noos-worker-kernel-receipt-v1", "ok": True}
    row = loops.run_critic(receipt=receipt, diff_files=["scripts/verify_living_system_governance_v1.py"])
    assert row["verdict"] == "REJECT"
    assert any(f["check"] == "verifier_edit" for f in row["findings"])


def test_critic_approves_clean_receipt():
    receipt = {"schema": "noos-local-closeout-v1", "ok": True, "written_at": "2026-07-03T10:00:00+00:00"}
    row = loops.run_critic(receipt=receipt, diff_files=["tests/test_foo.py"])
    assert row["verdict"] == "APPROVE"


def test_repair_dispatch_derives_narrow_paths():
    failure = {
        "task_id": "NOOS-LANE-1",
        "error": "failed tests/test_noos_integrator_sync_v1.py",
        "files_changed": ["scripts/foo.py"],
    }
    dispatch = loops.build_repair_dispatch(failure)
    assert dispatch["template_id"] == "repair-lane-v1"
    paths = dispatch["params"]["derived_paths"]
    assert "scripts/foo.py" in paths
    assert "tests/test_noos_integrator_sync_v1.py" in paths


def test_research_memo_routes_high_confidence():
    memo = loops.build_research_memo(
        question="Should we repair?",
        source_receipt={"schema": "noos-machine-critic-receipt-v1", "ok": False},
    )
    assert memo["schema"] == "noos-research-memo-v1"
    assert memo["confidence"] >= 0.75
    assert memo["machine_apply"] is True


def test_reconcile_queues_repair_from_failed_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    proof = tmp_path / "proof"
    proof.mkdir()
    fail = proof / "fail.json"
    fail.write_text(
        json.dumps(
            {
                "schema": "noos-worker-kernel-receipt-v1",
                "ok": False,
                "task_id": "T1",
                "status": "FAILED_WITH_RECEIPT",
            }
        ),
        encoding="utf-8",
    )
    runtime = tmp_path / "runtime"
    monkeypatch.setattr(loops, "PROOF_DIR", proof)
    monkeypatch.setattr(loops, "RUNTIME_DIR", runtime)
    config = loops.load_json(loops.CONFIG_PATH)
    config["dispatch_queue_path"] = str(runtime / "queue.json")
    monkeypatch.setattr(loops, "CONFIG_PATH", tmp_path / "config.json")
    (tmp_path / "config.json").write_text(json.dumps(config), encoding="utf-8")

    row = loops.reconcile_queue(write=True)
    assert row["new_this_run"] >= 1
    assert row["ok"] is True


def test_receipt_chain_seal_and_verify():
    a = chain.seal_receipt({"schema": "a", "n": 1})
    b = chain.seal_receipt({"schema": "b", "n": 2}, prev_hash=a["chain_hash"])
    row = chain.verify_chain([a, b])
    assert row["ok"] is True
    assert row["chained_count"] == 2


def test_shadow_decision_increments_counter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    ledger_path = tmp_path / "ledger.json"
    ledger = loops.load_json(loops.LEDGER_PATH)
    ledger["shadow_decision_threshold"] = 2
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")

    config_path = tmp_path / "config.json"
    config = loops.load_json(loops.CONFIG_PATH)
    config["shadow_decisions_path"] = str(tmp_path / "shadow.json")
    config_path.write_text(json.dumps(config), encoding="utf-8")

    monkeypatch.setattr(loops, "LEDGER_PATH", ledger_path)
    monkeypatch.setattr(loops, "CONFIG_PATH", config_path)

    loops.record_shadow_decision(trigger_id="FT-MERGE-T0-T1", machine_recommendation="approve", founder_decision="approve")
    row = loops.record_shadow_decision(trigger_id="FT-MERGE-T0-T1", machine_recommendation="approve", founder_decision="approve")
    assert row["ok"] is True
    assert len(row["proposals"]) >= 1


def test_machine_loops_verify_passes():
    row = loops.verify_installation()
    assert row["checks"]["templates"] is True
    assert row["checks"]["ledger"] is True


def test_classify_merge_tier_t3_for_verifier():
    config = loops.load_json(loops.CONFIG_PATH)
    tier = loops.classify_merge_tier(["scripts/verify_foo_v1.py"], config)
    assert tier == "T3"


def test_autonomy_status_ok():
    row = loops.autonomy_status()
    assert row["ok"] is True
    assert row.get("triggers") or row.get("canon_version")
