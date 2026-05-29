"""Public intake API — structured leads for operations."""

from __future__ import annotations

import re
import time
from collections import defaultdict, deque
from typing import Literal

from noetfield_config import CANONICAL_INTAKE_EMAIL
from noetfield_governance.intake_store import IntakeRecord, list_recent, record_intake

_MAX_ORG_LEN = 200
_MAX_MESSAGE_LEN = 8000
_MAX_NAME_LEN = 120
_RATE_LIMIT_WINDOW_SEC = 60
_RATE_LIMIT_MAX_PER_WINDOW = 10

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_RID_RE = re.compile(r"^RID-[A-Z0-9\-]{6,64}$", re.IGNORECASE)

IntakeSku = Literal["trust_brief", "copilot", "bank_pilot", "general"]
IntakeSource = Literal["web", "telegram", "api"]

_buckets: defaultdict[str, deque[float]] = defaultdict(deque)


def _check_rate_limit(client_key: str) -> None:
    now = time.monotonic()
    bucket = _buckets[client_key]
    while bucket and now - bucket[0] > _RATE_LIMIT_WINDOW_SEC:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT_MAX_PER_WINDOW:
        raise PermissionError("Too many intake submissions. Try again in a minute.")
    bucket.append(now)


def submit_intake(
    *,
    organization: str,
    contact_email: str,
    message: str,
    request_id: str | None = None,
    contact_name: str | None = None,
    sku: IntakeSku = "trust_brief",
    vector: str = "web-intake",
    source: IntakeSource = "api",
    client_key: str,
    metadata: dict | None = None,
) -> IntakeRecord:
    org = (organization or "").strip()
    email = (contact_email or "").strip().lower()
    body = (message or "").strip()

    if not org or len(org) > _MAX_ORG_LEN:
        raise ValueError("organization is required (max 200 characters)")
    if not email or len(email) > 254 or not _EMAIL_RE.match(email):
        raise ValueError("contact_email must be a valid email address")
    if not body or len(body) > _MAX_MESSAGE_LEN:
        raise ValueError("message is required (max 8000 characters)")

    rid = (request_id or "").strip().upper() or None
    if rid and not _RID_RE.match(rid):
        raise ValueError("request_id must match RID-… format when provided")

    name = (contact_name or "").strip()
    if name and len(name) > _MAX_NAME_LEN:
        raise ValueError("contact_name is too long")

    _check_rate_limit(client_key or "anonymous")

    return record_intake(
        organization=org,
        contact_email=email,
        message=body,
        request_id=rid,
        contact_name=name or None,
        sku=sku,
        vector=(vector or "web-intake").strip()[:120],
        source=source,
        metadata=metadata,
    )


def intake_ops_summary() -> dict[str, object]:
    recent = list_recent(limit=5)
    return {
        "intake_email": CANONICAL_INTAKE_EMAIL,
        "stored_recent_count": len(list_recent(limit=100)),
        "latest": recent,
    }
