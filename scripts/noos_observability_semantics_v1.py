#!/usr/bin/env python3
"""NOOS observability semantics v1 — separate execution-dispatch, completion
evidence, receipt-writer health, and observer availability.

Task: NF-NOOS-OBSERVABILITY-SEMANTICS-001.

Incident that motivated this module (2026-07-16T23:32:07Z -> ~2026-07-17T03:39:51Z):
dispatch heartbeat (noos_loop_registry.last_fired_at) stayed fresh and the
append-only deadman history reported stale_count=0, while the per-loop
completion/burst receipts (noetfield_factory_cycle_runs) went stale. The old
cockpit collapsed *completion-receipt* staleness into BLOCKED_WITH_REASON with
success_rate=0.0 — reporting "loop failed" when the true state was
"dispatch active, completion evidence unavailable".

This module is PURE and deterministic (no network, no clock reads except an
injected ``now``): it takes two independent freshness observations and returns
an explicit state, an honest success_rate (never a fabricated 0.0 for a missing
sample), an evidence_state, a presentation block, and a routing target.

DESIGN LAW (do not regress):
  * Do NOT suppress completion-receipt staleness merely because dispatch is fresh.
  * Do NOT report a stale or absent sample as success_rate=0.0.
  * Do NOT route evidence-writer staleness to production restart / redeploy.
"""

from __future__ import annotations

from typing import Any

# ---- Execution states (explicit, mutually exclusive) -----------------------
RUNNING_CONFIRMED = "RUNNING_CONFIRMED"
DISPATCHING_COMPLETION_UNPROVEN = "DISPATCHING_COMPLETION_UNPROVEN"
OBSERVER_DIVERGENCE_OR_REPLAY = "OBSERVER_DIVERGENCE_OR_REPLAY"
LOOP_EXECUTION_STALE = "LOOP_EXECUTION_STALE"
OBSERVER_UNAVAILABLE = "OBSERVER_UNAVAILABLE"

# ---- Provenance-aware states (NF-NOOS-MOTOR-V1-FULL-RUNWAY, Phase 4) --------
# These engage only when the caller supplies completion provenance / a separate
# organic-completion signal. They exist to make the false-green impossible:
# a repair/replay/manual completion, however fresh, must NEVER promote a loop to
# RUNNING_CONFIRMED. See classify_loop_state() and DESIGN LAW below.
DEGRADED_REPAIR_SUSTAINED = "DEGRADED_REPAIR_SUSTAINED"
COMPLETION_UNPROVEN = "COMPLETION_UNPROVEN"
EVIDENCE_INCONSISTENT = "EVIDENCE_INCONSISTENT"
STOPPED_OR_IDLE = "STOPPED_OR_IDLE"

# ---- Receipt provenance origins (aligned with noos_motor_route_owner_v1) ----
# CORRECTION (NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1): ``organic`` is reserved for the
# PRODUCTION canonical producer only. Local/offline reference execution is
# ``local_reference`` — it proves product behavior, NEVER deployed-system
# liveness. This closes the earlier defect where the local reference executor
# stamped ``receipt_origin=organic``.
ORIGIN_ORGANIC = "organic"
ORIGIN_LOCAL_REFERENCE = "local_reference"
ORIGIN_REPAIR = "repair"
ORIGIN_REPLAY = "replay"
ORIGIN_MANUAL = "manual"
ORIGIN_MIGRATION = "migration"
ORIGIN_TEST = "test"
ORIGIN_LEGACY_UNKNOWN = "legacy_unknown"

# Non-organic origins can never satisfy the RUNNING_CONFIRMED organic gate.
NON_ORGANIC_ORIGINS = frozenset(
    {ORIGIN_LOCAL_REFERENCE, ORIGIN_REPAIR, ORIGIN_REPLAY, ORIGIN_MANUAL,
     ORIGIN_MIGRATION, ORIGIN_TEST}
)
# Origins that may NEVER establish PRODUCTION liveness (everything except a
# genuine production organic completion). legacy_unknown included — never guess.
NON_PRODUCTION_LIVENESS_ORIGINS = frozenset(
    {ORIGIN_LOCAL_REFERENCE, ORIGIN_REPAIR, ORIGIN_REPLAY, ORIGIN_MANUAL,
     ORIGIN_MIGRATION, ORIGIN_TEST, ORIGIN_LEGACY_UNKNOWN}
)

# Production allowlist: only these producers on these execution planes may
# establish a PRODUCTION RUNNING_CONFIRMED. A workflow_dispatch / GHA factory run
# (manual origin) or the local reference executor is deliberately excluded.
PRODUCTION_ORGANIC_PRODUCERS = frozenset(
    {"railway:noos-loop-runner", "cf:noos-loop-fleet-tick", "http_loop"}
)
CANONICAL_EXECUTION_PLANES = frozenset(
    {"railway:noos-loop-runner", "production"}
)

