"""Request ID (RID) helpers for institutional lineage."""

from __future__ import annotations

import re
import secrets
from uuid import uuid4

from noetfield_governance.ledger_digest import policy_version_hash

_RID_RE = re.compile(r"^RID-[A-Z0-9\-]{6,64}$", re.IGNORECASE)


def normalize_rid(value: str | None) -> str | None:
    rid = (value or "").strip().upper()
    if not rid:
        return None
    if not _RID_RE.match(rid):
        raise ValueError("request_id must match RID-… format")
    return rid


def generate_rid() -> str:
    """Generate a new RID suitable for intake, evaluate, and audit export."""
    suffix = secrets.token_hex(4).upper()
    return f"RID-{uuid4().hex[:8].upper()}-{suffix}"


def bind_rid_lineage(
    *,
    rid: str,
    policy_refs: list[str],
    config_policy_version_hash: str | None = None,
) -> dict[str, str]:
    """Bind RID to policy version and optional governance-as-code hash."""
    lineage: dict[str, str] = {
        "request_id": rid,
        "policy_version_hash": policy_version_hash(policy_refs),
    }
    if config_policy_version_hash:
        lineage["config_policy_version_hash"] = config_policy_version_hash
    return lineage
