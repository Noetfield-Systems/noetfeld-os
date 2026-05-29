"""FastAPI entrypoint for the Noetfield backend runtime core."""

import asyncio
import logging
from pathlib import Path
from uuid import UUID

from noetfield_config import CANONICAL_INTAKE_EMAIL, COMPLIANCE_REMEDIATION_TIP

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from noetfield_governance.chat_errors import ChatAPIError, ChatConfigurationError
from noetfield_governance.public_chat import answer_public_question, resolve_chat_provider
from noetfield_governance.telegram_client import (
    TelegramAPIError,
    TelegramConfigurationError,
    get_webhook_info,
    set_webhook,
)
from noetfield_governance.telegram_webhook import handle_telegram_update

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
logger = logging.getLogger("noetfield.governance.api")

app = FastAPI(
    title="Noetfield Platform API",
    version="0.3.1",
    description="Backend runtime core for governed ambient intelligence.",
)

_cors_origins = [
    o.strip()
    for o in settings.public_chat_cors_origins.split(",")
    if o.strip()
]
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
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
        logger.warning(
            "governance_evaluation_anomaly decision=REJECT tenant_id=%s action=%s resource=%s/%s reason_code=%s %s intake=%s",
            request.tenant_id,
            request.action,
            request.resource_type,
            request.resource_id,
            result.reason_code,
            COMPLIANCE_REMEDIATION_TIP,
            CANONICAL_INTAKE_EMAIL,
        )
        await event_bus.publish(
            build_event(
                event_type=EventType.GOVERNANCE_VETOED,
                tenant_id=request.tenant_id,
                organization_id=request.organization_id,
                actor=actor,
                source_service="golden-edge-v3",
                entity_type=request.resource_type,
                entity_id=request.resource_id,
                payload={
                    "reason": result.reason,
                    "reason_code": result.reason_code,
                    "compliance_remediation_email": CANONICAL_INTAKE_EMAIL,
                    "compliance_remediation_tip": COMPLIANCE_REMEDIATION_TIP,
                },
            )
        )
    elif result.decision.value == "REQUIRE_HUMAN_REVIEW":
        logger.info(
            "governance_evaluation_review_required tenant_id=%s action=%s intake=%s",
            request.tenant_id,
            request.action,
            CANONICAL_INTAKE_EMAIL,
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


class PublicChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, max_length=64)


class PublicChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply: str
    provider: str
    intake_email: str = CANONICAL_INTAKE_EMAIL


def _secret(value: SecretStr | None) -> str:
    return value.get_secret_value().strip() if value else ""


@app.get("/api/public/chat/health", tags=["public-chat"])
async def public_chat_health() -> dict[str, object]:
    gemini_key = _secret(settings.gemini_api_key)
    openrouter_key = _secret(settings.openrouter_api_key)
    try:
        active, _ = resolve_chat_provider(
            preference=settings.public_chat_provider,
            gemini_api_key=gemini_key or None,
            openrouter_api_key=openrouter_key or None,
        )
        configured = True
    except ChatConfigurationError:
        active = None
        configured = False
    return {
        "enabled": settings.public_chat_enabled,
        "configured": configured,
        "provider_preference": settings.public_chat_provider,
        "active_provider": active,
        "gemini": {"configured": bool(gemini_key), "model": settings.gemini_model},
        "openrouter": {"configured": bool(openrouter_key), "model": settings.openrouter_model},
    }


