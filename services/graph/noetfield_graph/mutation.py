"""Live graph mutation and temporal reflection runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from uuid import UUID, uuid4

import asyncpg
from pydantic import BaseModel, ConfigDict, Field

from noetfield_events import AsyncEventBus, EventTrace, EventType, build_event
from noetfield_types import Actor, ActorType, ConfidenceScore, Entity, EntityRelationship


class GraphMutationCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    source_entity_id: UUID
    target_entity_id: UUID
    relationship_type: str
    evidence_ids: list[UUID] = Field(default_factory=list)
    confidence_delta: float = Field(default=0.0, ge=-1.0, le=1.0)
    base_confidence: float = Field(default=0.55, ge=0.0, le=1.0)
    reason: str
    actor_id: str = "graph-mutation-runtime"


class GraphMutationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relationship: EntityRelationship
    previous_confidence: float | None = None
    confidence_changed: bool
    trace: EventTrace


class GraphReflectionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reflection_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    relationship_count: int
    inferred_count: int
    low_confidence_count: int
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trace: EventTrace


@dataclass
class InMemoryGraphStore:
    """Runtime graph store for local operational cognition."""

    entities: dict[UUID, Entity] = field(default_factory=dict)
    relationships: dict[UUID, EntityRelationship] = field(default_factory=dict)

    async def put_entity(self, entity: Entity) -> Entity:
        self.entities[entity.entity_id] = entity
        return entity

    async def upsert_relationship(self, relationship: EntityRelationship) -> EntityRelationship:
        for existing_id, existing in self.relationships.items():
            same_edge = (
                existing.tenant_id == relationship.tenant_id
                and existing.source_entity_id == relationship.source_entity_id
                and existing.target_entity_id == relationship.target_entity_id
                and existing.relationship_type == relationship.relationship_type
            )
            if same_edge:
                merged = relationship.model_copy(update={"relationship_id": existing_id})
                self.relationships[existing_id] = merged
                return merged
        self.relationships[relationship.relationship_id] = relationship
        return relationship

    async def _ensure_entity(
        self,
        connection: asyncpg.Connection,
        tenant_id: UUID,
        organization_id: UUID,
        entity_id: UUID,
        entity_type: str,
        canonical_name: str,
    ) -> None:
        await connection.execute(
            """
            insert into noetfield.entities (
              id,
              tenant_id,
              organization_id,
              entity_type,
              canonical_name,
              confidence,
              attributes
            )
            values ($1, $2, $3, $4, $5, 0.5000, '{}'::jsonb)
            on conflict (id) do nothing
            """,
            entity_id,
            tenant_id,
            organization_id,
            entity_type,
            canonical_name,
        )

    async def relationships_for_tenant(self, tenant_id: UUID) -> list[EntityRelationship]:
        return [
            relationship
            for relationship in self.relationships.values()
            if relationship.tenant_id == tenant_id
        ]

    async def find_relationship(
        self,
        *,
        tenant_id: UUID,
        source_entity_id: UUID,
        target_entity_id: UUID,
        relationship_type: str,
    ) -> EntityRelationship | None:
        for relationship in self.relationships.values():
            if (
                relationship.tenant_id == tenant_id
                and relationship.source_entity_id == source_entity_id
                and relationship.target_entity_id == target_entity_id
                and relationship.relationship_type == relationship_type
            ):
                return relationship
        return None


class PostgresGraphStore:
    """PostgreSQL-backed graph mutation store."""

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

    async def upsert_relationship(self, relationship: EntityRelationship) -> EntityRelationship:
        await self.connect()
        assert self._pool is not None
        existing = await self.find_relationship(
            tenant_id=relationship.tenant_id,
            source_entity_id=relationship.source_entity_id,
            target_entity_id=relationship.target_entity_id,
            relationship_type=relationship.relationship_type,
        )
        async with self._pool.acquire() as connection:
            if existing:
                await connection.execute(
                    """
                    update noetfield.entity_relationships
                    set confidence = $1,
                        metadata = metadata || $2::jsonb,
                        valid_to = null
                    where id = $3
                    """,
                    relationship.confidence.score,
                    json.dumps({"confidence_method": relationship.confidence.method}),
                    existing.relationship_id,
                )
                await connection.execute(
                    """
                    insert into noetfield.graph_evolution (
                      tenant_id,
                      organization_id,
                      relationship_id,
                      change_type,
                      previous_state,
                      new_state,
                      confidence_delta
                    )
                    values ($1, $2, $3, 'relationship_confidence_changed', $4::jsonb, $5::jsonb, $6)
                    """,
                    relationship.tenant_id,
                    relationship.organization_id,
                    existing.relationship_id,
                    json.dumps({"confidence": existing.confidence.score}, default=str),
                    json.dumps({"confidence": relationship.confidence.score}, default=str),
                    relationship.confidence.score - existing.confidence.score,
                )
                return relationship.model_copy(update={"relationship_id": existing.relationship_id})

            await self._ensure_entity(
                connection,
                relationship.tenant_id,
                relationship.organization_id,
                relationship.source_entity_id,
                "graph_node",
                f"source:{relationship.source_entity_id}",
            )
            await self._ensure_entity(
                connection,
                relationship.tenant_id,
                relationship.organization_id,
                relationship.target_entity_id,
                "graph_node",
                f"target:{relationship.target_entity_id}",
            )
            await connection.execute(
                """
                insert into noetfield.entity_relationships (
                  id,
                  tenant_id,
                  organization_id,
                  source_entity_id,
                  target_entity_id,
                  relationship_type,
                  confidence,
                  inferred,
                  metadata
                )
                values ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
                """,
                relationship.relationship_id,
                relationship.tenant_id,
                relationship.organization_id,
                relationship.source_entity_id,
                relationship.target_entity_id,
                relationship.relationship_type,
                relationship.confidence.score,
                relationship.inferred,
                json.dumps({"confidence_method": relationship.confidence.method}),
            )
            for evidence_id in relationship.evidence_ids:
                await connection.execute(
                    """
                    insert into noetfield.relationship_evidence (
                      tenant_id,
                      organization_id,
                      relationship_id,
                      evidence_summary
                    )
                    values ($1, $2, $3, $4)
                    """,
                    relationship.tenant_id,
                    relationship.organization_id,
                    relationship.relationship_id,
                    f"Evidence reference {evidence_id}",
                )
            return relationship

    async def relationships_for_tenant(self, tenant_id: UUID) -> list[EntityRelationship]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select *
                from noetfield.entity_relationships
                where tenant_id = $1
                order by created_at
                """,
                tenant_id,
            )
        return [self._row_to_relationship(row) for row in rows]

    async def find_relationship(
        self,
        *,
        tenant_id: UUID,
        source_entity_id: UUID,
        target_entity_id: UUID,
        relationship_type: str,
    ) -> EntityRelationship | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                select *
                from noetfield.entity_relationships
                where tenant_id = $1
                  and source_entity_id = $2
                  and target_entity_id = $3
                  and relationship_type = $4
                order by created_at desc
                limit 1
                """,
                tenant_id,
                source_entity_id,
                target_entity_id,
                relationship_type,
            )
        return self._row_to_relationship(row) if row else None

    def _row_to_relationship(self, row: asyncpg.Record) -> EntityRelationship:
        return EntityRelationship(
            relationship_id=row["id"],
            tenant_id=row["tenant_id"],
            organization_id=row["organization_id"],
            source_entity_id=row["source_entity_id"],
            target_entity_id=row["target_entity_id"],
            relationship_type=row["relationship_type"],
            confidence=ConfidenceScore(
                score=float(row["confidence"]),
                method="postgres_projection",
                rationale="Loaded from PostgreSQL graph state.",
            ),
            evidence_ids=[],
            inferred=row["inferred"],
        )


@dataclass
class RelationshipConfidenceEvolution:
    """Deterministic confidence evolution with bounded deltas."""

    minimum_confidence: float = 0.0
    maximum_confidence: float = 1.0

    def evolve(self, current: float, delta: float) -> ConfidenceScore:
        bounded = max(self.minimum_confidence, min(self.maximum_confidence, current + delta))
        return ConfidenceScore(
            score=bounded,
            method="bounded_delta_evolution",
            rationale="Relationship confidence evolved from new evidence and bounded policy limits.",
        )


@dataclass
class LiveGraphMutationEngine:
    """Applies graph mutations and emits replayable graph events."""

    event_bus: AsyncEventBus
    store: InMemoryGraphStore | PostgresGraphStore
    confidence_evolution: RelationshipConfidenceEvolution = field(
        default_factory=RelationshipConfidenceEvolution
    )

    async def mutate_relationship(self, command: GraphMutationCommand) -> GraphMutationResult:
        previous = await self.store.find_relationship(
            tenant_id=command.tenant_id,
            source_entity_id=command.source_entity_id,
            target_entity_id=command.target_entity_id,
            relationship_type=command.relationship_type,
        )
        previous_confidence = previous.confidence.score if previous else None
        starting_confidence = previous_confidence if previous_confidence is not None else command.base_confidence
        confidence = self.confidence_evolution.evolve(starting_confidence, command.confidence_delta)
        relationship = EntityRelationship(
            tenant_id=command.tenant_id,
            organization_id=command.organization_id,
            source_entity_id=command.source_entity_id,
            target_entity_id=command.target_entity_id,
            relationship_type=command.relationship_type,
            confidence=confidence,
            evidence_ids=command.evidence_ids,
            inferred=False,
        )
        relationship = await self.store.upsert_relationship(relationship)

        event_type = (
            EventType.RELATIONSHIP_CONFIDENCE_CHANGED
            if previous_confidence is not None
            else EventType.RELATIONSHIP_INFERRED
        )
        actor = Actor(
            actor_type=ActorType.SERVICE,
            actor_id=command.actor_id,
            display_name="Live Graph Mutation Engine",
        )
        event = build_event(
            event_type=event_type,
            tenant_id=command.tenant_id,
            organization_id=command.organization_id,
            actor=actor,
            source_service="graph",
            entity_type="entity_relationship",
            entity_id=str(relationship.relationship_id),
            payload={
                "source_entity_id": str(command.source_entity_id),
                "target_entity_id": str(command.target_entity_id),
                "relationship_type": command.relationship_type,
                "previous_confidence": previous_confidence,
                "current_confidence": confidence.score,
                "confidence_delta": command.confidence_delta,
                "reason": command.reason,
                "evidence_ids": [str(evidence_id) for evidence_id in command.evidence_ids],
            },
        )
        trace = await self.event_bus.publish(event)
        return GraphMutationResult(
            relationship=relationship,
            previous_confidence=previous_confidence,
            confidence_changed=previous_confidence != confidence.score,
            trace=trace,
        )


@dataclass
class TemporalGraphReflectionCycle:
    """Periodic graph reflection that emits an audit-safe summary event."""

    event_bus: AsyncEventBus
    store: InMemoryGraphStore | PostgresGraphStore
    low_confidence_threshold: float = 0.65

    async def run(self, tenant_id: UUID, organization_id: UUID) -> GraphReflectionResult:
        relationships = await self.store.relationships_for_tenant(tenant_id)
        low_confidence = [
            relationship
            for relationship in relationships
            if relationship.confidence.score < self.low_confidence_threshold
        ]
        inferred = [relationship for relationship in relationships if relationship.inferred]
        actor = Actor(
            actor_type=ActorType.SERVICE,
            actor_id="temporal-graph-reflection",
            display_name="Temporal Graph Reflection Cycle",
        )
        reflection_id = uuid4()
        event = build_event(
            event_type=EventType.GRAPH_REFLECTION_COMPLETED,
            tenant_id=tenant_id,
            organization_id=organization_id,
            actor=actor,
            source_service="graph",
            entity_type="graph_reflection",
            entity_id=str(reflection_id),
            payload={
                "relationship_count": len(relationships),
                "inferred_count": len(inferred),
                "low_confidence_count": len(low_confidence),
                "low_confidence_threshold": self.low_confidence_threshold,
            },
        )
        trace = await self.event_bus.publish(event)
        return GraphReflectionResult(
            reflection_id=reflection_id,
            tenant_id=tenant_id,
            relationship_count=len(relationships),
            inferred_count=len(inferred),
            low_confidence_count=len(low_confidence),
            trace=trace,
        )
