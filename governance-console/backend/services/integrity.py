from __future__ import annotations

import hashlib
import json
from typing import Any


def audit_integrity_hash(payload: dict[str, Any]) -> str:
    """SHA-256 of canonical JSON for append-only audit rows."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
