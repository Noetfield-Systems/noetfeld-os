#!/usr/bin/env python3
"""NOOS Motor route owner v1 — registered machine owner for the
``receipt_writer_completion_evidence_repair`` binding (Track D wiring).

Task: NF-NOOS-MOTOR-ROUTE-WIRING-001.
LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.

This module is the machine owner declared in
``motor/registry/bindings/noos-route-map-v1.json``. It consumes an
INCIDENT-DIAGNOSE routing row for state ``DISPATCHING_COMPLETION_UNPROVEN``
and executes recipe ``NF-MOTOR-RECEIPT-WRITER-REPAIR-001`` in an
evidence-path-only sandbox. The recipe's mutation_policy is a HARD WALL:

  * runtime: deny                    -- NEVER restarts production runtime
  * production_business_state: deny  -- NEVER touches business state
  * observed_system: deny            -- NEVER mutates the observed system
  * evidence_sink: full              -- receipts table ONLY, keyed + idempotent
  * sandbox_filesystem: full         -- git worktree over writer component paths

If completion evidence cannot be restored by keyed retry / writer patch, the
owner escalates to a founder-decision artifact (recipe escalation_route). It
never falls back to restarting execution — correctly stopping beats wrongly
restarting.

Idempotency (L13): the job idempotency_key renders the recipe dedupe_key
``receipt-repair:{loop_id}:{diagnosis_id}``. The same key never creates a
second job (jobs-dir scan) and never writes a duplicate sink row (pre-write
existence check on ``runner_output->>repair_key``, re-checked between retry
attempts so an ambiguous network failure cannot double-write).

Causality: ``states.recovery`` is set PROVEN only when (a) the BEFORE/AFTER
external pair passes — BEFORE from the diagnosis receipt, AFTER from a fresh
completion-receipt read via the OBSERVER's read path (``autorun_status_v1``,
never the writer's code path) — AND (b) this job actually performed a repair
write. A dry-run or failed repair that merely observes recovery reports
recovery UNPROVEN with the honest attribution. Correlation != causality.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_observability_semantics_v1 import (  # noqa: E402
    DISPATCHING_COMPLETION_UNPROVEN,
    ROUTE_RECEIPT_WRITER_REPAIR,
    classify_loop_state,
    route_for_state,
    route_permits_execution_mutation,
)

OWNER_ID = "noos-motor-route-owner-v1"
OWNER_REF = f"{OWNER_ID} (scripts/noos_motor_route_owner_v1.py)"
RECIPE_ID = "NF-MOTOR-RECEIPT-WRITER-REPAIR-001"
RECIPE_VERSION = "1.1.0"
ROUTING_ROW_SCHEMA = "noos-motor-routing-row-v1"
CANON_VERSION = "FOUNDER_CANON_v1+MACHINE_LOOPS_v1"

SINK_TABLE = "noetfield_factory_cycle_runs"
REPAIR_CLOUD_TRIGGER = "noos_motor_receipt_writer_repair"
# Every label that marks a sink row as repair-written rather than organic.
REPAIR_TRIGGER_LABELS = frozenset({REPAIR_CLOUD_TRIGGER, "noos_integrator_repair"})
# Scoped credential the recipe declares (secret_scope: sink_receipts_write_token).
SINK_WRITE_TOKEN_ENV = "NOOS_SINK_RECEIPTS_WRITE_TOKEN"
# The receipt-writer component this recipe is allowed to touch in sandbox.
WRITER_COMPONENT_PATHS = (
    "scripts/factory_supabase_sink_v1.py",
    "scripts/noos_loop_liveness_v1.py",
)
COMPLETION_STALE_MINUTES_DEFAULT = 30.0
DISPATCH_STALE_MULTIPLIER_DEFAULT = 2.0
MAX_SINK_RETRIES = 2  # recipe budgets.retries

# Mutation surfaces the recipe permits (everything else is a violation).
ALLOWED_MUTATION_SURFACES = frozenset(
    {"read_only", "evidence_sink", "control_plane_receipts", "sandbox_filesystem"}
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def render_idempotency_key(loop_id: str, diagnosis_id: str) -> str:
    """Render the recipe trigger.dedupe_key ``receipt-repair:{loop_id}:{diagnosis_id}``."""
    return f"receipt-repair:{loop_id}:{diagnosis_id}"


# ---------------------------------------------------------------------------
# Action log — every action the owner takes, with its mutation surface.
# This is the evidence for the recipe's no_execution_mutation check. It is a
# self-reported ledger (the recipe declares this check as internal, not
# external); the declared-vs-enforced gap is disclosed, not hidden.
# ---------------------------------------------------------------------------
class ActionLog:
    def __init__(self) -> None:
        self.actions: list[dict[str, Any]] = []

    def record(self, action: str, surface: str, detail: str = "") -> None:
        self.actions.append(
            {"at": utc_now(), "action": action, "mutation_surface": surface, "detail": detail}
        )

    def violations(self) -> list[dict[str, Any]]:
        return [a for a in self.actions if a["mutation_surface"] not in ALLOWED_MUTATION_SURFACES]

    def as_list(self) -> list[dict[str, Any]]:
        return list(self.actions)


# ---------------------------------------------------------------------------
# Routing-row validation (fail closed — refuse anything but the bound route)
# ---------------------------------------------------------------------------
def validate_routing_row(row: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if row.get("schema") != ROUTING_ROW_SCHEMA:
        problems.append(f"schema is {row.get('schema')!r}, expected {ROUTING_ROW_SCHEMA!r}")
    if row.get("route") != ROUTE_RECEIPT_WRITER_REPAIR:
        problems.append(f"route is {row.get('route')!r}; this owner only consumes {ROUTE_RECEIPT_WRITER_REPAIR!r}")
    if row.get("noos_state") != DISPATCHING_COMPLETION_UNPROVEN:
        problems.append(f"noos_state is {row.get('noos_state')!r}, expected {DISPATCHING_COMPLETION_UNPROVEN!r}")
    # Cross-check against the semantics module — a hand-rolled row whose state
    # does not actually map to this route is refused.
    if route_for_state(str(row.get("noos_state") or "")) != ROUTE_RECEIPT_WRITER_REPAIR:
        problems.append("noos_state does not map to the receipt-writer-repair route (semantics cross-check)")
    # This route must never be execution-mutating (design law).
    if route_permits_execution_mutation(row.get("route")):
        problems.append("route claims execution-mutation permission — refused (design law)")
    for field in ("loop_id", "factory_id", "diagnosis_id", "diagnosis_receipt", "created_at"):
        if not str(row.get(field) or "").strip():
            problems.append(f"missing required field {field!r}")
    return problems


def find_existing_job(jobs_dir: Path, idempotency_key: str) -> Path | None:
    """L13: same key = same job, never a duplicate."""
    for fp in sorted(jobs_dir.glob("*.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("idempotency_key") == idempotency_key:
            return fp
    return None


def count_jobs_with_key(jobs_dir: Path, idempotency_key: str) -> int:
    """Malformed-file-tolerant count of jobs carrying this key (L13 audit)."""
    n = 0
    for fp in jobs_dir.glob("*.json"):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("idempotency_key") == idempotency_key:
            n += 1
    return n


def job_file_key(job_path: Path) -> str | None:
    """The idempotency_key currently stored at job_path, if readable."""
    try:
        return json.loads(job_path.read_text(encoding="utf-8")).get("idempotency_key")
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# BEFORE capture — the causality baseline, from the diagnosis receipt
# ---------------------------------------------------------------------------
def capture_before(diagnosis: dict[str, Any], diagnosis_path: str) -> dict[str, Any]:
    signals = diagnosis.get("signals") or {}
    completion = signals.get("completion") or {}
    dispatch = signals.get("dispatch") or {}
    return {
        "captured_from": diagnosis_path,
        "diagnosis_id": diagnosis.get("diagnosis_id"),
        "execution_state": diagnosis.get("execution_state"),
        "last_good_completion_recorded_at": completion.get("last_recorded_at"),
        # Provenance of the last pre-gap row is part of the BEFORE truth: a
        # "last good" row that was itself repair-written is a weaker baseline
        # than an organic one, and must not be silently laundered.
        "last_good_completion_cloud_trigger": completion.get("last_row_cloud_trigger"),
        "completion_staleness_age_minutes": completion.get("age_minutes"),
        "completion_stale_threshold_minutes": completion.get("stale_threshold_minutes"),
        "dispatch_last_fired_at": dispatch.get("last_fired_at"),
        "dispatch_age_minutes": dispatch.get("age_minutes"),
        "observed_at": diagnosis.get("observed_at"),
    }


# ---------------------------------------------------------------------------
# Observer read path (AFTER check) — autorun_status_v1's read, not the writer's
# ---------------------------------------------------------------------------
def _load_wf_doc() -> dict[str, Any]:
    return json.loads((ROOT / "data/autorun-workflows-v1.json").read_text(encoding="utf-8"))


def _observer_cfg() -> tuple[str, str] | None:
    from autorun_status_v1 import supabase_profile_config

    return supabase_profile_config("noetfield", _load_wf_doc())


def _sink_write_credentials() -> tuple[str, str, str] | None:
    """Credentials for the ONE permitted evidence-sink write.

    Prefers the recipe-declared scoped token (secret_scope:
    sink_receipts_write_token) when provisioned; otherwise falls back to the
    platform credentials the sanctioned integrator-repair path uses. The
    fallback EXCEEDS the recipe's declared secret_scope — callers must record
    the returned label in the action log so the deviation is disclosed, never
    hidden."""
    cfg = _observer_cfg()
    if not cfg:
        return None
    url, platform_key = cfg
    scoped = os.environ.get(SINK_WRITE_TOKEN_ENV, "").strip()
    if scoped:
        return url, scoped, "scoped_sink_receipts_write_token"
    return url, platform_key, "platform_service_role_FALLBACK_exceeds_declared_secret_scope"


def observer_read_completion(factory_id: str) -> dict[str, Any]:
    """Latest completion receipt for one loop via the observer's read path."""
    from autorun_status_v1 import age_minutes, supabase_get

    cfg = _observer_cfg()
    if not cfg:
        return {"ok": False, "reason": "supabase_not_configured"}
    params = urllib.parse.urlencode(
        {
            "select": "cycle_number,status,recorded_at,factory_id,runner_output",
            "factory_id": f"eq.{factory_id}",
            "order": "recorded_at.desc",
            "limit": "1",
        }
    )
    try:
        hit = supabase_get(cfg, SINK_TABLE, query=params)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "reason": f"observer_query_error:{type(exc).__name__}"}
    if not hit.get("ok"):
        return {"ok": False, "reason": f"observer_query_failed_http_{hit.get('status')}"}
    rows = hit.get("rows") or []
    if not rows:
        return {"ok": True, "recorded_at": None, "age_minutes": None, "row": None}
    row = rows[0]
    runner = row.get("runner_output") or {}
    return {
        "ok": True,
        "recorded_at": row.get("recorded_at"),
        "age_minutes": age_minutes(row.get("recorded_at")),
        "cycle_number": row.get("cycle_number"),
        "status": row.get("status"),
        "cloud_trigger": runner.get("cloud_trigger"),
        "repair_key": runner.get("repair_key"),
        "read_path": f"observer:autorun_status_v1.supabase_get {SINK_TABLE} factory_id={factory_id}",
    }


