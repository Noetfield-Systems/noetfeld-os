"""Control plane state machine — INITIATED through ARCHIVED."""

from __future__ import annotations

from enum import StrEnum


class ControlPlaneState(StrEnum):
    INITIATED = "INITIATED"
    INTENT_PARSED = "INTENT_PARSED"
    ROUTED = "ROUTED"
    GOVERNANCE_CHECKED = "GOVERNANCE_CHECKED"
    EXECUTED = "EXECUTED"
    ARCHIVED = "ARCHIVED"


CONTROL_PLANE_TRANSITIONS: dict[ControlPlaneState, ControlPlaneState] = {
    ControlPlaneState.INITIATED: ControlPlaneState.INTENT_PARSED,
    ControlPlaneState.INTENT_PARSED: ControlPlaneState.ROUTED,
    ControlPlaneState.ROUTED: ControlPlaneState.GOVERNANCE_CHECKED,
    ControlPlaneState.GOVERNANCE_CHECKED: ControlPlaneState.EXECUTED,
    ControlPlaneState.EXECUTED: ControlPlaneState.ARCHIVED,
}


def advance_control_plane(state: ControlPlaneState) -> ControlPlaneState:
    return CONTROL_PLANE_TRANSITIONS.get(state, state)


def initial_control_plane_state() -> ControlPlaneState:
    return ControlPlaneState.INITIATED
