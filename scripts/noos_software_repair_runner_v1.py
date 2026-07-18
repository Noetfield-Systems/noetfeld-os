#!/usr/bin/env python3
"""NOOS Software Repair runner v1 (NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §7).

Drives one repair commission end to end:

  validate job -> load+verify recipe -> verify authorization -> resolve base
  commit -> isolated worktree -> reproduce failure (tests BEFORE) -> classify ->
  plan -> model router proposes -> apply bounded patch -> run tests (AFTER) ->
  <=max_attempts -> final diff + hashes -> verification evidence -> patch bundle
  (+ draft PR when authorized) -> idempotent authoritative record -> receipt.

Never auto-merges, never auto-deploys, never touches forbidden paths. Model
output is untrusted; only real tests passing prove the repair.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_motor_state_machine_v1 as fsm  # noqa: E402
import noos_recipe_registry_v1 as registry  # noqa: E402
import noos_repair_model_adapter_v1 as adapter  # noqa: E402
import noos_repair_engine_v1 as engine  # noqa: E402

RUNWAY = ROOT / "receipts" / "runway"
BUNDLES = ROOT / "dist" / "repair-bundles"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def validate_job(job: dict[str, Any]) -> list[str]:
    errs = []
    for f in ("commission_id", "recipe_id", "repository", "failure"):
        if f not in job:
            errs.append(f"missing field: {f}")
    repo = job.get("repository", {})
    if repo and repo.get("kind") not in ("local_fixture", "github"):
        errs.append("repository.kind must be local_fixture|github")
    fail = job.get("failure", {})
    if fail and not fail.get("test_command"):
        errs.append("failure.test_command required")
    return errs


def _classify_failure(output: str) -> str:
    o = output.lower()
    if "f401" in o or "imported but unused" in o or "ruff" in o:
        return "lint_failure"
    if "assertionerror" in o or "assert" in o:
        return "unit_test_regression"
    if "typeerror" in o or "mypy" in o:
        return "type_error"
    if "keyerror" in o or "indexerror" in o:
        return "data_handling_defect"
    return "test_failure"


def run_repair_job(
    job: dict[str, Any],
    *,
    workdir: Path | None = None,
    ledger: "fsm.MotorLedger | None" = None,
    prefer_model: str = "auto",
    execution_origin: str = fsm.ORIGIN_LOCAL_REFERENCE,
    producer: str = "noos-software-repair-runner-local",
) -> dict[str, Any]:
    now = utc_now()
    ledger = ledger if ledger is not None else fsm.MotorLedger()
    errs = validate_job(job)

    ex, created = ledger.submit(
        task_kind=f"repair:{job.get('recipe_id','?')}",
        payload={"commission": job.get("commission_id"), "repo": job.get("repository"), "failure": job.get("failure")},
        now=now, producer=producer, execution_origin=execution_origin,
    )
    if not created:
        return _finalize(ex, job, now, status="deduplicated", deduplicated=True)

    if errs:
        ex.fail(now=now, error_code="invalid_job", error_summary="; ".join(errs))
        return _finalize(ex, job, now, status="invalid", validation_errors=errs)

    # recipe (reject unknown/unversioned)
    try:
        recipe = registry.load_recipe(job["recipe_id"], version=job.get("recipe_version"))
    except registry.UnknownRecipe as e:
        ex.fail(now=now, error_code="unknown_recipe", error_summary=str(e))
        return _finalize(ex, job, now, status="rejected_recipe", validation_errors=[str(e)])

    repo_spec = job["repository"]
    # authorization
    if repo_spec["kind"] == "github" and not job.get("pr_authorized") and job.get("open_pr"):
        ex.fail(now=now, error_code="unauthorized", error_summary="open_pr requested without pr_authorized")
        return _finalize(ex, job, now, status="unauthorized")

    # isolated worktree (copy of the base)
    tmp = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="noos-repair-job-"))
    repo_dir = tmp / "repo"
    base_src = ROOT / repo_spec["path"] if repo_spec["kind"] == "local_fixture" else None
    if base_src is None or not base_src.is_dir():
        ex.fail(now=now, error_code="repo_unavailable", error_summary=f"base not found: {repo_spec.get('path')}")
        return _finalize(ex, job, now, status="repo_unavailable")
    shutil.copytree(base_src, repo_dir, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))

    test_cmd = job["failure"]["test_command"]
    allowed_files = job["failure"].get("allowed_files") or _default_allowed(repo_dir)

    # plan + FSM to RUNNING
    ex.plan(now=now, dispatch_id=f"dsp_{ex.execution_id[4:12]}").dispatch(now=now)
    ex.claim(now=now, owner="repair-worker-1", lease_ttl_seconds=recipe["limits"]["execution_timeout_seconds"])
    ex.start(now=now)

    # reproduce failure (tests BEFORE) — must actually fail
    before = engine.run_tests(repo_dir, test_cmd, timeout=recipe["limits"]["execution_timeout_seconds"])
    failure_class = _classify_failure(before["output"])
    if before["passed"]:
        ex.fail(now=now, error_code="not_reproducible", error_summary="tests already pass; nothing to repair")
        return _finalize(ex, job, now, status="not_reproducible", recipe=recipe, tests_before=before)

    # repair loop (bounded attempts)
    attempts_log: list[dict[str, Any]] = []
    model_calls: list[dict[str, Any]] = []
    repaired = None
    max_attempts = recipe["limits"]["max_repair_attempts"]
    for attempt in range(1, max_attempts + 1):
        proposal = adapter.propose_repair(
            repo_dir=repo_dir, test_cmd=test_cmd, allowed_files=allowed_files,
            failure_output=before["output"], recipe=recipe, prefer=prefer_model,
            timeout=recipe["limits"]["execution_timeout_seconds"],
        )
        # record the hosted attempt too when the router fell back to deterministic
        if proposal.get("hosted_attempt", {}).get("model_call"):
            model_calls.append(proposal["hosted_attempt"]["model_call"])
        model_calls.append(proposal.get("model_call", {}))
        attempts_log.append({"attempt": attempt, "strategy": proposal.get("strategy"),
                             "ok": proposal.get("ok"), "fell_back_from_hosted": proposal.get("fell_back_from_hosted", False)})
        if proposal.get("ok") and proposal.get("patch"):
            # enforce recipe path + limits on the proposed file
            rel = proposal["file"]
            allowed, why = registry.path_allowed(recipe, rel)
            ok_lim, viol = registry.within_limits(
                recipe, changed_files=1, patch_bytes=len(proposal["patch"]),
                model_calls=len(model_calls), attempts=attempt,
            )
            if allowed and ok_lim:
                repaired = proposal
                break
            attempts_log[-1]["rejected"] = why or ("limits:" + ",".join(viol))

    if not repaired:
        ex.fail(now=now, error_code="unrepaired", error_summary=f"no verified patch within {max_attempts} attempts")
        return _finalize(ex, job, now, status="unrepaired", recipe=recipe,
                         tests_before=before, failure_class=failure_class,
                         attempts=attempts_log, model_calls=model_calls)

    # Apply the ALREADY-VERIFIED full file content directly. The proposal was
    # verified in an isolated copy, so new_content is authoritative; reconstructing
    # from a unified diff (_apply_unified) is fragile for model-generated multi-line
    # patches (this failed on the product-PR GEL CI). Fall back to diff-apply only
    # if new_content is absent.
    if repaired.get("new_content") is not None:
        engine.apply_patch_to_repo(repo_dir, repaired["file"], repaired["new_content"])
    else:
        engine.apply_patch_to_repo(repo_dir, repaired["file"],
                                   _apply_unified(repo_dir / repaired["file"], repaired["patch"]))
    after = engine.run_tests(repo_dir, test_cmd, timeout=recipe["limits"]["execution_timeout_seconds"])

    # patch bundle + hashes
    BUNDLES.mkdir(parents=True, exist_ok=True)
    patch_hash = _sha(repaired["patch"])
    bundle_path = BUNDLES / f"{ex.execution_id}.patch"
    bundle_path.write_text(repaired["patch"], encoding="utf-8")
    report = _customer_report(job, recipe, repaired, before, after, failure_class, ex)
    report_path = BUNDLES / f"{ex.execution_id}.report.md"
    report_path.write_text(report, encoding="utf-8")

    ex.commit_output(now=now, output={"patch_hash": patch_hash, "file": repaired["file"]},
                     artifact_uri=bundle_path.as_uri())
    if after["passed"]:
        ex.complete(now=now)
        status = "repaired"
    else:
        ex.fail(now=now, error_code="verification_failed", error_summary="post-apply tests did not pass")
        status = "verification_failed"

    return _finalize(
        ex, job, now, status=status, recipe=recipe, failure_class=failure_class,
        tests_before=before, tests_after=after, repaired=repaired,
        attempts=attempts_log, model_calls=model_calls,
        patch_path=str(bundle_path), patch_hash=patch_hash, report_path=str(report_path),
        delivery={"patch_bundle": str(bundle_path), "draft_pr": None,
                  "pr_command": _pr_command(job, ex, repaired) if job.get("open_pr") else None},
    )


def _default_allowed(repo_dir: Path) -> list[str]:
    out = []
    for p in repo_dir.rglob("*.py"):
        rel = str(p.relative_to(repo_dir))
        if "/test" not in "/" + rel and not rel.startswith("test"):
            out.append(rel)
    return out


def _apply_unified(target: Path, patch: str) -> str:
    """Apply a single-file unified diff produced by the engine. The engine's diff
    is derived from before/after full content, so we reconstruct 'after' by
    replaying the hunks against the current file content."""
    original = target.read_text(encoding="utf-8")
    orig_lines = original.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    hunk_lines = [ln for ln in patch.splitlines(keepends=True)]
    # simple, robust unified-diff apply for our own single-hunk diffs
    import re as _re
    idx = 0
    while idx < len(hunk_lines) and not hunk_lines[idx].startswith("@@"):
        idx += 1
    while idx < len(hunk_lines):
        m = _re.match(r"@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@", hunk_lines[idx])
        idx += 1
        if not m:
            break
        start = int(m.group(1)) - 1
        out.extend(orig_lines[i:start])
        i = start
        while idx < len(hunk_lines) and not hunk_lines[idx].startswith("@@"):
            ln = hunk_lines[idx]
            idx += 1
            if ln.startswith("+"):
                out.append(ln[1:])
            elif ln.startswith("-"):
                i += 1
            elif ln.startswith(" "):
                out.append(orig_lines[i] if i < len(orig_lines) else ln[1:])
                i += 1
    out.extend(orig_lines[i:])
    return "".join(out)


def _customer_report(job, recipe, repaired, before, after, failure_class, ex) -> str:
    return "\n".join([
        f"# Repair report — {job.get('commission_id')}",
        "",
        f"- Execution ID: `{ex.execution_id}`",
        f"- Recipe: `{recipe['recipe_id']}` v{recipe['recipe_version']}",
        f"- Repository: `{job['repository'].get('path') or job['repository'].get('url')}`",
        f"- Failure class: **{failure_class}**",
        f"- Strategy: `{repaired['strategy']}`",
        f"- File changed: `{repaired['file']}`",
        "",
        "## Verification",
        f"- Tests before: exit={before['exit_code']} (FAILING)",
        f"- Tests after: exit={after['exit_code']} ({'PASSING' if after['passed'] else 'STILL FAILING'})",
        "",
        "## Patch",
        "```diff",
        repaired["patch"].rstrip(),
        "```",
        "",
        "Human approval required before merge. NOOS never auto-merges or deploys.",
    ])


def _pr_command(job, ex, repaired) -> str:
    branch = f"noos/repair/{ex.execution_id}"
    return (f"git checkout -b {branch} && git apply <patch> && git commit -am 'fix: {job.get('commission_id')}' "
            f"&& git push -u origin {branch} && gh pr create --draft --title 'NOOS repair: {job.get('commission_id')}' --body-file <report>")


def _finalize(ex, job, now, *, status, **extra) -> dict[str, Any]:
    rec = ex.to_record()
    receipt = {
        "schema": "software-repair-job-receipt-v1",
        "not_a_verdict": "Repair job receipt. A repaired JOB is a customer outcome, NOT infrastructure liveness. SUBMITTED for independent verification.",
        "canon_version": "FOUNDER_CANON_v1+MACHINE_LOOPS_v1",
        "commission_id": job.get("commission_id"),
        "customer_id": job.get("customer_id"),
        "recipe_id": job.get("recipe_id"),
        "declared_defect_class": job.get("defect_class"),
        "job_status": status,
        "receipt_origin": ex.execution_origin,
        "producer": ex.producer,
        **{k: v for k, v in extra.items() if k not in ("recipe",)},
        "execution": rec,
    }
    RUNWAY.mkdir(parents=True, exist_ok=True)
    rp = RUNWAY / f"software-repair-job-{ex.execution_id}.json"
    rp.write_text(json.dumps(receipt, indent=2, default=str) + "\n", encoding="utf-8")
    return {
        "ok": status == "repaired",
        "job_status": status,
        "execution_id": ex.execution_id,
        "state": ex.state,
        "receipt_path": str(rp),
        **{k: v for k, v in extra.items() if k in ("patch_path", "patch_hash", "report_path", "delivery", "failure_class", "tests_before", "tests_after")},
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--job", type=Path, required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    job = json.loads(a.job.read_text(encoding="utf-8"))
    res = run_repair_job(job)
    print(json.dumps(res, indent=2, default=str) if a.json else f"{res['job_status']} {res['execution_id']}")
    raise SystemExit(0 if res["ok"] else 1)
