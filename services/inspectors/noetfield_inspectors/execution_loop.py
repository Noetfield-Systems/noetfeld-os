"""Bounded inspector execution loop with durable run records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Protocol
from uuid import UUID, uuid4

import asyncpg
from pydantic import BaseModel, ConfigDict, Field

from .collaboration import (
    InspectorCollaborationCommand,
    InspectorCollaborationResult,
    InspectorCollaborationRuntime,
)


class InspectorExecutionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    organization_id: UUID
    objective: str
    inspector_names: list[str]
    status: str = "started"
    findings: list[dict[str, object]] = Field(default_factory=list)
    requires_human_review: bool = True
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None


class InspectorRunStore(Protocol):
    async def start(self, record: InspectorExecutionRecord) -> InspectorExecutionRecord:
        ...

    async def complete(
        self, record: InspectorExecutionRecord, result: InspectorCollaborationResult
    ) -> InspectorExecutionRecord:
        ...


@dataclass
class InMemoryInspectorRunStore:
    records: dict[UUID, InspectorExecutionRecord] = field(default_factory=dict)

    async def start(self, record: InspectorExecutionRecord) -> InspectorExecutionRecord:
        self.records[record.run_id] = record
        return record

    async def complete(
        self, record: InspectorExecutionRecord, result: InspectorCollaborationResult
    ) -> InspectorExecutionRecord:
        completed = record.model_copy(
            update={
                "status": "completed",
                "findings": [finding.model_dump(mode="json") for finding in result.combined_findings],
                "requires_human_review": result.requires_human_review,
                "completed_at": datetime.now(timezone.utc),
            }
        )
        self.records[record.run_id] = completed
        return completed


class PostgresInspectorRunStore:
    """PostgreSQL-backed inspector execution store."""

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

    async def start(self, record: InspectorExecutionRecord) -> InspectorExecutionRecord:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.inspector_execution_runs (
                  id,
                  tenant_id,
                  organization_id,
                  objective,
                  inspector_names,
                  status,
                  findings,
                  requires_human_review,
                  started_at
                )
                values ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9)
                """,
                record.run_id,
                record.tenant_id,
                record.organization_id,
                record.objective,
                record.inspector_names,
                record.status,
                json.dumps(record.findings, default=str),
                record.requires_human_review,
                record.started_at,
            )
        return record

    async def complete(
        self, record: InspectorExecutionRecord, result: InspectorCollaborationResult
    ) -> InspectorExecutionRecord:
        completed = record.model_copy(
            update={
                "status": "completed",
                "findings": [finding.model_dump(mode="json") for finding in result.combined_findings],
                "requires_human_review": result.requires_human_review,
                "completed_at": datetime.now(timezone.utc),
            }
        )
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                update noetfield.inspector_execution_runs
                set status = $1,
                    findings = $2::jsonb,
                    requires_human_review = $3,
                    completed_at = $4
                where id = $5 and tenant_id = $6
                """,
                completed.status,
                json.dumps(completed.findings, default=str),
                completed.requires_human_review,
                completed.completed_at,
                completed.run_id,
                completed.tenant_id,
            )
        return completed


@dataclass
class InspectorExecutionLoop:
    """Runs bounded inspector collaborations through auditable execution state."""

    runtime: InspectorCollaborationRuntime
    store: InspectorRunStore

    async def run_once(self, command: InspectorCollaborationCommand) -> InspectorExecutionRecord:
        record = InspectorExecutionRecord(
            tenant_id=command.tenant_id,
            organization_id=command.organization_id,
            objective=command.objective,
            inspector_names=command.inspector_names or sorted(self.runtime.inspectors.keys()),
        )
        record = await self.store.start(record)
        result = await self.runtime.run(command)
        return await self.store.complete(record, result)
