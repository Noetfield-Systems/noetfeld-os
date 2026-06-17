"""FastAPI entrypoint for the Noetfield backend runtime core."""

from uuid import UUID, uuid4

from fastapi import FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict

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
from noetfield_events.context import reset_request_context, set_request_context
from noetfield_factories import (
    FactoryRunRequest,
    FactoryStatus,
    FactoryValidationError,
    catalog_factory_entries,
    get_factory_runner,
    is_factory_live,
    list_factory_ids,
    load_factory_catalog,
    load_tier_catalog,
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

golden_edge_v3 = GoldenEdgeV3Engine(governance_runtime=governance_runtime)

copilot_demo_runtime = CopilotGovernanceDemoRuntime(
    signal_pipeline=signal_pipeline,
    graph_mutations=graph_mutations,
    graph_reflections=graph_reflections,
    workflow_state_machine=workflow_state_machine,
    governance_runtime=governance_runtime,
    golden_edge=golden_edge_v3,
    inspector_execution_loop=inspector_execution_loop,
    run_store=copilot_run_store,
)

copilot_factory_runner = get_factory_runner(
    "copilot_governance_readiness_v1",
    demo_runtime=copilot_demo_runtime,
    event_bus=event_bus,
    audit_store=audit_store,
    graph_store=graph_store,
    governance_runtime=governance_runtime,
)


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


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or request.headers.get("X-Request-ID")
    correlation_id = uuid4()
    correlation_header = request.headers.get("X-Correlation-Id")
    if correlation_header:
        try:
            correlation_id = UUID(correlation_header)
        except ValueError:
            pass
    rid_token, corr_token = set_request_context(
        source_request_id=request_id,
        correlation_id=correlation_id,
    )
    try:
        response = await call_next(request)
        if request_id:
            response.headers["X-Request-Id"] = request_id
        return response
    finally:
        reset_request_context(rid_token, corr_token)


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
    return result.model_dump(mode="json")


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


@app.get("/factories", tags=["factories"])
async def list_factories() -> dict[str, object]:
    catalog = load_factory_catalog()
    factories = []
    for entry in catalog_factory_entries():
        factories.append(
            {
                "id": entry["id"],
                "name": entry.get("name"),
                "tier": entry.get("tier"),
                "capability": entry.get("capability"),
                "sku": entry.get("sku"),
                "status": entry.get("status"),
                "route": entry.get("route"),
                "visibility": entry.get("visibility"),
                "callable": entry.get("status") == "live",
            }
        )
    return {
        "catalog_version": catalog.get("catalog_version"),
        "platform_layers": catalog.get("platform_layers"),
        "live_factories": list_factory_ids(),
        "factories": factories,
    }


@app.get("/catalog/tiers", tags=["catalog"])
async def catalog_tiers() -> dict[str, object]:
    tier_catalog = load_tier_catalog()
    factory_catalog = load_factory_catalog()
    return {
        "catalog_version": tier_catalog.get("catalog_version"),
        "allowed_gtm_skus": tier_catalog.get("allowed_gtm_skus"),
        "tiers": tier_catalog.get("tiers"),
        "factory_catalog_entries": tier_catalog.get("factory_catalog_entries"),
        "platform_layers": factory_catalog.get("platform_layers"),
        "platform_layer_anchors": factory_catalog.get("platform_layer_anchors"),
    }


@app.post("/factories/{factory_id}/run", tags=["factories"])
async def run_factory(
    factory_id: str,
    command: CopilotGovernanceCommand,
    response: Response,
    x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
) -> dict[str, object]:
    if not is_factory_live(factory_id):
        raise HTTPException(status_code=404, detail=f"Factory not live or unknown: {factory_id}")
    if factory_id != copilot_factory_runner.FACTORY_ID:
        raise HTTPException(status_code=404, detail=f"Factory runner not wired: {factory_id}")

    try:
        result = await copilot_factory_runner.run(
            FactoryRunRequest(command=command, source_request_id=x_request_id)
        )
    except FactoryValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = result.model_dump(mode="json")
    if result.factory_status == FactoryStatus.VETOED:
        raise HTTPException(status_code=403, detail=payload)
    if result.factory_status == FactoryStatus.PENDING_APPROVAL:
        response.status_code = 202
    return payload


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
