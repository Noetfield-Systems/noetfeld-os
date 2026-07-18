"""NF-NOOS-MOTOR-V1-FULL-RUNWAY Phase 4 — provenance-aware classifier gate.

These are the deterministic gate for the false-green fix: a repair / replay /
manual / migration / test completion, however fresh by age, must NEVER promote a
loop to RUNNING_CONFIRMED. Reproduces the 2026-07-12 incident (fresh
noos_integrator_repair rows masking a stalled organic http_loop producer) and
asserts the classifier now reports DEGRADED_REPAIR_SUSTAINED instead.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_observability_semantics_v1 as sem  # noqa: E402

DISPATCH_THRESH = 10.0
COMPLETION_THRESH = 30.0
FRESH = 2.0
STALE = 999.0


def _classify(**kw):
    base = dict(
        dispatch_age_minutes=FRESH,
        dispatch_stale_threshold_minutes=DISPATCH_THRESH,
        completion_age_minutes=FRESH,
        completion_stale_threshold_minutes=COMPLETION_THRESH,
    )
    base.update(kw)
    return sem.classify_loop_state(**base)


# ---- normalize_receipt_origin ---------------------------------------------
def test_normalize_repair_labels_match_route_owner():
    assert sem.normalize_receipt_origin("noos_integrator_repair") == sem.ORIGIN_REPAIR
    assert sem.normalize_receipt_origin("noos_motor_receipt_writer_repair") == sem.ORIGIN_REPAIR
    assert sem.normalize_receipt_origin("http_loop") == sem.ORIGIN_ORGANIC
    assert sem.normalize_receipt_origin("some_replay_run") == sem.ORIGIN_REPLAY
    assert sem.normalize_receipt_origin("workflow_dispatch") == sem.ORIGIN_MANUAL
    assert sem.normalize_receipt_origin("0020_backfill") == sem.ORIGIN_MIGRATION
    assert sem.normalize_receipt_origin(None) == sem.ORIGIN_LEGACY_UNKNOWN
    assert sem.normalize_receipt_origin("") == sem.ORIGIN_LEGACY_UNKNOWN
    assert not sem.is_organic_origin(sem.ORIGIN_REPAIR)
    assert not sem.is_organic_origin(sem.ORIGIN_LEGACY_UNKNOWN)  # never guess
    assert sem.is_organic_origin(sem.ORIGIN_ORGANIC)


# ---- The incident: fresh repair row must NOT be RUNNING_CONFIRMED ----------
def test_fresh_repair_row_is_degraded_not_running():
    r = _classify(completion_origin="noos_integrator_repair")
    assert r["execution_state"] == sem.DEGRADED_REPAIR_SUSTAINED
    assert r["execution_state"] != sem.RUNNING_CONFIRMED
    assert r["success_rate"] is None
    assert r["route"] == sem.ROUTE_ORGANIC_PRODUCER_ESCALATION
    # Escalate/surface — must NOT auto-restart, must NOT loop to receipt repair.
    assert r["route_permits_execution_mutation"] is False
    assert r["route"] != sem.ROUTE_RECEIPT_WRITER_REPAIR


def test_fresh_organic_row_is_running_confirmed():
    r = _classify(completion_origin="http_loop")
    assert r["execution_state"] == sem.RUNNING_CONFIRMED
    assert r["success_rate"] == 1.0
    assert r["provenance"]["organic_completion_fresh"] is True


def test_dispatch_fresh_no_organic_is_completion_unproven():
    # organic explicitly stale, no repair sustaining it
    r = _classify(completion_age_minutes=STALE, completion_origin="http_loop")
    assert r["execution_state"] == sem.COMPLETION_UNPROVEN
    assert r["route"] == sem.ROUTE_ORGANIC_PRODUCER_ESCALATION


def test_separate_fresh_organic_age_confirms_even_if_newest_is_repair():
    # A repair row is newest, but a real organic completion IS within SLO.
    r = _classify(
        completion_origin="noos_integrator_repair",
        organic_completion_age_minutes=5.0,
    )
    assert r["execution_state"] == sem.RUNNING_CONFIRMED
    assert r["provenance"]["organic_completion_fresh"] is True


def test_evidence_inconsistent_wins():
    r = _classify(completion_origin="http_loop", consistency_ok=False)
    assert r["execution_state"] == sem.EVIDENCE_INCONSISTENT
    assert r["success_rate"] is None


def test_stopped_or_idle_only_when_expected():
    # both stale + expected_idle -> STOPPED_OR_IDLE; without the flag -> stale
    idle = _classify(dispatch_age_minutes=STALE, completion_age_minutes=STALE,
                     completion_origin="http_loop", expected_idle=True)
    assert idle["execution_state"] == sem.STOPPED_OR_IDLE
    not_idle = _classify(dispatch_age_minutes=STALE, completion_age_minutes=STALE,
                         completion_origin="http_loop")
    assert not_idle["execution_state"] == sem.LOOP_EXECUTION_STALE


# ---- PROPERTY: no non-organic origin can EVER be RUNNING_CONFIRMED ---------
def test_property_no_non_organic_origin_ever_running_confirmed():
    non_organic = [
        "noos_integrator_repair",
        "noos_motor_receipt_writer_repair",
        "some_replay",
        "manual",
        "workflow_dispatch",
        "0020_backfill_migration",
        "ci_test_run",
    ]
    for trig in non_organic:
        for c_age in (0.0, 1.0, 5.0, 29.0):  # every "fresh by age" value
            for d_age in (0.0, 1.0, 5.0):
                r = _classify(
                    dispatch_age_minutes=d_age,
                    completion_age_minutes=c_age,
                    completion_origin=trig,
                )
                assert r["execution_state"] != sem.RUNNING_CONFIRMED, (trig, c_age, d_age, r["execution_state"])


# ---- derive_completion_provenance reconstructs the incident ----------------
def _age_fn(now_iso):
    now = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))

    def age(ts):
        if not ts:
            return None
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return (now - t).total_seconds() / 60.0

    return age


def test_derive_provenance_incident_shape():
    rows = [
        {"recorded_at": "2026-07-18T02:00:00Z", "runner_output": {"cloud_trigger": "noos_integrator_repair"}},
        {"recorded_at": "2026-07-18T01:50:00Z", "runner_output": {"cloud_trigger": "noos_integrator_repair"}},
        {"recorded_at": "2026-07-12T13:50:49Z", "status": "ok", "exit_code": 0, "runner_output": {"cloud_trigger": "http_loop"}},
    ]
    p = sem.derive_completion_provenance(rows, age_fn=_age_fn("2026-07-18T02:06:00Z"))
    assert p["completion_origin"] == sem.ORIGIN_REPAIR
    assert p["organic_completion_age_minutes"] > 7000  # ~5.5 days stale
    assert p["repair_completion_age_minutes"] < 30  # fresh repair masking
    assert p["metrics"]["repair_receipts_since_last_organic"] == 2


def test_derive_then_classify_incident_end_to_end():
    rows = [
        {"recorded_at": "2026-07-18T02:00:00Z", "runner_output": {"cloud_trigger": "noos_integrator_repair"}},
        {"recorded_at": "2026-07-12T13:50:49Z", "status": "ok", "exit_code": 0, "runner_output": {"cloud_trigger": "http_loop"}},
    ]
    p = sem.derive_completion_provenance(rows, age_fn=_age_fn("2026-07-18T02:06:00Z"))
    r = sem.classify_loop_state(
        dispatch_age_minutes=1.0, dispatch_stale_threshold_minutes=DISPATCH_THRESH,
        completion_age_minutes=6.0, completion_stale_threshold_minutes=COMPLETION_THRESH,
        completion_origin=p["completion_origin"],
        organic_completion_age_minutes=p["organic_completion_age_minutes"],
        repair_completion_age_minutes=p["repair_completion_age_minutes"],
        provenance_metrics=p["metrics"],
    )
    # End to end: repair-sustained fresh row -> DEGRADED, never RUNNING.
    assert r["execution_state"] == sem.DEGRADED_REPAIR_SUSTAINED
    assert r["provenance"]["repair_receipts_since_last_organic"] == 1


def test_empty_rows_derive_is_empty():
    p = sem.derive_completion_provenance([], age_fn=_age_fn("2026-07-18T02:06:00Z"))
    assert p["completion_origin"] is None
    assert p["organic_completion_age_minutes"] is None