# Raw cloud_trigger labels the repair path stamps (must match
# noos_motor_route_owner_v1.REPAIR_TRIGGER_LABELS — single source of truth).
_REPAIR_TRIGGER_LABELS = frozenset(
    {"noos_motor_receipt_writer_repair", "noos_integrator_repair"}
)
# Raw cloud_trigger labels that mark a genuine organic cloud producer.
_ORGANIC_TRIGGER_LABELS = frozenset({"http_loop"})

# ---- Evidence sufficiency --------------------------------------------------
EVIDENCE_SUFFICIENT = "SUFFICIENT_RECENT_EVIDENCE"
EVIDENCE_INSUFFICIENT = "INSUFFICIENT_RECENT_EVIDENCE"

# ---- Freshness labels ------------------------------------------------------
FRESH = "FRESH"
STALE = "STALE"
UNKNOWN = "UNKNOWN"

# ---- Routing targets -------------------------------------------------------
ROUTE_EXECUTION_RECONCILE = "execution_reconcile_self_heal"
ROUTE_RECEIPT_WRITER_REPAIR = "receipt_writer_completion_evidence_repair"
ROUTE_OBSERVER_RECONCILIATION = "observer_reconciliation"
ROUTE_MONITORING_AVAILABILITY = "monitoring_availability"
# Organic producer stalled while the sink/writer is healthy (repair rows land):
# escalate + surface, NEVER auto-restart (cloud producer restart is founder-gated
# and off-host). This route deliberately does NOT loop back to receipt-writer
# repair — that is exactly what masked the 2026-07-12 stall.
ROUTE_ORGANIC_PRODUCER_ESCALATION = "organic_producer_reconcile_escalation"
ROUTE_NONE = None

# Routes that are allowed to trigger execution restart / redeploy. Evidence
# and observer routes are intentionally excluded (design law above).
EXECUTION_MUTATING_ROUTES = frozenset({ROUTE_EXECUTION_RECONCILE})

_STATE_ROUTE = {
    RUNNING_CONFIRMED: ROUTE_NONE,
    DISPATCHING_COMPLETION_UNPROVEN: ROUTE_RECEIPT_WRITER_REPAIR,
    OBSERVER_DIVERGENCE_OR_REPLAY: ROUTE_OBSERVER_RECONCILIATION,
    LOOP_EXECUTION_STALE: ROUTE_EXECUTION_RECONCILE,
    OBSERVER_UNAVAILABLE: ROUTE_MONITORING_AVAILABILITY,
    # Provenance-aware states: repair masking / organic stall / inconsistency.
    DEGRADED_REPAIR_SUSTAINED: ROUTE_ORGANIC_PRODUCER_ESCALATION,
    COMPLETION_UNPROVEN: ROUTE_ORGANIC_PRODUCER_ESCALATION,
    EVIDENCE_INCONSISTENT: ROUTE_OBSERVER_RECONCILIATION,
    STOPPED_OR_IDLE: ROUTE_NONE,
}

# success_rate per state. ``None`` means "no trustworthy recent sample" and MUST
# be surfaced as evidence_state=INSUFFICIENT_RECENT_EVIDENCE, never as 0.0.
_STATE_SUCCESS_RATE: dict[str, float | None] = {
    RUNNING_CONFIRMED: 1.0,
    DISPATCHING_COMPLETION_UNPROVEN: None,
    OBSERVER_DIVERGENCE_OR_REPLAY: None,
    LOOP_EXECUTION_STALE: 0.0,  # both signals confirm real execution staleness
    OBSERVER_UNAVAILABLE: None,
    # No trustworthy ORGANIC sample => never a fabricated success_rate.
    DEGRADED_REPAIR_SUSTAINED: None,
    COMPLETION_UNPROVEN: None,
    EVIDENCE_INCONSISTENT: None,
    STOPPED_OR_IDLE: None,
}

# States whose evidence is sufficient to *act on* (confirmed running, or
# confirmed stale). Everything else is evidence-insufficient by construction.
_STATE_EVIDENCE = {
    RUNNING_CONFIRMED: EVIDENCE_SUFFICIENT,
    LOOP_EXECUTION_STALE: EVIDENCE_SUFFICIENT,
    DISPATCHING_COMPLETION_UNPROVEN: EVIDENCE_INSUFFICIENT,
    OBSERVER_DIVERGENCE_OR_REPLAY: EVIDENCE_INSUFFICIENT,
    OBSERVER_UNAVAILABLE: EVIDENCE_INSUFFICIENT,
    # Repair-sustained / unproven organic completion is, by construction, NOT
    # sufficient ORGANIC evidence — even though a (repair) row is fresh.
    DEGRADED_REPAIR_SUSTAINED: EVIDENCE_INSUFFICIENT,
    COMPLETION_UNPROVEN: EVIDENCE_INSUFFICIENT,
    EVIDENCE_INCONSISTENT: EVIDENCE_INSUFFICIENT,
    STOPPED_OR_IDLE: EVIDENCE_SUFFICIENT,  # inactivity is expected by config
}

