#!/usr/bin/env python3
"""Governed-autorun L13 / D1–D8 — deterministic loop primitives for NOOS."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

LEGAL_TRANSITIONS: dict[str, frozenset[str]] = {
    "IDLE_NO_WORK": frozenset({"RUNNING"}),
    "RUNNING": frozenset(
        {"COMPLETE", "FAILED_WITH_RECEIPT", "BLOCKED_WITH_REASON", "IDLE_NO_WORK", "TRIAGE_REQUIRED", "THROTTLED_ROI"}
    ),
    "COMPLETE": frozenset({"IDLE_NO_WORK", "RUNNING"}),
    "FAILED_WITH_RECEIPT": frozenset({"IDLE_NO_WORK", "RUNNING", "BLOCKED_WITH_REASON"}),
    "BLOCKED_WITH_REASON": frozenset({"IDLE_NO_WORK", "RUNNING"}),
    "TRIAGE_REQUIRED": frozenset({"IDLE_NO_WORK", "RUNNING", "BLOCKED_WITH_REASON"}),
    "THROTTLED_ROI": frozenset({"IDLE_NO_WORK", "RUNNING", "BLOCKED_WITH_REASON"}),
}


def op_key(*, workflow_id: str, loop_id: str, cycle_number: int) -> str:
    """D1 — deterministic side-effect key (no time/random)."""
    material = f"{workflow_id}|{loop_id}|cycle:{cycle_number}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def advance_state(
    *,
    no_work: bool,
    execute_ok: bool,
    validate_ok: bool,
    sink_acked: bool,
) -> tuple[str, str | None]:
    """D4 — advance := f(execute_ok AND validate_ok AND sink_acked)."""
    if no_work:
        return "IDLE_NO_WORK", None
    if not validate_ok:
        return "BLOCKED_WITH_REASON", "validate_ok=false"
    if not execute_ok:
        return "FAILED_WITH_RECEIPT", "execute_ok=false"
    if sink_acked:
        return "COMPLETE", None
    return "BLOCKED_WITH_REASON", "sink_unacked"


def transition_allowed(state_before: str, state_after: str) -> bool:
    allowed = LEGAL_TRANSITIONS.get(state_before, frozenset())
    return state_after in allowed


def cas_advance(expected: int, observed: int, new_value: int) -> dict[str, Any]:
    """D2 — compare-and-swap; mismatch = REJECTED receipt payload."""
    if observed != expected:
        return {
            "verdict": "REJECTED",
            "expected": expected,
            "observed": observed,
            "new_value": new_value,
            "reason": "cas_mismatch",
        }
    return {"verdict": "ACCEPTED", "expected": expected, "observed": observed, "new_value": new_value}


def fold_cycle_events(cycle_files: list[Path]) -> dict[str, Any]:
    """D5 — derive state from append-only cycle event files."""
    events: list[dict[str, Any]] = []
    for path in sorted(cycle_files):
        try:
            events.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    if not events:
        return {"cycle_number": 0, "last_state": "IDLE_NO_WORK", "events": 0}
    last = events[-1]
    return {
        "cycle_number": int(last.get("cycle_number") or len(events)),
        "last_state": last.get("state_after") or last.get("last_state") or "UNKNOWN",
        "last_status": last.get("status"),
        "events": len(events),
        "op_keys": [e.get("op_key") for e in events if e.get("op_key")],
    }


def replay_matches_state(cycle_files: list[Path], state_file: Path) -> dict[str, Any]:
    """D5 — rebuilt fold must match persisted state-v1.json."""
    folded = fold_cycle_events(cycle_files)
    if not state_file.is_file():
        return {"ok": False, "reason": "state_file_missing", "folded": folded}
    try:
        live = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "reason": str(exc), "folded": folded}
    ok = (
        int(live.get("cycle_number") or 0) == int(folded["cycle_number"])
        and str(live.get("last_state") or "") == str(folded["last_state"])
    )
    return {"ok": ok, "folded": folded, "live": live}
