from __future__ import annotations

import hashlib
import json
import re

CONTENT_HASH_RE = re.compile(r"^sha256:[a-f0-9]{64}$")


def validate_content_hash(value: str) -> str:
    """Normalize and validate evidence content_hash (evidence-intake-contract v1)."""
    normalized = (value or "").strip().lower()
    if not CONTENT_HASH_RE.match(normalized):
        raise ValueError("content_hash must match sha256:<64 lowercase hex chars>")
    return normalized


def content_hash_for_metadata(
    *,
    evidence_id: str,
    source: str,
    title: str,
    storage_ref: str = "",
) -> str:
    """Deterministic sha256 for metadata_only evidence (connector stubs + seed)."""
    payload = {
        "evidence_id": evidence_id,
        "source": source,
        "title": title,
        "storage_ref": storage_ref,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return validate_content_hash(f"sha256:{digest}")