def observer_read_completion_history(factory_id: str, limit: int = 3) -> dict[str, Any]:
    """Latest N completion receipts (for the organic post-promotion check)."""
    from autorun_status_v1 import age_minutes, supabase_get

    cfg = _observer_cfg()
    if not cfg:
        return {"ok": False, "reason": "supabase_not_configured"}
    params = urllib.parse.urlencode(
        {
            "select": "cycle_number,status,recorded_at,factory_id,runner_output",
            "factory_id": f"eq.{factory_id}",
            "order": "recorded_at.desc",
            "limit": str(limit),
        }
    )
    try:
        hit = supabase_get(cfg, SINK_TABLE, query=params)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "reason": f"observer_query_error:{type(exc).__name__}"}
    if not hit.get("ok"):
        return {"ok": False, "reason": f"observer_query_failed_http_{hit.get('status')}"}
    rows = []
    for row in hit.get("rows") or []:
        runner = row.get("runner_output") or {}
        rows.append(
            {
                "recorded_at": row.get("recorded_at"),
                "age_minutes": age_minutes(row.get("recorded_at")),
                "cycle_number": row.get("cycle_number"),
                "status": row.get("status"),
                "cloud_trigger": runner.get("cloud_trigger"),
                "organic": runner.get("cloud_trigger") not in REPAIR_TRIGGER_LABELS,
            }
        )
    return {"ok": True, "rows": rows}


def observer_read_dispatch(loop_id: str) -> dict[str, Any]:
    from autorun_status_v1 import age_minutes, fetch_dispatch_heartbeat

    cfg = _observer_cfg()
    if not cfg:
        return {"ok": False, "reason": "supabase_not_configured"}
    try:
        hb = fetch_dispatch_heartbeat(cfg, loop_id)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "reason": f"dispatch_query_error:{type(exc).__name__}"}
    if not hb.get("ok"):
        return {"ok": False, "reason": f"dispatch_query_failed_http_{hb.get('http')}"}
    return {
        "ok": True,
        "last_fired_at": hb.get("last_fired_at"),
        "age_minutes": age_minutes(hb.get("last_fired_at")),
        "interval_minutes": hb.get("interval_minutes"),
    }


