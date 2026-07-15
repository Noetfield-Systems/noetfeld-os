"""Repair fix 5 — Railway /health and /health/deep must reflect real write-path
liveness, not just process-alive. Before this, _ready was set once at process
start and never touched again; neither endpoint probed Supabase or write
recency, which is exactly why health stayed green while noos_loop_registry
writes silently died."""

from __future__ import annotations

import importlib.util
import sys
import urllib.error
from pathlib import Path

import pytest

_SERVER_PATH = (
    Path(__file__).resolve().parents[1] / "ops" / "railway" / "noos-loop-runner" / "server.py"
)
_spec = importlib.util.spec_from_file_location("noos_railway_server", _SERVER_PATH)
server = importlib.util.module_from_spec(_spec)
sys.modules["noos_railway_server"] = server
_spec.loader.exec_module(server)  # type: ignore[union-attr]


@pytest.fixture(autouse=True)
def _reset_liveness_state(monkeypatch):
    monkeypatch.setattr(server, "_last_liveness_ok_at", None)
    monkeypatch.setattr(server, "_last_liveness_error", None)
    for key in (
        "NOETFIELD_SUPABASE_URL",
        "SUPABASE_URL",
        "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ):
        monkeypatch.delenv(key, raising=False)


def test_probe_supabase_not_configured() -> None:
    result = server.probe_supabase()
    assert result == {"ok": False, "reason": "supabase_not_configured"}


def test_probe_supabase_url_error_returns_clean_dict(monkeypatch) -> None:
    monkeypatch.setenv("NOETFIELD_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "test-key")

    def _raise(*_args, **_kwargs):
        raise urllib.error.URLError("connection reset")

    import urllib.request as _urllib_request

    monkeypatch.setattr(_urllib_request, "urlopen", _raise)
    result = server.probe_supabase()
    assert result["ok"] is False
    assert "connection reset" in result["error"]


def test_probe_supabase_success(monkeypatch) -> None:
    monkeypatch.setenv("NOETFIELD_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "test-key")

    class _FakeResp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_exc) -> None:
            return None

    import urllib.request as _urllib_request

    monkeypatch.setattr(_urllib_request, "urlopen", lambda *_a, **_k: _FakeResp())
    result = server.probe_supabase()
    assert result == {"ok": True, "status": 200}


def test_probe_supabase_never_raises_on_bounded_timeout(monkeypatch) -> None:
    def _raise(*_args, **_kwargs):
        raise TimeoutError("probe timed out")

    monkeypatch.setenv("NOETFIELD_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "test-key")
    import urllib.request as _urllib_request

    monkeypatch.setattr(_urllib_request, "urlopen", _raise)
    result = server.probe_supabase()  # must not raise
    assert result["ok"] is False


def test_run_loop_records_liveness_success(monkeypatch) -> None:
    class _FakeCompletedProcess:
        returncode = 0
        stdout = '{"status": "ok", "liveness_upsert": {"ok": true}}'
        stderr = ""

    monkeypatch.setattr(server.subprocess, "run", lambda *_a, **_k: _FakeCompletedProcess())
    assert server._last_liveness_ok_at is None

    server.run_loop("test_tick", source="test", run_id="run-1")

    assert server._last_liveness_ok_at is not None
    assert server._last_liveness_error is None


def test_run_loop_records_liveness_failure_without_crashing(monkeypatch) -> None:
    """Meaningful specifically because of repair fix 1: liveness_upsert now
    populates even when the cycle itself failed."""

    class _FakeCompletedProcess:
        returncode = 0
        stdout = '{"status": "degraded", "liveness_upsert": {"ok": false, "error": "http_500"}}'
        stderr = ""

    monkeypatch.setattr(server.subprocess, "run", lambda *_a, **_k: _FakeCompletedProcess())

    server.run_loop("test_tick", source="test", run_id="run-2")

    assert server._last_liveness_ok_at is None
    assert server._last_liveness_error == "http_500"


def test_run_loop_missing_liveness_upsert_does_not_crash(monkeypatch) -> None:
    """Malformed/legacy stdout with no liveness_upsert key must not raise."""

    class _FakeCompletedProcess:
        returncode = 1
        stdout = "not json at all"
        stderr = "boom"

    monkeypatch.setattr(server.subprocess, "run", lambda *_a, **_k: _FakeCompletedProcess())
    result = server.run_loop("test_tick", source="test", run_id="run-3")  # must not raise
    assert result["ok"] is False
