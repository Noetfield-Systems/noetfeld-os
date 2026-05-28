"""Signal ingestion pipeline for live governed cognition."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Protocol
from uuid import UUID, uuid4

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


class SignalStore(Protocol):
    async def append(self, signal: IngestedSignal) -> IngestedSignal:
        ...

    async def recent(self, tenant_id: UUID, limit: int = 25) -> list[IngestedSignal]:
        ...


@dataclass
class InMemorySignalStore:
    """Append-only signal store for local runtime activation."""

    _signals: list[IngestedSignal] = field(default_factory=list)

    async def append(self, signal: IngestedSignal) -> IngestedSignal:
        self._signals.append(signal)
        return signal

    async def recent(self, tenant_id: UUID, limit: int = 25) -> list[IngestedSignal]:
        return [signal for signal in self._signals if signal.tenant_id == tenant_id][-limit:]


@dataclass
class SignalIngestionPipeline:
    """Preserves raw signal truth and emits replayable governance events."""

    event_bus: AsyncEventBus
    store: SignalStore

    async def ingest(self, command: IngestSignalCommand) -> tuple[IngestedSignal, EventTrace]:
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
            entity_id=str(uuid4()),
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
            signal_id=UUID(event.entity_id),
            tenant_id=command.tenant_id,
            organization_id=command.organization_id,
            signal_type=command.signal_type,
            payload_hash=payload_hash,
            observed_at=command.observed_at,
            received_at=datetime.now(timezone.utc),
            provenance=command.provenance,
            governance_event_id=event.event_id,
        )
        await self.store.append(signal)
        trace = await self.event_bus.publish(event)
        return signal, trace

    def _hash_payload(self, payload: dict[str, object]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return sha256(canonical.encode("utf-8")).hexdigest()
