"""Request ID (RID) helpers for institutional lineage."""

from __future__ import annotations

import re
import secrets
from uuid import uuid4

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
