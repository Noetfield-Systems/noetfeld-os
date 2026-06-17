"""Tests for Copilot Governance AI factory."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from uuid import UUID, uuid5, NAMESPACE_URL

import pytest
import yaml

from noetfield_copilot_governance import CopilotGovernanceCommand, CopilotGovernanceDemoRuntime
from noetfield_events import AsyncEventBus, EventReplayCursor, InMemoryDeadLetterStore, InMemoryEventStore
from noetfield_factories import (
    FactoryRunRequest,
    FactoryStatus,
    FactoryValidationError,
    get_factory_runner,
    list_factory_ids,
    load_factory_spec,
)
from noetfield_factories.nodes import intake_validate
from noetfield_governance import GovernanceRuntime, HumanApprovalQueue
from noetfield_governance.golden_edge_v3 import GoldenEdgeV3Engine
from noetfield_graph import (
    InMemoryGraphReflectionStore,
    InMemoryGraphStore,
    LiveGraphMutationEngine,
    TemporalGraphReflectionCycle,
)
from noetfield_inspectors import (
    InMemoryInspectorRunStore,
    InspectorCollaborationRuntime,
    InspectorExecutionLoop,
    LeadScoutInspector,
    OpportunityHunterInspector,
    ThreatMonitorInspector,
)
from noetfield_ledger import AuditLedgerRuntime, InMemoryAuditLedgerStore
from noetfield_signals import InMemorySignalStore, SignalIngestionPipeline
from noetfield_workflow import InMemoryWorkflowStore, WorkflowStateMachine

ROOT = Path(__file__).resolve().parents[2]


def stable_uuid(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"https://noetfield.local/factory-test/{name}")


def sample_command() -> CopilotGovernanceCommand:
    payload = json.loads(
        (ROOT / "demos/copilot-governance/sample_copilot_signal.json").read_text(encoding="utf-8")
    )
    return CopilotGovernanceCommand(
        tenant_id=stable_uuid("tenant"),
        organization_id=stable_uuid("organization"),
        submitted_by="factory.test@noetfield.local",
        signal_payload=payload,
        source_entity_id=stable_uuid("microsoft-copilot"),
        target_entity_id=stable_uuid("customer-tenant"),
        source_request_id="RID-factory-test-001",
    )


async def build_factory_runner() -> tuple[object, AsyncEventBus, AuditLedgerRuntime]:
    event_bus = AsyncEventBus(
        event_store=InMemoryEventStore(),
        dead_letter_store=InMemoryDeadLetterStore(),
    )
    audit_store = InMemoryAuditLedgerStore()
    audit_runtime = AuditLedgerRuntime(audit_store)
    await event_bus.subscribe(
        name="audit-ledger-runtime",
        event_types={"*"},
        handler=audit_runtime.record_event,
    )

    signal_pipeline = SignalIngestionPipeline(event_bus, InMemorySignalStore())
    graph_store = InMemoryGraphStore()
    graph_mutations = LiveGraphMutationEngine(event_bus, graph_store)
    graph_reflections = TemporalGraphReflectionCycle(
        event_bus,
        graph_store,
        InMemoryGraphReflectionStore(),
    )
    workflow_state_machine = WorkflowStateMachine(InMemoryWorkflowStore(), event_bus)
    governance_runtime = GovernanceRuntime(event_bus, HumanApprovalQueue())
    golden_edge = GoldenEdgeV3Engine(governance_runtime=governance_runtime)

    inspector_runtime = InspectorCollaborationRuntime(event_bus)
    inspector_runtime.register(OpportunityHunterInspector())
    inspector_runtime.register(ThreatMonitorInspector())
    inspector_runtime.register(LeadScoutInspector())
    inspector_loop = InspectorExecutionLoop(inspector_runtime, InMemoryInspectorRunStore())

    demo_runtime = CopilotGovernanceDemoRuntime(
        signal_pipeline=signal_pipeline,
        graph_mutations=graph_mutations,
        graph_reflections=graph_reflections,
        workflow_state_machine=workflow_state_machine,
        governance_runtime=governance_runtime,
        golden_edge=golden_edge,
        inspector_execution_loop=inspector_loop,
    )

    runner = get_factory_runner(
        "copilot_governance_readiness_v1",
        demo_runtime=demo_runtime,
        event_bus=event_bus,
        audit_store=audit_store,
        graph_store=graph_store,
        governance_runtime=governance_runtime,
    )
    return runner, event_bus, audit_runtime


def test_factory_spec_loads() -> None:
    spec = load_factory_spec("copilot_governance_readiness_v1")
    assert spec["metadata"]["id"] == "copilot_governance_readiness_v1"
    assert spec["metadata"]["factory_type"] == "copilot_governance_readiness"
    nodes = spec["spec"]["nodes"]
    assert 5 <= len(nodes) <= 12
    assert list_factory_ids() == ["copilot_governance_readiness_v1"]


def test_factory_yaml_parseable() -> None:
    path = ROOT / "packages/schemas/factories/copilot_governance_readiness_v1.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["kind"] == "Factory"


def test_intake_validate_rejects_missing_summary() -> None:
    command = sample_command()
    command = command.model_copy(update={"signal_payload": {"source": "manual"}})
    with pytest.raises(FactoryValidationError):
        intake_validate(command)


def test_factory_run_produces_board_brief_and_audit_package() -> None:
    async def _run() -> None:
        runner, event_bus, audit_runtime = await build_factory_runner()
        result = await runner.run(FactoryRunRequest(command=sample_command()))
        assert result.factory_id == "copilot_governance_readiness_v1"
        assert result.factory_status == FactoryStatus.PENDING_APPROVAL
        assert result.board_brief["title"] == "Copilot Governance Readiness Brief"
        assert result.board_brief["governance_state"]["approval_required"] is True
        assert result.audit_package["event_count"] >= 10
        assert result.runtime_result is not None

        events = await event_bus.replay(EventReplayCursor(after_sequence=0))
        event_types = {event.event_type for event in events}
        assert "FACTORY_RUN_STARTED" in event_types
        assert "FACTORY_NODE_COMPLETED" in event_types
        assert "SIGNAL_INGESTED" in event_types
        assert "INSPECTOR_COMPLETED" in event_types
        assert len(audit_runtime.store.records) >= 10

        rid_events = [event for event in events if event.source_request_id == "RID-factory-test-001"]
        assert rid_events, "RID should thread into governance events"

    asyncio.run(_run())


def test_factory_node_order_matches_spec() -> None:
    spec = load_factory_spec("copilot_governance_readiness_v1")
    node_ids = [node["id"] for node in spec["spec"]["nodes"]]
    assert node_ids == [
        "n01_intake_validate",
        "n02_signal_ingest",
        "n03_graph_mutate",
        "n04_graph_reflect",
        "n05_inspector_collaborate",
        "n06_policy_evaluate",
        "n07_workflow_govern",
        "n08_package_export",
    ]
