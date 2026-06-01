from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor: str = ""
    action: str = ""
    context: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluateResponse(BaseModel):
    decision: str
    risk_score: int = Field(ge=0, le=100)
    reason: list[str]
    conditions: list[str]
    rid: str


class AuditRecord(BaseModel):
    id: UUID
    rid: str
    actor: str
    action: str
    context: str
    metadata: dict[str, Any]
    decision: str
    risk_score: int
    reason: list[str]
    conditions: list[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
