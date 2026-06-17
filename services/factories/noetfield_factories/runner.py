"""Stateless AI factory runner."""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID, uuid4

from noetfield_copilot_governance import (
    CopilotGovernanceCommand,
    CopilotGovernanceDemoResult,
    CopilotGovernanceDemoRuntime,
    CopilotPipelineState,
)
from noetfield_events import AsyncEventBus, EventType, build_event
from noetfield_events.context import reset_request_context, set_request_context
from noetfield_governance.golden_edge_v3 import AgentLoopDecision

from .exceptions import FactoryNotFoundError, FactoryValidationError, FactoryVetoError
from .loader import factory_node_ids, load_factory_spec
from .models import CopilotGovernanceFactoryOutput, FactoryRunRequest, FactoryStatus
from .nodes import factory_actor, intake_validate, package_copilot_deliverable


class CopilotGovernanceFactoryRunner:
    """Executes the copilot_governance_readiness_v1 factory spec."""

    FACTORY_ID = "copilot_governance_readiness_v1"

    def __init__(
        self,
        *,
        demo_runtime: CopilotGovernanceDemoRuntime,
        event_bus: AsyncEventBus,
        audit_store: Any,
        graph_store: Any,
        governance_runtime: Any,
    ) -> None:
        self._demo_runtime = demo_runtime
        self._event_bus = event_bus
        self._audit_store = audit_store
        self._graph_store = graph_store
        self._governance_runtime = governance_runtime
        self._spec = load_factory_spec(self.FACTORY_ID)

    async def run(self, request: FactoryRunRequest) -> CopilotGovernanceFactoryOutput:
        command = request.command
        if request.source_request_id:
            command = command.model_copy(update={"source_request_id": request.source_request_id})

        run_id = uuid4()
        rid_token, corr_token = set_request_context(
            source_request_id=command.source_request_id,
            correlation_id=run_id,
        )
        try:
            return await self._execute(run_id, command)
        finally:
            reset_request_context(rid_token, corr_token)

    async def _execute(
        self,
        run_id: UUID,
        command: CopilotGovernanceCommand,
    ) -> CopilotGovernanceFactoryOutput:
        node_ids = factory_node_ids(self.FACTORY_ID)
        await self._emit_factory_event(
            EventType.FACTORY_RUN_STARTED,
            run_id=run_id,
            command=command,
            node_id=node_ids[0],
            payload={"factory_id": self.FACTORY_ID, "node_count": len(node_ids)},
        )

        try:
            validated = intake_validate(command)
        except FactoryValidationError:
            raise

        state = CopilotPipelineState(run_id=run_id, command=validated)
        await self._complete_node(run_id, command, "n01_intake_validate")

        state = await self._run_with_retry(
            run_id,
            command,
            "n02_signal_ingest",
            lambda: self._demo_runtime.step_signal_ingest(state),
            state,
        )
        state = await self._run_with_retry(
            run_id,
            command,
            "n03_graph_mutate",
            lambda: self._demo_runtime.step_graph_mutate(state),
            state,
        )
        state = await self._run_with_retry(
            run_id,
            command,
            "n04_graph_reflect",
            lambda: self._demo_runtime.step_graph_reflect(state),
            state,
        )
        state = await self._run_with_retry(
            run_id,
            command,
            "n05_inspector_collaborate",
            lambda: self._demo_runtime.step_inspector_collaborate(state),
            state,
        )
        state = await self._run_with_retry(
            run_id,
            command,
            "n06_policy_evaluate",
            lambda: self._demo_runtime.step_policy_evaluate(state),
            state,
        )

        if (
            state.policy_decision is not None
            and state.policy_decision.decision == AgentLoopDecision.REJECT
        ):
            packaged = await package_copilot_deliverable(
                factory_id=self.FACTORY_ID,
                state=state,
                event_bus=self._event_bus,
                audit_store=self._audit_store,
                graph_store=self._graph_store,
                governance_runtime=self._governance_runtime,
            )
            return CopilotGovernanceFactoryOutput(
                factory_id=self.FACTORY_ID,
                run_id=run_id,
                factory_status=FactoryStatus.VETOED,
                board_brief=packaged["board_brief"],
                audit_package=packaged["audit_package"],
                replay_hint=packaged["replay_hint"],
                runtime_result=None,
                policy_decision=state.policy_decision.model_dump(mode="json"),
            )

        state = await self._run_with_retry(
            run_id,
            command,
            "n07_workflow_govern",
            lambda: self._demo_runtime.step_workflow_govern(state),
            state,
        )

        packaged = await self._run_with_retry_packager(
            run_id,
            command,
            state,
        )
        await self._complete_node(run_id, command, "n08_package_export")

        runtime_result: CopilotGovernanceDemoResult | None = None
        try:
            runtime_result = self._demo_runtime.to_demo_result(state)
            if self._demo_runtime._run_store is not None:
                runtime_result = await self._demo_runtime._run_store.append(
                    runtime_result,
                    "Copilot Governance factory run",
                )
        except AssertionError:
            runtime_result = None

        factory_status = FactoryStatus(packaged["factory_status"])
        return CopilotGovernanceFactoryOutput(
            factory_id=self.FACTORY_ID,
            run_id=run_id,
            factory_status=factory_status,
            board_brief=packaged["board_brief"],
            audit_package=packaged["audit_package"],
            replay_hint=packaged["replay_hint"],
            runtime_result=runtime_result,
            policy_decision=(
                state.policy_decision.model_dump(mode="json")
                if state.policy_decision is not None
                else None
            ),
        )

    async def _run_with_retry(
        self,
        run_id: UUID,
        command: CopilotGovernanceCommand,
        node_id: str,
        step,
        state: CopilotPipelineState,
    ) -> CopilotPipelineState:
        node_spec = self._node_spec(node_id)
        timeout_sec = int(node_spec.get("timeout_sec", 15))
        retries = int(node_spec.get("retries", 1))
        backoff_ms = (
            self._spec.get("spec", {})
            .get("failure_handling", {})
            .get("transient_retry", {})
            .get("backoff_ms", [500, 2000])
        )

        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                result = await asyncio.wait_for(step(), timeout=timeout_sec)
                await self._complete_node(run_id, command, node_id, attempt=attempt)
                return result
            except Exception as exc:
                last_error = exc
                if attempt < retries:
                    delay = backoff_ms[min(attempt, len(backoff_ms) - 1)] / 1000
                    await asyncio.sleep(delay)
        assert last_error is not None
        raise last_error

    async def _run_with_retry_packager(
        self,
        run_id: UUID,
        command: CopilotGovernanceCommand,
        state: CopilotPipelineState,
    ) -> dict[str, Any]:
        node_id = "n08_package_export"
        node_spec = self._node_spec(node_id)
        timeout_sec = int(node_spec.get("timeout_sec", 15))

        async def pack() -> dict[str, Any]:
            return await package_copilot_deliverable(
                factory_id=self.FACTORY_ID,
                state=state,
                event_bus=self._event_bus,
                audit_store=self._audit_store,
                graph_store=self._graph_store,
                governance_runtime=self._governance_runtime,
            )

        return await asyncio.wait_for(pack(), timeout=timeout_sec)

    def _node_spec(self, node_id: str) -> dict[str, Any]:
        nodes = self._spec.get("spec", {}).get("nodes", [])
        for node in nodes:
            if isinstance(node, dict) and node.get("id") == node_id:
                return node
        return {}

    async def _complete_node(
        self,
        run_id: UUID,
        command: CopilotGovernanceCommand,
        node_id: str,
        *,
        attempt: int = 0,
    ) -> None:
        await self._emit_factory_event(
            EventType.FACTORY_NODE_COMPLETED,
            run_id=run_id,
            command=command,
            node_id=node_id,
            payload={"attempt": attempt},
        )

    async def _emit_factory_event(
        self,
        event_type: EventType,
        *,
        run_id: UUID,
        command: CopilotGovernanceCommand,
        node_id: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        event = build_event(
            event_type=event_type,
            tenant_id=command.tenant_id,
            organization_id=command.organization_id,
            actor=factory_actor(command.submitted_by),
            source_service=f"factory:{node_id}",
            entity_type="factory_run",
            entity_id=str(run_id),
            correlation_id=run_id,
            source_request_id=command.source_request_id,
            payload={"factory_id": self.FACTORY_ID, "node_id": node_id, **(payload or {})},
        )
        await self._event_bus.publish(event)


def get_factory_runner(
    factory_id: str,
    *,
    demo_runtime: CopilotGovernanceDemoRuntime,
    event_bus: AsyncEventBus,
    audit_store: Any,
    graph_store: Any,
    governance_runtime: Any,
) -> CopilotGovernanceFactoryRunner:
    if factory_id != CopilotGovernanceFactoryRunner.FACTORY_ID:
        raise FactoryNotFoundError(factory_id)
    return CopilotGovernanceFactoryRunner(
        demo_runtime=demo_runtime,
        event_bus=event_bus,
        audit_store=audit_store,
        graph_store=graph_store,
        governance_runtime=governance_runtime,
    )
