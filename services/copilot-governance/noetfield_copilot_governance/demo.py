"""Copilot Governance demo flow built on the runtime core."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Protocol
from uuid import UUID, uuid4

import asyncpg
from pydantic import BaseModel, ConfigDict, Field

from noetfield_governance import GovernanceActionCommand, GovernanceRuntime
from noetfield_governance.golden_edge_v3 import (
    AgentLoopDecision,
    GoldenEdgeEvaluateRequest,
    GoldenEdgeEvaluateResponse,
    GoldenEdgeV3Engine,
)
from noetfield_graph import GraphMutationCommand, LiveGraphMutationEngine, TemporalGraphReflectionCycle
from noetfield_inspectors import (
    InspectorCollaborationCommand,
    InspectorCollaborationRuntime,
    InspectorExecutionLoop,
    InspectorExecutionRecord,
)
from noetfield_signals import IngestSignalCommand, IngestedSignal, SignalIngestionPipeline
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
    source_request_id: str | None = None


class CopilotGovernanceDemoResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    organization_id: UUID
    signal_id: UUID
    relationship_id: UUID
    reflection_id: UUID
    workflow_id: UUID
    workflow_state: WorkflowState
    approval_id: UUID | None = None
    replay_hint: str


@dataclass
class CopilotPipelineState:
    """Intermediate state passed between factory pipeline nodes."""

    run_id: UUID
    command: CopilotGovernanceCommand
    signal: IngestedSignal | None = None
    relationship_id: UUID | None = None
    reflection_id: UUID | None = None
    workflow_id: UUID | None = None
    workflow_state: WorkflowState | None = None
    approval_id: UUID | None = None
    inspector_run: InspectorExecutionRecord | None = None
    policy_decision: GoldenEdgeEvaluateResponse | None = None


class CopilotGovernanceRunStore(Protocol):
    async def append(self, result: CopilotGovernanceDemoResult, objective: str) -> CopilotGovernanceDemoResult:
        ...


@dataclass
class InMemoryCopilotGovernanceRunStore:
    records: list[CopilotGovernanceDemoResult] = field(default_factory=list)

    async def append(
        self, result: CopilotGovernanceDemoResult, objective: str
    ) -> CopilotGovernanceDemoResult:
        self.records.append(result)
        return result


class PostgresCopilotGovernanceRunStore:
    """PostgreSQL-backed Copilot Governance use-case run store."""

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

    async def append(
        self, result: CopilotGovernanceDemoResult, objective: str
    ) -> CopilotGovernanceDemoResult:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.copilot_governance_runs (
                  id,
                  tenant_id,
                  organization_id,
                  signal_id,
                  workflow_id,
                  objective,
                  status,
                  result
                )
                values ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
                """,
                result.run_id,
                result.tenant_id,
                result.organization_id,
                result.signal_id,
                result.workflow_id,
                objective,
                "waiting_for_approval"
                if result.workflow_state == WorkflowState.PENDING_REVIEW
                else "completed",
                json.dumps(result.model_dump(mode="json"), default=str),
            )
        return result


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
        governance_runtime: GovernanceRuntime | None = None,
        golden_edge: GoldenEdgeV3Engine | None = None,
        inspector_execution_loop: InspectorExecutionLoop | None = None,
        run_store: CopilotGovernanceRunStore | None = None,
    ) -> None:
        self._signal_pipeline = signal_pipeline
        self._graph_mutations = graph_mutations
        self._graph_reflections = graph_reflections
        self._workflow_state_machine = workflow_state_machine
        self._governance_runtime = governance_runtime
        self._golden_edge = golden_edge
        self._inspector_execution_loop = inspector_execution_loop
        self._run_store = run_store

    async def step_signal_ingest(self, state: CopilotPipelineState) -> CopilotPipelineState:
        signal, _signal_trace = await self._signal_pipeline.ingest(
            IngestSignalCommand(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                signal_type="copilot_governance_signal",
                payload=state.command.signal_payload,
                provenance={"module": "copilot_governance", "ingestion": "manual_or_webhook"},
                actor_id=state.command.submitted_by,
            )
        )
        state.signal = signal
        return state

    async def step_graph_mutate(self, state: CopilotPipelineState) -> CopilotPipelineState:
        assert state.signal is not None
        mutation = await self._graph_mutations.mutate_relationship(
            GraphMutationCommand(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                source_entity_id=state.command.source_entity_id,
                target_entity_id=state.command.target_entity_id,
                relationship_type="copilot_governance_signal_for",
                confidence_delta=0.2,
                reason="Copilot Governance demo signal linked to governed entity graph.",
                actor_id=state.command.submitted_by,
            )
        )
        state.relationship_id = mutation.relationship.relationship_id
        return state

    async def step_graph_reflect(self, state: CopilotPipelineState) -> CopilotPipelineState:
        reflection = await self._graph_reflections.run(
            state.command.tenant_id,
            state.command.organization_id,
        )
        state.reflection_id = reflection.reflection_id
        return state

    async def step_inspector_collaborate(self, state: CopilotPipelineState) -> CopilotPipelineState:
        if self._inspector_execution_loop is None:
            return state
        assert state.relationship_id is not None
        inspector_run = await self._inspector_execution_loop.run_once(
            InspectorCollaborationCommand(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                invoked_by=state.command.submitted_by,
                objective="Assess Copilot governance opportunity, threat, and readiness signals.",
                inspector_names=["opportunity_hunter", "threat_monitor", "lead_scout"],
                graph_scope={
                    "module": "copilot_governance",
                    "relationship_id": str(state.relationship_id),
                },
            )
        )
        state.inspector_run = inspector_run
        return state

    async def step_policy_evaluate(self, state: CopilotPipelineState) -> CopilotPipelineState:
        if self._golden_edge is None:
            return state
        resource_id = str(state.workflow_id or state.reflection_id or state.run_id)
        decision = await self._golden_edge.evaluate(
            GoldenEdgeEvaluateRequest(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                action="run_copilot_governance_demo",
                resource_type="copilot_governance_run",
                resource_id=resource_id,
                actor_id=state.command.submitted_by,
                confidence=0.8,
                payload={"module": "copilot_governance", "run_id": str(state.run_id)},
            )
        )
        state.policy_decision = decision
        return state

    async def step_workflow_govern(self, state: CopilotPipelineState) -> CopilotPipelineState:
        assert state.signal is not None
        assert state.relationship_id is not None
        assert state.reflection_id is not None
        workflow = await self._workflow_state_machine.start(
            WorkflowInstance(
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                workflow_type="copilot_governance_review",
                target_entity_type="graph_reflection",
                target_entity_id=str(state.reflection_id),
                payload={
                    "signal_id": str(state.signal.signal_id),
                    "relationship_id": str(state.relationship_id),
                },
                created_by=state.command.submitted_by,
            )
        )
        workflow = await self._workflow_state_machine.transition(
            WorkflowTransitionCommand(
                workflow_id=workflow.workflow_id,
                tenant_id=state.command.tenant_id,
                organization_id=state.command.organization_id,
                actor_id=state.command.submitted_by,
                next_state=WorkflowState.PENDING_REVIEW,
                reason="Copilot Governance requires human approval before publication.",
            )
        )
        state.workflow_id = workflow.workflow_id
        state.workflow_state = workflow.state
        if self._governance_runtime is not None:
            governed = await self._governance_runtime.execute(
                GovernanceActionCommand(
                    tenant_id=state.command.tenant_id,
                    organization_id=state.command.organization_id,
                    action="run_copilot_governance_demo",
                    resource_type="copilot_governance_run",
                    resource_id=str(workflow.workflow_id),
                    actor_id=state.command.submitted_by,
                    confidence=0.8,
                    payload={
                        "module": "copilot_governance",
                        "workflow_id": str(workflow.workflow_id),
                        "reflection_id": str(state.reflection_id),
                    },
                )
            )
            state.approval_id = governed.approval_id
        return state

    def to_demo_result(self, state: CopilotPipelineState) -> CopilotGovernanceDemoResult:
        assert state.signal is not None
        assert state.relationship_id is not None
        assert state.reflection_id is not None
        assert state.workflow_id is not None
        assert state.workflow_state is not None
        return CopilotGovernanceDemoResult(
            run_id=state.run_id,
            tenant_id=state.command.tenant_id,
            organization_id=state.command.organization_id,
            signal_id=state.signal.signal_id,
            relationship_id=state.relationship_id,
            reflection_id=state.reflection_id,
            workflow_id=state.workflow_id,
            workflow_state=state.workflow_state,
            approval_id=state.approval_id,
            replay_hint=f"/events/replay?correlation_id={state.run_id}",
        )

    async def run(self, command: CopilotGovernanceCommand) -> CopilotGovernanceDemoResult:
        state = CopilotPipelineState(run_id=uuid4(), command=command)
        state = await self.step_signal_ingest(state)
        state = await self.step_graph_mutate(state)
        state = await self.step_graph_reflect(state)
        state = await self.step_workflow_govern(state)
        result = self.to_demo_result(state)
        if self._run_store is not None:
            return await self._run_store.append(result, "Copilot Governance demo flow")
        return result

    async def run_factory_pipeline(self, command: CopilotGovernanceCommand) -> CopilotPipelineState:
        """Full factory node sequence: reflect → inspectors → policy → workflow."""
        state = CopilotPipelineState(run_id=uuid4(), command=command)
        state = await self.step_signal_ingest(state)
        state = await self.step_graph_mutate(state)
        state = await self.step_graph_reflect(state)
        state = await self.step_inspector_collaborate(state)
        state = await self.step_policy_evaluate(state)
        if (
            state.policy_decision is not None
            and state.policy_decision.decision == AgentLoopDecision.REJECT
        ):
            return state
        state = await self.step_workflow_govern(state)
        return state
