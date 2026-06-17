"""Tests for control plane state machine."""

from noetfield_governance.control_plane import (
    ControlPlaneState,
    advance_control_plane,
    initial_control_plane_state,
)


def test_initial_state() -> None:
    assert initial_control_plane_state() == ControlPlaneState.INITIATED


def test_full_transition_chain() -> None:
    state = ControlPlaneState.INITIATED
    expected = [
        ControlPlaneState.INTENT_PARSED,
        ControlPlaneState.ROUTED,
        ControlPlaneState.GOVERNANCE_CHECKED,
        ControlPlaneState.EXECUTED,
        ControlPlaneState.ARCHIVED,
    ]
    for next_state in expected:
        state = advance_control_plane(state)
        assert state == next_state


def test_terminal_state_stays() -> None:
    assert advance_control_plane(ControlPlaneState.ARCHIVED) == ControlPlaneState.ARCHIVED
