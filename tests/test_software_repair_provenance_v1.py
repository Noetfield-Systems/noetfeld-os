"""NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §2 — production-liveness provenance gate.

Corrects the earlier defect (local-reference cycles labelled receipt_origin=organic).
Proves that local_reference / test / repair / replay / manual / migration /
legacy_unknown can NEVER establish PRODUCTION RUNNING_CONFIRMED, and that only an
allowlisted deployed producer on the canonical plane with a genuine organic
completion can. Also proves customer-job success and infra liveness are separate.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_observability_semantics_v1 as sem  # noqa: E402


def _prod(**over):
    base = dict(
        receipt_origin="organic",
        producer="railway:noos-loop-runner",
        execution_plane="railway:noos-loop-runner",
        dispatch_correlated=True,
        lifecycle_valid=True,
        terminal_evidence_valid=True,
        freshness_within_slo=True,
    )
    base.update(over)
    return sem.production_running_confirmed(**base)


# ---- the happy production case ---------------------------------------------
def test_canonical_organic_producer_confirms():
    r = _prod()
    assert r["production_running_confirmed"] is True
    assert r["execution_state"] == sem.RUNNING_CONFIRMED
    assert r["failed_predicates"] == []


# ---- §2 required proofs 1-3: non-production origins can NEVER confirm --------
def test_local_reference_cannot_confirm_production():
    r = _prod(receipt_origin="local_reference", producer="noos-motor-local-executor-v1",
              execution_plane="local_reference")
    assert r["production_running_confirmed"] is False
    assert r["execution_state"] != sem.RUNNING_CONFIRMED
    assert r["blocked_reason"] == "non_production_origin:local_reference"


def test_test_origin_cannot_confirm_production():
    r = _prod(receipt_origin="test", producer="pytest", execution_plane="ci")
    assert r["production_running_confirmed"] is False
    assert r["blocked_reason"] == "non_production_origin:test"


def test_repair_origin_cannot_confirm_production():
    r = _prod(receipt_origin="noos_integrator_repair")
    assert r["production_running_confirmed"] is False
    assert r["normalized_origin"] == sem.ORIGIN_REPAIR


def test_manual_workflow_dispatch_cannot_confirm_production():
    # A GHA factory-autorun via workflow_dispatch stamps manual origin — must NOT confirm.
    r = _prod(receipt_origin="workflow_dispatch", producer="gha:noos-factory-autorun",
              execution_plane="github-actions")
    assert r["production_running_confirmed"] is False
    assert r["normalized_origin"] == sem.ORIGIN_MANUAL


def test_replay_migration_legacy_cannot_confirm_production():
    for o in ("replay", "migration", "legacy_unknown"):
        r = _prod(receipt_origin=o)
        assert r["production_running_confirmed"] is False, o


# ---- §2 proof 4: only allowlisted deployed producer + canonical plane -------
def test_organic_but_non_allowlisted_producer_cannot_confirm():
    r = _prod(producer="some-random-worker")
    assert r["production_running_confirmed"] is False
    assert "producer_allowlisted" in r["failed_predicates"]


def test_organic_but_non_canonical_plane_cannot_confirm():
    r = _prod(execution_plane="staging")
    assert r["production_running_confirmed"] is False
    assert "execution_plane_canonical" in r["failed_predicates"]


def test_organic_but_dispatch_not_correlated_cannot_confirm():
    r = _prod(dispatch_correlated=False)
    assert r["production_running_confirmed"] is False
    assert "dispatch_correlated" in r["failed_predicates"]


def test_organic_but_stale_cannot_confirm():
    r = _prod(freshness_within_slo=False)
    assert r["production_running_confirmed"] is False
    assert "freshness_within_slo" in r["failed_predicates"]


# ---- PROPERTY: no non-production origin ever confirms, across all combos ----
def test_property_no_non_production_origin_ever_confirms():
    for origin in sem.NON_PRODUCTION_LIVENESS_ORIGINS:
        for prod in list(sem.PRODUCTION_ORGANIC_PRODUCERS) + ["x"]:
            for plane in list(sem.CANONICAL_EXECUTION_PLANES) + ["x"]:
                r = sem.production_running_confirmed(
                    receipt_origin=origin, producer=prod, execution_plane=plane,
                    dispatch_correlated=True, lifecycle_valid=True,
                    terminal_evidence_valid=True, freshness_within_slo=True,
                )
                assert r["production_running_confirmed"] is False, (origin, prod, plane)


# ---- §2 proof 5: customer-job success != infra liveness ---------------------
def test_customer_job_success_is_separate_from_infra_liveness():
    # A local_reference execution can be a fully successful CUSTOMER job
    # (COMPLETED, output present) while NOT establishing production liveness.
    r = _prod(receipt_origin="local_reference", producer="noos-motor-local-executor-v1",
              execution_plane="local_reference", terminal_evidence_valid=True)
    assert r["production_running_confirmed"] is False   # infra liveness: NO
    # terminal_evidence_valid=True models "the customer job produced output" —
    # success of the job is orthogonal to deployed-system health.
    assert r["checks"]["terminal_evidence_valid"] is True


# ---- NF-NOOS-PROVENANCE-CLASSIFIER-CORRECTION §5 — LIVE-PROBE regressions ----
# These exercise the REAL live projection (autorun_status_v1.probe_supabase_noos_loop)
# with the Supabase reads mocked, so the wired behaviour is what is tested.
import pytest  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

import autorun_status_v1 as autorun  # noqa: E402


def _iso(minutes_ago):
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat()


def _row(trigger, *, status="ok", exit_code=0, minutes_ago=2, cycle=1):
    return {
        "cycle_number": cycle, "status": status, "recorded_at": _iso(minutes_ago),
        "runner_output": {"cloud_trigger": trigger}, "exit_code": exit_code,
        "factory_id": "loop-inbox",
    }


def _probe(monkeypatch, rows, dispatch_min_ago=1):
    monkeypatch.setattr(autorun, "supabase_profile_config", lambda *a, **k: {"url": "x", "key": "y"})
    monkeypatch.setattr(autorun, "supabase_get", lambda cfg, table, query=None: {"ok": True, "rows": rows})
    monkeypatch.setattr(autorun, "fetch_dispatch_heartbeat",
                        lambda cfg, loop_id: {"ok": True, "last_fired_at": _iso(dispatch_min_ago), "interval_minutes": 5})
    wf = {"probe": {"supabase_profile": "noetfield", "supabase_table": "noetfield_factory_cycle_runs",
                    "factory_id": "loop-inbox"}, "run_command": "x"}
    return autorun.probe_supabase_noos_loop(wf, {}, 30.0)


# §5.1 fresh repair row while the organic completion FAILED -> repair masking
def test_liveprobe_fresh_repair_failed_organic(monkeypatch):
    r = _probe(monkeypatch, [
        _row("noos_integrator_repair", status="ok", minutes_ago=2, cycle=9),
        _row("http_loop", status="degraded", exit_code=1, minutes_ago=3, cycle=8),
    ])
    assert r["execution_state"] == sem.DEGRADED_REPAIR_SUSTAINED
    assert r["status"] == "BLOCKED_WITH_REASON"
    assert r["route"] == sem.ROUTE_ORGANIC_PRODUCER_ESCALATION


# §5.2 fresh local_reference is separate non-production evidence, NOT repair
def test_liveprobe_local_reference_is_unproven_not_repair(monkeypatch):
    r = _probe(monkeypatch, [_row("local_reference")])
    assert r["execution_state"] == sem.COMPLETION_UNPROVEN
    assert r["execution_state"] != sem.DEGRADED_REPAIR_SUSTAINED
    assert r["status"] == "BLOCKED_WITH_REASON"


# §5.3 manual / test / replay are separate non-production evidence, NOT repair
@pytest.mark.parametrize("trigger", ["workflow_dispatch", "ci_test_run", "nightly_replay"])
def test_liveprobe_manual_test_replay_unproven(monkeypatch, trigger):
    r = _probe(monkeypatch, [_row(trigger)])
    assert r["execution_state"] == sem.COMPLETION_UNPROVEN
    assert r["execution_state"] != sem.DEGRADED_REPAIR_SUSTAINED


# §5.4 mislabeled organic (claims http_loop but exited non-zero) must NOT confirm
def test_liveprobe_mislabeled_organic_not_running(monkeypatch):
    r = _probe(monkeypatch, [_row("http_loop", status="ok", exit_code=1)])
    assert r["execution_state"] != sem.RUNNING_CONFIRMED
    assert r["execution_state"] == sem.COMPLETION_UNPROVEN
    assert r["status"] == "BLOCKED_WITH_REASON"


# §5.5 a genuine successful organic completion DOES confirm
def test_liveprobe_valid_organic_confirms(monkeypatch):
    r = _probe(monkeypatch, [_row("http_loop", status="ok", exit_code=0)])
    assert r["execution_state"] == sem.RUNNING_CONFIRMED
    assert r["status"] == "RUNNING"
    assert r["route"] is None


# §3 the new states map into the canonical status vocabulary
def test_status_vocabulary_mapping():
    m = autorun._EXEC_STATE_TO_STATUS
    assert m[sem.DEGRADED_REPAIR_SUSTAINED] == "BLOCKED_WITH_REASON"
    assert m[sem.COMPLETION_UNPROVEN] == "BLOCKED_WITH_REASON"
    assert m[sem.EVIDENCE_INCONSISTENT] == "BLOCKED_WITH_REASON"
    assert m[sem.STOPPED_OR_IDLE] == "IDLE_NO_WORK"


# §4 the full production gate is DECLARED_NOT_WIRED in the live projection
def test_production_gate_declared_not_wired():
    w = sem.production_gate_wiring_status()
    assert w["status"] == "DECLARED_NOT_WIRED"
    assert w["production_running_confirmed_wired_into_live_projection"] is False
    assert set(w["not_wired_predicates"]) >= {"producer_allowlisted", "dispatch_correlated", "lifecycle_valid"}
