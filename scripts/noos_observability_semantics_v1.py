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
}

# success_rate per state. ``None`` means "no trustworthy recent sample" and MUST
# be surfaced as evidence_state=INSUFFICIENT_RECENT_EVIDENCE, never as 0.0.
_STATE_SUCCESS_RATE: dict[str, float | None] = {
    RUNNING_CONFIRMED: 1.0,
    DISPATCHING_COMPLETION_UNPROVEN: None,
    OBSERVER_DIVERGENCE_OR_REPLAY: None,
    LOOP_EXECUTION_STALE: 0.0,  # both signals confirm real execution staleness
    OBSERVER_UNAVAILABLE: None,
}

# States whose evidence is sufficient to *act on* (confirmed running, or
# confirmed stale). Everything else is evidence-insufficient by construction.
_STATE_EVIDENCE = {
    RUNNING_CONFIRMED: EVIDENCE_SUFFICIENT,
    LOOP_EXECUTION_STALE: EVIDENCE_SUFFICIENT,
    DISPATCHING_COMPLETION_UNPROVEN: EVIDENCE_INSUFFICIENT,
    OBSERVER_DIVERGENCE_OR_REPLAY: EVIDENCE_INSUFFICIENT,
    OBSERVER_UNAVAILABLE: EVIDENCE_INSUFFICIENT,
}

_STATE_CONFIDENCE = {
    RUNNING_CONFIRMED: "HIGH",
    LOOP_EXECUTION_STALE: "HIGH",
    DISPATCHING_COMPLETION_UNPROVEN: "LOW",
    OBSERVER_DIVERGENCE_OR_REPLAY: "LOW",
    OBSERVER_UNAVAILABLE: "NONE",
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
    routes must never trigger a runner restart or redeploy."""
    return route in EXECUTION_MUTATING_ROUTES


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
) -> dict[str, Any]:
    """Return the explicit dual-signal classification for one loop.

    ``dispatch_*`` comes from the execution dispatch heartbeat
    (noos_loop_registry.last_fired_at). ``completion_*`` comes from the
    per-loop completion receipt (noetfield_factory_cycle_runs.recorded_at).
    ``*_query_ok`` is False when that authoritative source could not be read.

    The result carries both signals separately plus the derived state — the
    cockpit renders every field; nothing is collapsed.
    """
    dispatch_fresh_label = _fresh_label(
        dispatch_age_minutes, dispatch_stale_threshold_minutes, query_ok=dispatch_query_ok
    )
    completion_fresh_label = _fresh_label(
        completion_age_minutes, completion_stale_threshold_minutes, query_ok=completion_query_ok
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
        )

    dispatch_fresh = dispatch_fresh_label == FRESH
    completion_fresh = completion_fresh_label == FRESH

    if dispatch_fresh and completion_fresh:
        state = RUNNING_CONFIRMED
    elif dispatch_fresh and not completion_fresh:
        state = DISPATCHING_COMPLETION_UNPROVEN
    elif not dispatch_fresh and completion_fresh:
        # Completion looks fresh while dispatch heartbeat is stale/inconsistent
        # or temporally impossible — trust neither; this is observer divergence
        # or a replay, not a confirmed run.
        state = OBSERVER_DIVERGENCE_OR_REPLAY
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
    )


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
) -> dict[str, Any]:
    success_rate = success_rate_for_state(state)
    evidence_state = evidence_state_for(state)
    route = route_for_state(state)
    return {
        "execution_state": state,
        "success_rate": success_rate,
        "evidence_state": evidence_state,
        "route": route,
        "route_permits_execution_mutation": route_permits_execution_mutation(route),
        "observation_confidence": _STATE_CONFIDENCE.get(state, "NONE"),
        # cockpit presentation block — every signal shown separately
        "presentation": {
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
        },
    }


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
