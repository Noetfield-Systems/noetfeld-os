"""Read-only origin diagnostic never leaks endpoint secrets or tries alternate DB writes."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import noos_uos_ri_backend_probe_v1 as diag  # noqa: E402


def test_missing_config_reports_only_absence():
    row = diag._target("noos_supabase_primary", "")
    assert row["configured"] is False
    assert row["http_status"] is None


def test_origin_dns_failure_returns_safe_error(monkeypatch):
    import socket
    def fail(*args, **kwargs):
        raise socket.gaierror(-2, "SECRET_HOST_DO_NOT_LOG")
    monkeypatch.setattr(diag.socket, "getaddrinfo", fail)
    row = diag._target("motor_staging_expected", "https://tkgpapowwplupyekpivy.supabase.co")
    assert row["configured"] and row["dns_resolved"] is False
    assert row["dns_error"] == "gaierror"
    assert row["dns_errno"] == -2
    assert "SECRET_HOST_DO_NOT_LOG" not in str(row)


def test_health_401_counts_as_reachable(monkeypatch):
    from urllib.error import HTTPError
    monkeypatch.setattr(diag.socket, "getaddrinfo", lambda *a, **k: [])
    def http_error(req, timeout):
        raise HTTPError(req.full_url, 401, "SHOULD_NOT_APPEAR", {}, None)
    monkeypatch.setattr(diag.urllib.request, "urlopen", http_error)
    row = diag._target("motor_staging_expected", "https://tkgpapowwplupyekpivy.supabase.co")
    assert row["dns_resolved"] is True
    assert row["http_status"] == 401
    assert "SHOULD_NOT_APPEAR" not in str(row)


def test_rejects_non_https():
    row = diag._target("bad", "http://example.com")
    assert row["http_error"] == "INVALID_URL"


def test_project_controls_are_present_without_hostnames(monkeypatch):
    monkeypatch.delenv("NOETFIELD_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("NOETFIELD_RUNWAY_API_URL", raising=False)
    monkeypatch.setattr(diag.socket, "getaddrinfo", lambda *a, **k: [])
    from urllib.error import HTTPError
    monkeypatch.setattr(diag.urllib.request, "urlopen", lambda req, timeout: (_ for _ in ()).throw(HTTPError(req.full_url,401,"no",{},None)))
    records = diag.probe()["targets"]
    assert {r["target"] for r in records} >= {"motor_staging_expected","supabase_root_control","supabase_api_control"}
    assert all("hostname" not in r and "ip" not in r for r in records)
