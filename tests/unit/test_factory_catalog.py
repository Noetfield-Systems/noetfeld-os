"""Tests for dual factory + tier catalog registry."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from noetfield_factories import (
    allowed_gtm_skus,
    catalog_factory_entries,
    is_factory_live,
    list_catalog_factory_ids,
    list_factory_ids,
    load_factory_catalog,
    load_factory_spec,
    load_tier_catalog,
)

ROOT = Path(__file__).resolve().parents[2]


def test_factory_catalog_has_live_copilot() -> None:
    catalog = load_factory_catalog()
    live = [f for f in catalog["factories"] if f["status"] == "live"]
    assert len(live) >= 1
    assert any(f["id"] == "copilot_governance_readiness_v1" for f in live)


def test_list_factory_ids_matches_live_catalog() -> None:
    assert "copilot_governance_readiness_v1" in list_factory_ids()
    assert is_factory_live("copilot_governance_readiness_v1")
    assert not is_factory_live("trust_brief_diligence_v1")


def test_tier_catalog_gtm_skus_allowed() -> None:
    allowed = set(allowed_gtm_skus())
    tier_cat = load_tier_catalog()
    for tier in tier_cat["tiers"]:
        for cap in tier["capabilities"]:
            sku = cap.get("gtm_sku")
            if sku:
                assert sku in allowed


def test_planned_factory_stubs_exist() -> None:
    planned = [
        f
        for f in catalog_factory_entries()
        if f.get("status") == "planned" and f.get("spec_path")
    ]
    assert len(planned) >= 5
    for entry in planned:
        path = ROOT / entry["spec_path"]
        assert path.is_file(), f"missing stub: {entry['id']}"
        meta = yaml.safe_load(path.read_text(encoding="utf-8"))["metadata"]
        assert meta["id"] == entry["id"]
        assert meta["status"] == "planned"


def test_live_factory_yaml_matches_catalog() -> None:
    spec = load_factory_spec("copilot_governance_readiness_v1")
    assert spec["metadata"]["tier"] == "tier_3"
    assert spec["metadata"]["status"] == "live"


def test_catalog_factory_ids_include_all_entries() -> None:
    catalog_ids = set(list_catalog_factory_ids())
    assert "copilot_governance_readiness_v1" in catalog_ids
    assert "ecommerce_engine_v1" in catalog_ids
    assert len(catalog_ids) >= 8


def test_blocked_ecommerce_not_live() -> None:
    entry = next(f for f in catalog_factory_entries() if f["id"] == "ecommerce_engine_v1")
    assert entry["status"] == "blocked"
    assert not is_factory_live("ecommerce_engine_v1")


def test_tier_catalog_json_valid() -> None:
    data = json.loads((ROOT / "governance/CAPABILITY_TIER_CATALOG.json").read_text())
    assert len(data["tiers"]) == 3
    assert "factory_catalog_entries" in data
