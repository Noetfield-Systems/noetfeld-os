"""Machine-readable factory and tier catalog loaders."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
FACTORY_CATALOG_PATH = REPO_ROOT / "governance" / "FACTORY_CATALOG.json"
TIER_CATALOG_PATH = REPO_ROOT / "governance" / "CAPABILITY_TIER_CATALOG.json"


@lru_cache(maxsize=1)
def load_factory_catalog() -> dict[str, Any]:
    return json.loads(FACTORY_CATALOG_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_tier_catalog() -> dict[str, Any]:
    return json.loads(TIER_CATALOG_PATH.read_text(encoding="utf-8"))


def catalog_factory_entries() -> list[dict[str, Any]]:
    return list(load_factory_catalog().get("factories", []))


def live_factory_entries() -> list[dict[str, Any]]:
    return [f for f in catalog_factory_entries() if f.get("status") == "live"]


def factory_entry(factory_id: str) -> dict[str, Any] | None:
    for entry in catalog_factory_entries():
        if entry.get("id") == factory_id:
            return entry
    return None


def is_factory_live(factory_id: str) -> bool:
    entry = factory_entry(factory_id)
    return entry is not None and entry.get("status") == "live"


def allowed_gtm_skus() -> list[str]:
    return list(load_factory_catalog().get("allowed_gtm_skus", []))


def blocked_capabilities() -> list[str]:
    return list(load_factory_catalog().get("blocked_capabilities", []))
