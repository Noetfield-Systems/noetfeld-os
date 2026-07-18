"""NF-NOOS-MOTOR-V1-FULL-RUNWAY Phase 5/7 — local reference executor.

End-to-end (input -> output artifact -> receipt -> retrieval), plus the
failure-path suite: invalid input, idempotency dedupe, replay lineage, and
output-hash tamper detection. All offline; artifacts go to a tmp dir.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_motor_local_executor_v1 as ex  # noqa: E402
import noos_motor_state_machine_v1 as fsm  # noqa: E402

NOW = "2026-07-18T00:00:00Z"
JOB = {
    "task_kind": "digest",
    "title": "test digest",
    "records": [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}],
}


def _dirs(tmp_path):
    return {"artifact_dir": tmp_path / "art", "receipt_dir": tmp_path / "rcp"}


# ---- end-to-end organic path -----------------------------------------------
def test_end_to_end_produces_real_output_and_receipt(tmp_path):
    res = ex.run_job(JOB, now=NOW, **_dirs(tmp_path))
    assert res["ok"] is True
    assert res["status"] == fsm.COMPLETED
    # real artifact on disk
    art = Path(res["json_artifact"])
    assert art.is_file()
    output = json.loads(art.read_text())
    assert output["record_count"] == 2
    assert output["numeric_totals"]["a"] == 3.0
    # receipt is provenance-honest: local execution is local_reference, NOT organic
    receipt = json.loads(Path(res["receipt_path"]).read_text())
    assert receipt["receipt_origin"] == fsm.ORIGIN_LOCAL_REFERENCE
    assert receipt["receipt_origin"] != fsm.ORIGIN_ORGANIC
    assert receipt["execution_plane"] == "local_reference"
    assert receipt["producer"] == "noos-motor-local-executor-v1"
    assert receipt["state"] == fsm.COMPLETED
    # markdown report exists and is non-trivial
    assert Path(res["md_artifact"]).read_text().startswith("# test digest")


def test_retrieval_and_integrity(tmp_path):
    d = _dirs(tmp_path)
    res = ex.run_job(JOB, now=NOW, **d)
    got = ex.retrieve(res["execution_id"], **d)
    assert got["ok"] is True
    assert got["status"] == fsm.COMPLETED
    assert got["output_integrity_ok"] is True
    assert got["output"]["record_count"] == 2


# ---- failure path: truthful rejection --------------------------------------
def test_invalid_input_fails_truthfully_no_artifact(tmp_path):
    d = _dirs(tmp_path)
    bad = {"task_kind": "digest", "records": []}  # empty records
    res = ex.run_job(bad, now=NOW, **d)
    assert res["ok"] is False
    assert res["status"] == fsm.FAILED
    assert res["json_artifact"] is None
    assert any("non-empty" in e for e in res["validation_errors"])
    # a FAILED receipt exists (failure is recorded, not disappeared)
    receipt = json.loads(Path(res["receipt_path"]).read_text())
    assert receipt["state"] == fsm.FAILED
    assert receipt["error_code"] == "invalid_input"


def test_unknown_task_kind_fails(tmp_path):
    res = ex.run_job({"task_kind": "nope"}, now=NOW, **_dirs(tmp_path))
    assert res["status"] == fsm.FAILED


# ---- failure path: idempotency (no duplicate logical run) -------------------
def test_duplicate_input_deduplicates(tmp_path):
    d = _dirs(tmp_path)
    ledger = fsm.MotorLedger()
    r1 = ex.run_job(JOB, now=NOW, ledger=ledger, **d)
    r2 = ex.run_job(JOB, now="2026-07-18T00:05:00Z", ledger=ledger, **d)
    assert r1["execution_id"] == r2["execution_id"]
    assert r2["deduplicated"] is True


# ---- failure path: replay preserves lineage, new attempt -------------------
def test_replay_preserves_lineage(tmp_path):
    d = _dirs(tmp_path)
    ledger = fsm.MotorLedger()
    r1 = ex.run_job(JOB, now=NOW, ledger=ledger, **d)
    parent = ledger.get(r1["execution_id"])
    child = ledger.replay(parent.execution_id, now="2026-07-18T01:00:00Z", payload=JOB)
    assert child.root_execution_id == parent.root_execution_id
    assert child.correlation_id == parent.correlation_id
    assert child.execution_id != parent.execution_id
    assert child.execution_origin == fsm.ORIGIN_REPLAY


# ---- failure path: output hash mismatch is detectable ----------------------
def test_output_hash_mismatch_detected(tmp_path):
    d = _dirs(tmp_path)
    res = ex.run_job(JOB, now=NOW, **d)
    art = Path(res["json_artifact"])
    tampered = json.loads(art.read_text())
    tampered["record_count"] = 999  # corrupt the artifact
    art.write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n")
    got = ex.retrieve(res["execution_id"], **d)
    assert got["output_integrity_ok"] is False  # tamper caught by hash
