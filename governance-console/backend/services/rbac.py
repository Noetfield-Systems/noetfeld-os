from __future__ import annotations

import os

WORKSPACE_ROLES = frozenset({"viewer", "approver", "compliance_owner", "governance_admin"})


def resolve_workspace_role(header_value: str | None) -> str:
    """Local dev: NF_DEV_ROLE env overrides header; default approver for pilot."""
    env_role = os.getenv("NF_DEV_ROLE", "").strip().lower()
    if env_role in WORKSPACE_ROLES:
        return env_role
    if header_value and header_value.strip().lower() in WORKSPACE_ROLES:
        return header_value.strip().lower()
    return "approver"


def can_approve_tle(role: str) -> bool:
    return role in ("approver", "compliance_owner", "governance_admin")


def can_read_tle(role: str) -> bool:
    return role in WORKSPACE_ROLES