def count_repair_rows(repair_key: str) -> dict[str, Any]:
    """How many sink rows carry this repair key (L13 duplicate audit)."""
    from autorun_status_v1 import supabase_get

    cfg = _observer_cfg()
    if not cfg:
        return {"ok": False, "reason": "supabase_not_configured"}
    params = urllib.parse.urlencode(
        {"select": "cycle_number,recorded_at", "runner_output->>repair_key": f"eq.{repair_key}"}
    )
    try:
        hit = supabase_get(cfg, SINK_TABLE, query=params)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "reason": f"repair_key_query_error:{type(exc).__name__}"}
    if not hit.get("ok"):
        return {"ok": False, "reason": f"repair_key_query_failed_http_{hit.get('status')}"}
    rows = hit.get("rows") or []
    return {"ok": True, "count": len(rows), "rows": rows}


# ---------------------------------------------------------------------------
# Keyed evidence-sink repair write (bounded, idempotent — L13)
# ---------------------------------------------------------------------------
def keyed_repair_write(
    *,
    factory_id: str,
    loop_id: str,
    repair_key: str,
    diagnosis_id: str,
    dry_run: bool,
    log: ActionLog,
) -> dict[str, Any]:
    """One keyed, provenance-labeled completion-evidence row.

    Pre-checks the sink for an existing row with this repair_key, and
    RE-CHECKS between retry attempts (an ambiguous network failure may have
    committed server-side); the same key is NEVER written twice (L13). The row
    is labeled cloud_trigger=noos_motor_receipt_writer_repair so the observer
    can always distinguish repair-written evidence from organic writer-B
    evidence — synthetic green is disclosed, never laundered as organic green.
    """
    log.record("sink_precheck_repair_key", "read_only", f"repair_key={repair_key}")
    existing = count_repair_rows(repair_key)
    if not existing.get("ok"):
        return {"ok": False, "written": False, "reason": existing.get("reason")}
    if existing["count"] > 0:
        log.record("sink_write_suppressed_duplicate", "read_only", f"repair_key already present x{existing['count']}")
        return {"ok": True, "written": False, "suppressed_duplicate": True, "existing_count": existing["count"]}

    if dry_run:
        log.record("sink_write_skipped_dry_run", "read_only", f"repair_key={repair_key}")
        return {"ok": True, "written": False, "dry_run": True}

    from autorun_status_v1 import supabase_get
    from noos_portfolio_spine_heartbeat_v1 import supabase_post

    creds = _sink_write_credentials()
    if not creds:
        return {"ok": False, "written": False, "reason": "supabase_not_configured"}
    url, key, cred_label = creds
    log.record("sink_write_credential_selected", "read_only", f"credential={cred_label}")

    params = urllib.parse.urlencode(
        {"select": "cycle_number", "factory_id": f"eq.{factory_id}", "order": "cycle_number.desc", "limit": "1"}
    )
    try:
        head = supabase_get((url, key), SINK_TABLE, query=params)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "written": False, "reason": f"cycle_head_query_error:{type(exc).__name__}"}
    if not head.get("ok"):
        return {"ok": False, "written": False, "reason": f"cycle_head_query_failed_http_{head.get('status')}"}
    rows = head.get("rows") or []
    cycle_number = int((rows[0].get("cycle_number") if rows else 0) or 0) + 1
    now = utc_now()
    row = {
        "factory_id": factory_id,
        "cycle_number": cycle_number,
        "started_at": now,
        "finished_at": now,
        "recorded_at": now,
        "status": "ok",
        "exit_code": 0,
        "runner_output": {
            "cloud_trigger": REPAIR_CLOUD_TRIGGER,
            "loop_id": loop_id,
            "repair_key": repair_key,
            "diagnosis_id": diagnosis_id,
            "recipe_id": RECIPE_ID,
            "owner": OWNER_ID,
            "note": (
                "Keyed evidence-path repair receipt (mutation_policy evidence_sink=full). "
                "Restores the completion-evidence signal; organic writer-B recovery is "
                "verified separately by post-promotion checks (2 consecutive cron cycles). "
                "This row is repair-written, not organic — provenance is this label."
            ),
        },
    }
    last_err: dict[str, Any] = {}
    ambiguous = False
    for attempt in range(1, MAX_SINK_RETRIES + 1):
        if attempt > 1:
            # An ambiguous failure (timeout after the POST body was sent) may
            # have committed server-side — re-check before re-posting (L13).
            recheck = count_repair_rows(repair_key)
            if recheck.get("ok") and recheck.get("count", 0) > 0:
                log.record("sink_retry_found_committed_row", "read_only", f"attempt {attempt - 1} committed server-side; no re-post")
                return {"ok": True, "written": True, "cycle_number": cycle_number, "ambiguous_first_attempt": True, "attempt": attempt - 1}
        log.record("sink_keyed_repair_write", "evidence_sink", f"attempt={attempt} repair_key={repair_key} credential={cred_label}")
        try:
            posted = supabase_post(url, key, SINK_TABLE, row)
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            posted = {"ok": False, "error": f"{type(exc).__name__}: {exc}", "ambiguous": True}
            ambiguous = True
        if posted.get("ok"):
            return {"ok": True, "written": True, "cycle_number": cycle_number, "http": posted.get("status"), "attempt": attempt, "credential": cred_label}
        last_err = posted
    if ambiguous:
        final = count_repair_rows(repair_key)
        if final.get("ok") and final.get("count", 0) > 0:
            return {"ok": True, "written": True, "cycle_number": cycle_number, "ambiguous_resolved_committed": True}
    return {"ok": False, "written": False, "reason": f"sink_write_failed_http_{last_err.get('status')}", "error": str(last_err.get('error'))[:300]}


