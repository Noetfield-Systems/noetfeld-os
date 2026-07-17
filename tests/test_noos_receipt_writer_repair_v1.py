"""Hermetic tests for the Track D machine owner (receipt-writer repair).

Every test is offline: classification inputs are injected, sink existence is
injected via existing_run_ids, and no network or Supabase access occurs.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_receipt_writer_repair_v1 as rw  # noqa: E402
from noos_observability_semantics_v1 import DISPATCHING_COMPLETION_UNPROVEN  # noqa: E402


def _before(state_kwargs=None):
    kw = {
        "dispatch_age": 5.0, "completion_age": 900.0,
        "dispatch_threshold": 60.0, "completion_threshold": 240.0,
        "dispatch_ok": True, "completion_ok": True,
        "dispatch_at": "2026-07-17T09:00:00Z", "completion_at": "2026-07-16T00:00:00Z",
    }
    kw.update(state_kwargs or {})
    return rw.classify_and_wrap(**kw)


def test_intent_created_only_for_bound_route():
    before = _before()
    assert before["execution_state"] == DISPATCHING_COMPLETION_UNPROVEN
    intent = rw.build_repair_intent("loop-x", "loop-loop-x", before)
    assert intent is not None
    assert intent["recipe_id"] == rw.RECIPE_ID
    assert intent["dedupe_key"] == f"receipt-repair:loop-x:{intent['diagnosis_id']}"

    healthy = _before({"completion_age": 5.0, "completion_at": "2026-07-17T09:00:00Z"})
    assert rw.build_repair_intent("loop-x", "loop-loop-x", healthy) is None


def test_no_outbox_escalates_never_improvises():
    intent = rw.build_repair_intent("loop-x", "loop-loop-x", _before())
    result = rw.repair(intent, creds=None, outbox_rows=None)
    assert result["action"] == rw.ESCALATE
    assert "diagnosis" in result and result["dedupe_key"] == intent["dedupe_key"]


def test_outbox_retry_is_idempotent_on_run_id():
    intent = rw.build_repair_intent("loop-x", "loop-loop-x", _before())
    rows = [{"run_id": "railway-aaa", "factory_id": "loop-x"}, {"run_id": "railway-bbb", "factory_id": "loop-x"}, {"factory_id": "loop-x"}]
    result = rw.repair(intent, creds=None, outbox_rows=rows, existing_run_ids={"railway-aaa"})
    assert result["skipped_existing"] == ["railway-aaa"]          # duplicate never rewritten
    assert result["retried"] == ["railway-bbb"]
    assert result["failed"] and "idempotency key" in result["failed"][0]["error"]


def test_before_after_pair_proves_only_on_fresh_after():
    before = _before()
    fresh_after = _before({"completion_age": 2.0, "completion_at": "2026-07-17T09:30:00Z"})
    pair = rw.before_after_pair(before, fresh_after)
    assert pair["decision"] == "PASS" and pair["recovery_state"] == "PROVEN" and pair["external"] is True

    stale_after = _before()
    pair2 = rw.before_after_pair(before, stale_after)
    assert pair2["decision"] == "FAIL" and pair2["recovery_state"] == "UNPROVEN"

    missing_after = {"ok": False, "execution_state": None}
    pair3 = rw.before_after_pair(before, missing_after)
    assert pair3["recovery_state"] == "UNPROVEN"  # missing AFTER never proves


def test_module_has_no_execution_mutation_vocabulary():
    src = (ROOT / "scripts/noos_receipt_writer_repair_v1.py").read_text()
    assert "/motor-restart" not in src            # founder-only runner endpoint
    assert "run_loop(" not in src and "run_factory(" not in src  # never dispatches execution
    for action in rw.FORBIDDEN_ACTIONS:
        assert action in src                       # declared, so receipts disclose them
    # the only table this owner may write is the evidence sink
    assert rw.SINK_TABLE == "noetfield_factory_cycle_runs"
