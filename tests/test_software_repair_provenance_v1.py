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