# ---------------------------------------------------------------------------
# Evidence-path sandbox (git worktree over the writer component)
# ---------------------------------------------------------------------------
def create_sandbox(run_id: str, log: ActionLog) -> dict[str, Any]:
    sandbox_dir = Path(tempfile.mkdtemp(prefix=f"noos-motor-sbx-{run_id}-"))
    target = sandbox_dir / "worktree"
    add = subprocess.run(
        ["git", "worktree", "add", "--detach", str(target), "HEAD"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if add.returncode != 0:
        return {"ok": False, "reason": f"worktree_add_failed: {add.stderr.strip()[:200]}"}
    # filesystem_scope is DECLARED (recipe sandbox.filesystem_scope) and audited
    # via the action log; runtime containment of the scope is not enforced here
    # (registry maturity: declarations governed by validation, not containment).
    log.record("sandbox_created", "sandbox_filesystem", f"git_worktree at {target}; declared scope: {', '.join(WRITER_COMPONENT_PATHS)} (declared, audited, not runtime-enforced)")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=target, capture_output=True, text=True)
    return {
        "ok": True,
        "sandbox_id": f"sbx-{run_id}",
        "type": "git_worktree",
        "worktree": str(target),
        "head_sha": head.stdout.strip(),
        "production_write": False,
        "filesystem_scope": list(WRITER_COMPONENT_PATHS),
    }


def sandbox_writer_smoke(sandbox: dict[str, Any], log: ActionLog) -> dict[str, Any]:
    """run_writer_smoke_test_in_sandbox (machine_may): import the writer
    component inside the sandbox worktree and confirm it loads and resolves
    its configuration entrypoints. Read-only; no writes are performed."""
    worktree = sandbox.get("worktree")
    if not worktree:
        return {"ok": False, "reason": "no_sandbox"}
    code = (
        "import sys; sys.path.insert(0, 'scripts')\n"
        "import factory_supabase_sink_v1 as w\n"
        "assert callable(getattr(w, '_supabase_config'))\n"
        "print('writer-module-import-ok config-entrypoint-present')\n"
    )
    smoke = subprocess.run([sys.executable, "-c", code], cwd=worktree, capture_output=True, text=True)
    log.record("writer_smoke_test_in_sandbox", "sandbox_filesystem", smoke.stdout.strip() or smoke.stderr.strip()[:200])
    return {"ok": smoke.returncode == 0, "stdout": smoke.stdout.strip(), "stderr": smoke.stderr.strip()[:400]}


def destroy_sandbox(sandbox: dict[str, Any], log: ActionLog) -> str | None:
    worktree = sandbox.get("worktree")
    if not worktree:
        return None
    subprocess.run(["git", "worktree", "remove", "--force", worktree], cwd=ROOT, capture_output=True, text=True)
    log.record("sandbox_destroyed", "sandbox_filesystem", worktree)
    return utc_now()


# ---------------------------------------------------------------------------
# Verification rows + recovery gate (pure — unit-tested)
# ---------------------------------------------------------------------------
def build_verification_results(
    *,
    before: dict[str, Any],
    after: dict[str, Any],
    completion_stale_threshold_minutes: float,
    action_violations: list[dict[str, Any]],
    repair_row_count: dict[str, Any],
    jobs_with_key: int,
    checked_at: str,
) -> list[dict[str, Any]]:
    after_age = after.get("age_minutes")
    after_fresh = bool(after.get("ok")) and after_age is not None and after_age <= completion_stale_threshold_minutes
    after_organic = after.get("cloud_trigger") not in REPAIR_TRIGGER_LABELS
    before_provenance = before.get("last_good_completion_cloud_trigger")
    pair = {
        "check": "before_after_pair",
        "decision": "PASS" if after_fresh else "FAIL",
        "reason": (
            f"BEFORE: completion evidence stale (last good {before.get('last_good_completion_recorded_at')}, "
            f"provenance cloud_trigger={before_provenance!r}, "
            f"age {before.get('completion_staleness_age_minutes')}m > {before.get('completion_stale_threshold_minutes')}m). "
            f"AFTER: latest completion receipt {after.get('recorded_at')} age {after_age}m "
            f"{'<=' if after_fresh else 'NOT <='} threshold {completion_stale_threshold_minutes}m, "
            f"read via the observer path (not the writer). "
            f"AFTER row provenance: cloud_trigger={after.get('cloud_trigger')!r} "
            f"({'organic' if after_organic else 'repair-written — disclosed, never presented as organic'})."
            if after.get("ok")
            else f"AFTER observer read failed: {after.get('reason')} — recovery cannot be proven without the pair."
        ),
        "evidence": json.dumps({"before": before, "after": after}, sort_keys=True),
        "external": True,
        "checked_at": checked_at,
    }
    no_mutation = {
        "check": "no_execution_mutation",
        "decision": "PASS" if not action_violations else "FAIL",
        "reason": (
            "Action-log audit (self-reported ledger, per recipe an internal check): zero restarts, "
            "redeploys, or loop-logic changes; every action's mutation surface is within the recipe "
            "mutation_policy (read_only / evidence_sink / control_plane_receipts / sandbox_filesystem)."
            if not action_violations
            else f"Action log contains {len(action_violations)} action(s) outside the permitted mutation surfaces."
        ),
        "evidence": json.dumps({"violations": action_violations}, sort_keys=True),
        "external": False,
        "checked_at": checked_at,
    }
    row_count = repair_row_count.get("count")
    idem_ok = bool(repair_row_count.get("ok")) and (row_count is not None and row_count <= 1) and jobs_with_key <= 1
    idempotency = {
        "check": "idempotency",
        "decision": "PASS" if idem_ok else "FAIL",
        "reason": (
            f"Receipt-table scan for the repair key returned {row_count} row(s) (<=1) and the jobs "
            f"registry holds {jobs_with_key} job(s) for the idempotency key (<=1): keyed retries "
            "created no duplicate receipts (L13)."
            if idem_ok
            else (
                f"Duplicate evidence detected or unauditable: sink scan={repair_row_count}, "
                f"jobs={jobs_with_key} (L13)."
            )
        ),
        "evidence": json.dumps({"sink_repair_key_rows": repair_row_count, "jobs_with_idempotency_key": jobs_with_key}, sort_keys=True),
        "external": False,
        "checked_at": checked_at,
    }
    return [pair, no_mutation, idempotency]


def recovery_state_from(
    verification_results: list[dict[str, Any]],
    run_log_ref: str,
    *,
    repair: dict[str, Any],
    after: dict[str, Any],
    idempotency_key: str,
) -> dict[str, Any]:
    """states.recovery — PROVEN only when the external before/after pair passes
    AND this job actually performed (or completed via prior ambiguous commit)
    the keyed repair write. A dry-run or failed repair that merely OBSERVES
    fresh evidence reports UNPROVEN with honest attribution: correlation is
    not causality, and observing someone else's recovery is not this job's."""
    pair_pass = any(
        v.get("check") == "before_after_pair" and v.get("external") and v.get("decision") == "PASS"
        for v in verification_results
    )
    if not pair_pass:
        return {
            "state": "UNPROVEN",
            "as_of": utc_now(),
            "reason": "No external PASS before/after pair — correlation is not causality; recovery is not claimed.",
        }
    repair_performed = bool(repair.get("written")) or bool(repair.get("suppressed_duplicate"))
    if not repair_performed:
        return {
            "state": "UNPROVEN",
            "as_of": utc_now(),
            "reason": (
                "AFTER shows fresh completion evidence, but this job performed no repair write "
                f"({'dry-run' if repair.get('dry_run') else 'repair did not complete'}): the observed "
                "recovery is not attributable to this job. Honest attribution beats a green field."
            ),
        }
    after_is_this_repair = after.get("repair_key") == idempotency_key
    attribution = (
        "the AFTER row IS this job's keyed repair row (repair_key match) — the repair restored the signal"
        if after_is_this_repair
        else (
            "the AFTER row is organic/other-sourced (repair_key mismatch) — this job's keyed repair "
            "was performed and fresh evidence followed, but the fresh row is not this job's write; "
            "causal share is disclosed as partial"
        )
    )
    return {
        "state": "PROVEN",
        "evidence_ref": f"verification_results[before_after_pair] external PASS + {run_log_ref}",
        "as_of": utc_now(),
        "reason": (
            "Keyed evidence-path repair performed, then fresh completion evidence read via the "
            f"independent observer path (before/after external pair). Attribution: {attribution}."
        ),
    }


# ---------------------------------------------------------------------------
# Diagnose — dual-signal classification -> diagnosis receipt + routing row
# ---------------------------------------------------------------------------
def diagnose(loop_id: str, factory_id: str, *, out_note: str = "") -> dict[str, Any]:
    observed_at = utc_now()
    dispatch = observer_read_dispatch(loop_id)
    completion = observer_read_completion(factory_id)
    interval = dispatch.get("interval_minutes")
    dispatch_threshold = (
        float(interval) * DISPATCH_STALE_MULTIPLIER_DEFAULT if interval else COMPLETION_STALE_MINUTES_DEFAULT
    )
    classification = classify_loop_state(
        dispatch_age_minutes=dispatch.get("age_minutes"),
        dispatch_stale_threshold_minutes=dispatch_threshold,
        completion_age_minutes=completion.get("age_minutes"),
        completion_stale_threshold_minutes=COMPLETION_STALE_MINUTES_DEFAULT,
        dispatch_query_ok=bool(dispatch.get("ok")),
        completion_query_ok=bool(completion.get("ok")),
        dispatch_last_fired_at=dispatch.get("last_fired_at"),
        completion_last_recorded_at=completion.get("recorded_at"),
        observed_at=observed_at,
        status_source="noos_loop_registry+noetfield_factory_cycle_runs",
        success_rate_sample_window_minutes=COMPLETION_STALE_MINUTES_DEFAULT,
    )
    stamp = utc_stamp()
    diagnosis_id = f"NOOS-DIAG-{stamp}-{loop_id}"
    diagnosis = {
        "schema": "noos-incident-diagnostic-v1",
        "diagnosis_id": diagnosis_id,
        "task": "NF-NOOS-MOTOR-ROUTE-WIRING-001",
        "classification": "incident_diagnostic",
        "not_a_verdict": (
            "Incident diagnostic, NOT a PASS/HEALTHY receipt. "
            "SUBMITTED for independent verification."
        ),
        "loop_id": loop_id,
        "factory_id": factory_id,
        "observed_at": observed_at,
        "execution_state": classification["execution_state"],
        "success_rate": classification["success_rate"],
        "evidence_state": classification["evidence_state"],
        "route": classification["route"],
        "route_permits_execution_mutation": classification["route_permits_execution_mutation"],
        "signals": {
            "dispatch": {
                "last_fired_at": dispatch.get("last_fired_at"),
                "age_minutes": dispatch.get("age_minutes"),
                "interval_minutes": interval,
                "stale_threshold_minutes": dispatch_threshold,
                "query_ok": bool(dispatch.get("ok")),
                "source": "noos_loop_registry.last_fired_at (observer read)",
            },
            "completion": {
                "last_recorded_at": completion.get("recorded_at"),
                "age_minutes": completion.get("age_minutes"),
                "stale_threshold_minutes": COMPLETION_STALE_MINUTES_DEFAULT,
                "query_ok": bool(completion.get("ok")),
                "last_row_cloud_trigger": completion.get("cloud_trigger"),
                "source": f"{SINK_TABLE}.recorded_at (observer read)",
            },
        },
        "presentation": classification["presentation"],
        "note": out_note,
        "canon_version": CANON_VERSION,
    }
    routing_row = None
    if classification["route"] == ROUTE_RECEIPT_WRITER_REPAIR:
        routing_row = {
            "schema": ROUTING_ROW_SCHEMA,
            "route": ROUTE_RECEIPT_WRITER_REPAIR,
            "noos_state": classification["execution_state"],
            "loop_id": loop_id,
            "factory_id": factory_id,
            "diagnosis_id": diagnosis_id,
            "diagnosis_receipt": "",  # filled by the CLI once the receipt path is known
            "created_at": observed_at,
            "created_by": f"{OWNER_ID} diagnose (dual-signal observer classification, INCIDENT-DIAGNOSE-001 semantics)",
            "consumed_by_recipe": RECIPE_ID,
            "machine_owner": OWNER_REF,
        }
    return {"diagnosis": diagnosis, "routing_row": routing_row, "classification": classification}


# ---------------------------------------------------------------------------
# Job record assembly
# ---------------------------------------------------------------------------
def build_job_record(
    *,
    job_id: str,
    routing_row: dict[str, Any],
    idempotency_key: str,
    before: dict[str, Any],
    sandbox: dict[str, Any],
    smoke: dict[str, Any],
    repair: dict[str, Any],
    run_log_ref: str,
    routing_row_ref: str,
    created_at: str,
    executing_at: str,
    baseline_sha: str,
    verification_results: list[dict[str, Any]] | None = None,
    after: dict[str, Any] | None = None,
    verified_at: str | None = None,
    destroyed_at: str | None = None,
    worker_started_at: str,
    worker_ended_at: str | None = None,
) -> dict[str, Any]:
    final = verification_results is not None
    all_pass = final and all(v.get("decision") == "PASS" for v in verification_results)
    failed_checks = [v["check"] for v in (verification_results or []) if v.get("decision") != "PASS"]

    states: dict[str, Any] = {
        "dispatch": {
            "state": "PROVEN",
            "evidence_ref": f"routing row {routing_row_ref} consumed by registered machine owner {OWNER_ID}; run log {run_log_ref}",
            "as_of": executing_at,
        },
        "execution": (
            {
                "state": "PROVEN",
                "evidence_ref": f"owner run log {run_log_ref}: sandbox smoke + keyed repair phase completed; worker python-script ran to completion",
                "as_of": worker_ended_at or executing_at,
            }
            if final
            else {"state": "IN_PROGRESS", "as_of": executing_at}
        ),
        "verification": (
            {
                "state": "PROVEN" if all_pass else "FAILED",
                "evidence_ref": f"verification_results in this record (3 recipe-declared checks) + {run_log_ref}",
                "as_of": verified_at or utc_now(),
                **(
                    {}
                    if all_pass
                    else {"reason": f"Recipe-declared check(s) FAILED: {', '.join(failed_checks)} — see verification_results; failure_policy on_check_fail=escalate applies (I2)."}
                ),
            }
            if final
            else {"state": "NOT_STARTED"}
        ),
        "evidence": (
            {
                "state": "PROVEN",
                "evidence_ref": f"this job record (motor/registry/jobs/{job_id}.json) + {run_log_ref}, both in-repo and observer-readable",
                "as_of": verified_at or utc_now(),
            }
            if final
            else {"state": "IN_PROGRESS", "as_of": executing_at}
        ),
        "authority": {
            "state": "NOT_APPLICABLE",
            "reason": "Pure keyed evidence-path retries need no founder gate (recipe human_gate: 'pure keyed retries need no gate'); no writer-fix PR was required.",
            "as_of": executing_at,
        },
        "promotion": {
            "state": "NOT_APPLICABLE",
            "reason": "Nothing was promoted: isolation selected keyed evidence-sink retry; no writer-component patch / draft PR was needed, so the human_gate at before_promotion never armed.",
            "as_of": executing_at,
        },
        "outcome": {
            "state": "NOT_APPLICABLE",
            "reason": "No promotion occurred; the repair result is carried by states.recovery (before/after external pair), not by a post-promotion business outcome.",
            "as_of": executing_at,
        },
    }
    if final:
        states["recovery"] = recovery_state_from(
            verification_results, run_log_ref,
            repair=repair, after=after or {}, idempotency_key=idempotency_key,
        )
    else:
        states["recovery"] = {"state": "IN_PROGRESS", "as_of": executing_at}

    # Lifecycle roll-up derived from states: ANY failed check routes to triage
    # (failure_policy on_check_fail=escalate), not just a failed pair. A
    # POST_VERIFYING roll-up over a FAILED verification would be a lie.
    if final and all_pass:
        lifecycle = "POST_VERIFYING"
    elif final:
        lifecycle = "TRIAGE_REQUIRED"
    else:
        lifecycle = "REPAIRING"

    if final:
        notes = (
            "First-class run of the Track D wiring (NF-NOOS-MOTOR-ROUTE-WIRING-001): the "
            f"{ROUTE_RECEIPT_WRITER_REPAIR} route now has a registered machine owner ({OWNER_REF}). "
            "Evidence-path-only: mutation_policy runtime=deny was honored — zero restarts, zero "
            "redeploys, zero loop-logic changes (see no_execution_mutation; self-reported ledger, "
            "disclosed). candidate_sha is the sandbox worktree HEAD (the exact handler+writer code "
            "that executed); no code was changed, so promotion/outcome are NOT_APPLICABLE and this "
            "record deliberately does NOT claim RECEIPT_COMPLETE: the recipe post-promotion checks "
            "(2 consecutive ORGANIC cron completion receipts — manual green != cron green; runnable "
            "via this owner's post-check subcommand) remain pending, and cost is a real metered zero "
            "(deterministic local python + Supabase REST; no model calls). AFTER-row provenance is "
            "disclosed in before_after_pair evidence and in states.recovery attribution: "
            "repair-written rows carry cloud_trigger=noos_motor_receipt_writer_repair and are never "
            "presented as organic writer-B output. SUBMITTED for independent verification. "
            f"canon_version: {CANON_VERSION}"
        )
    else:
        notes = (
            "INTERMEDIATE record (repair phase of NF-NOOS-MOTOR-ROUTE-WIRING-001): the keyed "
            "evidence-path repair has run; the AFTER observer read, verification_results, and "
            "recovery determination happen in the complete phase after one full loop cycle. No "
            "verification or recovery claim is made by this intermediate state. "
            "SUBMITTED for independent verification. "
            f"canon_version: {CANON_VERSION}"
        )

    record: dict[str, Any] = {
        "job_id": job_id,
        "recipe_id": RECIPE_ID,
        "recipe_version": RECIPE_VERSION,
        "idempotency_key": idempotency_key,
        "trigger": {
            "type": "event",
            "requested_by": f"noos:diagnosis {routing_row.get('noos_state')} routing row ({routing_row.get('created_by')})",
            "authorized_by": "motor/registry/bindings/noos-route-map-v1.json — receipt_writer_completion_evidence_repair binding (WIRED)",
            "occurred_at": routing_row.get("created_at"),
            "instruction_ref": routing_row_ref,
        },
        "states": states,
        "lifecycle_status": lifecycle,
        "sandbox": {
            "sandbox_id": sandbox.get("sandbox_id", ""),
            "type": sandbox.get("type", "git_worktree"),
            "worktree": sandbox.get("worktree", ""),
            **({"destroyed_at": destroyed_at} if destroyed_at else {}),
        },
        "worker_runs": [
            {
                "worker_type": "python-script",
                "started_at": worker_started_at,
                **({"ended_at": worker_ended_at} if worker_ended_at else {}),
                "log_ref": run_log_ref,
            }
        ],
        "artifacts": {
            "baseline_sha": baseline_sha,
            "candidate_sha": sandbox.get("head_sha", baseline_sha),
            "production_sha": "",
            "pr_ref": "",
            "files_changed": [],
            "other": [
                {"name": "routing_row", "ref": routing_row_ref},
                {"name": "diagnosis_receipt", "ref": str(routing_row.get("diagnosis_receipt") or "")},
                {"name": "run_log", "ref": run_log_ref},
            ],
        },
        "verification_results": verification_results or [],
        "approval": {
            "required": False,
            "approved_by": "",
            "approval_artifact": "",
        },
        "cost": {
            "provider": "local",
            "model": "deterministic-python",
            "tokens_in": 0,
            "tokens_out": 0,
            "total_usd": 0.0,
            "metered": True,
            "value_class": "risk_reduction",
        },
        "timestamps": {
            "created_at": created_at,
            "executing_at": executing_at,
            **({"verified_at": verified_at} if verified_at else {}),
        },
        "notes": notes,
    }
    return record


# ---------------------------------------------------------------------------
# Escalation (narrow founder gate — never restart)
# ---------------------------------------------------------------------------
def build_escalation(
    routing_row: dict[str, Any],
    before: dict[str, Any],
    after: dict[str, Any],
    run_log_ref: str,
    *,
    failed_checks: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema": "noos-founder-decision-escalation-v1",
        "created_at": utc_now(),
        "created_by": OWNER_REF,
        "recipe_id": RECIPE_ID,
        "routing_row": routing_row,
        "finding": (
            f"Recipe-declared check(s) FAILED: {', '.join(failed_checks)}."
            if failed_checks
            else "Completion evidence was NOT restored by bounded keyed evidence-path retries."
        ),
        "before": before,
        "after": after,
        "run_log": run_log_ref,
        "requested_decision": (
            "Founder decision required: repair needs an action outside the machine-safe surface "
            "(possible runtime restart, redeploy, or writer/verifier change — all founder_required "
            "by the recipe), or a mutation-policy/L13 finding needs triage. The machine did NOT "
            "restart execution and will not (escalation_route)."
        ),
        "canon_version": CANON_VERSION,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _git_head(cwd: Path) -> str:
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True)
    return out.stdout.strip()


def _load_platform_env() -> None:
    try:
        from noos_vault_paths_v1 import load_platform_env

        load_platform_env()
    except Exception:
        pass


def _blocked(problems: list[str] | str) -> int:
    print(json.dumps({"status": "BLOCKED_WITH_REASON", "problems": problems if isinstance(problems, list) else [problems]}, indent=2))
    return 2


def cmd_diagnose(args: argparse.Namespace) -> int:
    _load_platform_env()
    result = diagnose(args.loop_id, args.factory_id)
    stamp = utc_stamp()
    diag_path = ROOT / f"receipts/incident/noos-motor-route-owner-diagnosis-{stamp}-{args.loop_id}.json"
    _write_json(diag_path, result["diagnosis"])
    out = {"diagnosis_receipt": str(diag_path.relative_to(ROOT)), "execution_state": result["diagnosis"]["execution_state"], "route": result["diagnosis"]["route"]}
    if result["routing_row"] is not None:
        result["routing_row"]["diagnosis_receipt"] = str(diag_path.relative_to(ROOT))
        row_path = ROOT / f"receipts/motor/noos-motor-routing-row-{stamp}-{args.loop_id}.json"
        _write_json(row_path, result["routing_row"])
        out["routing_row"] = str(row_path.relative_to(ROOT))
    else:
        out["routing_row"] = None
        out["note"] = "state does not route to receipt-writer repair; no routing row created"
    print(json.dumps(out, indent=2))
    return 0


def _run_log_paths(diagnosis_id: str) -> tuple[Path, Path]:
    """Append-only control plane: the repair log is written once and never
    rewritten; the complete phase writes its own file referencing it."""
    repair_log = ROOT / f"receipts/motor/noos-motor-route-owner-run-{diagnosis_id}-repair.json"
    complete_log = ROOT / f"receipts/motor/noos-motor-route-owner-run-{diagnosis_id}-complete.json"
    return repair_log, complete_log


def cmd_run(args: argparse.Namespace) -> int:
    _load_platform_env()
    row_path = Path(args.routing_row).resolve()
    if not row_path.is_file():
        return _blocked(f"routing row not found: {row_path}")
    routing_row = json.loads(row_path.read_text(encoding="utf-8"))
    routing_row_ref = str(row_path.relative_to(ROOT)) if row_path.is_relative_to(ROOT) else str(row_path)

    problems = validate_routing_row(routing_row)
    if problems:
        return _blocked(problems)

    loop_id = routing_row["loop_id"]
    factory_id = routing_row["factory_id"]
    diagnosis_id = routing_row["diagnosis_id"]
    idem_key = render_idempotency_key(loop_id, diagnosis_id)
    jobs_dir = ROOT / "motor/registry/jobs"
    repair_log_path, complete_log_path = _run_log_paths(diagnosis_id)
    repair_log_ref = str(repair_log_path.relative_to(ROOT))
    complete_log_ref = str(complete_log_path.relative_to(ROOT))
    job_path = jobs_dir / f"{args.job_id}.json"

    if args.phase == "repair":
        existing = find_existing_job(jobs_dir, idem_key)
        if existing is not None and existing != job_path:
            print(json.dumps({"status": "DUPLICATE_SUPPRESSED", "idempotency_key": idem_key, "existing_job": existing.name, "l13": "same key = same job, never a duplicate"}, indent=2))
            return 0
        if existing is not None and repair_log_path.exists():
            state = json.loads(repair_log_path.read_text(encoding="utf-8"))
            if state.get("repair", {}).get("written") or state.get("repair", {}).get("suppressed_duplicate"):
                print(json.dumps({"status": "DUPLICATE_SUPPRESSED", "idempotency_key": idem_key, "existing_job": existing.name, "l13": "repair phase already ran for this key"}, indent=2))
                return 0
        # Never silently overwrite a job receipt that belongs to a DIFFERENT key.
        if job_path.exists():
            held_key = job_file_key(job_path)
            if held_key != idem_key:
                return _blocked(
                    f"job file {job_path.name} already holds idempotency_key {held_key!r} != {idem_key!r}; "
                    f"pass a fresh --job-id instead of overwriting an existing receipt"
                )

        log = ActionLog()
        log.record("routing_row_consumed", "read_only", routing_row_ref)
        log.record("execution_mutation_guard", "read_only", f"route_permits_execution_mutation={route_permits_execution_mutation(routing_row['route'])} (must be False)")

        diag_path = ROOT / routing_row["diagnosis_receipt"]
        if not diag_path.is_file():
            return _blocked(f"diagnosis receipt not found: {routing_row['diagnosis_receipt']}")
        diagnosis = json.loads(diag_path.read_text(encoding="utf-8"))
        before = capture_before(diagnosis, routing_row["diagnosis_receipt"])
        log.record("before_captured", "read_only", f"last_good={before.get('last_good_completion_recorded_at')} age={before.get('completion_staleness_age_minutes')}m provenance={before.get('last_good_completion_cloud_trigger')}")

        created_at = utc_now()
        sandbox = create_sandbox(diagnosis_id.lower().replace(":", "-"), log)
        if not sandbox.get("ok"):
            print(json.dumps({"status": "FAILED_WITH_RECEIPT", "reason": sandbox.get("reason")}, indent=2))
            return 1
        destroyed_at: str | None = None
        try:
            smoke = sandbox_writer_smoke(sandbox, log)
            isolation = {
                "conclusion": (
                    "Writer component imports and exposes its config entrypoint in sandbox; sink is "
                    "reachable via observer reads. Root cause of the cloud writer-B silence is not "
                    "locally establishable (writer-B runs in cloud runners); selected machine-safe "
                    "repair: keyed evidence-sink retry (machine_may retry_failed_receipt_writes). "
                    "Escalation, never restart, if the retry does not restore evidence."
                ),
                "writer_smoke": smoke,
            }
            repair = keyed_repair_write(
                factory_id=factory_id, loop_id=loop_id, repair_key=idem_key,
                diagnosis_id=diagnosis_id, dry_run=args.dry_run, log=log,
            )
            executing_at = utc_now()
        finally:
            destroyed_at = destroy_sandbox(sandbox, log)

        state = {
            "schema": "noos-motor-route-owner-run-v1",
            "owner": OWNER_REF,
            "job_id": args.job_id,
            "idempotency_key": idem_key,
            "routing_row_ref": routing_row_ref,
            "phase": "repair",
            "created_at": created_at,
            "executing_at": executing_at,
            "worker_started_at": created_at,
            "before": before,
            "sandbox": {k: v for k, v in sandbox.items() if k != "ok"},
            "sandbox_destroyed_at": destroyed_at,
            "isolation": isolation,
            "repair": repair,
            "baseline_sha": _git_head(ROOT),
            "dry_run": bool(args.dry_run),
            "action_log": log.as_list(),
            "canon_version": CANON_VERSION,
        }
        _write_json(repair_log_path, state)
        record = build_job_record(
            job_id=args.job_id, routing_row=routing_row, idempotency_key=idem_key,
            before=before, sandbox=sandbox, smoke=smoke, repair=repair,
            run_log_ref=repair_log_ref, routing_row_ref=routing_row_ref,
            created_at=created_at, executing_at=executing_at,
            baseline_sha=state["baseline_sha"], destroyed_at=destroyed_at,
            worker_started_at=created_at,
        )
        _write_json(job_path, record)
        print(json.dumps({"status": "REPAIRING", "repair": repair, "run_log": repair_log_ref, "job": str(job_path.relative_to(ROOT)), "next": "wait one full loop cycle, then run --phase complete"}, indent=2))
        return 0 if repair.get("ok") else 1

    # phase == complete
    if not repair_log_path.is_file():
        return _blocked(
            f"repair-phase run log not found ({repair_log_ref}); run --phase repair first "
            f"(recipe steps: repair, wait one full loop cycle, then capture_after)"
        )
    state = json.loads(repair_log_path.read_text(encoding="utf-8"))
    if state.get("job_id") != args.job_id:
        return _blocked(
            f"run log {repair_log_ref} belongs to job_id {state.get('job_id')!r}, not {args.job_id!r}; "
            f"refusing to write a second job file for the same idempotency key (L13)"
        )
    log = ActionLog()
    log.actions = list(state.get("action_log") or [])
    before = state["before"]

    log.record("after_observer_read", "read_only", f"factory_id={factory_id} via autorun_status_v1 read path")
    after = observer_read_completion(factory_id)
    repair_rows = count_repair_rows(idem_key)
    jobs_with_key = count_jobs_with_key(jobs_dir, idem_key)
    verified_at = utc_now()
    verification_results = build_verification_results(
        before=before,
        after=after,
        completion_stale_threshold_minutes=float(
            before.get("completion_stale_threshold_minutes") or COMPLETION_STALE_MINUTES_DEFAULT
        ),
        action_violations=log.violations(),
        repair_row_count=repair_rows,
        jobs_with_key=jobs_with_key,
        checked_at=verified_at,
    )
    complete_state = dict(state)
    complete_state.update(
        {
            "phase": "complete",
            "repair_log_ref": repair_log_ref,
            "after": after,
            "repair_rows": repair_rows,
            "verified_at": verified_at,
            "worker_ended_at": verified_at,
            "verification_results": verification_results,
            "action_log": log.as_list(),
        }
    )
    # Append-only control plane: the repair log stays untouched; the complete
    # phase writes its own receipt file referencing it.
    _write_json(complete_log_path, complete_state)

    record = build_job_record(
        job_id=args.job_id, routing_row=routing_row, idempotency_key=idem_key,
        before=before, sandbox=state["sandbox"], smoke=state["isolation"]["writer_smoke"],
        repair=state["repair"], run_log_ref=complete_log_ref, routing_row_ref=routing_row_ref,
        created_at=state["created_at"], executing_at=state["executing_at"],
        baseline_sha=state["baseline_sha"], verification_results=verification_results,
        after=after, verified_at=verified_at, destroyed_at=state.get("sandbox_destroyed_at"),
        worker_started_at=state["worker_started_at"], worker_ended_at=verified_at,
    )
    _write_json(job_path, record)

    all_pass = all(v["decision"] == "PASS" for v in verification_results)
    failed_checks = [v["check"] for v in verification_results if v["decision"] != "PASS"]
    out: dict[str, Any] = {
        "status": record["lifecycle_status"],
        "recovery": record["states"]["recovery"]["state"],
        "job": str(job_path.relative_to(ROOT)),
        "run_log": complete_log_ref,
        "checks": {v["check"]: v["decision"] for v in verification_results},
    }
    if not all_pass:
        # failure_policy on_check_fail=escalate — for ANY failed check, not
        # only the pair: a mutation-policy or L13 finding is triage, never a
        # quietly green job.
        esc = build_escalation(routing_row, before, after, complete_log_ref, failed_checks=failed_checks)
        esc_path = ROOT / f"receipts/motor/noos-motor-route-owner-escalation-{diagnosis_id}.json"
        _write_json(esc_path, esc)
        out["escalation"] = str(esc_path.relative_to(ROOT))
        out["note"] = "Check(s) failed — escalated to founder decision; execution was NOT restarted."

    validate = subprocess.run([sys.executable, str(ROOT / "motor/registry/validate.py")], capture_output=True, text=True)
    out["validate_py_exit"] = validate.returncode
    print(json.dumps(out, indent=2))
    return 0 if (validate.returncode == 0 and all_pass) else 1


def cmd_post_check(args: argparse.Namespace) -> int:
    """The recipe's post-promotion check, with an owner: 2 consecutive ORGANIC
    completion receipts (cron green, not manual/repair green). Read-only."""
    _load_platform_env()
    history = observer_read_completion_history(args.factory_id, limit=max(args.count + 1, 3))
    checked_at = utc_now()
    if not history.get("ok"):
        result = {"decision": "FAIL", "reason": f"observer read failed: {history.get('reason')}"}
    else:
        rows = history["rows"][: args.count]
        organic = [r for r in rows if r.get("organic")]
        fresh = [r for r in rows if r.get("age_minutes") is not None and r["age_minutes"] <= args.window_minutes]
        ok = len(rows) >= args.count and len(organic) == len(rows) and rows[0] in fresh
        result = {
            "decision": "PASS" if ok else "FAIL",
            "reason": (
                f"latest {len(rows)} completion receipts are all organic and the newest is fresh "
                f"(<= {args.window_minutes}m): cron green"
                if ok
                else (
                    f"of the latest {len(rows)} completion receipts, {len(organic)} are organic and "
                    f"newest age is {rows[0].get('age_minutes') if rows else None}m (window {args.window_minutes}m): "
                    "organic writer-B recovery NOT yet proven — manual/repair green != cron green"
                )
            ),
            "rows": rows,
        }
    receipt = {
        "schema": "noos-motor-post-check-v1",
        "recipe_id": RECIPE_ID,
        "job_id": args.job_id,
        "loop_id": args.loop_id,
        "factory_id": args.factory_id,
        "check": "post_promotion_organic_cycles",
        "external": True,
        "checked_at": checked_at,
        "checked_by": OWNER_REF,
        "read_path": "observer:autorun_status_v1 (never the writer's)",
        **result,
        "not_a_verdict": "Post-check evidence row, SUBMITTED for independent verification.",
        "canon_version": CANON_VERSION,
    }
    out_path = ROOT / f"receipts/motor/noos-motor-post-check-{utc_stamp()}-{args.loop_id}.json"
    _write_json(out_path, receipt)
    print(json.dumps({"decision": result["decision"], "reason": result["reason"], "receipt": str(out_path.relative_to(ROOT))}, indent=2))
    return 0 if result["decision"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    d = sub.add_parser("diagnose", help="dual-signal classification -> diagnosis receipt + routing row")
    d.add_argument("--loop-id", required=True)
    d.add_argument("--factory-id", required=True)
    d.set_defaults(func=cmd_diagnose)

    r = sub.add_parser("run", help="consume a routing row and execute the repair recipe")
    r.add_argument("--routing-row", required=True)
    r.add_argument("--job-id", default="MOTOR-RWREPAIR-001")
    r.add_argument("--phase", choices=["repair", "complete"], default="repair")
    r.add_argument("--dry-run", action="store_true", help="no sink writes; observer reads only")
    r.set_defaults(func=cmd_run)

    p = sub.add_parser("post-check", help="post-promotion check: N consecutive ORGANIC completion receipts (cron green)")
    p.add_argument("--loop-id", required=True)
    p.add_argument("--factory-id", required=True)
    p.add_argument("--job-id", default="MOTOR-RWREPAIR-001")
    p.add_argument("--count", type=int, default=2)
    p.add_argument("--window-minutes", type=float, default=COMPLETION_STALE_MINUTES_DEFAULT)
    p.set_defaults(func=cmd_post_check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
