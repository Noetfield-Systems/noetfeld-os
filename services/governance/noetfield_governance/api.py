"""FastAPI entrypoint for the Noetfield Phase 3 runtime."""

from uuid import UUID

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from noetfield_events import AsyncEventBus, EventReplayCursor, event_catalog
from noetfield_governance.runtime import (
    ApprovalDecision,
    GovernanceActionCommand,
    GovernanceRuntime,
    HumanApprovalQueue,
)
from noetfield_graph import (
    GraphMutationCommand,
    InMemoryGraphStore,
    LiveGraphMutationEngine,
    TemporalGraphReflectionCycle,
)
from noetfield_inspectors import (
    InspectorCollaborationCommand,
    InspectorCollaborationRuntime,
    LeadScoutInspector,
    OpportunityHunterInspector,
    ThreatMonitorInspector,
)
from noetfield_signals import InMemorySignalStore, IngestSignalCommand, SignalIngestionPipeline

app = FastAPI(
    title="Noetfield Platform API",
    version="0.3.1",
    description="Runtime activation for governed ambient intelligence.",
)

event_bus = AsyncEventBus()
signal_store = InMemorySignalStore()
graph_store = InMemoryGraphStore()
approval_queue = HumanApprovalQueue()

signal_pipeline = SignalIngestionPipeline(event_bus=event_bus, store=signal_store)
graph_mutations = LiveGraphMutationEngine(event_bus=event_bus, store=graph_store)
graph_reflections = TemporalGraphReflectionCycle(event_bus=event_bus, store=graph_store)
governance_runtime = GovernanceRuntime(event_bus=event_bus, approvals=approval_queue)
inspector_runtime = InspectorCollaborationRuntime(event_bus=event_bus)
inspector_runtime.register(OpportunityHunterInspector())
inspector_runtime.register(ThreatMonitorInspector())
inspector_runtime.register(LeadScoutInspector())


class ApprovalDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    decision: ApprovalDecision


class ReflectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "noetfield-platform", "runtime": "phase-3"}


@app.get("/events/catalog", tags=["events"])
async def events_catalog() -> dict[str, dict[str, str]]:
    return event_catalog()


@app.get("/events/replay", tags=["events"])
async def replay_events(after_sequence: int = 0, event_type: str = "*") -> list[dict[str, object]]:
    events = await event_bus.replay(
        EventReplayCursor(after_sequence=after_sequence, event_types=frozenset({event_type}))
    )
    return [event.model_dump(mode="json") for event in events]


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


@app.get("/runtime/console", tags=["runtime"])
async def runtime_console() -> dict[str, object]:
    event_snapshot = await event_bus.snapshot(limit=20)
    pending_approvals = await approval_queue.list_pending()
    relationships = list(graph_store.relationships.values())
    return {
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
            "relationship_count": len(relationships),
            "low_confidence_relationship_count": len(
                [
                    relationship
                    for relationship in relationships
                    if relationship.confidence.score < graph_reflections.low_confidence_threshold
                ]
            ),
        },
        "inspectors": {
            "registered": sorted(inspector_runtime.inspectors.keys()),
        },
    }
