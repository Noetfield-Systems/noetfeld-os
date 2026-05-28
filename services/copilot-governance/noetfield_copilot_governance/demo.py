"""Copilot Governance demo flow built on the runtime core."""

from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from noetfield_graph import GraphMutationCommand, LiveGraphMutationEngine, TemporalGraphReflectionCycle
from noetfield_signals import IngestSignalCommand, SignalIngestionPipeline
from noetfield_types import WorkflowState
from noetfield_workflow import WorkflowInstance, WorkflowStateMachine, WorkflowTransitionCommand


class CopilotGovernanceCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    submitted_by: str
    signal_payload: dict[str, object]
    source_entity_id: UUID = Field(default_factory=uuid4)
    target_entity_id: UUID = Field(default_factory=uuid4)


class CopilotGovernanceDemoResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signal_id: UUID
    relationship_id: UUID
    reflection_id: UUID
    workflow_id: UUID
    workflow_state: WorkflowState
    replay_hint: str


class CopilotGovernanceDemoRuntime:
    """Use-case orchestration on top of the platform runtime.

    This module deliberately depends on core runtime services. Core services do
    not depend on Copilot Governance.
    """

    def __init__(
        self,
        *,
        signal_pipeline: SignalIngestionPipeline,
        graph_mutations: LiveGraphMutationEngine,
        graph_reflections: TemporalGraphReflectionCycle,
        workflow_state_machine: WorkflowStateMachine,
    ) -> None:
        self._signal_pipeline = signal_pipeline
        self._graph_mutations = graph_mutations
        self._graph_reflections = graph_reflections
        self._workflow_state_machine = workflow_state_machine

    async def run(self, command: CopilotGovernanceCommand) -> CopilotGovernanceDemoResult:
        signal, _signal_trace = await self._signal_pipeline.ingest(
            IngestSignalCommand(
                tenant_id=command.tenant_id,
                organization_id=command.organization_id,
                signal_type="copilot_governance_signal",
                payload=command.signal_payload,
                provenance={"module": "copilot_governance", "ingestion": "manual_or_webhook"},
                actor_id=command.submitted_by,
            )
        )
        mutation = await self._graph_mutations.mutate_relationship(
            GraphMutationCommand(
                tenant_id=command.tenant_id,
                organization_id=command.organization_id,
                source_entity_id=command.source_entity_id,
                target_entity_id=command.target_entity_id,
                relationship_type="copilot_governance_signal_for",
                confidence_delta=0.2,
                reason="Copilot Governance demo signal linked to governed entity graph.",
                actor_id=command.submitted_by,
            )
        )
        reflection = await self._graph_reflections.run(command.tenant_id, command.organization_id)
        workflow = await self._workflow_state_machine.start(
            WorkflowInstance(
                tenant_id=command.tenant_id,
                organization_id=command.organization_id,
                workflow_type="copilot_governance_review",
                target_entity_type="graph_reflection",
                target_entity_id=str(reflection.reflection_id),
                payload={
                    "signal_id": str(signal.signal_id),
                    "relationship_id": str(mutation.relationship.relationship_id),
                },
                created_by=command.submitted_by,
            )
        )
        workflow = await self._workflow_state_machine.transition(
            WorkflowTransitionCommand(
                workflow_id=workflow.workflow_id,
                tenant_id=command.tenant_id,
                organization_id=command.organization_id,
                actor_id=command.submitted_by,
                next_state=WorkflowState.PENDING_REVIEW,
                reason="Copilot Governance requires human approval before publication.",
            )
        )
        return CopilotGovernanceDemoResult(
            signal_id=signal.signal_id,
            relationship_id=mutation.relationship.relationship_id,
            reflection_id=reflection.reflection_id,
            workflow_id=workflow.workflow_id,
            workflow_state=workflow.state,
            replay_hint=f"/events/replay?after_sequence=0&event_type=*",
        )
