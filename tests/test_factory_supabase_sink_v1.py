"""Repair fix 2 — factory_supabase_sink_v1._post_row must not crash on transient
network errors; it must catch them and return a clean {"ok": False, ...} dict,
matching noos_loop_liveness_v1's already-correct pattern."""

from __future__ import annotations

import json
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import factory_supabase_sink_v1 as sink  # noqa: E402


@pytest.fixture(autouse=True)
def _configured(monkeypatch):
    monkeypatch.setenv("NOETFIELD_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "test-key")


def test_post_row_url_error_returns_clean_dict(monkeypatch) -> None:
    def _raise(*_args, **_kwargs):
        raise urllib.error.URLError("connection reset")

    monkeypatch.setattr(sink.urllib.request, "urlopen", _raise)
    result = sink._post_row("cycle_receipts", {"a": 1})
    assert result == {"ok": False, "error": "<urlopen error connection reset>"}


def test_post_row_timeout_error_returns_clean_dict(monkeypatch) -> None:
    def _raise(*_args, **_kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(sink.urllib.request, "urlopen", _raise)
    result = sink._post_row("cycle_receipts", {"a": 1})
    assert result["ok"] is False
    assert "timed out" in result["error"]


def test_post_row_os_error_returns_clean_dict(monkeypatch) -> None:
    def _raise(*_args, **_kwargs):
        raise OSError("network unreachable")

    monkeypatch.setattr(sink.urllib.request, "urlopen", _raise)
    result = sink._post_row("cycle_receipts", {"a": 1})
    assert result["ok"] is False
    assert "network unreachable" in result["error"]


def test_post_row_malformed_json_body_returns_clean_dict(monkeypatch) -> None:
    class _FakeResp:
        status = 200

        def read(self) -> bytes:
            return b"not json"

        def __enter__(self):
            return self

        def __exit__(self, *_exc) -> None:
            return None

    monkeypatch.setattr(sink.urllib.request, "urlopen", lambda *_a, **_k: _FakeResp())
    result = sink._post_row("cycle_receipts", {"a": 1})
    assert result["ok"] is False


def test_post_row_http_error_still_handled(monkeypatch) -> None:
    """Success path for the pre-existing HTTPError branch must be unaffected."""

    def _raise(*_args, **_kwargs):
        raise urllib.error.HTTPError("url", 500, "server error", {}, None)

    monkeypatch.setattr(sink.urllib.request, "urlopen", _raise)
    monkeypatch.setattr(
        urllib.error.HTTPError, "read", lambda self: b"boom", raising=False
    )
    result = sink._post_row("cycle_receipts", {"a": 1})
    assert result["ok"] is False
    assert result["status"] == 500


def test_post_row_success_path_unaffected(monkeypatch) -> None:
    class _FakeResp:
        status = 201

        def read(self) -> bytes:
            return json.dumps({"id": "abc-123"}).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *_exc) -> None:
            return None

    monkeypatch.setattr(sink.urllib.request, "urlopen", lambda *_a, **_k: _FakeResp())
    result = sink._post_row("cycle_receipts", {"a": 1})
    assert result == {"ok": True, "id": "abc-123", "status": 201}
