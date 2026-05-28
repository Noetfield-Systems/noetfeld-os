"""Audit ledger runtime for backend operational integrity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Protocol
from uuid import UUID, uuid4

import asyncpg
from pydantic import BaseModel, ConfigDict, Field

from noetfield_types import GovernanceEvent


class AuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    organization_id: UUID
    actor_type: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    integrity_hash: str | None = None


class AuditLedgerStore(Protocol):
    async def append(self, record: AuditRecord) -> AuditRecord:
        ...

    async def recent(self, tenant_id: UUID, limit: int = 25) -> list[AuditRecord]:
        ...


@dataclass
class InMemoryAuditLedgerStore:
    records: list[AuditRecord] = field(default_factory=list)

    async def append(self, record: AuditRecord) -> AuditRecord:
        self.records.append(record)
        return record

    async def recent(self, tenant_id: UUID, limit: int = 25) -> list[AuditRecord]:
        return [record for record in self.records if record.tenant_id == tenant_id][-limit:]


class PostgresAuditLedgerStore:
    """PostgreSQL-backed append-only audit log writer."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._database_url)

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def append(self, record: AuditRecord) -> AuditRecord:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.audit_log (
                  id,
                  tenant_id,
                  organization_id,
                  actor_type,
                  actor_id,
                  action,
                  resource_type,
                  resource_id,
                  occurred_at,
                  request_id,
                  metadata,
                  integrity_hash
                )
                values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11::jsonb, $12)
                """,
                record.audit_id,
                record.tenant_id,
                record.organization_id,
                record.actor_type,
                record.actor_id,
                record.action,
                record.resource_type,
                record.resource_id,
                record.occurred_at,
                record.request_id,
                json.dumps(record.metadata, default=str),
                record.integrity_hash,
            )
        return record

    async def recent(self, tenant_id: UUID, limit: int = 25) -> list[AuditRecord]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select *
                from noetfield.audit_log
                where tenant_id = $1
                order by occurred_at desc
                limit $2
                """,
                tenant_id,
                limit,
            )
        return [
            AuditRecord(
                audit_id=row["id"],
                tenant_id=row["tenant_id"],
                organization_id=row["organization_id"],
                actor_type=row["actor_type"],
                actor_id=row["actor_id"],
                action=row["action"],
                resource_type=row["resource_type"],
                resource_id=row["resource_id"],
                occurred_at=row["occurred_at"],
                request_id=row["request_id"],
                metadata=dict(row["metadata"] or {}),
                integrity_hash=row["integrity_hash"],
            )
            for row in reversed(rows)
        ]


@dataclass
class AuditLedgerRuntime:
    """Subscriber-friendly runtime that mirrors governance events into audit log."""

    store: AuditLedgerStore

    async def record_event(self, event: GovernanceEvent) -> AuditRecord:
        record = AuditRecord(
            tenant_id=event.tenant_id,
            organization_id=event.organization_id,
            actor_type=event.actor.actor_type.value,
            actor_id=event.actor.actor_id,
            action=event.event_type,
            resource_type=event.entity_type,
            resource_id=event.entity_id,
            occurred_at=event.occurred_at,
            request_id=event.source_request_id,
            metadata={
                "event_id": str(event.event_id),
                "correlation_id": str(event.correlation_id),
                "source_service": event.source_service,
            },
            integrity_hash=event.integrity_hash,
        )
        return await self.store.append(record)
