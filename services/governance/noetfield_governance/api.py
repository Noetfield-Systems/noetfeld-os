"""FastAPI entrypoint for the Noetfield backend runtime core."""

from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict

from noetfield_events import EventType, build_event
from noetfield_types import Actor, ActorType

from noetfield_config import get_settings
from noetfield_copilot_governance import (
    CopilotGovernanceCommand,
    CopilotGovernanceDemoRuntime,
    InMemoryCopilotGovernanceRunStore,
    PostgresCopilotGovernanceRunStore,
)
from noetfield_events import (
    AsyncEventBus,
    EventReplayCursor,
    PostgresDeadLetterStore,
    PostgresEventStore,
    event_catalog,
)
from noetfield_governance.golden_edge_v3 import (
    GoldenEdgeEvaluateRequest,
    GoldenEdgeV3Engine,
)
from noetfield_governance.runtime import (
    ApprovalDecision,
    GovernanceActionCommand,
    GovernanceRuntime,
    HumanApprovalQueue,
    PostgresApprovalQueueStore,
)
from noetfield_graph import (
    GraphMutationCommand,
    InMemoryGraphReflectionStore,
    InMemoryGraphStore,
    LiveGraphMutationEngine,
    PostgresGraphReflectionStore,
    PostgresGraphStore,
    TemporalGraphReflectionCycle,
)
from noetfield_inspectors import (
    InMemoryInspectorRunStore,
    InspectorCollaborationCommand,
    InspectorCollaborationRuntime,
    InspectorExecutionLoop,
    LeadScoutInspector,
    OpportunityHunterInspector,
    PostgresInspectorRunStore,
    ThreatMonitorInspector,
)
from noetfield_ledger import AuditLedgerRuntime, InMemoryAuditLedgerStore, PostgresAuditLedgerStore
from noetfield_signals import (
    InMemorySignalStore,
    IngestSignalCommand,
    PostgresSignalStore,
    SignalIngestionPipeline,
)
from noetfield_workflow import (
    InMemoryWorkflowStore,
    PostgresWorkflowStore,
    WorkflowInstance,
    WorkflowStateMachine,
    WorkflowTransitionCommand,
)

settings = get_settings()

app = FastAPI(
    title="Noetfield Platform API",
    version="0.3.1",
    description="Backend runtime core for governed ambient intelligence.",
)

postgres_mode = settings.runtime_event_store == "postgres"

event_store = PostgresEventStore(settings.database_url) if postgres_mode else None
dead_letter_store = PostgresDeadLetterStore(settings.database_url) if postgres_mode else None
event_bus = AsyncEventBus(event_store=event_store, dead_letter_store=dead_letter_store)

signal_store = PostgresSignalStore(settings.database_url) if postgres_mode else InMemorySignalStore()
graph_store = PostgresGraphStore(settings.database_url) if postgres_mode else InMemoryGraphStore()
audit_store = (
    PostgresAuditLedgerStore(settings.database_url) if postgres_mode else InMemoryAuditLedgerStore()
)
workflow_store = PostgresWorkflowStore(settings.database_url) if postgres_mode else InMemoryWorkflowStore()
inspector_store = (
    PostgresInspectorRunStore(settings.database_url) if postgres_mode else InMemoryInspectorRunStore()
)
approval_queue = PostgresApprovalQueueStore(settings.database_url) if postgres_mode else HumanApprovalQueue()
reflection_store = (
    PostgresGraphReflectionStore(settings.database_url) if postgres_mode else InMemoryGraphReflectionStore()
)
copilot_run_store = (
    PostgresCopilotGovernanceRunStore(settings.database_url)
    if postgres_mode
    else InMemoryCopilotGovernanceRunStore()
)

audit_runtime = AuditLedgerRuntime(store=audit_store)
signal_pipeline = SignalIngestionPipeline(event_bus=event_bus, store=signal_store)
graph_mutations = LiveGraphMutationEngine(event_bus=event_bus, store=graph_store)
graph_reflections = TemporalGraphReflectionCycle(
    event_bus=event_bus, store=graph_store, reflection_store=reflection_store
)
governance_runtime = GovernanceRuntime(event_bus=event_bus, approvals=approval_queue)
workflow_state_machine = WorkflowStateMachine(store=workflow_store, event_bus=event_bus)

inspector_runtime = InspectorCollaborationRuntime(event_bus=event_bus)
inspector_runtime.register(OpportunityHunterInspector())
inspector_runtime.register(ThreatMonitorInspector())
inspector_runtime.register(LeadScoutInspector())
inspector_execution_loop = InspectorExecutionLoop(runtime=inspector_runtime, store=inspector_store)

copilot_demo_runtime = CopilotGovernanceDemoRuntime(
    signal_pipeline=signal_pipeline,
    graph_mutations=graph_mutations,
    graph_reflections=graph_reflections,
    workflow_state_machine=workflow_state_machine,
    governance_runtime=governance_runtime,
    run_store=copilot_run_store,
)

