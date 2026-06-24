"""Deterministic audit digest and signature helpers for Trust Ledger v1."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def audit_integrity_hash(document: dict[str, Any]) -> str:
    material = json.dumps(document, sort_keys=True, default=str)
    return f"sha256:{hashlib.sha256(material.encode('utf-8')).hexdigest()}"


def compute_tle_audit_digest(tle_body: dict[str, Any]) -> str:
    digest_src = {key: value for key, value in tle_body.items() if key != "audit_digest"}
    return audit_integrity_hash(digest_src)


def signature_key_id(policy_version: str) -> str:
    safe = policy_version.replace(" ", "-").lower()
    return f"nf-governance-v1-{safe}"


def signature_hash_for_approval(*, tle_id: str, approver_id: str, policy_version: str) -> str:
    material = f"{tle_id}:{approver_id}:{policy_version}"
    return f"sig:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:32]}"


def policy_version_hash(policy_refs: list[str]) -> str:
    material = "|".join(sorted(policy_refs))
    return f"sha256:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:16]}"