_STATE_CONFIDENCE = {
    RUNNING_CONFIRMED: "HIGH",
    LOOP_EXECUTION_STALE: "HIGH",
    DISPATCHING_COMPLETION_UNPROVEN: "LOW",
    OBSERVER_DIVERGENCE_OR_REPLAY: "LOW",
    OBSERVER_UNAVAILABLE: "NONE",
    DEGRADED_REPAIR_SUSTAINED: "MEDIUM",
    COMPLETION_UNPROVEN: "MEDIUM",
    EVIDENCE_INCONSISTENT: "LOW",
    STOPPED_OR_IDLE: "HIGH",
}


def route_for_state(state: str) -> str | None:
    """Routing target for an execution state (see design law)."""
    return _STATE_ROUTE.get(state, ROUTE_NONE)


def success_rate_for_state(state: str) -> float | None:
    return _STATE_SUCCESS_RATE.get(state)


def evidence_state_for(state: str) -> str:
    return _STATE_EVIDENCE.get(state, EVIDENCE_INSUFFICIENT)


def route_permits_execution_mutation(route: str | None) -> bool:
    """True only for the execution-reconcile route. Evidence-writer / observer
    / organic-producer-escalation routes must never trigger a runner restart or
    redeploy from the machine (cloud producer restart is founder-gated)."""
    return route in EXECUTION_MUTATING_ROUTES


def normalize_receipt_origin(cloud_trigger: str | None) -> str:
    """Map a raw ``noetfield_factory_cycle_runs.runner_output.cloud_trigger``
    (or a receipt ``receipt_origin``) to a normalized provenance origin.

    Single source of truth for repair labels is shared with
    ``noos_motor_route_owner_v1.REPAIR_TRIGGER_LABELS``. Unknown / missing
    provenance is ``legacy_unknown`` (never guessed as organic)."""
    if cloud_trigger is None:
        return ORIGIN_LEGACY_UNKNOWN
    raw = str(cloud_trigger).strip().lower()
    if not raw:
        return ORIGIN_LEGACY_UNKNOWN
    # Already-normalized values pass through.
    if raw in {
        ORIGIN_ORGANIC, ORIGIN_LOCAL_REFERENCE, ORIGIN_REPAIR, ORIGIN_REPLAY,
        ORIGIN_MANUAL, ORIGIN_MIGRATION, ORIGIN_TEST, ORIGIN_LEGACY_UNKNOWN,
    }:
        return raw
    if raw in _REPAIR_TRIGGER_LABELS or "repair" in raw:
        return ORIGIN_REPAIR
    if raw in _ORGANIC_TRIGGER_LABELS:
        return ORIGIN_ORGANIC
    if "local_reference" in raw or "local-reference" in raw or raw.startswith("local"):
        return ORIGIN_LOCAL_REFERENCE
    if "replay" in raw:
        return ORIGIN_REPLAY
    if "migration" in raw or "backfill" in raw:
        return ORIGIN_MIGRATION
    if raw in {"manual", "workflow_dispatch"} or "manual" in raw:
        return ORIGIN_MANUAL
    if "test" in raw:
        return ORIGIN_TEST
    return ORIGIN_LEGACY_UNKNOWN


def is_organic_origin(origin: str | None) -> bool:
    """True only for a genuinely organic origin. local_reference/repair/replay/
    manual/migration/test are never organic. ``legacy_unknown`` is NOT organic
    (do not guess)."""
    return origin == ORIGIN_ORGANIC


# ---- Live-projection wiring status (NF-NOOS-PROVENANCE-CLASSIFIER-CORRECTION §4) ----
# production_running_confirmed() is a COMPLETE gate, but its full inputs
# (producer allowlist, canonical execution plane, dispatch correlation, lifecycle
# validity) are NOT present in the trusted Supabase completion row. It is
# therefore NOT wired into the live projection (probe_supabase_noos_loop) and is
# DECLARED_NOT_WIRED. The live projection enforces the trustable SUBSET via
# classify_loop_state: organic origin + successful terminal + freshness +
# repair-only-repair-sustained. Do not claim the full live production gate is
# enforced until the missing inputs exist.
PRODUCTION_GATE_LIVE_WIRED = False
PRODUCTION_GATE_LIVE_STATUS = "DECLARED_NOT_WIRED"
PRODUCTION_GATE_MISSING_INPUTS = (
    "producer_allowlisted", "execution_plane_canonical",
    "dispatch_correlated", "lifecycle_valid",
)


