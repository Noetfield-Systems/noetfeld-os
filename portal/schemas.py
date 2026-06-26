"""
Pydantic schemas for the NOETFELD OS portal.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime
    request_id: str
    applicant_id: str
    tenant_id: str
    decision: str
    composite_score: float
    input_payload: dict[str, Any]
    score_breakdown: dict[str, float]
    policy_decision: str | None = None
    corridor_decision: str | None = None
    corridor_breaches: list[str] = []
    rule_set_id: str | None = None
    rule_set_version: str | None = None
    policy_base_hash: str | None = None
    policy_corridor_hash: str | None = None
    api_key_id: str | None = None
    correlation_id: str | None = None
    notes: str | None = None


class AuditQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str | None = None
    applicant_id: str | None = None
    decision: str | None = None
    limit: int = 50
    offset: int = 0


__all__ = ["AuditRecord", "AuditQuery"]
