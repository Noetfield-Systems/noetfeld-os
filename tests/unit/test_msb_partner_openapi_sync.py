"""NF-PLAN-0103 — msb partner routes documented in committed public OpenAPI."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "docs" / "api" / "openapi.json"

MSB_PARTNER_PATHS = (
    "/api/v1/governance/partner-signals",
    "/api/v1/governance/scenario-presets/{preset}",
)

TRUST_LEDGER_PATHS = (
    "/api/v1/tle",
    "/api/v1/tle/draft",
    "/api/v1/evidence/ingest",
    "/api/v1/connectors",
)


def _load_openapi() -> dict:
    return json.loads(OPENAPI.read_text(encoding="utf-8"))


def test_msb_partner_routes_in_committed_openapi() -> None:
    schema = _load_openapi()
    paths = set(schema.get("paths", {}))
    for path in MSB_PARTNER_PATHS:
        assert path in paths, f"missing msb partner path: {path}"

    partner_post = schema["paths"]["/api/v1/governance/partner-signals"]["post"]
    assert "PartnerSignalIngestRequest" in json.dumps(partner_post)

    preset_get = schema["paths"]["/api/v1/governance/scenario-presets/{preset}"]["get"]
    desc = preset_get.get("description", "")
    assert "msb" in desc.lower()

    preset_param = preset_get["parameters"][0]["schema"]
    enum = preset_param.get("enum") or []
    assert "msb" in enum


def test_trust_ledger_routes_in_committed_openapi() -> None:
    schema = _load_openapi()
    paths = set(schema.get("paths", {}))
    for path in TRUST_LEDGER_PATHS:
        assert path in paths, f"missing trust ledger path: {path}"


def test_live_openapi_matches_committed() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "services" / "governance"))
    sys.path.insert(0, str(ROOT / "packages" / "config"))
    sys.path.insert(0, str(ROOT / "packages" / "types"))
    from noetfield_governance.api import app

    live = app.openapi()
    committed = _load_openapi()
    assert set(live.get("paths", {})) == set(committed.get("paths", {}))
