"""Read-only partner exchange / VASP signal normalization (no order execution)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from noetfield_signals import IngestSignalCommand

# Payload keys that imply write/trade execution — rejected at ingest boundary.
_FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "place_order",
        "submit_order",
        "withdraw",
        "transfer",
        "mint",
        "redeem",
        "payment_intent",
        "settlement_instruction",
    }
)


class PartnerSignalIngestRequest(BaseModel):
    """Read-only operational signal from a licensed partner (exchange/VASP/PSP)."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    partner_id: str = Field(..., min_length=1, max_length=120)
    signal_kind: str = Field(
        ...,
        description="e.g. balance_snapshot, order_status, risk_flag, market_data",
        max_length=64,
    )
    request_id: str | None = Field(default=None, max_length=64)
    payload: dict[str, object] = Field(default_factory=dict)
    actor_id: str = "partner-signal-ingest"


def validate_read_only_payload(payload: dict[str, object]) -> None:
    """Reject payloads that look like execution instructions."""
    lowered = {str(k).lower() for k in payload}
    blocked = lowered & _FORBIDDEN_PAYLOAD_KEYS
    if blocked:
        raise ValueError(f"partner signal payload contains forbidden execution keys: {sorted(blocked)}")


def normalize_partner_signal(request: PartnerSignalIngestRequest) -> IngestSignalCommand:
    """Map partner webhook body to signal ingestion (read-only provenance)."""
    validate_read_only_payload(request.payload)
    rid = (request.request_id or "").strip().upper() or None
    return IngestSignalCommand(
        tenant_id=request.tenant_id,
        organization_id=request.organization_id,
        signal_type="partner_exchange_signal",
        payload={
            **request.payload,
            "signal_kind": request.signal_kind,
            "partner_id": request.partner_id,
            "request_id": rid,
            "read_only": True,
        },
        provenance={
            "ingestion": "partner_signal",
            "partner_id": request.partner_id,
            "signal_kind": request.signal_kind,
            "boundary": "no_execution_from_noetfield",
        },
        actor_id=request.actor_id,
    )


def partner_evaluate_scenario_preset(preset: str) -> dict[str, Any]:
    """Console / demo JSON presets for partner pilots (shadow only)."""
    base = {
        "tenant_id": "00000000-0000-4000-8000-000000000001",
        "organization_id": "00000000-0000-4000-8000-000000000002",
        "actor_id": "partner-pilot",
        "confidence": 0.95,
        "mode": "shadow",
    }
    presets: dict[str, dict[str, Any]] = {
        "exchange": {
            **base,
            "action": "place_order_intent",
            "resource_type": "partner_exchange",
            "resource_id": "staging-order-intent-1",
            "payload": {"partner_program": "exchange", "read_only_signal": True},
        },
        "bank": {
            **base,
            "action": "publish_board_report",
            "resource_type": "governance_artifact",
            "resource_id": "bank-pilot-1",
            "payload": {"partner_program": "bank"},
        },
        "copilot": {
            **base,
            "action": "copilot_content_generation",
            "resource_type": "m365_copilot",
            "resource_id": "copilot-session-1",
            "payload": {"partner_program": "copilot"},
        },
        "msb": {
            **base,
            "action": "initiate_transfer_intent",
            "resource_type": "msb_payment",
            "resource_id": "staging-transfer-001",
            "payload": {"partner_program": "msb", "currency": "CAD", "read_only_signal": True},
        },
    }
    if preset not in presets:
        raise ValueError(f"unknown preset: {preset}")
    return presets[preset]
