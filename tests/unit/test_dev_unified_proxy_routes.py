"""[NF-CLOUD-AGENT] Route table for scripts/dev-unified-proxy.py — workspace, gov API, trust-ledger split."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROXY = ROOT / "scripts" / "dev-unified-proxy.py"


def _load_proxy():
    spec = importlib.util.spec_from_file_location("dev_unified_proxy", PROXY)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["dev_unified_proxy"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_workspace_routes_to_next():
    mod = _load_proxy()
    assert mod._proxy_target("/workspace", "GET", {}) == mod.NEXT
    assert mod._proxy_target("/workspace/connectors", "GET", {}) == mod.NEXT


def test_gov_api_routes():
    mod = _load_proxy()
    assert mod._proxy_target("/tle", "GET", {}) == mod.GOV_API
    assert mod._proxy_target("/tle/TLE-1/export?format=pdf", "GET", {}) == mod.GOV_API
    assert mod._proxy_target("/connectors", "GET", {}) == mod.GOV_API
    assert mod._proxy_target("/connectors/m365/oauth/start", "GET", {}) == mod.GOV_API
    assert mod._proxy_target("/audit/export", "GET", {}) == mod.GOV_API


def test_trust_ledger_static_vs_next():
    mod = _load_proxy()
    assert mod._proxy_target("/trust-ledger", "GET", {}) == mod.NEXT
    assert mod._proxy_target("/trust-ledger/new", "GET", {}) == mod.NEXT
    assert mod._proxy_target("/trust-ledger/TLE-ABC", "GET", {}) == mod.NEXT
    assert mod._proxy_target("/trust-ledger/", "GET", {}) is None
    assert mod._proxy_target(
        "/trust-ledger/sample-report/samples/tle-go-approved.yaml", "GET", {}
    ) is None


def test_evaluate_audit_split():
    mod = _load_proxy()
    assert mod._proxy_target("/evaluate", "POST", {}) == mod.GOV_API
    assert mod._proxy_target("/evaluate", "GET", {}) == mod.NEXT
    assert mod._proxy_target("/audit", "GET", {"Accept": "text/html"}) == mod.NEXT
    assert mod._proxy_target("/audit", "GET", {"Accept": "application/json"}) == mod.GOV_API
