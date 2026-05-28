"""Async event bus runtime for Noetfield Phase 3 activation.

This module intentionally starts as an in-process runtime. It gives the
platform live behavior, replayable append-only event memory, tracing metadata,
and dead-letter handling without introducing premature infrastructure
complexity. A Redis, Postgres, or cloud event adapter can later implement the
same contracts.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from uuid import UUID, uuid4

from noetfield_types import GovernanceEvent


EventHandler = Callable[[GovernanceEvent], Awaitable[None]]


@dataclass(frozen=True)
class EventTrace:
    trace_id: UUID
    span_id: UUID
    correlation_id: UUID
    event_id: UUID
    event_type: str
    published_at: datetime
    dispatch_duration_ms: float | None = None


@dataclass(frozen=True)
class DeadLetterRecord:
    dead_letter_id: UUID
    event: GovernanceEvent
    subscriber_name: str
    error_type: str
    error_message: str
    failed_at: datetime
    trace: EventTrace


@dataclass(frozen=True)
class Subscription:
    name: str
    event_types: frozenset[str]
    handler: EventHandler

    def accepts(self, event: GovernanceEvent) -> bool:
        return "*" in self.event_types or event.event_type in self.event_types


@dataclass(frozen=True)
class EventReplayCursor:
    after_sequence: int = 0
    event_types: frozenset[str] = frozenset({"*"})


@dataclass(frozen=True)
class EventBusMetrics:
    published: int
    delivered: int
    dead_lettered: int
    subscribers: int
    retained_events: int


@dataclass
class EventBusSnapshot:
    metrics: EventBusMetrics
    recent_events: list[GovernanceEvent] = field(default_factory=list)
    dead_letters: list[DeadLetterRecord] = field(default_factory=list)


class AsyncEventBus:
    """Replayable append-only event bus with subscriber dispatch."""

    def __init__(self, max_retained_events: int = 10_000) -> None:
        self._max_retained_events = max_retained_events
        self._events: list[tuple[int, GovernanceEvent, EventTrace]] = []
        self._subscriptions: dict[str, Subscription] = {}
        self._dead_letters: list[DeadLetterRecord] = []
        self._sequence = 0
        self._delivered = 0
        self._lock = asyncio.Lock()

    async def publish(self, event: GovernanceEvent) -> EventTrace:
        """Append an event and dispatch it to interested subscribers."""

        trace = EventTrace(
            trace_id=uuid4(),
            span_id=uuid4(),
            correlation_id=event.correlation_id,
            event_id=event.event_id,
            event_type=event.event_type,
            published_at=datetime.now(timezone.utc),
        )

        async with self._lock:
            self._sequence += 1
            self._events.append((self._sequence, event, trace))
            if len(self._events) > self._max_retained_events:
                self._events = self._events[-self._max_retained_events :]
            subscriptions = list(self._subscriptions.values())

        start = perf_counter()
        await asyncio.gather(
            *(self._dispatch(subscription, event, trace) for subscription in subscriptions),
            return_exceptions=False,
        )
        duration_ms = (perf_counter() - start) * 1000
        return EventTrace(
            trace_id=trace.trace_id,
            span_id=trace.span_id,
            correlation_id=trace.correlation_id,
            event_id=trace.event_id,
            event_type=trace.event_type,
            published_at=trace.published_at,
            dispatch_duration_ms=duration_ms,
        )

    async def subscribe(
        self,
        *,
        name: str,
        event_types: set[str] | frozenset[str],
        handler: EventHandler,
        replay: EventReplayCursor | None = None,
    ) -> None:
        """Register a subscriber and optionally replay retained events."""

        subscription = Subscription(name=name, event_types=frozenset(event_types), handler=handler)
        async with self._lock:
            self._subscriptions[name] = subscription

        if replay:
            for event in await self.replay(replay):
                await self._dispatch(subscription, event, self._trace_for_event(event))

    async def unsubscribe(self, name: str) -> None:
        async with self._lock:
            self._subscriptions.pop(name, None)

    async def replay(self, cursor: EventReplayCursor) -> list[GovernanceEvent]:
        """Replay retained events after a sequence number."""

        async with self._lock:
            return [
                event
                for sequence, event, _trace in self._events
                if sequence > cursor.after_sequence
                and ("*" in cursor.event_types or event.event_type in cursor.event_types)
            ]

    async def snapshot(self, *, limit: int = 25) -> EventBusSnapshot:
        async with self._lock:
            metrics = EventBusMetrics(
                published=self._sequence,
                delivered=self._delivered,
                dead_lettered=len(self._dead_letters),
                subscribers=len(self._subscriptions),
                retained_events=len(self._events),
            )
            recent_events = [event for _seq, event, _trace in self._events[-limit:]]
            dead_letters = self._dead_letters[-limit:]
        return EventBusSnapshot(metrics=metrics, recent_events=recent_events, dead_letters=dead_letters)

    async def _dispatch(
        self, subscription: Subscription, event: GovernanceEvent, trace: EventTrace
    ) -> None:
        if not subscription.accepts(event):
            return

        try:
            await subscription.handler(event)
        except Exception as exc:  # pragma: no cover - defensive runtime boundary
            dead_letter = DeadLetterRecord(
                dead_letter_id=uuid4(),
                event=event,
                subscriber_name=subscription.name,
                error_type=type(exc).__name__,
                error_message=str(exc),
                failed_at=datetime.now(timezone.utc),
                trace=trace,
            )
            async with self._lock:
                self._dead_letters.append(dead_letter)
        else:
            async with self._lock:
                self._delivered += 1

    def _trace_for_event(self, event: GovernanceEvent) -> EventTrace:
        return EventTrace(
            trace_id=uuid4(),
            span_id=uuid4(),
            correlation_id=event.correlation_id,
            event_id=event.event_id,
            event_type=event.event_type,
            published_at=datetime.now(timezone.utc),
        )
