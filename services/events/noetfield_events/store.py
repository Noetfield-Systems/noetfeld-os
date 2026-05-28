"""Durable event store adapters for Phase 3.1 runtime persistence."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Protocol

import asyncpg

from .bus import DeadLetterRecord, EventTrace
from noetfield_types import Actor, ActorType, GovernanceEvent


@dataclass(frozen=True)
class StoredEventRecord:
    sequence: int
    event: GovernanceEvent
    trace: EventTrace


class EventStore(Protocol):
    async def append(self, event: GovernanceEvent, trace: EventTrace) -> int:
        ...

    async def replay(self, *, after_sequence: int, event_types: frozenset[str]) -> list[StoredEventRecord]:
        ...

    async def recent(self, *, limit: int) -> list[StoredEventRecord]:
        ...


class DeadLetterStore(Protocol):
    async def append(self, record: DeadLetterRecord) -> None:
        ...

    async def recent(self, *, limit: int) -> list[DeadLetterRecord]:
        ...


@dataclass
class InMemoryEventStore:
    """Append-only event store for local runtime and tests."""

    _records: list[StoredEventRecord] = field(default_factory=list)

    async def append(self, event: GovernanceEvent, trace: EventTrace) -> int:
        sequence = len(self._records) + 1
        self._records.append(StoredEventRecord(sequence=sequence, event=event, trace=trace))
        return sequence

    async def replay(self, *, after_sequence: int, event_types: frozenset[str]) -> list[StoredEventRecord]:
        return [
            record
            for record in self._records
            if record.sequence > after_sequence
            and ("*" in event_types or record.event.event_type in event_types)
        ]

    async def recent(self, *, limit: int) -> list[StoredEventRecord]:
        return self._records[-limit:]


@dataclass
class InMemoryDeadLetterStore:
    """Append-only dead-letter store for local runtime and tests."""

    _records: list[DeadLetterRecord] = field(default_factory=list)

    async def append(self, record: DeadLetterRecord) -> None:
        self._records.append(record)

    async def recent(self, *, limit: int) -> list[DeadLetterRecord]:
        return self._records[-limit:]


class PostgresEventStore:
    """PostgreSQL-backed event and trace adapter.

    It writes to `noetfield.governance_events` and `noetfield.event_traces`.
    The adapter can be enabled with `RUNTIME_EVENT_STORE=postgres` after the
    Supabase/PostgreSQL migrations have been applied.
    """

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

    async def append(self, event: GovernanceEvent, trace: EventTrace) -> int:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    """
                    insert into noetfield.governance_events (
                      event_id,
                      event_type,
                      event_version,
                      tenant_id,
                      organization_id,
                      actor_type,
                      actor_id,
                      actor_display_name,
                      source_service,
                      source_request_id,
                      correlation_id,
                      causation_id,
                      occurred_at,
                      entity_type,
                      entity_id,
                      policy_context,
                      risk_context,
                      payload,
                      integrity_hash
                    )
                    values (
                      $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                      $11, $12, $13, $14, $15, $16::jsonb, $17::jsonb,
                      $18::jsonb, $19
                    )
                    """,
                    event.event_id,
                    event.event_type,
                    event.event_version,
                    event.tenant_id,
                    event.organization_id,
                    event.actor.actor_type.value,
                    event.actor.actor_id,
                    event.actor.display_name,
                    event.source_service,
                    event.source_request_id,
                    event.correlation_id,
                    event.causation_id,
                    event.occurred_at,
                    event.entity_type,
                    event.entity_id,
                    json.dumps(event.policy_context, default=str),
                    json.dumps(event.risk_context, default=str),
                    json.dumps(event.payload, default=str),
                    event.integrity_hash or "runtime-unsealed",
                )
                await connection.execute(
                    """
                    insert into noetfield.event_traces (
                      tenant_id,
                      organization_id,
                      event_id,
                      event_type,
                      trace_id,
                      span_id,
                      correlation_id,
                      published_at,
                      dispatch_duration_ms
                    )
                    values ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                    event.tenant_id,
                    event.organization_id,
                    event.event_id,
                    event.event_type,
                    trace.trace_id,
                    trace.span_id,
                    trace.correlation_id,
                    trace.published_at,
                    trace.dispatch_duration_ms,
                )
                sequence = await connection.fetchval(
                    "select count(*)::integer from noetfield.governance_events"
                )
                return int(sequence)

    async def replay(self, *, after_sequence: int, event_types: frozenset[str]) -> list[StoredEventRecord]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select *
                from (
                  select
                    row_number() over (order by ge.received_at, ge.id)::integer as sequence,
                    ge.*,
                    et.trace_id,
                    et.span_id,
                    et.published_at,
                    et.dispatch_duration_ms
                  from noetfield.governance_events ge
                  left join noetfield.event_traces et on et.event_id = ge.event_id
                ) events
                where sequence > $1
                  and ($2::text[] @> array['*']::text[] or event_type = any($2::text[]))
                order by sequence
                limit 1000
                """,
                after_sequence,
                list(event_types),
            )
        return [self._row_to_record(row) for row in rows]

    async def recent(self, *, limit: int) -> list[StoredEventRecord]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select *
                from (
                  select
                    row_number() over (order by ge.received_at, ge.id)::integer as sequence,
                    ge.*,
                    et.trace_id,
                    et.span_id,
                    et.published_at,
                    et.dispatch_duration_ms
                  from noetfield.governance_events ge
                  left join noetfield.event_traces et on et.event_id = ge.event_id
                ) events
                order by sequence desc
                limit $1
                """,
                limit,
            )
        return [self._row_to_record(row) for row in reversed(rows)]

    def _row_to_record(self, row: asyncpg.Record) -> StoredEventRecord:
        actor = Actor(
            actor_type=ActorType(row["actor_type"]),
            actor_id=row["actor_id"],
            display_name=row["actor_display_name"] or row["actor_id"],
        )
        event = GovernanceEvent(
            event_id=row["event_id"],
            event_type=row["event_type"],
            event_version=row["event_version"],
            tenant_id=row["tenant_id"],
            organization_id=row["organization_id"],
            actor=actor,
            source_service=row["source_service"],
            source_request_id=row["source_request_id"],
            correlation_id=row["correlation_id"],
            causation_id=row["causation_id"],
            occurred_at=row["occurred_at"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            policy_context=dict(row["policy_context"] or {}),
            risk_context=dict(row["risk_context"] or {}),
            payload=dict(row["payload"] or {}),
            integrity_hash=row["integrity_hash"],
        )
        trace = EventTrace(
            trace_id=row["trace_id"],
            span_id=row["span_id"],
            correlation_id=row["correlation_id"],
            event_id=row["event_id"],
            event_type=row["event_type"],
            published_at=row["published_at"],
            dispatch_duration_ms=row["dispatch_duration_ms"],
        )
        return StoredEventRecord(sequence=row["sequence"], event=event, trace=trace)


class PostgresDeadLetterStore:
    """PostgreSQL-backed dead-letter adapter."""

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

    async def append(self, record: DeadLetterRecord) -> None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.dead_letter_events (
                  tenant_id,
                  organization_id,
                  event_id,
                  event_type,
                  subscriber_name,
                  error_type,
                  error_message,
                  payload,
                  trace,
                  failed_at
                )
                values ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::jsonb, $10)
                """,
                record.event.tenant_id,
                record.event.organization_id,
                record.event.event_id,
                record.event.event_type,
                record.subscriber_name,
                record.error_type,
                record.error_message,
                json.dumps(record.event.payload, default=str),
                json.dumps(
                    {
                        "trace_id": str(record.trace.trace_id),
                        "span_id": str(record.trace.span_id),
                        "correlation_id": str(record.trace.correlation_id),
                    }
                ),
                record.failed_at,
            )

    async def recent(self, *, limit: int) -> list[DeadLetterRecord]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select *
                from noetfield.dead_letter_events
                order by failed_at desc
                limit $1
                """,
                limit,
            )
        records: list[DeadLetterRecord] = []
        for row in reversed(rows):
            trace_payload = dict(row["trace"] or {})
            event = GovernanceEvent(
                event_id=row["event_id"],
                event_type=row["event_type"],
                tenant_id=row["tenant_id"],
                organization_id=row["organization_id"],
                actor=Actor(
                    actor_type=ActorType.SERVICE,
                    actor_id="dead-letter-store",
                    display_name="Dead Letter Store",
                ),
                source_service="dead-letter-store",
                entity_type="event",
                entity_id=str(row["event_id"]),
                occurred_at=row["failed_at"],
                payload=dict(row["payload"] or {}),
            )
            trace = EventTrace(
                trace_id=trace_payload.get("trace_id"),
                span_id=trace_payload.get("span_id"),
                correlation_id=trace_payload.get("correlation_id"),
                event_id=row["event_id"],
                event_type=row["event_type"],
                published_at=row["failed_at"],
            )
            records.append(
                DeadLetterRecord(
                    dead_letter_id=row["id"],
                    event=event,
                    subscriber_name=row["subscriber_name"],
                    error_type=row["error_type"],
                    error_message=row["error_message"],
                    failed_at=row["failed_at"],
                    trace=trace,
                )
            )
        return records
