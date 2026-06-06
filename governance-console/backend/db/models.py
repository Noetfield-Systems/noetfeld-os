from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# Default pilot tenant for local dev (Copilot Governance Pack)
PILOT_TENANT_ID = uuid.UUID("00000000-0000-4000-8000-000000000101")


class Tenant(Base):
    __tablename__ = "tenants"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pilot")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)

    audit_events: Mapped[list["AuditEvent"]] = relationship(back_populates="tenant")


class AuditEvent(Base):
    """Append-only governance evaluation ledger (Trust Ledger Bridge v1)."""

    __tablename__ = "audit_events"

    event_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.tenant_id"),
        nullable=False,
        index=True,
    )
    rid: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, default="governance.evaluate")
    actor: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    action: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    context: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    conditions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    integrity_hash: Mapped[str | None] = mapped_column(String(80), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="audit_events")


class EvidenceIndex(Base):
    __tablename__ = "evidence_index"

    evidence_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    sensitivity: Mapped[str] = mapped_column(String(64), nullable=False, default="internal")
    retention_policy: Mapped[str] = mapped_column(String(64), nullable=False, default="standard")
    storage_ref: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    ingest_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="metadata_only")
    link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)


class ConnectorRecord(Base):
    __tablename__ = "connectors"

    connector_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False, index=True
    )
    connector_type: Mapped[str] = mapped_column(String(64), nullable=False)
    required_scopes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    ingest_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="metadata_only")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="registered")
    last_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    oauth_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class TleEntry(Base):
    """Trust Ledger Entry v1 — append-only after final approval."""

    __tablename__ = "tle_entries"

    tle_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="Draft")
    source_rid: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    document_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    audit_digest: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    """Legacy table — retained for backward compatibility during migration."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rid: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    actor: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    action: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    context: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    conditions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
