"""Load schema-validated policy packs from packages/policy-packs/."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from noetfield_governance.policy_pack import GovernancePolicyPack, GovernancePolicyRule

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_PACKS_DIR = _REPO_ROOT / "packages" / "policy-packs"
_DEFAULT_PACK_ID = "copilot-governance-v1"


def policy_packs_dir() -> Path:
    return _DEFAULT_PACKS_DIR


def _pack_path(pack_id: str) -> Path:
    return policy_packs_dir() / f"{pack_id}.json"


def load_pack_document(pack_id: str) -> dict[str, Any]:
    path = _pack_path(pack_id)
    if not path.is_file():
        raise FileNotFoundError(f"Policy pack not found: {pack_id} ({path})")
    with path.open(encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError(f"Policy pack must be a JSON object: {pack_id}")
    required = ("policy_id", "version", "title", "tenant_scope", "controls", "status")
    missing = [field for field in required if field not in document]
    if missing:
        raise ValueError(f"Policy pack {pack_id} missing required fields: {missing}")
    return document


def pack_document_to_runtime(document: dict[str, Any]) -> GovernancePolicyPack:
    runtime = (document.get("metadata") or {}).get("runtime") or {}
    rules = tuple(
        GovernancePolicyRule(rule_id=control, description=f"Control {control}")
        for control in document.get("controls", [])
    )
    version = str(document.get("version", "1.0.0"))
    pack_version = f"{document.get('policy_id', 'unknown')}@{version}"
    return GovernancePolicyPack(
        version=pack_version,
        minimum_confidence=float(runtime.get("minimum_confidence", 0.75)),
        high_impact_actions=frozenset(runtime.get("high_impact_actions", []))
        or GovernancePolicyPack().high_impact_actions,
        blocked_autonomous_actions=frozenset(runtime.get("blocked_autonomous_actions", []))
        or GovernancePolicyPack().blocked_autonomous_actions,
        forbidden_financial_actions=frozenset(runtime.get("forbidden_financial_actions", []))
        or GovernancePolicyPack().forbidden_financial_actions,
        inspector_execution_limit=int(runtime.get("inspector_execution_limit", 3)),
        rules=rules or GovernancePolicyPack().rules,
    )


@lru_cache(maxsize=16)
def load_policy_pack(pack_id: str = _DEFAULT_PACK_ID) -> GovernancePolicyPack:
    document = load_pack_document(pack_id)
    return pack_document_to_runtime(document)


def load_default_policy_pack() -> GovernancePolicyPack:
    try:
        return load_policy_pack(_DEFAULT_PACK_ID)
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        return GovernancePolicyPack()
