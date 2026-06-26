"""Governance-as-Code loader — governance.yaml → policy version hash."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from noetfield_governance.ledger_digest import audit_integrity_hash


@dataclass(frozen=True)
class GovernanceConfig:
    policy_pack_id: str
    max_cost_usd: float
    human_required: bool
    pii_deny: bool
    audit_enabled: bool
    retain_days: int
    config_hash: str
    raw: dict[str, Any]


def _parse_scalar(value: str) -> object:
    value = value.strip()
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"').strip("'")


def _parse_minimal_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        match = re.match(r"^(\s*)(\w[\w_-]*):\s*(.*)$", line)
        if not match:
            continue
        indent, key, raw_value = match.groups()
        depth = len(indent) // 2
        while stack and stack[-1][0] >= depth:
            stack.pop()
        parent = stack[-1][1]
        if raw_value.strip():
            parent[key] = _parse_scalar(raw_value)
        else:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((depth, child))
    return root


def parse_governance_config(data: dict[str, Any]) -> GovernanceConfig:
    governance = data.get("governance") or data
    budget = governance.get("budget") or {}
    approval = governance.get("approval") or {}
    pii = governance.get("pii") or {}
    audit = governance.get("audit") or {}
    policy_pack_id = str(governance.get("policy_pack") or "copilot-governance-v1")
    config_hash = audit_integrity_hash(governance if isinstance(governance, dict) else {})
    return GovernanceConfig(
        policy_pack_id=policy_pack_id,
        max_cost_usd=float(budget.get("max_cost_usd", 5.0)),
        human_required=bool(approval.get("human_required", True)),
        pii_deny=bool(pii.get("deny", True)),
        audit_enabled=bool(audit.get("enabled", True)),
        retain_days=int(audit.get("retain_days", 365)),
        config_hash=config_hash,
        raw=data,
    )


def load_governance_config(path: Path | str) -> GovernanceConfig:
    config_path = Path(path)
    text = config_path.read_text(encoding="utf-8")
    if config_path.suffix in {".yaml", ".yml"}:
        data = _parse_minimal_yaml(text)
    else:
        data = json.loads(text)
    return parse_governance_config(data)


def config_policy_version_hash(config: GovernanceConfig) -> str:
    material = f"{config.policy_pack_id}:{config.config_hash}"
    return f"sha256:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:16]}"
