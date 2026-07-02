"""UPG-0214 / L13 — external-verify determinism gate (D1, D2, D5, transitions)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from noos_loop_determinism_v1 import (
    advance_state,
    cas_advance,
    fold_cycle_events,
    op_key,
    replay_matches_state,
    transition_allowed,
)


def test_d1_idempotency_op_key_stable():
    a = op_key(workflow_id="noos-inbox-loop.yml", loop_id="inbox", cycle_number=3)
    b = op_key(workflow_id="noos-inbox-loop.yml", loop_id="inbox", cycle_number=3)
    c = op_key(workflow_id="noos-inbox-loop.yml", loop_id="inbox", cycle_number=4)
    assert a == b
    assert a != c
    assert len(a) == 24


def test_d2_cas_rejects_stale_advance():
    accepted = cas_advance(expected=5, observed=5, new_value=6)
    rejected = cas_advance(expected=5, observed=4, new_value=6)
    assert accepted["verdict"] == "ACCEPTED"
    assert rejected["verdict"] == "REJECTED"


def test_d4_advance_requires_sink_ack():
    state, reason = advance_state(no_work=False, execute_ok=True, validate_ok=True, sink_acked=False)
    assert state == "BLOCKED_WITH_REASON"
    assert reason == "sink_unacked"
    ok_state, ok_reason = advance_state(no_work=False, execute_ok=True, validate_ok=True, sink_acked=True)
    assert ok_state == "COMPLETE"
    assert ok_reason is None


def test_d5_replay_fold_matches_state(tmp_path: Path):
    loop_dir = tmp_path / "inbox"
    loop_dir.mkdir()
    for n, state in ((1, "COMPLETE"), (2, "COMPLETE")):
        (loop_dir / f"cycle-{n:06d}.json").write_text(
            json.dumps(
                {
                    "cycle_number": n,
                    "state_after": state,
                    "status": "ok",
                    "op_key": op_key(workflow_id="wf.yml", loop_id="inbox", cycle_number=n),
                }
            )
            + "\n",
            encoding="utf-8",
        )
    state_file = loop_dir / "state-v1.json"
    state_file.write_text(
        json.dumps({"cycle_number": 2, "last_state": "COMPLETE", "last_status": "ok"}) + "\n",
        encoding="utf-8",
    )
    result = replay_matches_state(sorted(loop_dir.glob("cycle-*.json")), state_file)
    assert result["ok"] is True
    folded = fold_cycle_events(sorted(loop_dir.glob("cycle-*.json")))
    assert folded["events"] == 2
    assert folded["last_state"] == "COMPLETE"


@pytest.mark.parametrize(
    "before,after,ok",
    [
        ("IDLE_NO_WORK", "RUNNING", True),
        ("RUNNING", "COMPLETE", True),
        ("RUNNING", "BLOCKED_WITH_REASON", True),
        ("COMPLETE", "RUNNING", True),
        ("COMPLETE", "IDLE_NO_WORK", True),
        ("IDLE_NO_WORK", "COMPLETE", False),
        ("RUNNING", "TRIAGE_REQUIRED", True),
    ],
)
def test_illegal_transition_fuzz(before: str, after: str, ok: bool):
    assert transition_allowed(before, after) is ok
