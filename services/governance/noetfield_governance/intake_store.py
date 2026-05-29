"""In-memory intake queue for operations (persist to warehouse in production)."""

from __future__ import annotations

import threading
import uuid
from collections import deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

_MAX_RECORDS = 500

_lock = threading.Lock()
_records: deque[dict[str, Any]] = deque(maxlen=_MAX_RECORDS)


@dataclass(frozen=True)
class IntakeRecord:
    intake_id: str
    created_at: str
    request_id: str | None
    organization: str
    contact_name: str | None
    contact_email: str
    sku: str
    vector: str
    source: str
    message: str
    metadata: dict[str, Any]


def record_intake(
    *,
    organization: str,
    contact_email: str,
    message: str,
    request_id: str | None = None,
    contact_name: str | None = None,
    sku: str = "trust_brief",
    vector: str = "web-intake",
    source: str = "api",
    metadata: dict[str, Any] | None = None,
) -> IntakeRecord:
    rec = IntakeRecord(
        intake_id="INT-" + uuid.uuid4().hex[:12].upper(),
        created_at=datetime.now(UTC).isoformat(),
        request_id=request_id,
        organization=organization.strip(),
        contact_name=(contact_name or "").strip() or None,
        contact_email=contact_email.strip().lower(),
        sku=sku,
        vector=vector,
        source=source,
        message=message.strip(),
        metadata=metadata or {},
    )
    with _lock:
        _records.appendleft(asdict(rec))
    return rec


def list_recent(*, limit: int = 50) -> list[dict[str, Any]]:
    cap = max(1, min(limit, 100))
    with _lock:
        return list(_records)[:cap]