def production_gate_wiring_status() -> dict[str, Any]:
    """Honest declaration of what the LIVE projection enforces vs. what the full
    production gate would require but cannot (inputs absent from the trusted row)."""
    return {
        "production_running_confirmed_wired_into_live_projection": PRODUCTION_GATE_LIVE_WIRED,
        "status": PRODUCTION_GATE_LIVE_STATUS,
        "live_enforced_subset": [
            "receipt_origin == organic",
            "organic row is a successful terminal (status/exit)",
            "freshness within SLO",
            "only ORIGIN_REPAIR counts as repair-sustained",
        ],
        "not_wired_predicates": list(PRODUCTION_GATE_MISSING_INPUTS),
        "reason": "producer / execution_plane / dispatch correlation / lifecycle validity are not present in the trusted noetfield_factory_cycle_runs row; production_running_confirmed() remains test-only until those inputs exist.",
    }


def production_running_confirmed(
    *,
    receipt_origin: str | None,
    producer: str | None,
    execution_plane: str | None,
    dispatch_correlated: bool,
    lifecycle_valid: bool,
    terminal_evidence_valid: bool,
    freshness_within_slo: bool,
) -> dict[str, Any]:
    """The PRODUCTION liveness gate (NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §2).

    NOTE: this is TEST-ONLY / DECLARED_NOT_WIRED in the live projection — see
    production_gate_wiring_status(). The live probe enforces only the trustable
    subset via classify_loop_state.

    A PRODUCTION ``RUNNING_CONFIRMED`` requires ALL of:
      * ``receipt_origin == organic``;
      * producer in ``PRODUCTION_ORGANIC_PRODUCERS``;
      * execution plane in ``CANONICAL_EXECUTION_PLANES``;
      * dispatch correlates to a real production dispatch;
      * lifecycle ordering valid;
      * terminal evidence valid (output exists OR a valid failure terminal);
      * freshness within the configured SLO.

    local_reference / test / repair / replay / manual / migration / legacy_unknown
    can NEVER pass this gate — they may prove local product behavior, never
    deployed-system health. Returns the decision plus a per-predicate breakdown
    so a caller can see exactly which production predicate failed."""
    origin = normalize_receipt_origin(receipt_origin)
    checks = {
        "origin_is_organic": is_organic_origin(origin),
        "origin_is_production_eligible": origin not in NON_PRODUCTION_LIVENESS_ORIGINS,
        "producer_allowlisted": producer in PRODUCTION_ORGANIC_PRODUCERS,
        "execution_plane_canonical": execution_plane in CANONICAL_EXECUTION_PLANES,
        "dispatch_correlated": bool(dispatch_correlated),
        "lifecycle_valid": bool(lifecycle_valid),
        "terminal_evidence_valid": bool(terminal_evidence_valid),
        "freshness_within_slo": bool(freshness_within_slo),
    }
    confirmed = all(checks.values())
    failed = [k for k, v in checks.items() if not v]
    return {
        "production_running_confirmed": confirmed,
        "execution_state": RUNNING_CONFIRMED if confirmed else COMPLETION_UNPROVEN,
        "normalized_origin": origin,
        "checks": checks,
        "failed_predicates": failed,
        # A non-production origin is the single most common masking vector — name it.
        "blocked_reason": None if confirmed else (
            f"non_production_origin:{origin}" if origin in NON_PRODUCTION_LIVENESS_ORIGINS
            else f"failed:{','.join(failed)}"
        ),
    }


def _row_cloud_trigger(row: dict[str, Any]) -> str | None:
    """Read the provenance label off a completion row, whether it lives on
    ``runner_output.cloud_trigger`` (Supabase noetfield_factory_cycle_runs) or a
    top-level ``cloud_trigger`` / ``receipt_origin``."""
    runner = row.get("runner_output")
    if isinstance(runner, dict) and runner.get("cloud_trigger") is not None:
        return runner.get("cloud_trigger")
    if row.get("cloud_trigger") is not None:
        return row.get("cloud_trigger")
    return row.get("receipt_origin")


# Statuses that represent a successful terminal completion.
_SUCCESS_TERMINAL_STATUSES = frozenset({"ok", "success", "succeeded", "completed", "passed"})


def row_successful_terminal(row: dict[str, Any]) -> bool:
    """True only if the row carries evidence of a SUCCESSFUL terminal completion:
    a success status AND a non-failing exit code. A fresh organic row that FAILED
    (e.g. status=degraded / exit!=0) must NOT contribute to RUNNING_CONFIRMED
    (NF-NOOS-PROVENANCE-CLASSIFIER-CORRECTION §1)."""
    status = str(row.get("status") or "").strip().lower()
    if status and status not in _SUCCESS_TERMINAL_STATUSES:
        return False
    exit_code = row.get("exit_code")
    if exit_code is not None:
        try:
            if int(exit_code) != 0:
                return False
        except (TypeError, ValueError):
            return False
    # Require at least one positive terminal signal (a success status or exit 0).
    return status in _SUCCESS_TERMINAL_STATUSES or row.get("exit_code") == 0