golden_edge_v3 = GoldenEdgeV3Engine(governance_runtime=governance_runtime)


class ApprovalDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    decision: ApprovalDecision


class ReflectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID


class WebhookIngestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    payload: dict[str, object]
    actor_id: str = "webhook-ingestion"


class ManualIngestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    signal_type: str = "manual_signal"
    payload: dict[str, object]
    submitted_by: str


@app.on_event("startup")
async def subscribe_runtime_audit() -> None:
    await event_bus.subscribe(name="audit-ledger-runtime", event_types={"*"}, handler=audit_runtime.record_event)


@app.on_event("shutdown")
async def shutdown_runtime() -> None:
    stores = [
        event_store,
        dead_letter_store,
        signal_store,
        graph_store,
        audit_store,
        workflow_store,
        inspector_store,
        approval_queue,
        reflection_store,
        copilot_run_store,
    ]
    for store in stores:
        close = getattr(store, "close", None)
        if close is not None:
            await close()


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "noetfield-platform",
        "runtime": "phase-3.1-backend-core",
        "golden_edge": "v3",
        "system_of_record": "postgresql" if postgres_mode else "memory-test-mode",
        "supabase_authority": "optional-tooling-only",
    }


@app.post("/v3/evaluate", tags=["golden-edge-v3"])
async def golden_edge_evaluate(request: GoldenEdgeEvaluateRequest) -> dict[str, object]:
    result = await golden_edge_v3.evaluate(request)
    actor = Actor(
        actor_type=request.actor_type,
        actor_id=request.actor_id,
        display_name=request.actor_id,
    )
    await event_bus.publish(
        build_event(
            event_type=EventType.POLICY_EVALUATED,
            tenant_id=request.tenant_id,
            organization_id=request.organization_id,
            actor=actor,
            source_service="golden-edge-v3",
            entity_type=request.resource_type,
            entity_id=request.resource_id,
            payload={
                "decision": result.decision.value,
                "allowed": result.allowed,
                "reason": result.reason,
                "reason_code": result.reason_code,
                "policy_refs": result.policy_refs,
                "console": "governance-console-v1",
            },
        )
    )
    if result.decision.value == "REJECT":
        await event_bus.publish(
            build_event(
                event_type=EventType.GOVERNANCE_VETOED,
                tenant_id=request.tenant_id,
                organization_id=request.organization_id,
                actor=actor,
                source_service="golden-edge-v3",
                entity_type=request.resource_type,
                entity_id=request.resource_id,
                payload={"reason": result.reason, "reason_code": result.reason_code},
            )
        )
    return result.model_dump(mode="json")


@app.get("/v3/ledger", tags=["golden-edge-v3"])
async def golden_edge_ledger(tenant_id: UUID | None = None, limit: int = 100) -> dict[str, object]:
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
    records = await audit_store.list_entries(tenant_id=tenant_id, limit=limit)
    return {
        "source": "audit_log",
        "immutable": True,
        "count": len(records),
        "entries": [record.model_dump(mode="json") for record in records],
    }


_CONSOLE_HTML = Path(__file__).resolve().parent / "static" / "governance-console-v1.html"


@app.get("/console", tags=["governance-console-v1"], include_in_schema=True)
@app.get("/", tags=["governance-console-v1"], include_in_schema=False)
async def governance_console_v1() -> FileResponse:
    if not _CONSOLE_HTML.is_file():
        raise HTTPException(status_code=503, detail="Governance Evaluation Interface assets missing")
    return FileResponse(_CONSOLE_HTML, media_type="text/html")


@app.post("/v3/agent-loop", tags=["golden-edge-v3"])
async def golden_edge_agent_loop(request: GoldenEdgeEvaluateRequest) -> dict[str, object]:
    result = await golden_edge_v3.agent_loop(request)
    return result.model_dump(mode="json")


@app.get("/events/catalog", tags=["events"])
async def events_catalog() -> dict[str, dict[str, str]]:
    return event_catalog()


@app.get("/events/replay", tags=["events"])
async def replay_events(after_sequence: int = 0, event_type: str = "*") -> list[dict[str, object]]:
    events = await event_bus.replay(
        EventReplayCursor(after_sequence=after_sequence, event_types=frozenset({event_type}))
    )
    return [event.model_dump(mode="json") for event in events]


@app.post("/ingestion/manual", tags=["ingestion"])
async def ingest_manual(request: ManualIngestionRequest) -> dict[str, object]:
    signal, trace = await signal_pipeline.ingest(
        IngestSignalCommand(
            tenant_id=request.tenant_id,
            organization_id=request.organization_id,
            signal_type=request.signal_type,
            payload=request.payload,
            provenance={"ingestion": "manual"},
            actor_id=request.submitted_by,
        )
    )
    return {"signal": signal.model_dump(mode="json"), "trace": trace}


