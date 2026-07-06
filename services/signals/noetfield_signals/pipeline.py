"""Signal ingestion pipeline for live governed cognition."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Protocol
from uuid import UUID, uuid4

import asyncpg
from pydantic import BaseModel, ConfigDict, Field

from noetfield_events import AsyncEventBus, EventTrace, EventType, build_event
from noetfield_types import Actor, ActorType


class IngestSignalCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    signal_source_id: UUID | None = None
    ingestion_run_id: UUID | None = None
    raw_document_id: UUID | None = None
    signal_type: str
    source_event_id: str | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, object]
    provenance: dict[str, object] = Field(default_factory=dict)
    actor_id: str = "signal-ingestion-runtime"


class IngestedSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signal_id: UUID
    tenant_id: UUID
    organization_id: UUID
    signal_type: str
    payload_hash: str
    observed_at: datetime
    received_at: datetime
    provenance: dict[str, object] = Field(default_factory=dict)
    governance_event_id: UUID
    source_event_id: str | None = None


class SignalStore(Protocol):
    async def append(self, signal: IngestedSignal, payload: dict[str, object]) -> IngestedSignal:
        ...

    async def recent(self, tenant_id: UUID, limit: int = 25) -> list[IngestedSignal]:
        ...


@dataclass
class InMemorySignalStore:
    """Append-only signal store for local runtime activation."""

    _signals: list[IngestedSignal] = field(default_factory=list)

    async def append(self, signal: IngestedSignal, payload: dict[str, object]) -> IngestedSignal:
        self._signals.append(signal)
        return signal

    async def recent(self, tenant_id: UUID, limit: int = 25) -> list[IngestedSignal]:
        return [signal for signal in self._signals if signal.tenant_id == tenant_id][-limit:]


class PostgresSignalStore:
    """PostgreSQL-backed raw signal store."""

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

    async def append(self, signal: IngestedSignal, payload: dict[str, object]) -> IngestedSignal:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.signals (
                  id,
                  tenant_id,
                  organization_id,
                  signal_type,
                  source_event_id,
                  observed_at,
                  received_at,
                  payload,
                  payload_hash,
                  provenance
                )
                values ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10::jsonb)
                """,
                signal.signal_id,
                signal.tenant_id,
                signal.organization_id,
                signal.signal_type,
                signal.source_event_id,
                signal.observed_at,
                signal.received_at,
                json.dumps(payload, default=str),
                signal.payload_hash,
                json.dumps(signal.provenance, default=str),
            )
        return signal

    async def recent(self, tenant_id: UUID, limit: int = 25) -> list[IngestedSignal]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select *
                from noetfield.signals
                where tenant_id = $1
                order by received_at desc
                limit $2
                """,
                tenant_id,
                limit,
            )
        return [
            IngestedSignal(
                signal_id=row["id"],
                tenant_id=row["tenant_id"],
                organization_id=row["organization_id"],
                signal_type=row["signal_type"],
                payload_hash=row["payload_hash"],
                observed_at=row["observed_at"],
                received_at=row["received_at"],
                provenance=dict(row["provenance"] or {}),
                governance_event_id=row["id"],
                source_event_id=row["source_event_id"],
            )
            for row in reversed(rows)
        ]


@dataclass
class SignalIngestionPipeline:
    """Preserves raw signal truth and emits replayable governance events."""

    event_bus: AsyncEventBus
    store: SignalStore

    async def ingest(self, command: IngestSignalCommand) -> tuple[IngestedSignal, EventTrace]:
        signal_id = uuid4()
        payload_hash = self._hash_payload(command.payload)
        actor = Actor(
            actor_type=ActorType.SERVICE,
            actor_id=command.actor_id,
            display_name="Signal Ingestion Runtime",
        )
        event = build_event(
            event_type=EventType.SIGNAL_INGESTED,
            tenant_id=command.tenant_id,
            organization_id=command.organization_id,
            actor=actor,
            source_service="signals",
            entity_type="signal",
            entity_id=str(signal_id),
            payload={
                "signal_type": command.signal_type,
                "signal_source_id": str(command.signal_source_id)
                if command.signal_source_id
                else None,
                "ingestion_run_id": str(command.ingestion_run_id)
                if command.ingestion_run_id
                else None,
                "raw_document_id": str(command.raw_document_id) if command.raw_document_id else None,
                "source_event_id": command.source_event_id,
                "observed_at": command.observed_at.isoformat(),
                "payload_hash": payload_hash,
                "provenance": command.provenance,
            },
        )
        signal = IngestedSignal(
            signal_id=signal_id,
            tenant_id=command.tenant_id,
            organization_id=command.organization_id,
            signal_type=command.signal_type,
            payload_hash=payload_hash,
            observed_at=command.observed_at,
            received_at=datetime.now(timezone.utc),
            provenance=command.provenance,
            governance_event_id=event.event_id,
            source_event_id=command.source_event_id,
        )
        await self.store.append(signal, command.payload)
        trace = await self.event_bus.publish(event)
        return signal, trace

    def _hash_payload(self, payload: dict[str, object]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return sha256(canonical.encode("utf-8")).hexdigest()
