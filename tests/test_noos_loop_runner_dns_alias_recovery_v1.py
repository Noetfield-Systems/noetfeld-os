"""Regression: recover a stale Supabase DNS alias only with the SAME backend key.

The authoritative Supabase CAS high-water mark must still be read before any
cycle is acquired. No second project, guessed URL or fabricated cycle allowed.
"""
from __future__ import annotations

import io
import socket
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import noos_loop_runner_v1 as runner  # noqa: E402
import noos_vault_paths_v1  # noqa: E402

BAD = "https://stale-ref.supabase.co"
GOOD = "https://live-ref.supabase.co"
KEY = "a-unique-service-role-key-for-test-only"


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setattr(noos_vault_paths_v1, "load_platform_env", lambda: {})
    monkeypatch.setenv("NOETFIELD_SUPABASE_URL", BAD)
    monkeypatch.setenv("SUPABASE_URL", GOOD)
    monkeypatch.setenv("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", KEY)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", KEY)


def _mock_dns_then_recovered(monkeypatch):
    urls = []
    def response(req, timeout):
        urls.append(req.full_url)
        if req.full_url.startswith(BAD):
            raise urllib.error.URLError(socket.gaierror(-2, "Name or service not known"))
        return io.BytesIO(b'[{"cycle_number": 42}]')
    monkeypatch.setattr(runner.urllib.request, "urlopen", response)
    return urls


def test_dns_alias_recovers_real_supabase_high_water_mark(monkeypatch):
    urls = _mock_dns_then_recovered(monkeypatch)
    number, proof = runner.supabase_max_cycle_number("loop-runtime")
    assert number == 42
    assert proof["same_key_dns_alias_recovered"] is True
    assert len(urls) == 2
    assert urls[0].startswith(BAD)
    assert urls[1].startswith(GOOD)
    assert runner.os.environ["NOETFIELD_SUPABASE_URL"] == GOOD


def test_dns_different_keys_never_crosses_cas_namespace(monkeypatch):
    urls = _mock_dns_then_recovered(monkeypatch)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "another-project-key")
    number, proof = runner.supabase_max_cycle_number("loop-runtime")
    assert number is None
    assert proof["reason"] == "request_failed"
    assert proof["same_key_dns_alias_recovery"] == "NOT_ELIGIBLE"
    assert len(urls) == 1
    assert runner.os.environ["NOETFIELD_SUPABASE_URL"] == BAD


def test_non_dns_failure_never_switches_database(monkeypatch):
    urls = []
    def fail(req, timeout):
        urls.append(req.full_url)
        raise urllib.error.URLError("connection refused")
    monkeypatch.setattr(runner.urllib.request, "urlopen", fail)
    number, proof = runner.supabase_max_cycle_number("loop-runtime")
    assert number is None
    assert proof["reason"] == "request_failed"
    assert len(urls) == 1
    assert runner.os.environ["NOETFIELD_SUPABASE_URL"] == BAD


def test_alias_must_be_https_origin_without_query_or_path(monkeypatch):
    urls = _mock_dns_then_recovered(monkeypatch)
    monkeypatch.setenv("SUPABASE_URL", GOOD + "/wrong-database")
    number, proof = runner.supabase_max_cycle_number("loop-runtime")
    assert number is None
    assert proof["reason"] == "request_failed"
    assert len(urls) == 1
