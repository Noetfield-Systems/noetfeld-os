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
    tenant_id: UUID
    confidence_factors: list[dict[str, Any]] = Field(default_factory=list)
    risk_summary: list[dict[str, Any]] = Field(default_factory=list)


class AuditRecord(BaseModel):
    id: UUID
    tenant_id: UUID
    rid: str
    actor: str
    action: str
    context: str
    metadata: dict[str, Any]
    decision: str
    risk_score: int
    reason: list[str]
    conditions: list[str]
    integrity_hash: str | None = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditExportBundle(BaseModel):
    tenant_id: UUID
    exported_at: datetime
    event_count: int
    events: list[AuditRecord]


class EvidenceIngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=3, max_length=64)
    source: str
    title: str = ""
    content_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    sensitivity: str = "internal"
    retention_policy: str = "standard"
    storage_ref: str = ""
    ingest_mode: str = "metadata_only"
    link: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceIngestResponse(BaseModel):
    evidence_id: str
    tenant_id: UUID
    ingested_at: datetime


class ConnectorRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connector_id: str
    connector_type: str
    required_scopes: list[str] = Field(default_factory=list)
    ingest_mode: str = "metadata_only"


class ConnectorResponse(BaseModel):
    connector_id: str
    tenant_id: UUID
    connector_type: str
    required_scopes: list[str]
    ingest_mode: str
    status: str
    oauth_connected: bool = False
    created_at: datetime


class ConnectorStatusResponse(BaseModel):
    connector_id: str
    status: str
    oauth_connected: bool
    last_sync: datetime | None
    scopes: list[str]


class TleDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Lane C forbidden: payment_rail, custody_account, wire_transfer_id — not in schema by design.
    source_rid: str | None = None
    evidence_ids: list[str] = Field(min_length=1)
    owner: dict[str, str] | None = None
    baseline_tle_id: str | None = None


class TleDiffEvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_rid: str | None = None
    evidence_ids: list[str] = Field(min_length=1)


class TleDiffEvaluateResponse(BaseModel):
    helper: str
    last_tle_id: str | None
    last_tle_status: str | None
    baseline_tle_id: str | None
    proposed_confidence_score: float
    baseline_confidence_score: float | None
    confidence_delta: float | None
    drift_class: str
    severity: str
    delta_summary: dict[str, Any]
    evidence_added: list[str]
    evidence_removed: list[str]
    source_rid: str | None
    has_baseline: bool


class TleApproveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approver_id: str
    decision: str = Field(pattern="^(Approved|Rejected|Conditional)$")
    conditions: str | None = None


class TleSummary(BaseModel):
    tle_id: str
    status: str
    decision: str
    confidence_score: float
    date: str
    source_rid: str | None = None
    created_at: datetime


class TleDetail(BaseModel):
    tle_id: str
    tenant_id: UUID
    status: str
    confidence_score: float
    audit_digest: str | None
    created_at: datetime
    finalized_at: datetime | None
    document: dict[str, Any]