def derive_completion_provenance(
    rows: list[dict[str, Any]],
    *,
    age_fn: Any,
) -> dict[str, Any]:
    """Given newest-first completion rows, derive the provenance signals
    ``classify_loop_state`` needs to tell organic liveness from repair-sustained
    freshness. PURE: the caller injects ``age_fn(recorded_at) -> minutes|None``
    (no clock read here). Each row may carry ``runner_output.cloud_trigger`` /
    ``cloud_trigger`` / ``receipt_origin`` and a ``recorded_at`` timestamp.

    Returns ``completion_origin`` (newest row), ``organic_completion_age_minutes``
    (newest organic row), ``repair_completion_age_minutes`` (newest non-organic
    row) and a ``metrics`` block with the separated organic/repair timestamps and
    ``repair_receipts_since_last_organic``."""
    if not rows:
        return {
            "completion_origin": None,
            "organic_completion_age_minutes": None,
            "repair_completion_age_minutes": None,
            "metrics": {},
        }
    newest_origin = normalize_receipt_origin(_row_cloud_trigger(rows[0]))
    newest_terminal_valid = row_successful_terminal(rows[0])
    organic_at: str | None = None          # newest SUCCESSFUL-terminal organic (§1)
    repair_at: str | None = None           # newest ORIGIN_REPAIR row only (§2)
    repair_since_organic = 0
    seen_organic = False
    for row in rows:  # newest-first
        origin = normalize_receipt_origin(_row_cloud_trigger(row))
        recorded_at = row.get("recorded_at")
        # §1: an organic row contributes ONLY if it is a successful terminal.
        if is_organic_origin(origin) and row_successful_terminal(row):
            if organic_at is None:
                organic_at = recorded_at
            seen_organic = True
        # §2: only ORIGIN_REPAIR counts as repair-sustained evidence.
        # local_reference/manual/test/replay/migration stay separate non-production.
        elif origin == ORIGIN_REPAIR:
            if repair_at is None:
                repair_at = recorded_at
            if not seen_organic:
                repair_since_organic += 1
    organic_age = age_fn(organic_at) if organic_at is not None else None
    repair_age = age_fn(repair_at) if repair_at is not None else None
    return {
        "completion_origin": newest_origin,
        "completion_terminal_valid": newest_terminal_valid,
        "organic_completion_age_minutes": organic_age,
        "repair_completion_age_minutes": repair_age,
        "metrics": {
            "last_organic_completion_at": organic_at,
            "organic_completion_age_minutes": organic_age,
            "last_repair_receipt_at": repair_at,
            "repair_receipt_age_minutes": repair_age,
            "repair_receipts_since_last_organic": repair_since_organic,
        },
    }


def _fresh_label(age_minutes: float | None, threshold_minutes: float | None, *, query_ok: bool) -> str:
    if not query_ok:
        return UNKNOWN
    if age_minutes is None or threshold_minutes is None:
        return UNKNOWN
    return FRESH if age_minutes <= threshold_minutes else STALE


