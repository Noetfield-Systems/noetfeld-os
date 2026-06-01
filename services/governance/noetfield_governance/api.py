"""FastAPI entrypoint for the Noetfield backend runtime core."""

import asyncio
import logging
from pathlib import Path
from typing import Literal
from uuid import UUID

from noetfield_config import CANONICAL_INTAKE_EMAIL, COMPLIANCE_REMEDIATION_TIP

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from noetfield_governance.chat_errors import ChatAPIError, ChatConfigurationError
from noetfield_governance.public_chat import answer_public_question, resolve_chat_provider
from noetfield_governance import intake_repository, redis_runtime
from noetfield_governance.intake_notify import notify_ops_webhook
from noetfield_governance.public_intake import submit_intake
from noetfield_governance.telegram_client import (
    TelegramAPIError,
    TelegramConfigurationError,
    get_me,
    get_webhook_info,
    set_my_commands,
    set_webhook,
    summarize_webhook_info,
)
from noetfield_governance.telegram_commands import BOT_COMMANDS
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
from noetfield_governance.governance_rid import generate_rid, normalize_rid
from noetfield_governance.governance_v1 import GovernanceV1Deps, router as governance_v1_router
from noetfield_governance.governance_webhooks import GovernanceWebhookDispatcher
from noetfield_governance.public_openapi import install_public_openapi
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
    version="0.4.0",
    description="Backend runtime core for governed ambient intelligence.",
)

install_public_openapi(app)
app.include_router(governance_v1_router)

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
        allow_headers=["Content-Type", "Authorization"],
    )

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ASSETS_DIR = _REPO_ROOT / "assets"
if _ASSETS_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=_ASSETS_DIR), name="noetfield-assets")

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

governance_webhooks = GovernanceWebhookDispatcher.from_settings(
    settings.governance_webhook_urls,
    settings.governance_webhook_secret,
)
app.state.governance_v1_deps = GovernanceV1Deps(
    engine=golden_edge_v3,
    event_bus=event_bus,
    audit_store=audit_store,
    webhooks=governance_webhooks,
    signal_pipeline=signal_pipeline,
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
async def startup_platform() -> None:
    await intake_repository.init_intake_repository(settings)
    await redis_runtime.connect(
        settings.redis_url,
        enabled=settings.redis_sessions_enabled,
    )
    await event_bus.subscribe(name="audit-ledger-runtime", event_types={"*"}, handler=audit_runtime.record_event)


@app.on_event("shutdown")
async def shutdown_runtime() -> None:
    await intake_repository.close_intake_repository()
    await redis_runtime.close()
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


@app.get("/health", tags=["system"], include_in_schema=True)
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "noetfield-platform",
        "runtime": "phase-3.1-backend-core",
        "golden_edge": "v3",
        "governance_api": "/api/v1/governance",
        "system_of_record": "postgresql" if postgres_mode else "memory-test-mode",
        "supabase_authority": "optional-tooling-only",
        "intake_storage": intake_repository.storage_label(),
        "redis_sessions": redis_runtime.is_enabled(),
    }


@app.get("/api/status", tags=["system"], include_in_schema=True)
async def api_status() -> dict[str, object]:
    """Institutional status summary for www status page and monitors."""
    eco = await ecosystem_health()
    return {
        "service": "noetfield-platform",
        "status": "operational" if eco.get("ok") else "degraded",
        "status_page": settings.public_status_page_url,
        "legal": "https://www.noetfield.com/legal/",
        "ecosystem": eco,
        "governance_pilot_auth_required": settings.governance_pilot_auth_required,
        "openapi": "/openapi.json",
        "public_docs": "https://www.noetfield.com/docs/api/",
    }


@app.post("/v3/evaluate", tags=["golden-edge-v3"], include_in_schema=False)
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


@app.get("/v3/ledger", tags=["golden-edge-v3"], include_in_schema=False)
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


@app.get("/console", tags=["governance-console-v1"], include_in_schema=False)
@app.get("/", tags=["governance-console-v1"], include_in_schema=False)
async def governance_console_v1() -> FileResponse:
    if not _CONSOLE_HTML.is_file():
        raise HTTPException(status_code=503, detail="Governance Evaluation Interface assets missing")
    return FileResponse(_CONSOLE_HTML, media_type="text/html")


@app.post("/v3/agent-loop", tags=["golden-edge-v3"], include_in_schema=False)
async def golden_edge_agent_loop(request: GoldenEdgeEvaluateRequest) -> dict[str, object]:
    result = await golden_edge_v3.agent_loop(request)
    return result.model_dump(mode="json")


