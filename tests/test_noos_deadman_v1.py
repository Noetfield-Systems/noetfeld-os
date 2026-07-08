"""Phase B — deadman staleness math and restart cap."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from noos_deadman_v1 import cap_restart_attempts, evaluate_stale, is_stale, stale_minutes


def test_not_stale_within_window() -> None:
    now = datetime.now(timezone.utc)
    recent = now.isoformat().replace("+00:00", "Z")
    assert is_stale(recent, 5, multiplier=2.0) is False


def test_stale_past_double_interval() -> None:
    old = datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    assert is_stale(old, 5, multiplier=2.0) is True


def test_stale_minutes_positive_when_late() -> None:
    old = datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    assert stale_minutes(old, 5, multiplier=2.0) is not None
    assert stale_minutes(old, 5, multiplier=2.0) > 0


def test_never_fired_is_stale() -> None:
    assert is_stale(None, 10, multiplier=2.0) is True


def test_restart_attempts_capped() -> None:
    stale = [
        {"loop_id": "a", "event_type": "e1"},
        {"loop_id": "b", "event_type": "e2"},
        {"loop_id": "c", "event_type": "e3"},
    ]
    attempts, skipped = cap_restart_attempts(stale, max_attempts=1)
    assert len(attempts) == 1
    assert len(skipped) == 2
    assert skipped[0]["reason"] == "restart_attempts_max"


def test_evaluate_stale_marks_missing_registry_rows() -> None:
    intervals = {
        "inbox": {"loop_id": "inbox", "event_type": "noos_inbox_loop_tick", "interval_minutes": 5},
    }
    stale = evaluate_stale([], intervals=intervals, multiplier=2.0)
    assert len(stale) == 1
    assert stale[0]["loop_id"] == "inbox"
    assert stale[0]["reason"] == "never_fired"
