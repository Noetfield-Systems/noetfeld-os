"""
Audit store abstraction on top of the low-level SQLite helpers.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from database import get_audit


def list_audits(
    *,
    request_id: str | None = None,
    applicant_id: str | None = None,
    tenant_id: str | None = None,
    decision: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """
    Thin wrapper over `database.get_audit` with the same filtering
    semantics. This exists so that higher layers do not depend directly
    on the SQLite implementation details.
    """
    return get_audit(
        request_id=request_id,
        applicant_id=applicant_id,
        tenant_id=tenant_id,
        decision=decision,
        since=since,
        until=until,
        limit=limit,
        offset=offset,
    )


__all__ = ["list_audits"]