def classify_loop_state(
    *,
    dispatch_age_minutes: float | None,
    dispatch_stale_threshold_minutes: float | None,
    completion_age_minutes: float | None,
    completion_stale_threshold_minutes: float | None,
    dispatch_query_ok: bool = True,
    completion_query_ok: bool = True,
    dispatch_last_fired_at: str | None = None,
    completion_last_recorded_at: str | None = None,
    observed_at: str | None = None,
    status_source: str = "noos_loop_registry+noetfield_factory_cycle_runs",
    success_rate_sample_window_minutes: float | None = None,
    # ---- Provenance-aware inputs (opt-in; default keeps legacy behavior) -----
    completion_origin: str | None = None,
    organic_completion_age_minutes: float | None = None,
    repair_completion_age_minutes: float | None = None,
    completion_terminal_valid: bool = True,
    consistency_ok: bool = True,
    expected_idle: bool = False,
    provenance_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the explicit dual-signal classification for one loop.

    ``dispatch_*`` comes from the execution dispatch heartbeat
    (noos_loop_registry.last_fired_at). ``completion_*`` comes from the
    per-loop completion receipt (noetfield_factory_cycle_runs.recorded_at).
    ``*_query_ok`` is False when that authoritative source could not be read.

    PROVENANCE-AWARENESS (NF-NOOS-MOTOR-V1-FULL-RUNWAY, Phase 4): the optional
    ``completion_origin`` / ``organic_completion_age_minutes`` /
    ``repair_completion_age_minutes`` / ``consistency_ok`` / ``expected_idle``
    inputs engage a provenance-aware decision. Its DESIGN LAW:

      * RUNNING_CONFIRMED requires *fresh ORGANIC completion evidence*. A
        repair/replay/manual completion, however fresh by age, can NEVER promote
        a loop to RUNNING_CONFIRMED — it yields DEGRADED_REPAIR_SUSTAINED.
      * An organic stall while the sink/writer is healthy escalates
        (ROUTE_ORGANIC_PRODUCER_ESCALATION); it never loops back to
        receipt-writer repair (that is what masked the 2026-07-12 stall).

    When NONE of the provenance inputs are supplied, the classifier falls back to
    the original age-only dual-signal logic (backward compatible).

    The result carries both signals separately plus the derived state — the
    cockpit renders every field; nothing is collapsed.
    """
    dispatch_fresh_label = _fresh_label(
        dispatch_age_minutes, dispatch_stale_threshold_minutes, query_ok=dispatch_query_ok
    )
    completion_fresh_label = _fresh_label(
        completion_age_minutes, completion_stale_threshold_minutes, query_ok=completion_query_ok
    )

    provenance_aware = (
        completion_origin is not None
        or organic_completion_age_minutes is not None
        or repair_completion_age_minutes is not None
        or completion_terminal_valid is False
        or consistency_ok is False
        or expected_idle is True
    )
    norm_origin = (
        normalize_receipt_origin(completion_origin) if completion_origin is not None else None
    )

    # OBSERVER_UNAVAILABLE — either authoritative source cannot be queried, or a
    # queried source returned no usable timestamp (age is None despite ok).
    dispatch_usable = dispatch_query_ok and dispatch_age_minutes is not None
    completion_usable = completion_query_ok and completion_age_minutes is not None
    if not dispatch_query_ok or not completion_query_ok or not dispatch_usable or not completion_usable:
        # If exactly one side is usable and it is a *fresh completion while
        # dispatch is unobservable*, that is still an observer problem, not a
        # confirmed run — fall through to OBSERVER_UNAVAILABLE.
        state = OBSERVER_UNAVAILABLE
        return _assemble(
            state,
            dispatch_fresh_label=dispatch_fresh_label,
            completion_fresh_label=completion_fresh_label,
            dispatch_last_fired_at=dispatch_last_fired_at,
            completion_last_recorded_at=completion_last_recorded_at,
            dispatch_age_minutes=dispatch_age_minutes,
            completion_age_minutes=completion_age_minutes,
            observed_at=observed_at,
            status_source=status_source,
            success_rate_sample_window_minutes=success_rate_sample_window_minutes,
            provenance=_provenance_block(
                norm_origin, organic_completion_age_minutes,
                repair_completion_age_minutes, consistency_ok, provenance_metrics,
                organic_fresh=None, repair_fresh=None, provenance_aware=provenance_aware,
            ),
        )

    dispatch_fresh = dispatch_fresh_label == FRESH
    completion_fresh = completion_fresh_label == FRESH

    if not provenance_aware:
        # ---- Legacy age-only dual-signal path (unchanged) -------------------
        if dispatch_fresh and completion_fresh:
            state = RUNNING_CONFIRMED
        elif dispatch_fresh and not completion_fresh:
            state = DISPATCHING_COMPLETION_UNPROVEN
        elif not dispatch_fresh and completion_fresh:
            state = OBSERVER_DIVERGENCE_OR_REPLAY
        else:
            state = LOOP_EXECUTION_STALE
        organic_fresh = None
        repair_fresh = None
    else:
        # ---- Provenance-aware path ------------------------------------------
        thresh = completion_stale_threshold_minutes
        if organic_completion_age_minutes is not None and thresh is not None:
            # derive_completion_provenance already restricts this to a SUCCESSFUL
            # terminal organic row (§1), so age within SLO is sufficient here.
            organic_fresh = organic_completion_age_minutes <= thresh
        elif norm_origin is not None:
            # No separate organic age: the newest completion is organic-fresh only
            # if it is genuinely organic, fresh by age, AND a SUCCESSFUL terminal
            # (§1 — a fresh but failed organic row must not confirm).
            organic_fresh = (
                is_organic_origin(norm_origin) and completion_fresh and completion_terminal_valid
            )
        else:
            organic_fresh = False

        # §2: ONLY ORIGIN_REPAIR is repair-sustained evidence. local_reference /
        # manual / test / replay / migration are separate non-production evidence
        # and never count as repair masking.
        if repair_completion_age_minutes is not None and thresh is not None:
            repair_fresh = repair_completion_age_minutes <= thresh
        elif norm_origin == ORIGIN_REPAIR:
            repair_fresh = completion_fresh
        else:
            repair_fresh = False

        if not consistency_ok:
            state = EVIDENCE_INCONSISTENT
        elif dispatch_fresh and organic_fresh:
            state = RUNNING_CONFIRMED  # only reachable with FRESH ORGANIC evidence
        elif dispatch_fresh and not organic_fresh:
            # Dispatch active but no fresh organic proof. If a non-organic
            # (repair) completion is keeping the row fresh -> repair masking;
            # otherwise the organic completion is simply unproven.
            state = DEGRADED_REPAIR_SUSTAINED if repair_fresh else COMPLETION_UNPROVEN
        elif not dispatch_fresh and organic_fresh:
            state = OBSERVER_DIVERGENCE_OR_REPLAY
        else:
            # dispatch stale AND organic stale.
            if repair_fresh:
                state = DEGRADED_REPAIR_SUSTAINED  # repair masking both dead signals
            elif expected_idle:
                state = STOPPED_OR_IDLE  # inactivity expected by configuration
            else:
                state = LOOP_EXECUTION_STALE

    return _assemble(
        state,
        dispatch_fresh_label=dispatch_fresh_label,
        completion_fresh_label=completion_fresh_label,
        dispatch_last_fired_at=dispatch_last_fired_at,
        completion_last_recorded_at=completion_last_recorded_at,
        dispatch_age_minutes=dispatch_age_minutes,
        completion_age_minutes=completion_age_minutes,
        observed_at=observed_at,
        status_source=status_source,
        success_rate_sample_window_minutes=success_rate_sample_window_minutes,
        provenance=_provenance_block(
            norm_origin, organic_completion_age_minutes,
            repair_completion_age_minutes, consistency_ok, provenance_metrics,
            organic_fresh=organic_fresh, repair_fresh=repair_fresh,
            provenance_aware=provenance_aware,
        ),
    )


def _provenance_block(
    norm_origin: str | None,
    organic_completion_age_minutes: float | None,
    repair_completion_age_minutes: float | None,
    consistency_ok: bool,
    provenance_metrics: dict[str, Any] | None,
    *,
    organic_fresh: bool | None,
    repair_fresh: bool | None,
    provenance_aware: bool,
) -> dict[str, Any] | None:
    """Assemble the separated organic/repair evidence block the cockpit needs to
    tell organic liveness from repair-sustained freshness. ``None`` when the
    caller supplied no provenance signal (pure legacy call)."""
    if not provenance_aware:
        return None
    m = provenance_metrics or {}
    return {
        "completion_origin": norm_origin,
        "organic_completion_fresh": organic_fresh,
        "repair_sustained_fresh": repair_fresh,
        "consistency_ok": consistency_ok,
        # Separated metrics (directive Phase 4). Unknown -> None / 0, never faked.
        "last_organic_completion_at": m.get("last_organic_completion_at"),
        "organic_completion_age_minutes": (
            organic_completion_age_minutes
            if organic_completion_age_minutes is not None
            else m.get("organic_completion_age_minutes")
        ),
        "last_repair_receipt_at": m.get("last_repair_receipt_at"),
        "repair_receipt_age_minutes": (
            repair_completion_age_minutes
            if repair_completion_age_minutes is not None
            else m.get("repair_receipt_age_minutes")
        ),
        "repair_receipts_since_last_organic": m.get("repair_receipts_since_last_organic"),
        "last_dispatch_at": m.get("last_dispatch_at"),
        "oldest_unresolved_dispatch_at": m.get("oldest_unresolved_dispatch_at"),
        "unresolved_dispatch_count": m.get("unresolved_dispatch_count"),
        "dead_letter_count": m.get("dead_letter_count"),
    }


def _assemble(
    state: str,
    *,
    dispatch_fresh_label: str,
    completion_fresh_label: str,
    dispatch_last_fired_at: str | None,
    completion_last_recorded_at: str | None,
    dispatch_age_minutes: float | None,
    completion_age_minutes: float | None,
    observed_at: str | None,
    status_source: str,
    success_rate_sample_window_minutes: float | None,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    success_rate = success_rate_for_state(state)
    evidence_state = evidence_state_for(state)
    route = route_for_state(state)
    presentation = {
        "dispatch_last_fired_at": dispatch_last_fired_at,
        "completion_last_recorded_at": completion_last_recorded_at,
        "dispatch_freshness": dispatch_fresh_label,
        "completion_evidence_freshness": completion_fresh_label,
        "dispatch_age_minutes": dispatch_age_minutes,
        "completion_age_minutes": completion_age_minutes,
        "current_execution_state": state,
        "observation_confidence": _STATE_CONFIDENCE.get(state, "NONE"),
        "success_rate_sample_window_minutes": success_rate_sample_window_minutes,
        "status_source": status_source,
        "observed_at": observed_at,
    }
    result: dict[str, Any] = {
        "execution_state": state,
        "success_rate": success_rate,
        "evidence_state": evidence_state,
        "route": route,
        "route_permits_execution_mutation": route_permits_execution_mutation(route),
        "observation_confidence": _STATE_CONFIDENCE.get(state, "NONE"),
        # cockpit presentation block — every signal shown separately
        "presentation": presentation,
    }
    if provenance is not None:
        # Primary liveness decision uses ORGANIC evidence; the cockpit shows the
        # organic-vs-repair split so repair freshness can never read as organic.
        result["provenance"] = provenance
        presentation["completion_origin"] = provenance.get("completion_origin")
        presentation["organic_completion_fresh"] = provenance.get("organic_completion_fresh")
        presentation["repair_sustained_fresh"] = provenance.get("repair_sustained_fresh")
    return result


# ---- Reconciler queue classification --------------------------------------
QUEUE_CATEGORIES = (
    "new_dispatches",
    "actionable_pending",
    "active_leases",
    "backoff_pending",
    "deduplicated",
    "completed_unreflected",
    "orphaned_backlog",
    "unknown",
)


def classify_pending_item(
    item: dict[str, Any],
    *,
    now_ts: float,
    orphan_age_days: float = 3.0,
    item_age_ts: float | None = None,
) -> str:
    """Classify a single pending dispatch-queue item into one QUEUE_CATEGORIES
    bucket. Pure: caller supplies ``now_ts`` and the item's age timestamp.

    Heuristics (conservative — unknown beats a wrong confident label):
      * explicit lease/backoff/completed fields win;
      * repair dispatches sourced from an outside-audit receipt older than
        ``orphan_age_days`` with no consumer -> orphaned_backlog;
      * otherwise actionable_pending, else unknown.
    """
    if item.get("lease") or item.get("active_lease") or item.get("leased_until"):
        return "active_leases"
    if item.get("backoff_until") or item.get("in_backoff"):
        return "backoff_pending"
    if item.get("completed") or item.get("completed_unreflected"):
        return "completed_unreflected"

    src = str(item.get("source_receipt_path") or "")
    # Prefer an explicit created_at; otherwise derive age from the timestamp
    # embedded in the source-receipt filename (e.g. ...-20260705T123204Z.json).
    age_ts = item_age_ts
    if age_ts is None:
        age_ts = _parse_epoch(item.get("created_at"))
    if age_ts is None:
        age_ts = _epoch_from_path(src)
    is_old = age_ts is not None and (now_ts - age_ts) > orphan_age_days * 86400.0
    looks_orphan_source = "outside-audit" in src or item.get("orphaned") is True
    if looks_orphan_source and (is_old or item.get("orphaned") is True):
        return "orphaned_backlog"

    if item.get("schema") == "noos-machine-repair-dispatch-v1":
        # A repair dispatch with no lease/backoff and a resolvable, recent
        # source is actionable; an unresolvable/old one is orphaned.
        if is_old:
            return "orphaned_backlog"
        return "actionable_pending"

    if item.get("actionable") is True:
        return "actionable_pending"
    return "unknown"


def summarize_pending(
    pending: list[dict[str, Any]],
    *,
    new_dispatches: int,
    now_ts: float,
    orphan_age_days: float = 3.0,
    dedup_count: int = 0,
) -> dict[str, Any]:
    counts = {cat: 0 for cat in QUEUE_CATEGORIES}
    counts["new_dispatches"] = int(new_dispatches)
    counts["deduplicated"] = int(dedup_count)
    per_item: list[dict[str, Any]] = []
    for item in pending:
        cat = classify_pending_item(item, now_ts=now_ts, orphan_age_days=orphan_age_days)
        counts[cat] += 1
        per_item.append({"source_receipt_path": item.get("source_receipt_path"), "category": cat})
    return {
        "counts": counts,
        "pending_total": len(pending),
        "items": per_item,
    }


def _epoch_from_path(path: str) -> float | None:
    """Extract an epoch from a receipt filename timestamp like
    ``...-20260705T123204Z.json`` or ``...-20260705.json``."""
    import re
    from datetime import datetime, timezone

    m = re.search(r"(\d{8})T(\d{6})Z", path)
    if m:
        try:
            dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except ValueError:
            return None
    m = re.search(r"(\d{8})(?:[^\d]|$)", path)
    if m:
        try:
            dt = datetime.strptime(m.group(1), "%Y%m%d").replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except ValueError:
            return None
    return None


def _parse_epoch(ts: Any) -> float | None:
    if ts is None:
        return None
    try:
        from datetime import datetime, timezone

        text = str(ts).strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except (ValueError, TypeError):
        return None
