"""Tests for the noos-motor-route-owner-v1 machine owner (Track D wiring).

Network-free: everything exercised here is the pure/deterministic layer —
routing-row refusal, idempotency (L13), the recovery gate (PROVEN only from an
external PASS before/after pair AND an actually-performed repair), the
mutation-surface audit, and validator round-trips for BOTH the all-PASS and
the failure/escalation record shapes (adversarial-review regressions).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import noos_motor_route_owner_v1 as owner  # noqa: E402


def _routing_row(**overrides):
    row = {
        "schema": "noos-motor-routing-row-v1",
        "route": "receipt_writer_completion_evidence_repair",
        "noos_state": "DISPATCHING_COMPLETION_UNPROVEN",
        "loop_id": "inbox",
        "factory_id": "loop-inbox",
        "diagnosis_id": "NOOS-DIAG-20260717T081300Z-inbox",
        "diagnosis_receipt": "receipts/incident/some-diagnosis.json",
        "created_at": "2026-07-17T08:13:00Z",
    }
    row.update(overrides)
    return row


# ---- routing-row validation (fail closed) ----------------------------------

def test_valid_routing_row_passes():
    assert owner.validate_routing_row(_routing_row()) == []


def test_wrong_route_refused():
    problems = owner.validate_routing_row(_routing_row(route="execution_reconcile_self_heal"))
    assert any("only consumes" in p for p in problems)


def test_wrong_state_refused():
    problems = owner.validate_routing_row(_routing_row(noos_state="LOOP_EXECUTION_STALE"))
    assert problems  # both the direct check and the semantics cross-check fire
    assert any("semantics cross-check" in p for p in problems)


def test_execution_mutating_state_never_reaches_this_owner():
    # LOOP_EXECUTION_STALE maps to the execution-reconcile route; even a row
    # that lies about its route is refused by the semantics cross-check.
    problems = owner.validate_routing_row(
        _routing_row(noos_state="LOOP_EXECUTION_STALE", route="receipt_writer_completion_evidence_repair")
    )
    assert any("semantics cross-check" in p for p in problems)


def test_missing_fields_refused():
    problems = owner.validate_routing_row(_routing_row(diagnosis_id=""))
    assert any("diagnosis_id" in p for p in problems)


def test_wrong_schema_refused():
    problems = owner.validate_routing_row(_routing_row(schema="something-else"))
    assert any("schema" in p for p in problems)


# ---- idempotency (L13) ------------------------------------------------------

def test_idempotency_key_renders_recipe_dedupe_key():
    key = owner.render_idempotency_key("inbox", "NOOS-DIAG-X")
    assert key == "receipt-repair:inbox:NOOS-DIAG-X"


def test_find_existing_job_matches_same_key(tmp_path):
    jobs = tmp_path / "jobs"
    jobs.mkdir()
    (jobs / "MOTOR-RWREPAIR-001.json").write_text(
        json.dumps({"job_id": "MOTOR-RWREPAIR-001", "idempotency_key": "receipt-repair:inbox:D1"})
    )
    assert owner.find_existing_job(jobs, "receipt-repair:inbox:D1") is not None
    assert owner.find_existing_job(jobs, "receipt-repair:inbox:D2") is None


def test_find_existing_job_ignores_malformed_files(tmp_path):
    jobs = tmp_path / "jobs"
    jobs.mkdir()
    (jobs / "broken.json").write_text("{not json")
    assert owner.find_existing_job(jobs, "receipt-repair:inbox:D1") is None


def test_count_jobs_with_key_tolerates_malformed_files(tmp_path):
    # adversarial-review regression: the complete-phase scan must not crash on
    # a malformed job file in motor/registry/jobs.
    jobs = tmp_path / "jobs"
    jobs.mkdir()
    (jobs / "broken.json").write_text("{not json")
    (jobs / "a.json").write_text(json.dumps({"idempotency_key": "K"}))
    (jobs / "b.json").write_text(json.dumps({"idempotency_key": "K"}))
    assert owner.count_jobs_with_key(jobs, "K") == 2


def test_job_file_key_reads_and_tolerates(tmp_path):
    p = tmp_path / "j.json"
    p.write_text(json.dumps({"idempotency_key": "K1"}))
    assert owner.job_file_key(p) == "K1"
    p.write_text("{broken")
    assert owner.job_file_key(p) is None


# ---- BEFORE capture ---------------------------------------------------------

def test_capture_before_extracts_staleness_last_good_and_provenance():
    diagnosis = {
        "diagnosis_id": "NOOS-DIAG-X",
        "execution_state": "DISPATCHING_COMPLETION_UNPROVEN",
        "observed_at": "2026-07-17T08:13:00Z",
        "signals": {
            "completion": {
                "last_recorded_at": "2026-07-17T07:00:45+00:00",
                "age_minutes": 72.3,
                "stale_threshold_minutes": 30.0,
                "last_row_cloud_trigger": "noos_integrator_repair",
            },
            "dispatch": {"last_fired_at": "2026-07-17T08:10:51+00:00", "age_minutes": 2.2},
        },
    }
    before = owner.capture_before(diagnosis, "receipts/incident/x.json")
    assert before["last_good_completion_recorded_at"] == "2026-07-17T07:00:45+00:00"
    assert before["completion_staleness_age_minutes"] == 72.3
    assert before["captured_from"] == "receipts/incident/x.json"
    # adversarial-review regression: BEFORE provenance must not be dropped —
    # a repair-written "last good" row is a weaker baseline and stays visible.
    assert before["last_good_completion_cloud_trigger"] == "noos_integrator_repair"


# ---- verification rows + recovery gate --------------------------------------

def _before():
    return {
        "captured_from": "receipts/incident/x.json",
        "diagnosis_id": "NOOS-DIAG-X",
        "last_good_completion_recorded_at": "2026-07-17T07:00:45+00:00",
        "last_good_completion_cloud_trigger": None,
        "completion_staleness_age_minutes": 72.3,
        "completion_stale_threshold_minutes": 30.0,
    }


def _verification(after, violations=None, count=1, jobs=1):
    return owner.build_verification_results(
        before=_before(),
        after=after,
        completion_stale_threshold_minutes=30.0,
        action_violations=violations or [],
        repair_row_count={"ok": True, "count": count},
        jobs_with_key=jobs,
        checked_at="2026-07-17T08:30:00Z",
    )


IDEM_KEY = "receipt-repair:inbox:NOOS-DIAG-20260717T081300Z-inbox"
REPAIR_DONE = {"ok": True, "written": True, "cycle_number": 1330}
AFTER_FRESH_REPAIR_ROW = {
    "ok": True,
    "recorded_at": "2026-07-17T08:25:00+00:00",
    "age_minutes": 5.0,
    "cloud_trigger": "noos_motor_receipt_writer_repair",
    "repair_key": IDEM_KEY,
}
AFTER_FRESH_ORGANIC = {
    "ok": True,
    "recorded_at": "2026-07-17T08:25:00+00:00",
    "age_minutes": 5.0,
    "cloud_trigger": "gha_schedule",
    "repair_key": None,
}


def _recovery(results, repair=REPAIR_DONE, after=AFTER_FRESH_REPAIR_ROW):
    return owner.recovery_state_from(
        results, "receipts/motor/run.json", repair=repair, after=after, idempotency_key=IDEM_KEY
    )


def test_fresh_after_with_performed_repair_yields_recovery_proven():
    results = _verification(AFTER_FRESH_REPAIR_ROW)
    pair = next(v for v in results if v["check"] == "before_after_pair")
    assert pair["decision"] == "PASS" and pair["external"] is True
    recovery = _recovery(results)
    assert recovery["state"] == "PROVEN"
    assert "evidence_ref" in recovery
    # attribution names the repair row explicitly (repair_key match)
    assert "repair_key match" in recovery["reason"]


def test_recovery_attribution_discloses_organic_after_row():
    results = _verification(AFTER_FRESH_ORGANIC)
    recovery = _recovery(results, after=AFTER_FRESH_ORGANIC)
    assert recovery["state"] == "PROVEN"
    assert "not this job's write" in recovery["reason"]


def test_dry_run_observed_recovery_stays_unproven():
    # adversarial-review regression (critical): a dry-run that merely OBSERVES
    # fresh evidence must not claim recovery — honest attribution beats green.
    results = _verification(AFTER_FRESH_ORGANIC)
    recovery = _recovery(results, repair={"ok": True, "written": False, "dry_run": True}, after=AFTER_FRESH_ORGANIC)
    assert recovery["state"] == "UNPROVEN"
    assert "not attributable to this job" in recovery["reason"]


def test_failed_repair_with_fresh_after_stays_unproven():
    results = _verification(AFTER_FRESH_ORGANIC)
    recovery = _recovery(results, repair={"ok": False, "written": False, "reason": "sink_write_failed_http_500"}, after=AFTER_FRESH_ORGANIC)
    assert recovery["state"] == "UNPROVEN"


def test_stale_after_fails_pair_and_recovery_stays_unproven():
    after = {"ok": True, "recorded_at": "2026-07-17T07:00:45+00:00", "age_minutes": 90.0, "cloud_trigger": None}
    results = _verification(after)
    pair = next(v for v in results if v["check"] == "before_after_pair")
    assert pair["decision"] == "FAIL"
    recovery = _recovery(results, after=after)
    assert recovery["state"] == "UNPROVEN"
    assert "reason" in recovery  # I2: UNPROVEN requires reason


def test_failed_observer_read_fails_pair():
    after = {"ok": False, "reason": "observer_query_failed_http_500"}
    results = _verification(after)
    pair = next(v for v in results if v["check"] == "before_after_pair")
    assert pair["decision"] == "FAIL"
    assert _recovery(results, after=after)["state"] == "UNPROVEN"


def test_internal_pass_rows_never_prove_recovery():
    # Even if no_execution_mutation and idempotency PASS, a failed external
    # pair keeps recovery UNPROVEN — internal checks cannot substitute (L4).
    after = {"ok": True, "recorded_at": "old", "age_minutes": 90.0}
    results = _verification(after)
    internal_passes = [v for v in results if v["decision"] == "PASS" and not v.get("external")]
    assert internal_passes  # the other two checks did pass
    assert _recovery(results, after=after)["state"] == "UNPROVEN"


def test_duplicate_sink_rows_fail_idempotency_check():
    results = _verification(AFTER_FRESH_REPAIR_ROW, count=2)
    idem = next(v for v in results if v["check"] == "idempotency")
    assert idem["decision"] == "FAIL"
    assert "L13" in idem["reason"]


def test_duplicate_jobs_fail_idempotency_check():
    results = _verification(AFTER_FRESH_REPAIR_ROW, jobs=2)
    idem = next(v for v in results if v["check"] == "idempotency")
    assert idem["decision"] == "FAIL"


def test_pair_reason_discloses_after_row_provenance():
    results = _verification(AFTER_FRESH_REPAIR_ROW)
    pair = next(v for v in results if v["check"] == "before_after_pair")
    assert "repair-written" in pair["reason"]
    results2 = _verification(AFTER_FRESH_ORGANIC)
    pair2 = next(v for v in results2 if v["check"] == "before_after_pair")
    assert "organic" in pair2["reason"]


# ---- mutation-surface audit --------------------------------------------------

def test_action_log_within_policy_passes_no_execution_mutation():
    log = owner.ActionLog()
    log.record("routing_row_consumed", "read_only")
    log.record("sink_keyed_repair_write", "evidence_sink")
    log.record("sandbox_created", "sandbox_filesystem")
    assert log.violations() == []
    results = _verification(AFTER_FRESH_REPAIR_ROW, violations=log.violations())
    check = next(v for v in results if v["check"] == "no_execution_mutation")
    assert check["decision"] == "PASS"


def test_runtime_mutation_is_flagged_as_violation():
    log = owner.ActionLog()
    log.record("restart_production_runtime", "runtime")
    assert len(log.violations()) == 1
    results = _verification(AFTER_FRESH_REPAIR_ROW, violations=log.violations())
    check = next(v for v in results if v["check"] == "no_execution_mutation")
    assert check["decision"] == "FAIL"


# ---- job record assembly ------------------------------------------------------

def _record(verification_results=None, repair=REPAIR_DONE, after=AFTER_FRESH_REPAIR_ROW):
    return owner.build_job_record(
        job_id="MOTOR-RWREPAIR-001",
        routing_row=_routing_row(),
        idempotency_key=IDEM_KEY,
        before=_before(),
        sandbox={"sandbox_id": "sbx-x", "type": "git_worktree", "worktree": "/tmp/x", "head_sha": "a" * 40},
        smoke={"ok": True},
        repair=repair,
        run_log_ref="receipts/motor/run.json",
        routing_row_ref="receipts/motor/row.json",
        created_at="2026-07-17T08:20:00Z",
        executing_at="2026-07-17T08:21:00Z",
        baseline_sha="b" * 40,
        verification_results=verification_results,
        after=after,
        verified_at="2026-07-17T08:30:00Z" if verification_results is not None else None,
        destroyed_at="2026-07-17T08:22:00Z",
        worker_started_at="2026-07-17T08:20:00Z",
        worker_ended_at="2026-07-17T08:30:00Z" if verification_results is not None else None,
    )


def test_intermediate_record_is_repairing_and_claims_nothing():
    record = _record()
    assert record["lifecycle_status"] == "REPAIRING"
    assert record["states"]["recovery"]["state"] == "IN_PROGRESS"
    assert record["states"]["verification"]["state"] == "NOT_STARTED"
    assert record["verification_results"] == []
    # adversarial-review regression: intermediate notes must not reference
    # verification evidence that does not exist yet.
    assert "INTERMEDIATE" in record["notes"]
    assert "3 recipe-declared checks" not in record["notes"]


def test_final_record_with_pass_pair_is_post_verifying_never_receipt_complete():
    record = _record(_verification(AFTER_FRESH_REPAIR_ROW))
    assert record["lifecycle_status"] == "POST_VERIFYING"  # organic-cron post-checks pending
    assert record["lifecycle_status"] != "RECEIPT_COMPLETE"
    assert record["states"]["recovery"]["state"] == "PROVEN"
    assert record["states"]["promotion"]["state"] == "NOT_APPLICABLE"
    assert record["artifacts"]["production_sha"] == ""  # I7: runtime never touched
    assert record["trigger"]["type"] == "event"  # T: matches recipe trigger


def test_final_record_with_failed_pair_is_triage_and_unproven_with_reason():
    after = {"ok": True, "recorded_at": "old", "age_minutes": 90.0}
    record = _record(_verification(after), after=after)
    assert record["lifecycle_status"] == "TRIAGE_REQUIRED"
    assert record["states"]["recovery"]["state"] == "UNPROVEN"
    assert record["states"]["verification"]["state"] == "FAILED"
    # adversarial-review regression (critical): FAILED requires a meaningful
    # reason (I2) or the frozen validator rejects the honest-failure receipt.
    assert record["states"]["verification"].get("reason")


def test_any_failed_check_routes_to_triage_not_post_verifying():
    # adversarial-review regression: pair PASS + idempotency FAIL must NOT
    # roll up as a healthy POST_VERIFYING job (on_check_fail=escalate).
    results = _verification(AFTER_FRESH_REPAIR_ROW, jobs=2)
    record = _record(results)
    assert record["lifecycle_status"] == "TRIAGE_REQUIRED"
    assert record["states"]["verification"]["state"] == "FAILED"
    assert "idempotency" in record["states"]["verification"]["reason"]


def test_escalation_never_restarts():
    esc = owner.build_escalation(_routing_row(), _before(), {"ok": True, "age_minutes": 90.0}, "receipts/motor/run.json")
    assert "did NOT" in esc["requested_decision"] and "restart" in esc["requested_decision"]
    assert esc["schema"] == "noos-founder-decision-escalation-v1"


def test_escalation_names_failed_checks():
    esc = owner.build_escalation(
        _routing_row(), _before(), {"ok": True}, "receipts/motor/run.json",
        failed_checks=["no_execution_mutation"],
    )
    assert "no_execution_mutation" in esc["finding"]


# ---- validator round-trips against the frozen registry validator -------------

def _validate_with_record(tmp_path, record):
    import importlib
    import shutil

    registry_src = Path(__file__).resolve().parents[1] / "motor/registry"
    root = tmp_path / "registry"
    shutil.copytree(registry_src, root, ignore=shutil.ignore_patterns("__pycache__", "tests"))
    (root / "jobs" / "MOTOR-RWREPAIR-001.json").write_text(json.dumps(record, indent=2))
    sys.path.insert(0, str(root))
    try:
        validate = importlib.import_module("validate")
        importlib.reload(validate)
        return validate.validate_all(root)
    finally:
        sys.path.remove(str(root))


def test_final_pass_record_passes_motor_registry_validator(tmp_path):
    record = _record(_verification(AFTER_FRESH_REPAIR_ROW))
    failures, counts = _validate_with_record(tmp_path, record)
    assert failures == [], failures
    assert counts["jobs"] == 2  # MOTOR-WEB-001 + MOTOR-RWREPAIR-001


def test_failure_path_record_also_passes_motor_registry_validator(tmp_path):
    # adversarial-review regression (critical): the honest-failure/escalation
    # record the recipe designs for (on_check_fail=escalate) must itself be a
    # valid receipt — a failure the validator rejects is a silent failure.
    after = {"ok": True, "recorded_at": "2026-07-17T07:00:45+00:00", "age_minutes": 90.0, "cloud_trigger": None}
    record = _record(_verification(after), after=after)
    assert record["lifecycle_status"] == "TRIAGE_REQUIRED"
    failures, _ = _validate_with_record(tmp_path, record)
    assert failures == [], failures


def test_mixed_failure_record_passes_motor_registry_validator(tmp_path):
    # pair PASS + idempotency FAIL -> TRIAGE_REQUIRED, still schema-valid.
    record = _record(_verification(AFTER_FRESH_REPAIR_ROW, jobs=2))
    failures, _ = _validate_with_record(tmp_path, record)
    assert failures == [], failures
