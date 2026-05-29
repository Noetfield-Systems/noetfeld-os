"""Durable workflow state machine for governed runtime execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Protocol
from uuid import UUID, uuid4

import asyncpg
from pydantic import BaseModel, ConfigDict, Field

from noetfield_events import AsyncEventBus, EventType, build_event
from noetfield_types import Actor, ActorType, WorkflowState, coerce_jsonb_mapping


ALLOWED_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.DRAFT: {WorkflowState.PENDING_REVIEW, WorkflowState.CANCELLED},
    WorkflowState.PENDING_REVIEW: {
        WorkflowState.APPROVED,
        WorkflowState.REJECTED,
        WorkflowState.ESCALATED,
        WorkflowState.CANCELLED,
    },
    WorkflowState.ESCALATED: {WorkflowState.APPROVED, WorkflowState.REJECTED, WorkflowState.CANCELLED},
    WorkflowState.APPROVED: {WorkflowState.COMPLETED, WorkflowState.CANCELLED},
    WorkflowState.REJECTED: set(),
    WorkflowState.COMPLETED: set(),
    WorkflowState.CANCELLED: set(),
}


class WorkflowInstance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    organization_id: UUID
    workflow_type: str
    target_entity_type: str
    target_entity_id: str
    state: WorkflowState = WorkflowState.DRAFT
    payload: dict[str, object] = Field(default_factory=dict)
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowTransitionCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_id: UUID
    tenant_id: UUID
    organization_id: UUID
    actor_id: str
    next_state: WorkflowState
    reason: str
    payload: dict[str, object] = Field(default_factory=dict)


class WorkflowStore(Protocol):
    async def create(self, workflow: WorkflowInstance) -> WorkflowInstance:
        ...

    async def get(self, tenant_id: UUID, workflow_id: UUID) -> WorkflowInstance | None:
        ...

    async def update(self, workflow: WorkflowInstance, reason: str, actor_id: str) -> WorkflowInstance:
        ...


@dataclass
class InMemoryWorkflowStore:
    workflows: dict[UUID, WorkflowInstance] = field(default_factory=dict)

    async def create(self, workflow: WorkflowInstance) -> WorkflowInstance:
        self.workflows[workflow.workflow_id] = workflow
        return workflow

    async def get(self, tenant_id: UUID, workflow_id: UUID) -> WorkflowInstance | None:
        workflow = self.workflows.get(workflow_id)
        if workflow and workflow.tenant_id == tenant_id:
            return workflow
        return None

    async def update(self, workflow: WorkflowInstance, reason: str, actor_id: str) -> WorkflowInstance:
        self.workflows[workflow.workflow_id] = workflow
        return workflow


class PostgresWorkflowStore:
    """PostgreSQL-backed workflow instance and history store."""

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

    async def create(self, workflow: WorkflowInstance) -> WorkflowInstance:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.workflow_instances (
                  id,
                  tenant_id,
                  organization_id,
                  workflow_type,
                  target_entity_type,
                  target_entity_id,
                  state,
                  payload,
                  created_by,
                  created_at,
                  updated_at
                )
                values ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10, $11)
                """,
                workflow.workflow_id,
                workflow.tenant_id,
                workflow.organization_id,
                workflow.workflow_type,
                workflow.target_entity_type,
                workflow.target_entity_id,
                workflow.state.value,
                json.dumps(workflow.payload, default=str),
                workflow.created_by,
                workflow.created_at,
                workflow.updated_at,
            )
            await self._append_history(connection, workflow, "created", workflow.created_by)
        return workflow

    async def get(self, tenant_id: UUID, workflow_id: UUID) -> WorkflowInstance | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                select *
                from noetfield.workflow_instances
                where tenant_id = $1 and id = $2
                """,
                tenant_id,
                workflow_id,
            )
        if not row:
            return None
        return WorkflowInstance(
            workflow_id=row["id"],
            tenant_id=row["tenant_id"],
            organization_id=row["organization_id"],
            workflow_type=row["workflow_type"],
            target_entity_type=row["target_entity_type"],
            target_entity_id=row["target_entity_id"],
            state=WorkflowState(row["state"]),
            payload=coerce_jsonb_mapping(row["payload"]),
            created_by=row["created_by"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def update(self, workflow: WorkflowInstance, reason: str, actor_id: str) -> WorkflowInstance:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    """
                    update noetfield.workflow_instances
                    set state = $1,
                        payload = $2::jsonb,
                        updated_at = $3
                    where id = $4 and tenant_id = $5
                    """,
                    workflow.state.value,
                    json.dumps(workflow.payload, default=str),
                    workflow.updated_at,
                    workflow.workflow_id,
                    workflow.tenant_id,
                )
                await self._append_history(connection, workflow, reason, actor_id)
        return workflow

    async def _append_history(
        self,
        connection: asyncpg.Connection,
        workflow: WorkflowInstance,
        reason: str,
        actor_id: str,
    ) -> None:
        await connection.execute(
            """
            insert into noetfield.workflow_history (
              tenant_id,
              organization_id,
              workflow_id,
              workflow_type,
              step_name,
              state,
              actor_id,
              decision
            )
            values ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
            """,
            workflow.tenant_id,
            workflow.organization_id,
            workflow.workflow_id,
            workflow.workflow_type,
            reason,
            workflow.state.value,
            actor_id,
            json.dumps(workflow.payload, default=str),
        )


@dataclass
class WorkflowStateMachine:
    """Deterministic workflow engine with event emission."""

    store: WorkflowStore
    event_bus: AsyncEventBus

    async def start(self, workflow: WorkflowInstance) -> WorkflowInstance:
        created = await self.store.create(workflow)
        await self._emit(created, EventType.WORKFLOW_STARTED, workflow.created_by, "workflow_started")
        return created

    async def transition(self, command: WorkflowTransitionCommand) -> WorkflowInstance:
        workflow = await self.store.get(command.tenant_id, command.workflow_id)
        if workflow is None:
            raise ValueError("workflow not found")

        allowed = ALLOWED_TRANSITIONS[workflow.state]
        if command.next_state not in allowed:
            raise ValueError(f"invalid transition from {workflow.state} to {command.next_state}")

        updated = workflow.model_copy(
            update={
                "state": command.next_state,
                "payload": {**workflow.payload, **command.payload},
                "updated_at": datetime.now(timezone.utc),
            }
        )
        updated = await self.store.update(updated, command.reason, command.actor_id)
        event_type = EventType.WORKFLOW_APPROVED if updated.state == WorkflowState.APPROVED else EventType.WORKFLOW_STARTED
        await self._emit(updated, event_type, command.actor_id, command.reason)
        return updated

    async def _emit(
        self,
        workflow: WorkflowInstance,
        event_type: EventType,
        actor_id: str,
        reason: str,
    ) -> None:
        await self.event_bus.publish(
            build_event(
                event_type=event_type,
                tenant_id=workflow.tenant_id,
                organization_id=workflow.organization_id,
                actor=Actor(actor_type=ActorType.HUMAN, actor_id=actor_id, display_name=actor_id),
                source_service="workflow",
                entity_type="workflow",
                entity_id=str(workflow.workflow_id),
                payload={
                    "workflow_type": workflow.workflow_type,
                    "state": workflow.state.value,
                    "target_entity_type": workflow.target_entity_type,
                    "target_entity_id": workflow.target_entity_id,
                    "reason": reason,
                },
            )
        )
