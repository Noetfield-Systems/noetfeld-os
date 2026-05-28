"""Inspector collaboration runtime for bounded ambient intelligence."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from noetfield_events import AsyncEventBus, EventType, build_event
from noetfield_types import Actor, ActorType, InspectorFinding

from .base import InspectorContext, InspectorResult, NoetfieldInspector


class InspectorCollaborationCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    invoked_by: str
    objective: str
    inspector_names: list[str] = Field(default_factory=list)
    graph_scope: dict[str, object] = Field(default_factory=dict)


class InspectorCollaborationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    collaboration_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    objective: str
    inspector_results: list[InspectorResult]
    combined_findings: list[InspectorFinding]
    requires_human_review: bool = True


@dataclass
class InspectorCollaborationRuntime:
    """Coordinates inspectors while preserving governance boundaries."""

    event_bus: AsyncEventBus
    inspectors: dict[str, NoetfieldInspector] = field(default_factory=dict)

    def register(self, inspector: NoetfieldInspector) -> None:
        self.inspectors[inspector.name] = inspector

    async def run(self, command: InspectorCollaborationCommand) -> InspectorCollaborationResult:
        selected_names = command.inspector_names or list(self.inspectors)
        selected = [self.inspectors[name] for name in selected_names if name in self.inspectors]
        actor = Actor(
            actor_type=ActorType.HUMAN,
            actor_id=command.invoked_by,
            display_name=command.invoked_by,
        )
        await self.event_bus.publish(
            build_event(
                event_type=EventType.INSPECTOR_COLLABORATION_STARTED,
                tenant_id=command.tenant_id,
                organization_id=command.organization_id,
                actor=actor,
                source_service="inspectors",
                entity_type="inspector_collaboration",
                entity_id=str(uuid4()),
                payload={
                    "objective": command.objective,
                    "inspectors": [inspector.name for inspector in selected],
                    "graph_scope": command.graph_scope,
                },
            )
        )

        context = InspectorContext(
            tenant_id=command.tenant_id,
            organization_id=command.organization_id,
            invoked_by=command.invoked_by,
            objective=command.objective,
            graph_scope=command.graph_scope,
        )
        results = await asyncio.gather(*(inspector.run(context) for inspector in selected))
        findings = [finding for result in results for finding in result.findings]

        for result in results:
            await self.event_bus.publish(
                build_event(
                    event_type=EventType.INSPECTOR_COMPLETED,
                    tenant_id=command.tenant_id,
                    organization_id=command.organization_id,
                    actor=Actor(
                        actor_type=ActorType.INSPECTOR,
                        actor_id=result.inspector_name,
                        display_name=result.inspector_name,
                    ),
                    source_service="inspectors",
                    entity_type="inspector_run",
                    entity_id=str(result.run_id),
                    payload=result.model_dump(mode="json"),
                )
            )

        return InspectorCollaborationResult(
            tenant_id=command.tenant_id,
            objective=command.objective,
            inspector_results=list(results),
            combined_findings=findings,
            requires_human_review=True,
        )