@app.post("/ingestion/webhook/{source_name}", tags=["ingestion"])
async def ingest_webhook(source_name: str, request: WebhookIngestionRequest) -> dict[str, object]:
    signal, trace = await signal_pipeline.ingest(
        IngestSignalCommand(
            tenant_id=request.tenant_id,
            organization_id=request.organization_id,
            signal_type="webhook_signal",
            payload=request.payload,
            provenance={"ingestion": "webhook", "source_name": source_name},
            actor_id=request.actor_id,
        )
    )
    return {"signal": signal.model_dump(mode="json"), "trace": trace}


@app.post("/signals/ingest", tags=["signals"])
async def ingest_signal(command: IngestSignalCommand) -> dict[str, object]:
    signal, trace = await signal_pipeline.ingest(command)
    return {"signal": signal.model_dump(mode="json"), "trace": trace}


@app.post("/graph/relationships/mutate", tags=["graph"])
async def mutate_relationship(command: GraphMutationCommand) -> dict[str, object]:
    result = await graph_mutations.mutate_relationship(command)
    return result.model_dump(mode="json")


@app.post("/graph/reflections/run", tags=["graph"])
async def run_graph_reflection(request: ReflectionRequest) -> dict[str, object]:
    result = await graph_reflections.run(request.tenant_id, request.organization_id)
    return result.model_dump(mode="json")


@app.post("/workflows/start", tags=["workflow"])
async def start_workflow(workflow: WorkflowInstance) -> dict[str, object]:
    result = await workflow_state_machine.start(workflow)
    return result.model_dump(mode="json")


@app.post("/workflows/transition", tags=["workflow"])
async def transition_workflow(command: WorkflowTransitionCommand) -> dict[str, object]:
    result = await workflow_state_machine.transition(command)
    return result.model_dump(mode="json")


@app.post("/governance/execute", tags=["governance"])
async def execute_governance(command: GovernanceActionCommand) -> dict[str, object]:
    result = await governance_runtime.execute(command)
    return result.model_dump(mode="json")


@app.get("/approvals", tags=["governance"])
async def list_approvals(tenant_id: UUID | None = None) -> list[dict[str, object]]:
    approvals = await approval_queue.list_pending(tenant_id)
    return [approval.model_dump(mode="json") for approval in approvals]


@app.post("/approvals/decide", tags=["governance"])
async def decide_approval(request: ApprovalDecisionRequest) -> dict[str, object]:
    trace = await governance_runtime.decide_approval(
        tenant_id=request.tenant_id,
        organization_id=request.organization_id,
        decision=request.decision,
    )
    return {"trace": trace}


@app.post("/inspectors/collaborate", tags=["inspectors"])
async def collaborate_inspectors(command: InspectorCollaborationCommand) -> dict[str, object]:
    result = await inspector_runtime.run(command)
    return result.model_dump(mode="json")


@app.post("/inspectors/execute", tags=["inspectors"])
async def execute_inspectors(command: InspectorCollaborationCommand) -> dict[str, object]:
    result = await inspector_execution_loop.run_once(command)
    return result.model_dump(mode="json")


@app.post("/use-cases/copilot-governance/demo", tags=["copilot-governance"])
async def run_copilot_governance_demo(command: CopilotGovernanceCommand) -> dict[str, object]:
    result = await copilot_demo_runtime.run(command)
    return result.model_dump(mode="json")


@app.get("/runtime/console", tags=["runtime"])
async def runtime_console() -> dict[str, object]:
    event_snapshot = await event_bus.snapshot(limit=20)
    pending_approvals = await approval_queue.list_pending()
    relationships = await graph_store.relationships_for_tenant(pending_approvals[0].tenant_id) if pending_approvals else []
    return {
        "runtime": {
            "phase": "3.1-backend-core",
            "system_of_record": "postgresql" if postgres_mode else "memory-test-mode",
            "ui_status": "deferred",
        },
        "events": {
            "metrics": event_snapshot.metrics,
            "recent": [event.model_dump(mode="json") for event in event_snapshot.recent_events],
            "dead_letters": [
                {
                    "dead_letter_id": str(record.dead_letter_id),
                    "event_id": str(record.event.event_id),
                    "event_type": record.event.event_type,
                    "subscriber_name": record.subscriber_name,
                    "error_type": record.error_type,
                    "error_message": record.error_message,
                    "failed_at": record.failed_at.isoformat(),
                }
                for record in event_snapshot.dead_letters
            ],
        },
        "governance": {
            "pending_approvals": [approval.model_dump(mode="json") for approval in pending_approvals],
        },
        "graph": {
            "relationship_count_for_first_pending_tenant": len(relationships),
        },
        "inspectors": {
            "registered": sorted(inspector_runtime.inspectors.keys()),
        },
    }
