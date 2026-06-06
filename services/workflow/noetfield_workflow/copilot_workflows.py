"""Copilot QuickScan / Readiness workflow helpers (workflow lite)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from noetfield_types import WorkflowState
from noetfield_workflow.state_machine import (
    WorkflowInstance,
    WorkflowStateMachine,
    WorkflowTransitionCommand,
)

_SPEC_ROOT = Path(__file__).resolve().parents[3] / "docs" / "spec" / "workflows"

COPILOT_QUICKSCAN = "copilot_quickscan"
COPILOT_READINESS = "copilot_readiness"


@dataclass(frozen=True)
class CopilotWorkflowSpec:
    workflow_type: str
    sla_hours: int
    raw: dict[str, Any]


def load_workflow_spec(name: str) -> CopilotWorkflowSpec:
    path = _SPEC_ROOT / name
    data = json.loads(path.read_text(encoding="utf-8"))
    return CopilotWorkflowSpec(
        workflow_type=data["workflow_type"],
        sla_hours=int(data.get("sla_hours", 48)),
        raw=data,
    )


async def start_copilot_quickscan(
    *,
    machine: WorkflowStateMachine,
    tenant_id: UUID,
    organization_id: UUID,
    actor_id: str,
    rid: str,
    signal_payload: dict[str, object],
) -> WorkflowInstance:
    spec = load_workflow_spec("CopilotQuickScan.workflow.json")
    workflow = WorkflowInstance(
        tenant_id=tenant_id,
        organization_id=organization_id,
        workflow_type=spec.workflow_type,
        target_entity_type="governance_rid",
        target_entity_id=rid,
        payload={
            "sla_hours": spec.sla_hours,
            "signal": signal_payload,
            "dsl_version": spec.raw.get("version"),
        },
        created_by=actor_id,
    )
    started = await machine.start(workflow)
    return await machine.transition(
        WorkflowTransitionCommand(
            workflow_id=started.workflow_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            actor_id=actor_id,
            next_state=WorkflowState.PENDING_REVIEW,
            reason="Copilot QuickScan evaluate submitted — awaiting compliance review.",
            payload={"rid": rid, "submitted_at": datetime.now(timezone.utc).isoformat()},
        )
    )


async def mock_signoff_to_approved(
    *,
    machine: WorkflowStateMachine,
    tenant_id: UUID,
    organization_id: UUID,
    workflow_id: UUID,
    actor_id: str = "compliance-owner-mock",
) -> WorkflowInstance:
    """Human signoff mock for E2E scripts — transitions pending_review → approved."""
    pending = await machine.store.get(tenant_id, workflow_id)
    if pending is None:
        raise ValueError("workflow not found")
    approved = await machine.transition(
        WorkflowTransitionCommand(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            actor_id=actor_id,
            next_state=WorkflowState.APPROVED,
            reason="Mock human signoff (pilot E2E).",
        )
    )
    return await machine.transition(
        WorkflowTransitionCommand(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            actor_id=actor_id,
            next_state=WorkflowState.COMPLETED,
            reason="Audit ledger write acknowledged (mock).",
            payload={"ledger": "audit_events", "signed_at": datetime.now(timezone.utc).isoformat()},
        )
    )
