from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
