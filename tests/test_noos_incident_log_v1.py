"""Tests for the fail-open durable NOOS incident sink."""

from __future__ import annotations

import json
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import noos_incident_log_v1 as incidents  # noqa: E402


def test_incident_log_skips_cleanly_without_supabase_credentials(monkeypatch):
    monkeypatch.delenv("NOETFIELD_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    assert incidents.log_incident(source="test", message="blocked") == {
        "ok": False,
        "skipped": True,
        "reason": "supabase_not_configured",
    }


def test_incident_log_posts_minimal_payload(monkeypatch):
    monkeypatch.setenv("NOETFIELD_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "test-secret")
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = incidents.log_incident(
        source="noos-loop-runner",
        message="cycle failed",
        loop_id="inbox",
        event_type="noos_inbox_loop_tick",
        detail={"phase": "cycle_acquire"},
        run_id="run-1",
    )
    assert result == {"ok": True}
    assert captured["url"] == "https://example.supabase.co/rest/v1/noos_incident_log"
    assert captured["method"] == "POST"
    assert captured["payload"]["loop_id"] == "inbox"
    assert captured["payload"]["run_id"] == "run-1"
    assert captured["payload"]["detail"] == {"phase": "cycle_acquire"}
    assert captured["timeout"] == 8
    assert "test-secret" not in json.dumps(captured["payload"])


def test_incident_log_never_raises_on_database_error(monkeypatch):
    monkeypatch.setenv("NOETFIELD_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "test-secret")

    def fake_urlopen(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "https://example.supabase.co/rest/v1/noos_incident_log",
            404,
            "missing migration",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = incidents.log_incident(source="test", message="blocked")
    assert result["ok"] is False
    assert "404" in result["error"]
