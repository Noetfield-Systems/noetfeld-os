"""Repair fix 3 — sink_cycle() must not hang unbounded on a slow/stuck sink
subprocess, and must always clean up its temp file (success, failure, or
timeout)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import noos_loop_runner_v1 as runner  # noqa: E402


@pytest.fixture(autouse=True)
def _configured(monkeypatch):
    monkeypatch.setenv("NOETFIELD_SUPABASE_URL", "https://example.supabase.co")


def test_sink_cycle_timeout_returns_clean_dict_and_cleans_tmp(monkeypatch) -> None:
    seen_tmp_paths: list[str] = []

    def _raise(cmd, **_kwargs):
        seen_tmp_paths.append(cmd[2])
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=runner.SINK_TIMEOUT_SEC)

    monkeypatch.setattr(runner.subprocess, "run", _raise)
    result = runner.sink_cycle({"status": "ok"}, factory_id="f1")

    assert result["ok"] is False
    assert result["exit_code"] == -1
    assert f"sink_subprocess_timeout_{runner.SINK_TIMEOUT_SEC}s" in result["error"]
    assert len(seen_tmp_paths) == 1
    assert not Path(seen_tmp_paths[0]).exists(), "temp file must be cleaned up after a timeout"


def test_sink_cycle_success_path_still_cleans_tmp(monkeypatch) -> None:
    seen_tmp_paths: list[str] = []

    class _FakeCompletedProcess:
        returncode = 0
        stdout = '{"ok": true}'
        stderr = ""

    def _fake_run(cmd, **_kwargs):
        seen_tmp_paths.append(cmd[2])
        return _FakeCompletedProcess()

    monkeypatch.setattr(runner.subprocess, "run", _fake_run)
    result = runner.sink_cycle({"status": "ok"}, factory_id="f1")

    assert result["ok"] is True
    assert result["detail"] == {"ok": True}
    assert len(seen_tmp_paths) == 1
    assert not Path(seen_tmp_paths[0]).exists(), "temp file must be cleaned up on success too"


def test_sink_cycle_timeout_uses_configured_seconds(monkeypatch) -> None:
    captured_kwargs: dict = {}

    class _FakeCompletedProcess:
        returncode = 0
        stdout = ""
        stderr = ""

    def _fake_run(cmd, **kwargs):
        captured_kwargs.update(kwargs)
        return _FakeCompletedProcess()

    monkeypatch.setattr(runner.subprocess, "run", _fake_run)
    monkeypatch.setattr(runner, "SINK_TIMEOUT_SEC", 42)
    runner.sink_cycle({"status": "ok"}, factory_id="f1")

    assert captured_kwargs.get("timeout") == 42
