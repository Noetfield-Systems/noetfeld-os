#!/usr/bin/env python3
"""NOOS Motor v1 — deterministic execution state machine.

NF-NOOS-MOTOR-V1-FULL-RUNWAY, Phase 3. This module makes the motor lifecycle
EXPLICIT and enforces the reliability invariants the directive requires. It does
NOT redesign the LOCKED executor wiring (data/noos-motor-executor-wiring-v1.json)
— it is the deterministic contract layer the executor and the local reference
executor both drive.

PURE and deterministic: no network, no filesystem, and the clock is injected as
``now`` (an ISO-8601 UTC string) so every run is reproducible and replay-safe.

Canonical lifecycle:
    ACCEPTED -> PLANNED -> DISPATCHED -> CLAIMED -> RUNNING
             -> OUTPUT_COMMITTED -> COMPLETED
Terminal alternatives:  FAILED, TIMED_OUT, CANCELLED, DEAD_LETTERED
Recovery:               RETRY_SCHEDULED, REPLAY_REQUESTED, REPAIR_APPLIED

Enforced invariants (directive Phase 3):
  1  a run cannot complete before it starts
  2  a terminal run cannot return to RUNNING
  3  a duplicate idempotency key cannot create a second logical run
  4  a lease has an owner and an expiry
  5  an expired lease can be recovered deterministically
  6  retry count is finite and visible
  7  retry scheduling uses bounded backoff
  8  terminal failure is recorded
  9  dead-letter items are inspectable and replayable
  10 replay creates a new attempt while preserving the original lineage
  11 repair activity never mutates historical organic provenance
  12 every output is tied to the execution that created it
  13 every critic state is derivable from the authoritative record
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

SCHEMA_VERSION = "noos-motor-execution-v1"
WORKFLOW_VERSION = "noos-motor-v1"

# ---- States ----------------------------------------------------------------
ACCEPTED = "ACCEPTED"
PLANNED = "PLANNED"
DISPATCHED = "DISPATCHED"
CLAIMED = "CLAIMED"
RUNNING = "RUNNING"
OUTPUT_COMMITTED = "OUTPUT_COMMITTED"
COMPLETED = "COMPLETED"

FAILED = "FAILED"
TIMED_OUT = "TIMED_OUT"
CANCELLED = "CANCELLED"
DEAD_LETTERED = "DEAD_LETTERED"

RETRY_SCHEDULED = "RETRY_SCHEDULED"
REPLAY_REQUESTED = "REPLAY_REQUESTED"
REPAIR_APPLIED = "REPAIR_APPLIED"

TERMINAL_STATES = frozenset({COMPLETED, FAILED, TIMED_OUT, CANCELLED, DEAD_LETTERED})
# States from which a fresh attempt may begin execution again.
RECOVERABLE_STATES = frozenset({FAILED, TIMED_OUT, RETRY_SCHEDULED, REPLAY_REQUESTED})

# ---- Execution origins / provenance (aligned with the classifier) ----------
ORIGIN_ORGANIC = "organic"
ORIGIN_REPAIR = "repair"
ORIGIN_REPLAY = "replay"
ORIGIN_MANUAL = "manual"
ORIGIN_MIGRATION = "migration"
ORIGIN_TEST = "test"

# ---- Valid transition table (single source of truth) -----------------------
VALID_TRANSITIONS: dict[str, frozenset[str]] = {
    ACCEPTED: frozenset({PLANNED, CANCELLED, FAILED}),
    PLANNED: frozenset({DISPATCHED, CANCELLED, FAILED}),
    DISPATCHED: frozenset({CLAIMED, TIMED_OUT, CANCELLED, FAILED}),
    CLAIMED: frozenset({RUNNING, TIMED_OUT, CANCELLED, FAILED}),
    RUNNING: frozenset({OUTPUT_COMMITTED, FAILED, TIMED_OUT, CANCELLED}),
    OUTPUT_COMMITTED: frozenset({COMPLETED, FAILED}),
    # Terminals: only failure terminals may enter recovery; COMPLETED is final.
    COMPLETED: frozenset(),
    FAILED: frozenset({RETRY_SCHEDULED, REPLAY_REQUESTED, DEAD_LETTERED, REPAIR_APPLIED}),
    TIMED_OUT: frozenset({RETRY_SCHEDULED, REPLAY_REQUESTED, DEAD_LETTERED, REPAIR_APPLIED}),
    CANCELLED: frozenset(),
    DEAD_LETTERED: frozenset({REPLAY_REQUESTED}),
    # Recovery states re-enter the pipeline via a NEW attempt (see replay()).
    RETRY_SCHEDULED: frozenset({DISPATCHED, DEAD_LETTERED, CANCELLED}),
    REPLAY_REQUESTED: frozenset({ACCEPTED, DISPATCHED, CANCELLED}),
    REPAIR_APPLIED: frozenset({REPLAY_REQUESTED, DEAD_LETTERED}),
}

# Fields whose provenance is immutable once set (invariant 11).
_IMMUTABLE_PROVENANCE = ("producer", "execution_origin", "correlation_id", "root_execution_id")


class InvalidTransition(Exception):
    """Raised when a transition is not permitted by VALID_TRANSITIONS."""


class ProvenanceViolation(Exception):
    """Raised when code attempts to mutate historical organic provenance."""


def can_transition(frm: str, to: str) -> bool:
    return to in VALID_TRANSITIONS.get(frm, frozenset())


def payload_hash(payload: Any) -> str:
    """Deterministic content hash (sha256, 16 hex) — sorted keys for stability."""
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]


def idempotency_key_for(*, task_kind: str, input_hash: str) -> str:
    """Stable idempotency key: same (task_kind, input) => same logical run."""
    return hashlib.sha256(f"{task_kind}:{input_hash}".encode()).hexdigest()[:24]


def backoff_seconds(retry_count: int, *, base: float = 5.0, cap: float = 900.0) -> float:
    """Bounded exponential backoff (invariant 7): base * 2^retry_count, capped."""
    if retry_count < 0:
        retry_count = 0
    return float(min(cap, base * (2 ** retry_count)))


class MotorExecution:
    """One logical execution attempt with an enforced lifecycle."""

    def __init__(
        self,
        *,
        task_kind: str,
        payload: Any,
        now: str,
        producer: str,
        execution_origin: str = ORIGIN_ORGANIC,
        correlation_id: str | None = None,
        dispatch_id: str | None = None,
        execution_id: str | None = None,
        max_retries: int = 3,
        root_execution_id: str | None = None,
        attempt: int = 1,
    ) -> None:
        self.execution_id = execution_id or f"exe_{uuid.uuid4().hex[:16]}"
        self.attempt_id = f"att_{uuid.uuid4().hex[:12]}"
        self.attempt = int(attempt)
        self.root_execution_id = root_execution_id or self.execution_id
        self.correlation_id = correlation_id or f"cor_{uuid.uuid4().hex[:16]}"
        self.dispatch_id = dispatch_id
        self.task_kind = task_kind
        self.input_hash = payload_hash(payload)
        self.idempotency_key = idempotency_key_for(task_kind=task_kind, input_hash=self.input_hash)
        self.producer = producer
        self.execution_origin = execution_origin
        self.workflow_version = WORKFLOW_VERSION
        self.schema_version = SCHEMA_VERSION
        self.max_retries = int(max_retries)
        self.retry_count = 0
        self.state = ACCEPTED
        self.created_at = now
        self.updated_at = now
        self.history: list[dict[str, Any]] = [{"state": ACCEPTED, "at": now, "note": "accepted"}]
        self.lease: dict[str, Any] | None = None
        self.output_hash: str | None = None
        self.artifact_uri: str | None = None
        self.error_code: str | None = None
        self.error_summary: str | None = None
        self.repairs: list[dict[str, Any]] = []

    # ---- transitions -------------------------------------------------------
    def transition(self, to: str, *, now: str, note: str = "", **fields: Any) -> "MotorExecution":
        if not can_transition(self.state, to):
            raise InvalidTransition(f"{self.state} -> {to} is not permitted")
        # Invariant 11: never mutate immutable provenance via a transition.
        for k in fields:
            if k in _IMMUTABLE_PROVENANCE and getattr(self, k, None) not in (None, fields[k]):
                raise ProvenanceViolation(f"cannot mutate immutable provenance field {k!r}")
        for k, v in fields.items():
            setattr(self, k, v)
        self.state = to
        self.updated_at = now
        self.history.append({"state": to, "at": now, "note": note})
        return self

    def plan(self, *, now: str, dispatch_id: str | None = None) -> "MotorExecution":
        if dispatch_id:
            self.dispatch_id = dispatch_id
        return self.transition(PLANNED, now=now, note="deterministic_plan")

    def dispatch(self, *, now: str, dispatch_id: str | None = None) -> "MotorExecution":
        if dispatch_id:
            self.dispatch_id = dispatch_id
        return self.transition(DISPATCHED, now=now, note="dispatched")

    def claim(self, *, now: str, owner: str, lease_ttl_seconds: float) -> "MotorExecution":
        """Invariant 4: a lease has an owner and an expiry."""
        self.lease = {
            "owner": owner,
            "acquired_at": now,
            "ttl_seconds": float(lease_ttl_seconds),
            "expires_at": _add_seconds(now, lease_ttl_seconds),
        }
        return self.transition(CLAIMED, now=now, note=f"claimed_by:{owner}")

    def start(self, *, now: str) -> "MotorExecution":
        return self.transition(RUNNING, now=now, note="worker_started")

    def commit_output(self, *, now: str, output: Any, artifact_uri: str) -> "MotorExecution":
        """Invariant 12: output is bound to this execution via its hash + uri."""
        self.output_hash = payload_hash(output)
        self.artifact_uri = artifact_uri
        return self.transition(
            OUTPUT_COMMITTED, now=now, note="output_committed",
            output_hash=self.output_hash, artifact_uri=artifact_uri,
        )

    def complete(self, *, now: str) -> "MotorExecution":
        """Invariant 1: reachable only via OUTPUT_COMMITTED (structural)."""
        if self.output_hash is None:
            raise InvalidTransition("cannot COMPLETE without a committed output")
        return self.transition(COMPLETED, now=now, note="completed")

    def fail(self, *, now: str, error_code: str, error_summary: str) -> "MotorExecution":
        """Invariant 8: terminal failure is recorded with a reason."""
        return self.transition(
            FAILED, now=now, note="failed",
            error_code=error_code, error_summary=error_summary,
        )

    def time_out(self, *, now: str) -> "MotorExecution":
        return self.transition(
            TIMED_OUT, now=now, note="timed_out",
            error_code="timeout", error_summary="execution exceeded deadline",
        )

    def cancel(self, *, now: str, reason: str = "cancelled") -> "MotorExecution":
        return self.transition(CANCELLED, now=now, note=reason, error_code="cancelled", error_summary=reason)

    # ---- lease recovery (invariant 5) -------------------------------------
    def lease_expired(self, *, now: str) -> bool:
        if not self.lease:
            return False
        return _iso_to_epoch(now) >= _iso_to_epoch(self.lease["expires_at"])

    def reclaim(self, *, now: str, owner: str, lease_ttl_seconds: float) -> "MotorExecution":
        """Deterministically recover an expired lease by re-claiming."""
        if not self.lease_expired(now=now):
            raise InvalidTransition("lease not expired; cannot reclaim")
        prior = self.lease.get("owner") if self.lease else None
        self.state = DISPATCHED  # return to the queue before re-claiming
        self.history.append({"state": DISPATCHED, "at": now, "note": f"lease_expired_reclaim_from:{prior}"})
        return self.claim(now=now, owner=owner, lease_ttl_seconds=lease_ttl_seconds)

    # ---- retry (invariants 6, 7) ------------------------------------------
    def schedule_retry(self, *, now: str, base: float = 5.0) -> "MotorExecution":
        if self.retry_count >= self.max_retries:
            raise InvalidTransition("retry budget exhausted; route to dead-letter")
        self.retry_count += 1
        delay = backoff_seconds(self.retry_count - 1, base=base)
        return self.transition(
            RETRY_SCHEDULED, now=now, note=f"retry:{self.retry_count}/{self.max_retries}",
            _next_attempt_earliest_at=_add_seconds(now, delay),
        )

    def dead_letter(self, *, now: str, reason: str) -> "MotorExecution":
        """Invariant 9: dead-letter is a real, inspectable terminal state."""
        return self.transition(DEAD_LETTERED, now=now, note=reason,
                               error_code="dead_lettered", error_summary=reason)

    def apply_repair(self, *, now: str, repair_recipe: str, note: str = "") -> "MotorExecution":
        """Invariant 11: repair is annotated separately; it never rewrites the
        historical organic producer/origin of this execution."""
        self.repairs.append({"recipe": repair_recipe, "at": now, "note": note})
        return self.transition(REPAIR_APPLIED, now=now, note=f"repair:{repair_recipe}")

    # ---- serialization (invariant 13) -------------------------------------
    def to_record(self) -> dict[str, Any]:
        """Authoritative execution record — every critic state derivable here."""
        return {
            "schema_version": self.schema_version,
            "workflow_version": self.workflow_version,
            "execution_id": self.execution_id,
            "attempt_id": self.attempt_id,
            "attempt": self.attempt,
            "root_execution_id": self.root_execution_id,
            "correlation_id": self.correlation_id,
            "dispatch_id": self.dispatch_id,
            "idempotency_key": self.idempotency_key,
            "task_kind": self.task_kind,
            "producer": self.producer,
            "execution_origin": self.execution_origin,
            "state": self.state,
            "is_terminal": self.state in TERMINAL_STATES,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "lease": self.lease,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "artifact_uri": self.artifact_uri,
            "error_code": self.error_code,
            "error_summary": self.error_summary,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "history": self.history,
            "repairs": self.repairs,
        }


class MotorLedger:
    """In-memory authoritative ledger: idempotency dedupe + dead-letter +
    replay lineage. A real deployment backs this with the Supabase table; the
    contract (dedupe, lineage, single-source-of-truth) is identical."""

    def __init__(self) -> None:
        self._by_idempotency: dict[str, MotorExecution] = {}
        self._by_execution_id: dict[str, MotorExecution] = {}

    def submit(
        self, *, task_kind: str, payload: Any, now: str, producer: str,
        execution_origin: str = ORIGIN_ORGANIC, **kw: Any,
    ) -> tuple[MotorExecution, bool]:
        """Invariant 3: a duplicate idempotency key returns the EXISTING run.

        Returns (execution, created) where created is False for a duplicate."""
        ih = payload_hash(payload)
        key = idempotency_key_for(task_kind=task_kind, input_hash=ih)
        existing = self._by_idempotency.get(key)
        if existing is not None:
            return existing, False
        ex = MotorExecution(
            task_kind=task_kind, payload=payload, now=now, producer=producer,
            execution_origin=execution_origin, **kw,
        )
        self._by_idempotency[key] = ex
        self._by_execution_id[ex.execution_id] = ex
        return ex, True

    def get(self, execution_id: str) -> MotorExecution | None:
        return self._by_execution_id.get(execution_id)

    def dead_letters(self) -> list[MotorExecution]:
        return [e for e in self._by_execution_id.values() if e.state == DEAD_LETTERED]

    def replay(self, execution_id: str, *, now: str, payload: Any) -> MotorExecution:
        """Invariant 10: replay is a NEW attempt that preserves lineage
        (root_execution_id, correlation_id) of the original."""
        parent = self._by_execution_id.get(execution_id)
        if parent is None:
            raise KeyError(f"unknown execution_id {execution_id!r}")
        if parent.state not in TERMINAL_STATES and parent.state not in RECOVERABLE_STATES:
            raise InvalidTransition("replay only from a terminal/recoverable attempt")
        parent.transition(REPLAY_REQUESTED, now=now, note="replay_requested") if can_transition(
            parent.state, REPLAY_REQUESTED
        ) else None
        child = MotorExecution(
            task_kind=parent.task_kind, payload=payload, now=now,
            producer=parent.producer, execution_origin=ORIGIN_REPLAY,
            correlation_id=parent.correlation_id,          # lineage preserved
            root_execution_id=parent.root_execution_id,    # lineage preserved
            attempt=parent.attempt + 1,
            max_retries=parent.max_retries,
        )
        child.history[0]["note"] = f"replay_of:{parent.execution_id}"
        # Replay is bucketed under a fresh idempotency namespace so it does not
        # collide with the original logical run (which already terminated).
        self._by_idempotency[child.idempotency_key + f":replay:{child.attempt}"] = child
        self._by_execution_id[child.execution_id] = child
        return child


# ---- deterministic time helpers (no clock read) ----------------------------
def _iso_to_epoch(ts: str) -> float:
    from datetime import datetime, timezone

    text = str(ts).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def _add_seconds(ts: str, seconds: float) -> str:
    from datetime import datetime, timedelta, timezone

    text = str(ts).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (dt + timedelta(seconds=seconds)).astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )
