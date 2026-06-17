"""Factory pipeline node helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from noetfield_copilot_governance import CopilotGovernanceCommand, CopilotPipelineState
from noetfield_events import EventReplayCursor
from noetfield_governance.golden_edge_v3 import AgentLoopDecision
from noetfield_types import Actor, ActorType, WorkflowState

from .exceptions import FactoryValidationError


def intake_validate(command: CopilotGovernanceCommand) -> CopilotGovernanceCommand:
    """n01 — validate required factory input fields."""
    if not command.submitted_by.strip():
        raise FactoryValidationError("submitted_by is required")
    payload = dict(command.signal_payload)
    if not isinstance(payload, dict):
        raise FactoryValidationError("signal_payload must be an object")
    source = payload.get("source")
    summary = payload.get("summary")
    if not source or not summary:
        if payload.get("signal_type"):
            payload["source"] = "m365_copilot"
            payload["summary"] = str(
                payload.get("requested_outcome") or payload.get("signal_type")
            )
            return command.model_copy(update={"signal_payload": payload})
        raise FactoryValidationError(
            "signal_payload requires source and summary",
            details={"signal_payload": payload},
        )
    allowed_sources = {"m365_copilot", "manual", "webhook"}
    if str(source) not in allowed_sources:
        raise FactoryValidationError(
            f"signal_payload.source must be one of {sorted(allowed_sources)}"
        )
    return command


async def package_copilot_deliverable(
    *,
    factory_id: str,
    state: CopilotPipelineState,
    event_bus: Any,
    audit_store: Any,
    graph_store: Any,
    governance_runtime: Any,
) -> dict[str, Any]:
    """n08 — assemble board_brief and audit_package from pipeline state."""
    command = state.command
    tenant_id = command.tenant_id
    organization_id = command.organization_id

    replayed_events = await event_bus.replay(
        EventReplayCursor(after_sequence=0, event_types=frozenset({"*"}))
    )
    correlation_events = [
        event
        for event in replayed_events
        if event.correlation_id == state.run_id
        or (
            state.signal is not None
            and event.entity_id == str(state.signal.signal_id)
        )
    ]
    events = correlation_events if correlation_events else replayed_events
    event_types = [event.event_type for event in events]

    pending_approvals = []
    if governance_runtime is not None:
        pending_approvals = await governance_runtime.approvals.list_pending(tenant_id)

    relationships = await graph_store.relationships_for_tenant(tenant_id)

    workflow_state = (
        state.workflow_state.value
        if state.workflow_state is not None
        else WorkflowState.PENDING_REVIEW.value
    )
    approval_required = state.approval_id is not None or workflow_state == "pending_review"

    board_brief: dict[str, Any] = {
        "title": "Copilot Governance Readiness Brief",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "positioning": "AI Trust Infrastructure for regulated enterprises",
        "executive_summary": (
            "The governed signal was ingested, linked into the governance graph, "
            "evaluated by policy and inspectors, moved into workflow review, and "
            "preserved in a replayable audit trail."
        ),
        "risk_findings": [
            "Copilot usage creates oversharing and evidence-readiness exposure.",
            "Governance policy requires human review before publication or board use.",
            "Audit replay is available for signal, graph, workflow, and approval events.",
        ],
        "governance_state": {
            "workflow_state": workflow_state,
            "approval_required": approval_required,
            "approval_id": str(state.approval_id) if state.approval_id else None,
            "policy_enforced": "POLICY_EVALUATED" in event_types,
        },
        "graph_state": {
            "relationship_count": len(relationships),
            "relationship_id": str(state.relationship_id) if state.relationship_id else None,
            "reflection_id": str(state.reflection_id) if state.reflection_id else None,
        },
        "inspector_state": {
            "run_id": str(state.inspector_run.run_id) if state.inspector_run else None,
            "status": state.inspector_run.status if state.inspector_run else None,
            "finding_count": len(state.inspector_run.findings) if state.inspector_run else 0,
            "requires_human_review": (
                state.inspector_run.requires_human_review if state.inspector_run else True
            ),
        },
    }

    audit_records = getattr(audit_store, "records", [])
    audit_package: dict[str, Any] = {
        "tenant_id": str(tenant_id),
        "organization_id": str(organization_id),
        "signal_id": str(state.signal.signal_id) if state.signal else None,
        "workflow_id": str(state.workflow_id) if state.workflow_id else None,
        "event_count": len(events),
        "audit_record_count": len(audit_records),
        "event_types": event_types,
        "pending_approval_count": len(pending_approvals),
        "events": [event.model_dump(mode="json") for event in events],
    }

    if state.policy_decision and state.policy_decision.decision == AgentLoopDecision.REJECT:
        factory_status = "vetoed"
    elif approval_required:
        factory_status = "pending_approval"
    else:
        factory_status = "completed"

    return {
        "factory_id": factory_id,
        "factory_status": factory_status,
        "board_brief": board_brief,
        "audit_package": audit_package,
        "replay_hint": f"/events/replay?correlation_id={state.run_id}",
    }


def factory_actor(submitted_by: str) -> Actor:
    return Actor(actor_type=ActorType.SERVICE, actor_id=submitted_by, display_name=submitted_by)
