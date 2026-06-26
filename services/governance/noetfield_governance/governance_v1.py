"""Institutional pilot API — /api/v1/governance/* (documented stable surface)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from noetfield_config import CANONICAL_INTAKE_EMAIL, COMPLIANCE_REMEDIATION_TIP, get_settings
from noetfield_events import EventType, build_event
from noetfield_governance.gel_adapter import GelAdapter
from noetfield_governance.governance_config import config_policy_version_hash, load_governance_config
from noetfield_governance.golden_edge_v3 import (
    AgentLoopDecision,
    GoldenEdgeEvaluateRequest,
    GoldenEdgeV3Engine,
)
from noetfield_governance.governance_rid import generate_rid, normalize_rid
from noetfield_governance.governance_webhooks import GovernanceWebhookDispatcher
from noetfield_governance.governance_pilot_limits import check_governance_pilot_rate_limit
from noetfield_governance.pilot_auth import PilotAuthContext, assert_tenant_allowed, require_pilot_auth
from noetfield_governance.partner_signal import (
    PartnerSignalIngestRequest,
    normalize_partner_signal,
    partner_evaluate_scenario_preset,
)
from noetfield_ledger import AuditLedgerStore
from noetfield_signals import SignalIngestionPipeline
from noetfield_types import Actor, ActorType

logger = logging.getLogger("noetfield.governance.v1")

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_GOV_CONFIG = _REPO_ROOT / "docs" / "spec" / "samples" / "governance-copilot-v1.yaml"


def _resolve_governance_config_hash(payload: dict[str, object]) -> str | None:
    config_path = payload.get("governance_config_path")
    path = Path(str(config_path)) if config_path else _DEFAULT_GOV_CONFIG
    if not path.is_file():
        return None
    try:
        return config_policy_version_hash(load_governance_config(path))
    except (OSError, ValueError):
        return None


router = APIRouter(prefix="/api/v1/governance", tags=["governance-v1"])


@dataclass
class GovernanceV1Deps:
    engine: GoldenEdgeV3Engine
    event_bus: object
    audit_store: AuditLedgerStore
    webhooks: GovernanceWebhookDispatcher
    signal_pipeline: SignalIngestionPipeline | None = None


def get_governance_v1_deps(request: Request) -> GovernanceV1Deps:
    deps = getattr(request.app.state, "governance_v1_deps", None)
    if deps is None:
        raise HTTPException(status_code=503, detail="Governance API dependencies not initialized")
    return deps


class GovernanceEvaluateV1Request(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    action: str
    resource_type: str
    resource_id: str
    actor_id: str = "governance-api-v1"
    actor_type: ActorType = ActorType.SERVICE
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    payload: dict[str, object] = Field(default_factory=dict)
    request_id: str | None = Field(
        default=None,
        description="RID-… lineage id; auto-generated when omitted.",
    )
    correlation_id: str | None = Field(
        default=None,
        max_length=128,
        description="Bank orchestration correlation id (opaque string).",
    )
    mode: Literal["shadow", "enforce"] = Field(
        default="shadow",
        description="Bank Pilot uses shadow only — evaluate without execution side effects.",
    )


class GovernanceEvaluateV1Response(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    correlation_id: str | None = None
    mode: Literal["shadow", "enforce"]
    decision: str
    allowed: bool
    reason: str
    reason_code: str
    policy_refs: list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)
    policy_version_hash: str | None = None
    config_policy_version_hash: str | None = None
    ledger_event_id: str | None = None
    gel_lane: str | None = None
    non_psp_boundary: str = (
        "Noetfield does not execute payments, hold custody, or operate as a PSP/MSB."
    )


async def _publish_evaluate_events(
    deps: GovernanceV1Deps,
    request: GovernanceEvaluateV1Request,
    result: object,
    rid: str,
) -> None:
    from noetfield_events import AsyncEventBus

    assert isinstance(deps.event_bus, AsyncEventBus)
    actor = Actor(
        actor_type=request.actor_type,
        actor_id=request.actor_id,
        display_name=request.actor_id,
    )
    result_dump = result.model_dump(mode="json") if hasattr(result, "model_dump") else dict(result)
    payload = {
        **result_dump,
        "mode": request.mode,
        "correlation_id": request.correlation_id,
        "request_id": rid,
        "console": "governance-api-v1",
    }
    await deps.event_bus.publish(
        build_event(
            event_type=EventType.POLICY_EVALUATED,
            tenant_id=request.tenant_id,
            organization_id=request.organization_id,
            actor=actor,
            source_service="governance-api-v1",
            entity_type=request.resource_type,
            entity_id=request.resource_id,
            payload=payload,
            source_request_id=rid,
        )
    )
    if result_dump.get("decision") == "REJECT":
        await deps.event_bus.publish(
            build_event(
                event_type=EventType.GOVERNANCE_VETOED,
                tenant_id=request.tenant_id,
                organization_id=request.organization_id,
                actor=actor,
                source_service="governance-api-v1",
                entity_type=request.resource_type,
                entity_id=request.resource_id,
                payload={
                    "reason": result_dump.get("reason"),
                    "reason_code": result_dump.get("reason_code"),
                    "request_id": rid,
                    "compliance_remediation_email": CANONICAL_INTAKE_EMAIL,
                    "compliance_remediation_tip": COMPLIANCE_REMEDIATION_TIP,
                },
                source_request_id=rid,
            )
        )


@router.post("/evaluate", response_model=GovernanceEvaluateV1Response)
async def governance_evaluate_v1(
    body: GovernanceEvaluateV1Request,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: GovernanceV1Deps = Depends(get_governance_v1_deps),
) -> GovernanceEvaluateV1Response:
    await check_governance_pilot_rate_limit(auth, "evaluate")
    assert_tenant_allowed(auth, body.tenant_id)
    try:
        rid = normalize_rid(body.request_id) if body.request_id else generate_rid()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    config_hash = _resolve_governance_config_hash(body.payload)

    ge_request = GoldenEdgeEvaluateRequest(
        tenant_id=body.tenant_id,
        organization_id=body.organization_id,
        action=body.action,
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        actor_id=body.actor_id,
        actor_type=body.actor_type,
        confidence=body.confidence,
        payload={**body.payload, "governance_mode": body.mode, "request_id": rid},
    )
    gel_lane: str | None = None
    if body.payload.get("use_gel_adapter") or body.payload.get("lane") == "gel":
        gel = GelAdapter()
        gel_result = gel.evaluate_sync(
            tenant_id=str(body.tenant_id),
            applicant_id=body.actor_id,
            request_id=rid,
            input_payload=dict(body.payload),
        )
        if gel_result is not None:
            gel_lane = gel_result.platform_decision

    result = await deps.engine.evaluate(ge_request)
    if gel_lane == "REJECT" and result.decision.value != "REJECT":
        result = result.model_copy(
            update={
                "decision": AgentLoopDecision.REJECT,
                "allowed": False,
                "reason": "GEL credit lane declined action",
            }
        )
    await _publish_evaluate_events(deps, body, result, rid)

    if result.decision.value == "REJECT":
        logger.warning(
            "governance_v1_anomaly decision=REJECT tenant_id=%s rid=%s action=%s",
            body.tenant_id,
            rid,
            body.action,
        )

    webhook_payload = {
        "request_id": rid,
        "correlation_id": body.correlation_id,
        "tenant_id": str(body.tenant_id),
        "decision": result.decision.value,
        "allowed": result.allowed,
        "reason_code": result.reason_code,
        "policy_refs": result.policy_refs,
        "mode": body.mode,
        "action": body.action,
        "resource_type": body.resource_type,
        "resource_id": body.resource_id,
    }
    await deps.webhooks.emit_decision_recorded(webhook_payload)

    return GovernanceEvaluateV1Response(
        request_id=rid,
        correlation_id=body.correlation_id,
        mode=body.mode,
        decision=result.decision.value,
        allowed=result.allowed,
        reason=result.reason,
        reason_code=result.reason_code,
        policy_refs=result.policy_refs,
        obligations=result.obligations,
        policy_version_hash=result.policy_version_hash,
        config_policy_version_hash=config_hash,
        ledger_event_id=result.ledger_event_id,
        gel_lane=gel_lane,
    )


@router.get("/ledger")
async def governance_ledger_v1(
    tenant_id: UUID | None = None,
    request_id: str | None = None,
    limit: int = 100,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: GovernanceV1Deps = Depends(get_governance_v1_deps),
) -> dict[str, object]:
    await check_governance_pilot_rate_limit(auth, "ledger")
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
    if auth.tenant_id is not None:
        tenant_id = auth.tenant_id
    if tenant_id is None and auth.tenant_id is not None:
        tenant_id = auth.tenant_id

    records = await deps.audit_store.list_entries(tenant_id=tenant_id, limit=limit)
    if request_id:
        try:
            rid = normalize_rid(request_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        records = [r for r in records if (r.request_id or "").upper() == (rid or "")]
    return {
        "api_version": "v1",
        "source": "audit_log",
        "immutable": True,
        "count": len(records),
        "entries": [record.model_dump(mode="json") for record in records],
    }


@router.get("/audit-export")
async def governance_audit_export_v1(
    tenant_id: UUID | None = None,
    request_id: str | None = None,
    limit: int = 500,
    format: Literal["json"] = "json",
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: GovernanceV1Deps = Depends(get_governance_v1_deps),
) -> dict[str, object]:
    await check_governance_pilot_rate_limit(auth, "audit-export")
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500")
    if auth.tenant_id is not None:
        tenant_id = auth.tenant_id

    records = await deps.audit_store.list_entries(tenant_id=tenant_id, limit=limit)
    rid: str | None = None
    if request_id:
        try:
            rid = normalize_rid(request_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        records = [r for r in records if (r.request_id or "").upper() == (rid or "")]

    settings = get_settings()
    pack = {
        "export_type": "governance_audit",
        "format": format,
        "generated_at": datetime.now().isoformat(),
        "tenant_id": str(tenant_id) if tenant_id else None,
        "request_id": rid,
        "entry_count": len(records),
        "entries": [record.model_dump(mode="json") for record in records],
        "boundary_statement": (
            "Noetfield is a pre-execution governance layer. "
            "This export contains policy evaluation metadata only — not payment instructions or custody records."
        ),
        "status_page": settings.public_status_page_url,
    }
    return pack


@router.get("/vendor-evidence")
async def governance_vendor_evidence_v1(
    auth: PilotAuthContext = Depends(require_pilot_auth),
) -> dict[str, object]:
    """E-23 / procurement starter pack (public-safe metadata; full pack via secure share)."""
    _ = auth
    return {
        "pack": "e23-vendor-evidence-starter",
        "version": "2026.05",
        "scope": "third_party_ai_governance_adjacency",
        "osfi_alignment": {
            "framework": "OSFI E-23 (model risk, third-party AI)",
            "pilot_mode": "shadow",
            "artifacts": [
                "POST /api/v1/governance/evaluate — pre-execution policy decision",
                "GET /api/v1/governance/audit-export — immutable audit slice",
                "GET /api/v1/governance/ledger — compliance log entries",
            ],
        },
        "model_inventory_template": {
            "fields": [
                "model_id",
                "provider",
                "use_case",
                "data_classification",
                "human_review_required",
                "policy_refs",
            ],
            "note": "Complete inventory maintained in pilot engagement — export feeds vendor DD.",
        },
        "b10_third_party_risk": {
            "control_themes": [
                "pre_execution_policy_gate",
                "immutable_audit_lineage",
                "separation_from_payment_execution",
            ],
        },
        "canada_data_trust": {
            "processing_region": "Canada-first (pilot contract defines residency)",
            "subprocessors": "Provided in DPA / secure vendor pack",
            "cdb_positioning": "Policy and consent governance adjacency — not open-banking write APIs",
        },
        "non_psp_statement": (
            "Noetfield does not execute payments, hold customer funds, or operate as a PSP/MSB. "
            "Partner execution layers remain outside this boundary."
        ),
        "contact": CANONICAL_INTAKE_EMAIL,
    }


@router.post("/partner-signals")
async def governance_partner_signals_v1(
    body: PartnerSignalIngestRequest,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: GovernanceV1Deps = Depends(get_governance_v1_deps),
) -> dict[str, object]:
    """Ingest read-only partner exchange/VASP signals (no order execution from Noetfield)."""
    assert_tenant_allowed(auth, body.tenant_id)
    if deps.signal_pipeline is None:
        raise HTTPException(status_code=503, detail="Signal pipeline not available")
    try:
        command = normalize_partner_signal(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    signal, trace = await deps.signal_pipeline.ingest(command)
    trace_payload: dict[str, object] | object = trace
    if hasattr(trace, "model_dump"):
        trace_payload = trace.model_dump(mode="json")
    return {
        "api_version": "v1",
        "read_only": True,
        "signal_id": str(signal.signal_id),
        "signal_type": signal.signal_type,
        "trace": trace_payload,
    }


@router.get("/scenario-presets/{preset}")
async def governance_scenario_preset_v1(
    preset: Literal["exchange", "bank", "copilot", "msb"],
    auth: PilotAuthContext = Depends(require_pilot_auth),
) -> dict[str, object]:
    """Demo JSON presets for console: exchange, bank, copilot, msb."""
    _ = auth
    try:
        return partner_evaluate_scenario_preset(preset)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
