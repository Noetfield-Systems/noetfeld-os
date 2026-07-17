"""Negative-transition tests for the Motor registry v1.2 validator.

Each documented invariant must FAIL CLOSED. v1.0 accepted all of these; the
suite exists so a regression that re-loosens the validator turns red in CI
instead of silently shipping a paper invariant. Run via pytest, or standalone:
    python3 motor/registry/tests/test_motor_registry_invariants.py

Isolation note: several invariants (R2/I5a/I5b/I6) can be tripped incidentally
by a fixture that violates a *different* invariant first. The tests named after
a single invariant assert that invariant's own error code appears (e.g.
"(R2)"), so a regression isolated to that check is actually caught.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys

import pytest

pytest.importorskip("jsonschema", reason="motor registry validator needs jsonschema")
pytest.importorskip("yaml", reason="motor registry validator needs PyYAML")

REG = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REG))

import validate as V  # noqa: E402

RV, JV = V.build_validators(REG)
GOOD_JOB = json.loads((REG / "jobs/MOTOR-WEB-001.json").read_text())
import yaml  # noqa: E402

RECIPES = {}
for _f in sorted((REG / "recipes").glob("*.yaml")):
    _d = yaml.safe_load(_f.read_text())
    RECIPES[_d["recipe_id"]] = _d


def _schema_bad(job) -> bool:
    return len(V.schema_errors(job, JV, "t")) > 0


def _semantics_bad(job) -> bool:
    if V.schema_errors(job, JV, "t"):
        return True  # schema rejects it first — still fail-closed
    return len(V.check_job_semantics(job, RECIPES, "t")) > 0


# ---- baseline: the shipped archive is valid --------------------------------
def test_00_shipped_archive_is_valid():
    failures, counts = V.validate_all(REG)
    assert failures == [], failures
    assert counts["jobs"] >= 1 and counts["recipes"] == 5


# ---- I1: PROVEN/FAILED require evidence_ref --------------------------------
def test_I1_proven_without_evidence_ref_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["dispatch"] = {"state": "PROVEN"}  # drop evidence_ref
    assert _schema_bad(j)


def test_I1_failed_without_evidence_ref_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["execution"] = {"state": "FAILED", "reason": "x"}  # no evidence_ref
    assert _schema_bad(j)


# ---- I2: BLOCKED/FAILED/DIVERGED/UNPROVEN require reason --------------------
def test_I2_blocked_without_reason_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["authority"] = {"state": "BLOCKED"}  # no reason
    assert _schema_bad(j)


def test_I2_unproven_without_reason_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["verification"] = {"state": "UNPROVEN"}  # no reason
    assert _schema_bad(j)


def test_I2_diverged_without_reason_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["outcome"] = {"state": "DIVERGED"}  # no reason
    assert _schema_bad(j)


# ---- I3: invalid datetime rejected (FormatChecker) -------------------------
def test_I3_invalid_datetime_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["trigger"]["occurred_at"] = "not-a-date"
    assert _schema_bad(j)


# ---- I4: recipe_version must match the recipe ------------------------------
def test_I4_recipe_version_mismatch_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["recipe_version"] = "9.9.9"
    assert _semantics_bad(j)


# ---- R1: unknown recipe rejected -------------------------------------------
def test_R1_unknown_recipe_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["recipe_id"] = "NF-MOTOR-DOES-NOT-EXIST-001"
    assert _semantics_bad(j)


# ---- R2: outcome PROVEN requires promotion PROVEN --------------------------
def test_R2_outcome_proven_promotion_not_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["promotion"] = {"state": "NOT_STARTED"}
    j["states"]["outcome"] = {"state": "PROVEN", "evidence_ref": "probe"}
    assert _semantics_bad(j)


def test_R2_isolated_outcome_proven_promotion_not_started():
    """Isolated to R2: outcome carries observation+attribution PROVEN and an
    external PASS (so I5b/I6 are satisfied) while promotion is NOT_STARTED —
    only R2 can fire. Guards against R2 being silently redundant with I5b."""
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["promotion"] = {"state": "NOT_STARTED"}
    j["states"]["outcome"] = {
        "state": "PROVEN", "evidence_ref": "probe",
        "observation": {"state": "PROVEN", "evidence_ref": "marker"},
        "attribution": {"state": "PROVEN", "evidence_ref": "sha match"},
    }
    j["verification_results"] = [
        {"check": "unit_and_site_tests", "decision": "PASS", "reason": "green", "evidence": "ci", "external": True}
    ]
    errs = V.check_job_semantics(j, RECIPES, "t")
    assert any("(R2)" in e for e in errs), errs


# ---- I5a: promotion PROVEN needs source+runtime proven ---------------------
def test_I5a_promotion_proven_but_runtime_unproven_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["promotion"] = {
        "state": "PROVEN", "evidence_ref": "merge+deploy",
        "source": {"state": "PROVEN", "evidence_ref": "merge sha"},
        "runtime": {"state": "UNPROVEN", "reason": "deploy not confirmed"},
    }
    assert _semantics_bad(j)


# ---- I5b: outcome PROVEN needs observation+attribution proven --------------
def test_I5b_outcome_observed_but_unattributed_rejected():
    """Isolated to I5b: promotion is fully PROVEN (source+runtime), so I5a is
    satisfied; only attribution UNPROVEN can trip the check, and we assert the
    (I5b) code specifically so a regression narrowed to that comparison is
    caught (not masked by an incidental I5a failure)."""
    j = _fully_proven_job()
    j["states"]["outcome"] = {
        "state": "PROVEN", "evidence_ref": "probe",
        "observation": {"state": "PROVEN", "evidence_ref": "page shows marker"},
        "attribution": {"state": "UNPROVEN", "reason": "deployed sha unknown"},
    }
    errs = V.check_job_semantics(j, RECIPES, "t")
    assert any("(I5b)" in e for e in errs), errs


# ---- I6: external proof required but no external PASS -----------------------
def test_I6_outcome_proven_without_external_pass_rejected():
    """Isolated to I6: start from a fully-proven job (I5a/I5b satisfied) and
    strip the external PASS rows, so only I6 can fire. Assert the (I6) code."""
    j = _fully_proven_job()
    j["verification_results"] = [
        {"check": "unit_and_site_tests", "decision": "FAIL", "reason": "red", "evidence": "ci", "external": True}
    ]
    errs = V.check_job_semantics(j, RECIPES, "t")
    assert any("(I6)" in e for e in errs), errs


def test_I6_verification_proven_with_non_recipe_check_name_rejected():
    """The verification-PROVEN branch must, like the outcome branch, reject a
    PASS row whose check name the recipe never declared (closes the asymmetry
    where verification PROVEN accepted any PASS name)."""
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["verification"] = {"state": "PROVEN", "evidence_ref": "some receipt"}
    j["verification_results"] = [
        {"check": "totally_unrelated_check", "decision": "PASS", "reason": "x", "evidence": "y", "external": False}
    ]
    errs = V.check_job_semantics(j, RECIPES, "t")
    assert any("(I6)" in e for e in errs), errs


# ---- I7: SHA / artifact identity -------------------------------------------
def test_I7_production_sha_set_without_runtime_proven_rejected():
    j = copy.deepcopy(GOOD_JOB)
    # Force the premise explicitly instead of relying on the live record's
    # promotion state (which legitimately progressed to PROVEN).
    j["states"]["promotion"] = {"state": "DIVERGED", "reason": "runtime not proven"}
    j["artifacts"]["production_sha"] = "c" * 40
    assert _semantics_bad(j)


def test_I7_production_sha_not_full_hex_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["promotion"] = {
        "state": "PROVEN", "evidence_ref": "deploy",
        "source": {"state": "PROVEN", "evidence_ref": "m"},
        "runtime": {"state": "PROVEN", "evidence_ref": "d"},
    }
    j["artifacts"]["production_sha"] = "abc123"  # too short
    assert _semantics_bad(j)


def test_I7_execution_proven_without_candidate_sha_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["artifacts"]["candidate_sha"] = ""
    assert _semantics_bad(j)


# ---- I8: timestamp ordering ------------------------------------------------
def test_I8_executing_before_created_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["timestamps"] = {"created_at": "2026-07-10T00:00:00Z", "executing_at": "2026-07-09T00:00:00Z"}
    assert _semantics_bad(j)


def test_I8_outcome_observed_too_soon_after_promotion_rejected():
    j = copy.deepcopy(GOOD_JOB)
    # make a fully-proven external job, then violate the >=60s rule
    j["states"]["authority"] = {"state": "PROVEN", "evidence_ref": "merge"}
    j["states"]["verification"] = {"state": "PROVEN", "evidence_ref": "ci"}
    j["states"]["promotion"] = {
        "state": "PROVEN", "evidence_ref": "deploy",
        "source": {"state": "PROVEN", "evidence_ref": "m"},
        "runtime": {"state": "PROVEN", "evidence_ref": "d"},
    }
    j["artifacts"]["production_sha"] = "d" * 40
    j["states"]["outcome"] = {
        "state": "PROVEN", "evidence_ref": "probe",
        "observation": {"state": "PROVEN", "evidence_ref": "marker"},
        "attribution": {"state": "PROVEN", "evidence_ref": "sha match"},
    }
    j["timestamps"] = {
        "created_at": "2026-07-10T00:00:00Z",
        "promoted_at": "2026-07-16T10:00:00Z",
        "outcome_observed_at": "2026-07-16T10:00:30Z",  # only 30s later
    }
    assert _semantics_bad(j)


# ---- I9: RECEIPT_COMPLETE cannot be asserted over incomplete truth ---------
def test_I9_receipt_complete_while_promotion_not_started_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["lifecycle_status"] = "RECEIPT_COMPLETE"
    assert _semantics_bad(j)


def test_I9_receipt_complete_with_placeholder_cost_rejected():
    j = copy.deepcopy(GOOD_JOB)
    # fully prove the chain but leave cost.metered false
    j["states"]["authority"] = {"state": "PROVEN", "evidence_ref": "merge"}
    j["states"]["verification"] = {"state": "PROVEN", "evidence_ref": "ci"}
    j["states"]["promotion"] = {
        "state": "PROVEN", "evidence_ref": "deploy",
        "source": {"state": "PROVEN", "evidence_ref": "m"},
        "runtime": {"state": "PROVEN", "evidence_ref": "d"},
    }
    j["artifacts"]["production_sha"] = "e" * 40
    j["states"]["outcome"] = {
        "state": "PROVEN", "evidence_ref": "probe",
        "observation": {"state": "PROVEN", "evidence_ref": "marker"},
        "attribution": {"state": "PROVEN", "evidence_ref": "sha match"},
    }
    j["verification_results"] = [
        {"check": "prod", "decision": "PASS", "reason": "live", "evidence": "probe", "external": True}
    ]
    j["timestamps"] = {
        "created_at": "2026-07-10T00:00:00Z",
        "promoted_at": "2026-07-16T10:00:00Z",
        "outcome_observed_at": "2026-07-16T10:05:00Z",
    }
    j["receipt_hash"] = "sha256:deadbeef"
    j["cost"] = {"total_usd": 0, "metered": False, "value_class": "proof_asset"}  # placeholder
    j["lifecycle_status"] = "RECEIPT_COMPLETE"
    assert _semantics_bad(j)


def _fully_proven_job():
    """A genuinely complete WEB-PUBLISH job that satisfies every v1.2 rule."""
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["authority"] = {"state": "PROVEN", "evidence_ref": "founder merge of PR #115"}
    j["states"]["verification"] = {"state": "PROVEN", "evidence_ref": "ci run defb5506"}
    j["states"]["evidence"] = {"state": "PROVEN", "evidence_ref": "this receipt, readable by observer"}
    j["states"]["promotion"] = {
        "state": "PROVEN", "evidence_ref": "merge + deploy receipt",
        "source": {"state": "PROVEN", "evidence_ref": "merge sha abc"},
        "runtime": {"state": "PROVEN", "evidence_ref": "cloudflare deployment id + sha"},
    }
    j["artifacts"]["production_sha"] = "f" * 40
    j["states"]["outcome"] = {
        "state": "PROVEN", "evidence_ref": "live probe",
        "observation": {"state": "PROVEN", "evidence_ref": "page shows AI Motor marker"},
        "attribution": {"state": "PROVEN", "evidence_ref": "deployed sha == candidate"},
    }
    j["verification_results"] = [
        {"check": "unit_and_site_tests", "decision": "PASS", "reason": "green", "evidence": "ci", "external": True},
        {"check": "render_review", "decision": "PASS", "reason": "reviewed", "evidence": "screens", "external": True},
    ]
    j["timestamps"] = {
        "created_at": "2026-07-10T00:00:00Z",
        "executing_at": "2026-07-10T00:00:00Z",
        "verified_at": "2026-07-14T00:00:00Z",
        "promoted_at": "2026-07-16T10:00:00Z",
        "outcome_observed_at": "2026-07-16T10:05:00Z",
    }
    j["receipt_hash"] = "sha256:" + "a" * 64
    j["cost"] = {"total_usd": 1.23, "metered": True, "value_class": "proof_asset"}
    j["approval"] = {"required": True, "approved_by": "founder", "approval_artifact": "merge SHA " + "f" * 40}
    j["lifecycle_status"] = "RECEIPT_COMPLETE"
    return j


def test_I9_receipt_complete_fully_proven_accepted():
    """The positive mirror: a genuinely complete job IS allowed."""
    j = _fully_proven_job()
    assert not V.schema_errors(j, JV, "t")
    assert V.check_job_semantics(j, RECIPES, "t") == []


# ================= red-team regression tests (v1.1 gaps, now closed) ========
def test_RT_whitespace_evidence_ref_rejected():
    for blank in (" ", "\t", "\n", "​", "﻿", " "):
        j = copy.deepcopy(GOOD_JOB)
        j["states"]["dispatch"] = {"state": "PROVEN", "evidence_ref": blank}
        assert _semantics_bad(j), f"blank {blank!r} evidence_ref slipped through"


def test_RT_whitespace_reason_rejected():
    for blank in (" ", "\t", "​", "⁠"):
        j = copy.deepcopy(GOOD_JOB)
        j["states"]["authority"] = {"state": "UNPROVEN", "reason": blank}
        assert _semantics_bad(j), f"blank {blank!r} reason slipped through"


def test_RT_whitespace_in_substate_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["promotion"]["source"] = {"state": "PROVEN", "evidence_ref": "   "}
    assert _semantics_bad(j)


def test_RT_promotion_proven_split_omitted_on_external_rejected():
    """Headline gap: promotion PROVEN with source/runtime OMITTED on the
    external WEB-PUBLISH recipe must fail (I5a)."""
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["promotion"] = {"state": "PROVEN", "evidence_ref": "merged"}  # no split
    j["artifacts"]["production_sha"] = "a" * 40
    assert _semantics_bad(j)


def test_RT_outcome_proven_split_omitted_on_external_rejected():
    j = _fully_proven_job()
    j["states"]["outcome"] = {"state": "PROVEN", "evidence_ref": "probe"}  # no split
    assert V.check_job_semantics(j, RECIPES, "t") != []


def test_RT_receipt_complete_evidence_not_proven_rejected():
    j = _fully_proven_job()
    j["states"]["evidence"] = {"state": "STALE", "reason": "old"}
    assert _semantics_bad(j)


def test_RT_datetime_trailing_newline_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["trigger"]["occurred_at"] = "2026-07-10T00:00:00Z\n"
    assert _schema_bad(j)


def test_RT_lowercase_z_ordering_still_caught():
    j = copy.deepcopy(GOOD_JOB)
    j["timestamps"] = {"created_at": "2026-07-10T00:00:00Z", "executing_at": "2026-07-09T00:00:00z"}
    assert _semantics_bad(j)  # lowercase z must parse so ordering fires


def test_RT_production_sha_trailing_newline_rejected():
    j = _fully_proven_job()
    j["artifacts"]["production_sha"] = "a" * 40 + "\n"
    # schema (pattern) or semantic fullmatch must catch the 41-char value
    assert _schema_bad(j) or V.check_job_semantics(j, RECIPES, "t") != []


def test_RT_outcome_not_applicable_on_external_receipt_rejected():
    j = _fully_proven_job()
    j["states"]["outcome"] = {"state": "NOT_APPLICABLE"}
    assert _semantics_bad(j)


def test_RT_candidate_sha_junk_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["artifacts"]["candidate_sha"] = "not-a-sha-at-all!!!"  # execution is PROVEN
    assert _semantics_bad(j)


def test_RT_verification_proven_without_pass_row_rejected():
    j = _fully_proven_job()
    j["verification_results"] = [
        {"check": "unit_and_site_tests", "decision": "FAIL", "reason": "red", "evidence": "ci", "external": True}
    ]
    assert _semantics_bad(j)


def test_RT_external_pass_name_not_recipe_declared_rejected():
    j = _fully_proven_job()
    j["verification_results"] = [
        {"check": "totally_made_up", "decision": "PASS", "reason": "x", "evidence": "y", "external": True}
    ]
    assert _semantics_bad(j)


def test_RT_cost_over_budget_rejected():
    j = _fully_proven_job()
    j["cost"] = {"total_usd": 999999, "metered": True, "value_class": "proof_asset"}
    assert _semantics_bad(j)


def test_RT_trigger_type_mismatch_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["trigger"]["type"] = "schedule"  # recipe is founder_instruction
    assert _semantics_bad(j)


def test_RT_receipt_hash_junk_rejected():
    j = _fully_proven_job()
    j["receipt_hash"] = "lol"
    assert _semantics_bad(j)


# ===== second red-team round (invisible unicode / ordering / date-only) =====
def test_RT2_invisible_format_chars_evidence_rejected():
    """Cf/Mn/So invisible chars must not count as evidence (category rule,
    not a denylist). Covers the class beyond the original zero-width few."""
    for blank in ("­", "⁣", "⁡", "؜", "͏", "⠀", "﻿"):
        j = copy.deepcopy(GOOD_JOB)
        j["states"]["dispatch"] = {"state": "PROVEN", "evidence_ref": blank}
        assert _semantics_bad(j), f"invisible {blank!r} slipped through as evidence"


def test_RT2_invisible_approval_artifact_at_receipt_complete_rejected():
    j = _fully_proven_job()
    j["approval"]["approval_artifact"] = "­"  # invisible "approval"
    assert _semantics_bad(j)


def test_RT2_non_adjacent_timestamp_ordering_rejected():
    """created_at after promoted_at with executing/verified omitted must fail
    (monotonic over present stages, not just adjacent pairs)."""
    j = copy.deepcopy(GOOD_JOB)
    j["timestamps"] = {
        "created_at": "2026-08-01T00:00:00Z",
        "promoted_at": "2026-07-12T00:00:00Z",
        "outcome_observed_at": "2026-07-12T00:02:00Z",
    }
    assert _semantics_bad(j)


def test_RT2_date_only_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["trigger"]["occurred_at"] = "2026-07-12"  # no time component
    assert _schema_bad(j)


def test_RT2_timezoneless_datetime_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["trigger"]["occurred_at"] = "2026-07-12T00:00:00"  # no offset
    assert _schema_bad(j)


def test_RT2_dangling_schedule_cron_on_non_schedule_recipe_rejected():
    r = copy.deepcopy(RECIPES["NF-MOTOR-WEB-PUBLISH-001"])
    r["trigger"] = dict(r["trigger"])
    r["trigger"]["schedule_cron"] = "0 6 * * 1"  # founder_instruction recipe
    assert V.schema_errors(r, RV, "t") or V.check_recipe_semantics(r, "t")


def test_RT2_recovery_proven_without_external_pair_rejected():
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["recovery"] = {"state": "PROVEN", "evidence_ref": "restarted, seems fine"}
    j["verification_results"] = [
        {"check": "x", "decision": "PASS", "reason": "r", "evidence": "e", "external": False}
    ]
    assert _semantics_bad(j)


def test_RT2_control_fully_green_still_accepted():
    """Guard: hardening must not reject a genuinely complete job."""
    assert V.check_job_semantics(_fully_proven_job(), RECIPES, "t") == []


def test_I9_receipt_complete_missing_recipe_required_field_rejected():
    """Recipe-declared receipt.required_fields are enforced: drop the approval
    artifact from the otherwise-complete job and it must fail closed."""
    j = copy.deepcopy(GOOD_JOB)
    j["states"]["authority"] = {"state": "PROVEN", "evidence_ref": "merge"}
    j["states"]["verification"] = {"state": "PROVEN", "evidence_ref": "ci"}
    j["states"]["promotion"] = {
        "state": "PROVEN", "evidence_ref": "deploy",
        "source": {"state": "PROVEN", "evidence_ref": "m"},
        "runtime": {"state": "PROVEN", "evidence_ref": "d"},
    }
    j["artifacts"]["production_sha"] = "f" * 40
    j["states"]["outcome"] = {
        "state": "PROVEN", "evidence_ref": "probe",
        "observation": {"state": "PROVEN", "evidence_ref": "marker"},
        "attribution": {"state": "PROVEN", "evidence_ref": "sha match"},
    }
    j["verification_results"] = [
        {"check": "prod", "decision": "PASS", "reason": "live", "evidence": "probe", "external": True}
    ]
    j["timestamps"] = {
        "created_at": "2026-07-10T00:00:00Z",
        "promoted_at": "2026-07-16T10:00:00Z",
        "outcome_observed_at": "2026-07-16T10:05:00Z",
    }
    j["receipt_hash"] = "sha256:deadbeef"
    j["cost"] = {"total_usd": 1.23, "metered": True, "value_class": "proof_asset"}
    j["approval"] = {"required": True, "approved_by": "founder", "approval_artifact": ""}  # missing
    j["lifecycle_status"] = "RECEIPT_COMPLETE"
    assert _semantics_bad(j)


# ---- U: job_id / idempotency_key uniqueness across job files ---------------
def _registry_copy_with_extra_job(extra_job: dict, filename: str):
    """Copy the real registry into a temp dir (schema+recipes+jobs), drop in one
    extra job file, and run the whole validator over it. Uses tempfile (not the
    tmp_path fixture) so the standalone __main__ runner still works."""
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        reg = pathlib.Path(td) / "reg"
        shutil.copytree(REG, reg, ignore=shutil.ignore_patterns("__pycache__", "tests"))
        (reg / "jobs" / filename).write_text(json.dumps(extra_job))
        return V.validate_all(reg)[0]


def test_U_duplicate_idempotency_key_rejected():
    dup = copy.deepcopy(GOOD_JOB)
    dup["job_id"] = "MOTOR-WEB-002"  # distinct id, SAME idempotency_key
    failures = _registry_copy_with_extra_job(dup, "MOTOR-WEB-002.json")
    assert any("duplicate idempotency_key" in x for x in failures), failures


def test_U_duplicate_job_id_rejected():
    dup = copy.deepcopy(GOOD_JOB)
    dup["idempotency_key"] = "distinct-key-so-only-the-job-id-collides"  # SAME job_id
    failures = _registry_copy_with_extra_job(dup, "MOTOR-WEB-DUP.json")
    assert any("duplicate job_id" in x for x in failures), failures


def test_U_empty_idempotency_key_rejected_by_schema():
    """An empty idempotency_key must fail schema (minLength:1) so U never
    receives an empty key to silently skip."""
    j = copy.deepcopy(GOOD_JOB)
    j["idempotency_key"] = ""
    assert _schema_bad(j)


def test_U_whitespace_idempotency_key_flagged_not_skipped():
    """A whitespace-only key passes minLength but must still be flagged by the
    validator's U backstop rather than silently skipped for dedup."""
    whitespace_job = copy.deepcopy(GOOD_JOB)
    whitespace_job["idempotency_key"] = "   "
    failures = _registry_copy_with_extra_job(whitespace_job, "MOTOR-WEB-WS.json")
    assert any("cannot dedup" in x for x in failures), failures


if __name__ == "__main__":
    import traceback
    fns = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in fns:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception:
            failed += 1
            print(f"FAIL  {name}")
            traceback.print_exc()
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