@app.post("/api/public/chat", tags=["public-chat"], response_model=PublicChatResponse)
async def public_chat(body: PublicChatRequest, request: Request) -> PublicChatResponse:
    if not settings.public_chat_enabled:
        raise HTTPException(status_code=503, detail="Public chat is disabled")
    client_host = request.client.host if request.client else "unknown"
    client_key = f"{client_host}:{body.session_id or 'anon'}"
    try:
        reply, provider = await answer_public_question(
            message=body.message,
            provider=settings.public_chat_provider,
            gemini_api_key=_secret(settings.gemini_api_key) or None,
            gemini_model=settings.gemini_model,
            openrouter_api_key=_secret(settings.openrouter_api_key) or None,
            openrouter_model=settings.openrouter_model,
            client_key=client_key,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except ChatConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ChatAPIError as exc:
        logger.warning("public_chat_llm_error %s", exc)
        raise HTTPException(status_code=502, detail="Assistant temporarily unavailable") from exc
    return PublicChatResponse(reply=reply, provider=provider)


class TelegramWebhookBody(BaseModel):
    model_config = ConfigDict(extra="allow")


@app.get("/api/telegram/health", tags=["telegram"])
async def telegram_health() -> dict[str, object]:
    token = _secret(settings.telegram_bot_token)
    webhook_url = None
    if token and settings.telegram_webhook_base_url:
        webhook_url = settings.telegram_webhook_base_url.rstrip("/") + "/api/telegram/webhook"
    return {
        "enabled": settings.telegram_bot_enabled,
        "configured": bool(token),
        "webhook_url": webhook_url,
        "webhook_secret_configured": bool(_secret(settings.telegram_webhook_secret)),
    }


@app.get("/api/ecosystem/health", tags=["ecosystem"])
async def ecosystem_health() -> dict[str, object]:
    """Combined status for website chat + Telegram + LLM providers."""
    chat = await public_chat_health()
    telegram = await telegram_health()
    chat_ok = bool(chat.get("configured")) and settings.public_chat_enabled
    telegram_ok = bool(telegram.get("configured")) and settings.telegram_bot_enabled
    return {
        "intake_email": CANONICAL_INTAKE_EMAIL,
        "website_chat": chat,
        "telegram": telegram,
        "ok": chat_ok or telegram_ok,
    }


@app.post("/api/telegram/webhook", tags=["telegram"])
async def telegram_webhook(request: Request) -> dict[str, object]:
    if not settings.telegram_bot_enabled:
        raise HTTPException(status_code=503, detail="Telegram bot is disabled")
    token = _secret(settings.telegram_bot_token)
    if not token:
        raise HTTPException(status_code=503, detail="Telegram bot token not configured")

    expected_secret = _secret(settings.telegram_webhook_secret)
    if expected_secret:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if header_secret != expected_secret:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

    try:
        update = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc
    if not isinstance(update, dict):
        raise HTTPException(status_code=400, detail="Invalid update payload")

    handled = await handle_telegram_update(
        update,
        bot_token=token,
        chat_provider=settings.public_chat_provider,
        gemini_api_key=_secret(settings.gemini_api_key) or None,
        gemini_model=settings.gemini_model,
        openrouter_api_key=_secret(settings.openrouter_api_key) or None,
        openrouter_model=settings.openrouter_model,
    )
    return {"ok": True, "handled": handled}


@app.post("/api/telegram/register-webhook", tags=["telegram"])
async def telegram_register_webhook(request: Request) -> dict[str, object]:
    """Register Telegram webhook (requires TELEGRAM_WEBHOOK_SECRET header if configured)."""
    if not settings.telegram_bot_enabled:
        raise HTTPException(status_code=503, detail="Telegram bot is disabled")
    token = _secret(settings.telegram_bot_token)
    if not token:
        raise HTTPException(status_code=503, detail="Telegram bot token not configured")
    base = (settings.telegram_webhook_base_url or "").strip().rstrip("/")
    if not base:
        raise HTTPException(status_code=400, detail="TELEGRAM_WEBHOOK_BASE_URL is not set")

    admin_secret = _secret(settings.telegram_webhook_secret)
    if admin_secret:
        auth = request.headers.get("X-Admin-Secret", "")
        if auth != admin_secret:
            raise HTTPException(status_code=403, detail="Invalid admin secret")

    webhook_url = f"{base}/api/telegram/webhook"
    secret_token = admin_secret or None
    try:
        result = await asyncio.to_thread(
            set_webhook,
            token=token,
            webhook_url=webhook_url,
            secret_token=secret_token,
        )
        info = await asyncio.to_thread(get_webhook_info, token=token)
    except TelegramConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except TelegramAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"setWebhook": result, "webhookInfo": info, "url": webhook_url}


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
