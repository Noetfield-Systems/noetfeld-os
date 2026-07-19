"""Cloud CAS must follow Supabase max cycle_number so repair rows cannot desync organic writes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import noos_loop_runner_v1 as runner  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "RUNTIME", tmp_path)
    monkeypatch.setenv("NOOS_CLOUD_LOOP", "1")
    for key in (
        "NOETFIELD_SUPABASE_URL",
        "SUPABASE_URL",
        "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ):
        monkeypatch.delenv(key, raising=False)


def test_acquire_cycle_number_seeds_from_supabase_when_local_cas_lags(monkeypatch) -> None:
    monkeypatch.setattr(runner, "supabase_max_cycle_number", lambda factory_id: 1361 if factory_id == "loop-inbox" else None)
    number, meta = runner.acquire_cycle_number("inbox")
    assert number == 1362
    assert meta["cas"]["expected"] == 1361


def test_acquire_cycle_number_keeps_local_when_ahead_of_supabase(monkeypatch) -> None:
    runner.loop_state_path("runtime").parent.mkdir(parents=True, exist_ok=True)
    runner.loop_state_path("runtime").write_text(
        json.dumps({"cycle_number": 1400}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(runner, "supabase_max_cycle_number", lambda factory_id: 1361)
    number, _meta = runner.acquire_cycle_number("runtime")
    assert number == 1401