@app.get("/events/catalog", tags=["events"], include_in_schema=False)
async def events_catalog() -> dict[str, dict[str, str]]:
    return event_catalog()


@app.get("/events/replay", tags=["events"], include_in_schema=False)
async def replay_events(after_sequence: int = 0, event_type: str = "*") -> list[dict[str, object]]:
    events = await event_bus.replay(
        EventReplayCursor(after_sequence=after_sequence, event_types=frozenset({event_type}))
    )
    return [event.model_dump(mode="json") for event in events]


@app.post("/ingestion/manual", tags=["ingestion"], include_in_schema=False)
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


@app.post("/ingestion/webhook/{source_name}", tags=["ingestion"], include_in_schema=False)
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


@app.post("/signals/ingest", tags=["signals"], include_in_schema=False)
async def ingest_signal(command: IngestSignalCommand) -> dict[str, object]:
    signal, trace = await signal_pipeline.ingest(command)
    return {"signal": signal.model_dump(mode="json"), "trace": trace}


@app.post("/graph/relationships/mutate", tags=["graph"], include_in_schema=False)
async def mutate_relationship(command: GraphMutationCommand) -> dict[str, object]:
    result = await graph_mutations.mutate_relationship(command)
    return result.model_dump(mode="json")


@app.post("/graph/reflections/run", tags=["graph"], include_in_schema=False)
async def run_graph_reflection(request: ReflectionRequest) -> dict[str, object]:
    result = await graph_reflections.run(request.tenant_id, request.organization_id)
    return result.model_dump(mode="json")


@app.post("/workflows/start", tags=["workflow"], include_in_schema=False)
async def start_workflow(workflow: WorkflowInstance) -> dict[str, object]:
    result = await workflow_state_machine.start(workflow)
    return result.model_dump(mode="json")


@app.post("/workflows/transition", tags=["workflow"], include_in_schema=False)
async def transition_workflow(command: WorkflowTransitionCommand) -> dict[str, object]:
    result = await workflow_state_machine.transition(command)
    return result.model_dump(mode="json")


@app.post("/governance/execute", tags=["governance"], include_in_schema=False)
async def execute_governance(command: GovernanceActionCommand) -> dict[str, object]:
    result = await governance_runtime.execute(command)
    return result.model_dump(mode="json")


@app.get("/approvals", tags=["governance"], include_in_schema=False)
async def list_approvals(tenant_id: UUID | None = None) -> list[dict[str, object]]:
    approvals = await approval_queue.list_pending(tenant_id)
    return [approval.model_dump(mode="json") for approval in approvals]


@app.post("/approvals/decide", tags=["governance"], include_in_schema=False)
async def decide_approval(request: ApprovalDecisionRequest) -> dict[str, object]:
    trace = await governance_runtime.decide_approval(
        tenant_id=request.tenant_id,
        organization_id=request.organization_id,
        decision=request.decision,
    )
    return {"trace": trace}


@app.post("/inspectors/collaborate", tags=["inspectors"], include_in_schema=False)
async def collaborate_inspectors(command: InspectorCollaborationCommand) -> dict[str, object]:
    result = await inspector_runtime.run(command)
    return result.model_dump(mode="json")


@app.post("/inspectors/execute", tags=["inspectors"], include_in_schema=False)
async def execute_inspectors(command: InspectorCollaborationCommand) -> dict[str, object]:
    result = await inspector_execution_loop.run_once(command)
    return result.model_dump(mode="json")


@app.post("/use-cases/copilot-governance/demo", tags=["copilot-governance"], include_in_schema=False)
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
    citations: list[str] = Field(default_factory=list)
    intake_email: str = CANONICAL_INTAKE_EMAIL


class PublicIntakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization: str = Field(..., min_length=1, max_length=200)
    contact_email: str = Field(..., min_length=3, max_length=254)
    message: str = Field(..., min_length=1, max_length=8000)
    contact_name: str | None = Field(default=None, max_length=120)
    request_id: str | None = Field(default=None, max_length=64)
    sku: Literal["trust_brief", "copilot", "bank_pilot", "general"] = "trust_brief"
    vector: str = Field(default="web-intake", max_length=120)
    source: Literal["web", "telegram", "api"] = "web"
    metadata: dict[str, object] = Field(default_factory=dict)


class PublicIntakeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool = True
    intake_id: str
    request_id: str | None
    intake_email: str = CANONICAL_INTAKE_EMAIL
    message: str = "Intake recorded. Operations will follow up via email."


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
        reply, provider, citations = await answer_public_question(
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
    return PublicChatResponse(reply=reply, provider=provider, citations=citations)


@app.get("/api/intake/health", tags=["intake"])
async def intake_health() -> dict[str, object]:
    return {
        "enabled": settings.public_intake_enabled,
        "intake_email": CANONICAL_INTAKE_EMAIL,
        "storage": intake_repository.storage_label(),
        "ops_webhook_configured": bool((settings.intake_ops_webhook_url or "").strip()),
        "redis_rate_limit": redis_runtime.is_enabled(),
    }


async def _notify_intake_background(record: object) -> None:
    from noetfield_governance.intake_store import IntakeRecord

    if not isinstance(record, IntakeRecord):
        return
    url = (settings.intake_ops_webhook_url or "").strip()
    if url:
        await asyncio.to_thread(notify_ops_webhook, url, record)


@app.post("/api/intake", tags=["intake"], response_model=PublicIntakeResponse)
async def public_intake(
    body: PublicIntakeRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> PublicIntakeResponse:
    if not settings.public_intake_enabled:
        raise HTTPException(status_code=503, detail="Public intake API is disabled")
    client_host = request.client.host if request.client else "unknown"
    client_key = f"{client_host}:{body.contact_email}"
    try:
        rec = await submit_intake(
            organization=body.organization,
            contact_email=body.contact_email,
            message=body.message,
            request_id=body.request_id,
            contact_name=body.contact_name,
            sku=body.sku,
            vector=body.vector,
            source=body.source,
            client_key=client_key,
            metadata=body.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    logger.info(
        "public_intake_recorded intake_id=%s rid=%s org=%s",
        rec.intake_id,
        rec.request_id or "",
        rec.organization[:80],
    )
    background_tasks.add_task(_notify_intake_background, rec)
    return PublicIntakeResponse(
        intake_id=rec.intake_id,
        request_id=rec.request_id,
    )


@app.get("/api/intake/recent", tags=["intake"], include_in_schema=False)
async def intake_recent(request: Request, limit: int = 20) -> dict[str, object]:
    """Operations view — requires TELEGRAM_WEBHOOK_SECRET as X-Admin-Secret when configured."""
    admin_secret = _secret(settings.telegram_webhook_secret)
    if admin_secret:
        auth = request.headers.get("X-Admin-Secret", "")
        if auth != admin_secret:
            raise HTTPException(status_code=403, detail="Invalid admin secret")
    if not settings.public_intake_enabled:
        raise HTTPException(status_code=503, detail="Public intake API is disabled")

    return {
        "intake_email": CANONICAL_INTAKE_EMAIL,
        "storage": intake_repository.storage_label(),
        "records": await intake_repository.list_recent(limit=limit),
    }


@app.get("/api/ecosystem/public", tags=["ecosystem"])
async def ecosystem_public() -> dict[str, object]:
    """Non-secret config for www (also in assets/noetfield-ecosystem.json)."""
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[3] / "assets" / "noetfield-ecosystem.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    base = (settings.telegram_webhook_base_url or "https://platform.noetfield.com").strip().rstrip("/")
    return {
        "intake_email": CANONICAL_INTAKE_EMAIL,
        "intake_url": "https://www.noetfield.com/trust-brief/intake/",
        "chat_api_base": base,
    }


class TelegramWebhookBody(BaseModel):
    model_config = ConfigDict(extra="allow")


@app.get("/api/telegram/health", tags=["telegram"])
async def telegram_health() -> dict[str, object]:
    token = _secret(settings.telegram_bot_token)
    base = (settings.telegram_webhook_base_url or "").strip().rstrip("/")
    expected_webhook_url = f"{base}/api/telegram/webhook" if base else None
    payload: dict[str, object] = {
        "enabled": settings.telegram_bot_enabled,
        "configured": bool(token),
        "webhook_base_url_set": bool(base),
        "expected_webhook_url": expected_webhook_url,
        "webhook_secret_configured": bool(_secret(settings.telegram_webhook_secret)),
        "llm_configured": bool(_secret(settings.openrouter_api_key) or _secret(settings.gemini_api_key)),
    }
    if not token:
        payload["ready"] = False
        payload["hint"] = "Set TELEGRAM_BOT_TOKEN on the platform API host (not www)."
        return payload

    bot: dict[str, object] | None = None
    webhook: dict[str, object] | None = None
    try:
        me = await asyncio.to_thread(get_me, token=token)
        if isinstance(me.get("result"), dict):
            result = me["result"]
            bot = {
                "id": result.get("id"),
                "username": result.get("username"),
                "can_read_all_group_messages": result.get("can_read_all_group_messages"),
            }
        info = await asyncio.to_thread(get_webhook_info, token=token)
        webhook = summarize_webhook_info(info)
    except TelegramAPIError as exc:
        payload["telegram_api_error"] = str(exc)
        payload["ready"] = False
        return payload

    payload["bot"] = bot
    payload["webhook"] = webhook
    registered_url = str((webhook or {}).get("url") or "")
    url_ok = bool(expected_webhook_url and registered_url == expected_webhook_url)
    pending = int((webhook or {}).get("pending_update_count") or 0)
    last_err = (webhook or {}).get("last_error_message")
    payload["webhook_url_matches"] = url_ok
    payload["ready"] = (
        settings.telegram_bot_enabled
        and bool(bot)
        and bool(registered_url)
        and url_ok
        and not last_err
    )
    if not settings.telegram_bot_enabled:
        payload["hint"] = "TELEGRAM_BOT_ENABLED is false."
    elif not base:
        payload["hint"] = "Set TELEGRAM_WEBHOOK_BASE_URL and POST /api/telegram/register-webhook."
    elif not registered_url:
        payload["hint"] = "Webhook not registered — call POST /api/telegram/register-webhook."
    elif not url_ok:
        payload["hint"] = "Registered webhook URL does not match TELEGRAM_WEBHOOK_BASE_URL — re-register."
    elif last_err:
        payload["hint"] = f"Telegram reports webhook error: {last_err}"
    elif pending > 0:
        payload["hint"] = f"{pending} pending update(s) — delivery may be delayed; check API logs."
    elif not payload["llm_configured"]:
        payload["hint"] = "Commands work; free-text needs OPENROUTER_API_KEY or GEMINI_API_KEY."
    else:
        payload["hint"] = "Bot should respond. Send /start in Telegram to verify."
    return payload


@app.get("/api/ecosystem/health", tags=["ecosystem"])
async def ecosystem_health() -> dict[str, object]:
    """Combined status for website chat + Telegram + LLM providers."""
    chat = await public_chat_health()
    telegram = await telegram_health()
    intake = await intake_health()
    chat_ok = bool(chat.get("configured")) and settings.public_chat_enabled
    intake_ok = bool(intake.get("enabled"))
    telegram_ready = telegram.get("ready")
    if telegram_ready is not None:
        telegram_ok = bool(telegram_ready)
    else:
        telegram_ok = bool(telegram.get("configured")) and settings.telegram_bot_enabled
    return {
        "intake_email": CANONICAL_INTAKE_EMAIL,
        "website_chat": chat,
        "telegram": telegram,
        "intake_api": intake,
        "ok": chat_ok or telegram_ok or intake_ok,
    }


async def _process_telegram_update(update: dict[str, object]) -> None:
    """Background worker — Telegram requires a fast HTTP 200 from the webhook."""
    token = _secret(settings.telegram_bot_token)
    if not token:
        return
    try:
        handled = await handle_telegram_update(
            update,
            bot_token=token,
            chat_provider=settings.public_chat_provider,
            gemini_api_key=_secret(settings.gemini_api_key) or None,
            gemini_model=settings.gemini_model,
            openrouter_api_key=_secret(settings.openrouter_api_key) or None,
            openrouter_model=settings.openrouter_model,
        )
        if not handled:
            logger.warning("telegram_update_not_handled keys=%s", sorted(update.keys()))
    except Exception:
        logger.exception("telegram_update_worker_failed")


@app.post("/api/telegram/webhook", tags=["telegram"])
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, object]:
    if not settings.telegram_bot_enabled:
        raise HTTPException(status_code=503, detail="Telegram bot is disabled")
    token = _secret(settings.telegram_bot_token)
    if not token:
        raise HTTPException(status_code=503, detail="Telegram bot token not configured")

    expected_secret = _secret(settings.telegram_webhook_secret)
    if expected_secret:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if header_secret != expected_secret:
            logger.warning("telegram_webhook_secret_mismatch")
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

    try:
        update = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc
    if not isinstance(update, dict):
        raise HTTPException(status_code=400, detail="Invalid update payload")

    background_tasks.add_task(_process_telegram_update, update)
    return {"ok": True}


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
        commands = await asyncio.to_thread(
            set_my_commands,
            token=token,
            commands=BOT_COMMANDS,
        )
        info = await asyncio.to_thread(get_webhook_info, token=token)
    except TelegramConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except TelegramAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"setWebhook": result, "setMyCommands": commands, "webhookInfo": info, "url": webhook_url}


@app.get("/runtime/console", tags=["runtime"], include_in_schema=False)
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
