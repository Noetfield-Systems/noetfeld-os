"""YAML factory spec loader."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .catalog import catalog_factory_entries, factory_entry, live_factory_entries
from .exceptions import FactoryNotFoundError

REPO_ROOT = Path(__file__).resolve().parents[3]
FACTORY_SPECS_DIR = REPO_ROOT / "packages" / "schemas" / "factories"


def _spec_filename(factory_id: str) -> str | None:
    entry = factory_entry(factory_id)
    if entry is None:
        return None
    spec_path = entry.get("spec_path")
    if not spec_path:
        return None
    return Path(str(spec_path)).name


@lru_cache(maxsize=16)
def load_factory_spec(factory_id: str) -> dict[str, Any]:
    filename = _spec_filename(factory_id)
    if filename is None:
        raise FactoryNotFoundError(factory_id)
    path = FACTORY_SPECS_DIR / filename
    if not path.is_file():
        raise FactoryNotFoundError(factory_id)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise FactoryNotFoundError(factory_id)
    metadata = data.get("metadata", {})
    if metadata.get("id") != factory_id:
        raise FactoryNotFoundError(factory_id)
    return data


def list_factory_ids() -> list[str]:
    """Return IDs of live (callable) factories."""
    return sorted(entry["id"] for entry in live_factory_entries())


def list_catalog_factory_ids() -> list[str]:
    """Return all factory IDs registered in FACTORY_CATALOG.json."""
    return sorted(entry["id"] for entry in catalog_factory_entries())


def factory_node_ids(factory_id: str) -> list[str]:
    spec = load_factory_spec(factory_id)
    nodes = spec.get("spec", {}).get("nodes", [])
    return [node["id"] for node in nodes if isinstance(node, dict) and "id" in node]
