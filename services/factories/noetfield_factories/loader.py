"""YAML factory spec loader."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .exceptions import FactoryNotFoundError

REPO_ROOT = Path(__file__).resolve().parents[3]
FACTORY_SPECS_DIR = REPO_ROOT / "packages" / "schemas" / "factories"

REGISTERED_FACTORIES: dict[str, str] = {
    "copilot_governance_readiness_v1": "copilot_governance_readiness_v1.yaml",
}


@lru_cache(maxsize=8)
def load_factory_spec(factory_id: str) -> dict[str, Any]:
    filename = REGISTERED_FACTORIES.get(factory_id)
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
    return sorted(REGISTERED_FACTORIES.keys())


def factory_node_ids(factory_id: str) -> list[str]:
    spec = load_factory_spec(factory_id)
    nodes = spec.get("spec", {}).get("nodes", [])
    return [node["id"] for node in nodes if isinstance(node, dict) and "id" in node]
