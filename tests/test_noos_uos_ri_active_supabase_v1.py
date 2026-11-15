"""Active Supabase project reuse must prove schema without modifying data or leaking keys."""
import io
import json
import sys
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import noos_uos_ri_active_supabase_v1 as m  # noqa: E402


class Reply:
    status = 200
    def __init__(self, body): self.body = body
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, size): return json.dumps(self.body).encode()


def test_wrong_project_no_http():
    def fail(*a, **kw): raise AssertionError("never query")
    r = m.probe(url="https://tkgpapowwplupyekpivy.supabase.co", key="SECRET", opener=fail)
    assert r["ready_for_cutover"] is False
    assert not r["active_project_match"]


def test_active_openapi_but_missing_runtime_schema_fails_closed():
    def open_(request, timeout):
        assert request.get_method() == "GET"
        assert "SECRET" not in request.full_url
        assert request.headers["Apikey"] == "SECRET"
        return Reply({"paths": {"/unrelated_app": {"get": {}}}})
    r = m.probe(url="https://ldfruywifqnfpwsfgmdl.supabase.co", key="SECRET", opener=open_)
    assert r["authenticated_openapi"] is True
    assert r["ready_for_cutover"] is False
    assert r["reason"] == "MIGRATIONS_REQUIRED"
    assert "SECRET" not in json.dumps(r)


def test_all_required_runtime_objects_qualify_after_schema():
    paths = {"/" + x: {"get": {}} for x in m.REQUIRED_TABLES}
    paths.update({"/rpc/" + x: {"post": {}} for x in m.REQUIRED_RPC})
    r = m.probe(url="https://ldfruywifqnfpwsfgmdl.supabase.co", key="SECRET",
                opener=lambda req, timeout: Reply({"paths": paths}))
    assert r["ready_for_cutover"] is True and r["reason"] == "READY"


def test_no_key_blocks_network():
    r = m.probe(url="https://ldfruywifqnfpwsfgmdl.supabase.co", key="",
                opener=lambda *a, **kw: (_ for _ in ()).throw(AssertionError()))
    assert r["credential_present"] is False and not r["ready_for_cutover"]


def test_active_alias_consistency_without_secret_disclosure(monkeypatch):
    monkeypatch.setenv("PORTFOLIO_SPINE_SUPABASE_URL", "https://ldfruywifqnfpwsfgmdl.supabase.co")
    monkeypatch.setenv("PORTFOLIO_SPINE_SERVICE_ROLE_KEY", "SENSITIVE_KEY_TEST")
    monkeypatch.setenv("NOETFIELD_ACTIVE_SUPABASE_URL", "https://ldfruywifqnfpwsfgmdl.supabase.co")
    monkeypatch.setenv("NOETFIELD_ACTIVE_SUPABASE_SERVICE_ROLE_KEY", "SENSITIVE_KEY_TEST")
    r = m.probe(opener=lambda request, timeout: Reply({"paths": {}}))
    assert r["alias_configured"] is True
    assert r["alias_matches_existing_source"] is True
    assert "SENSITIVE_KEY_TEST" not in json.dumps(r)
