"""NF-NOOS-OBSERVABILITY-SEMANTICS-001 — deterministic fixtures.

Covers the required scenarios 1-11: the dual-signal loop classifier, the
success_rate / evidence-state honesty rules, evidence-vs-execution routing,
reconciler orphan classification, and the two deadman probe-authority modes.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_deadman_v1 as deadman  # noqa: E402
import noos_observability_semantics_v1 as sem  # noqa: E402

# Thresholds used across fixtures.
DISPATCH_THRESH = 10.0
COMPLETION_THRESH = 30.0
FRESH_AGE = 2.0
STALE_AGE = 999.0


def _classify(d_age, c_age, *, d_ok=True, c_ok=True):
    return sem.classify_loop_state(
        dispatch_age_minutes=d_age,
        dispatch_stale_threshold_minutes=DISPATCH_THRESH,
        completion_age_minutes=c_age,
        completion_stale_threshold_minutes=COMPLETION_THRESH,
        dispatch_query_ok=d_ok,
        completion_query_ok=c_ok,
        dispatch_last_fired_at="2026-07-17T03:50:00Z",
        completion_last_recorded_at="2026-07-17T03:50:00Z",
    )


# ---- Fixture 1: dispatch fresh + receipt fresh ----------------------------
def test_1_dispatch_fresh_receipt_fresh_running_confirmed():
    r = _classify(FRESH_AGE, FRESH_AGE)
    assert r["execution_state"] == sem.RUNNING_CONFIRMED
    assert r["success_rate"] == 1.0
    assert r["evidence_state"] == sem.EVIDENCE_SUFFICIENT
    assert r["route"] is None
    assert r["presentation"]["dispatch_freshness"] == sem.FRESH
    assert r["presentation"]["completion_evidence_freshness"] == sem.FRESH


# ---- Fixture 2: dispatch fresh + receipt stale ----------------------------
def test_2_dispatch_fresh_receipt_stale_completion_unproven():
    r = _classify(FRESH_AGE, STALE_AGE)
    assert r["execution_state"] == sem.DISPATCHING_COMPLETION_UNPROVEN
    assert r["success_rate"] is None
    assert r["evidence_state"] == sem.EVIDENCE_INSUFFICIENT
    assert r["route"] == sem.ROUTE_RECEIPT_WRITER_REPAIR
    assert r["presentation"]["dispatch_freshness"] == sem.FRESH
    assert r["presentation"]["completion_evidence_freshness"] == sem.STALE


# ---- Fixture 3: dispatch stale + receipt fresh ----------------------------
def test_3_dispatch_stale_receipt_fresh_observer_divergence():
    r = _classify(STALE_AGE, FRESH_AGE)
    assert r["execution_state"] == sem.OBSERVER_DIVERGENCE_OR_REPLAY
    assert r["route"] == sem.ROUTE_OBSERVER_RECONCILIATION
    assert r["success_rate"] is None


# ---- Fixture 4: both stale -------------------------------------------------
def test_4_both_stale_loop_execution_stale():
    r = _classify(STALE_AGE, STALE_AGE)
    assert r["execution_state"] == sem.LOOP_EXECUTION_STALE
    assert r["success_rate"] == 0.0
    assert r["evidence_state"] == sem.EVIDENCE_SUFFICIENT
    assert r["route"] == sem.ROUTE_EXECUTION_RECONCILE


# ---- Fixture 5: source query failure --------------------------------------
def test_5_source_query_failure_observer_unavailable():
    r = _classify(FRESH_AGE, FRESH_AGE, c_ok=False)
    assert r["execution_state"] == sem.OBSERVER_UNAVAILABLE
    assert r["route"] == sem.ROUTE_MONITORING_AVAILABILITY
    assert r["success_rate"] is None
    # dispatch-side failure too
    r2 = _classify(FRESH_AGE, FRESH_AGE, d_ok=False)
    assert r2["execution_state"] == sem.OBSERVER_UNAVAILABLE


def test_5b_missing_timestamp_is_observer_unavailable():
    # queried ok but no usable timestamp -> cannot confirm, not a failure
    r = _classify(None, FRESH_AGE)
    assert r["execution_state"] == sem.OBSERVER_UNAVAILABLE
    assert r["success_rate"] is None


# ---- Fixture 6: stale receipt must NOT produce success_rate=0.0 ------------
def test_6_stale_receipt_never_zero_success_rate():
    r = _classify(FRESH_AGE, STALE_AGE)
    assert r["success_rate"] is None
    assert r["success_rate"] != 0.0
    assert r["evidence_state"] == sem.EVIDENCE_INSUFFICIENT


# ---- Fixture 7: evidence staleness must NOT invoke execution restart -------
def test_7_evidence_staleness_no_execution_restart_route():
    for state_result in (
        _classify(FRESH_AGE, STALE_AGE),  # completion unproven
        _classify(STALE_AGE, FRESH_AGE),  # observer divergence
        _classify(FRESH_AGE, FRESH_AGE, c_ok=False),  # observer unavailable
    ):
        assert state_result["route"] != sem.ROUTE_EXECUTION_RECONCILE
        assert state_result["route_permits_execution_mutation"] is False
        assert not sem.route_permits_execution_mutation(state_result["route"])


# ---- Fixture 8: both stale -> execution reconcile --------------------------
def test_8_both_stale_routes_to_execution_reconcile():
    r = _classify(STALE_AGE, STALE_AGE)
    assert r["route"] == sem.ROUTE_EXECUTION_RECONCILE
    assert r["route_permits_execution_mutation"] is True
    assert sem.route_permits_execution_mutation(r["route"]) is True


# ---- Fixture 9: old queue records classified as orphaned -------------------
def test_9_old_queue_records_are_orphaned_not_actionable():
    now_ts = sem._parse_epoch("2026-07-17T04:00:00Z")
    july5 = [
        {
            "schema": "noos-machine-repair-dispatch-v1",
            "source_receipt_path": f"receipts/proof/noos-outside-audit-20260705T12320{i}Z.json",
            "created_at": "2026-07-05T12:32:00Z",
        }
        for i in range(8)
    ]
    fresh_actionable = {
        "schema": "noos-machine-repair-dispatch-v1",
        "source_receipt_path": "receipts/proof/noos-some-fresh-failure.json",
        "created_at": "2026-07-17T03:59:00Z",
    }
    summary = sem.summarize_pending(
        july5 + [fresh_actionable], new_dispatches=0, now_ts=now_ts, orphan_age_days=3.0
    )
    counts = summary["counts"]
    assert counts["orphaned_backlog"] == 8
    assert counts["actionable_pending"] == 1
    assert counts["new_dispatches"] == 0
    # each July-5 item individually classified orphaned
    for item in july5:
        assert sem.classify_pending_item(item, now_ts=now_ts) == "orphaned_backlog"


def test_9b_lease_and_backoff_buckets():
    now_ts = sem._parse_epoch("2026-07-17T04:00:00Z")
    assert sem.classify_pending_item({"active_lease": True}, now_ts=now_ts) == "active_leases"
    assert sem.classify_pending_item({"backoff_until": "x"}, now_ts=now_ts) == "backoff_pending"
    assert sem.classify_pending_item({"completed": True}, now_ts=now_ts) == "completed_unreflected"
    assert sem.classify_pending_item({"whatever": 1}, now_ts=now_ts) == "unknown"


# ---- Fixture 10: observe-only deadman performs NO write --------------------
def test_10_observe_only_mode_performs_no_write(monkeypatch):
    monkeypatch.setattr(deadman, "fetch_registry_rows", lambda: [])

    calls = {"sink": 0}

    def _forbidden_sink(receipt):  # pragma: no cover - must never run
        calls["sink"] += 1
        return {"ok": True}

    monkeypatch.setattr(deadman, "sink_deadman_receipt", _forbidden_sink)
    receipt = deadman.run_check(source="test", mode=deadman.MODE_OBSERVE_ONLY)
    assert receipt["probe_mode"] == deadman.MODE_OBSERVE_ONLY
    assert receipt["supabase_sink"]["write_performed"] is False
    assert receipt["supabase_sink"]["skipped"] is True
    assert calls["sink"] == 0  # sink never invoked in observe-only


# ---- Fixture 11: canary mode records and discloses its write --------------
def test_11_canary_mode_records_and_discloses(monkeypatch):
    monkeypatch.setattr(deadman, "fetch_registry_rows", lambda: [])

    calls = {"sink": 0}

    def _fake_sink(receipt):
        calls["sink"] += 1
        return {"ok": True, "run_id": "canary-test", "status": 201}

    monkeypatch.setattr(deadman, "sink_deadman_receipt", _fake_sink)
    receipt = deadman.run_check(source="test", mode=deadman.MODE_DIAGNOSTIC_CANARY_WRITE)
    assert receipt["probe_mode"] == deadman.MODE_DIAGNOSTIC_CANARY_WRITE
    assert calls["sink"] == 1
    disclosure = receipt["supabase_sink"]["disclosure"]
    assert disclosure["sink_table"] == "noos_deadman_runs"
    assert disclosure["affects_operational_state"] is False
    assert "INSERT" in disclosure["write_kind"]
    assert disclosure["persistence"]


def test_11b_observe_only_is_default_mode(monkeypatch):
    monkeypatch.setattr(deadman, "fetch_registry_rows", lambda: [])
    monkeypatch.setattr(deadman, "sink_deadman_receipt", lambda r: {"ok": True})
    receipt = deadman.run_check(source="test")
    assert receipt["probe_mode"] == deadman.MODE_OBSERVE_ONLY
    assert receipt["supabase_sink"]["write_performed"] is False
