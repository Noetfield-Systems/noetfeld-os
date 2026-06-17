"""Canonical, versioned event contracts for governed intelligence execution."""

from enum import StrEnum
from typing import Any
from uuid import UUID

from noetfield_types import Actor, GovernanceEvent


class EventType(StrEnum):
    SIGNAL_INGESTED = "SIGNAL_INGESTED"
    ENTITY_CREATED = "ENTITY_CREATED"
    ENTITY_UPDATED = "ENTITY_UPDATED"
    RELATIONSHIP_INFERRED = "RELATIONSHIP_INFERRED"
    RELATIONSHIP_CONFIDENCE_CHANGED = "RELATIONSHIP_CONFIDENCE_CHANGED"
    GRAPH_UPDATED = "GRAPH_UPDATED"
    GRAPH_REFLECTION_COMPLETED = "GRAPH_REFLECTION_COMPLETED"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    GOVERNANCE_VETOED = "GOVERNANCE_VETOED"
    HUMAN_APPROVAL_REQUESTED = "HUMAN_APPROVAL_REQUESTED"
    HUMAN_APPROVAL_GRANTED = "HUMAN_APPROVAL_GRANTED"
    HUMAN_APPROVAL_DENIED = "HUMAN_APPROVAL_DENIED"
    HUMAN_OVERRIDE_TRIGGERED = "HUMAN_OVERRIDE_TRIGGERED"
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_APPROVED = "WORKFLOW_APPROVED"
    WORKFLOW_REJECTED = "WORKFLOW_REJECTED"
    INSPECTOR_STARTED = "INSPECTOR_STARTED"
    INSPECTOR_COLLABORATION_STARTED = "INSPECTOR_COLLABORATION_STARTED"
    INSPECTOR_COMPLETED = "INSPECTOR_COMPLETED"
    AI_OUTPUT_GENERATED = "AI_OUTPUT_GENERATED"
    AI_OUTPUT_REVIEWED = "AI_OUTPUT_REVIEWED"
    EVIDENCE_ATTACHED = "EVIDENCE_ATTACHED"
    MEMORY_REFLECTION_RECORDED = "MEMORY_REFLECTION_RECORDED"
    DEAD_LETTER_RECORDED = "DEAD_LETTER_RECORDED"
    FACTORY_RUN_STARTED = "FACTORY_RUN_STARTED"
    FACTORY_NODE_COMPLETED = "FACTORY_NODE_COMPLETED"


def event_catalog() -> dict[str, dict[str, str]]:
    """Return the initial event catalog used by services and schema checks."""

    return {
        EventType.SIGNAL_INGESTED: {
            "description": "A raw signal was captured in immutable ingestion memory.",
            "layer": "raw_signal",
        },
        EventType.ENTITY_CREATED: {
            "description": "A normalized entity was created from extracted intelligence.",
            "layer": "normalized_intelligence",
        },
        EventType.RELATIONSHIP_INFERRED: {
            "description": "The graph engine inferred a relationship with evidence.",
            "layer": "living_knowledge_graph",
        },
        EventType.RELATIONSHIP_CONFIDENCE_CHANGED: {
            "description": "A relationship confidence score evolved from new evidence.",
            "layer": "living_knowledge_graph",
        },
        EventType.GRAPH_REFLECTION_COMPLETED: {
            "description": "A temporal graph reflection cycle completed.",
            "layer": "living_knowledge_graph",
        },
        EventType.POLICY_EVALUATED: {
            "description": "OPA or an internal policy evaluator produced a decision.",
            "layer": "governance_ledger",
        },
        EventType.GOVERNANCE_VETOED: {
            "description": "A governance boundary vetoed execution.",
            "layer": "governance_ledger",
        },
        EventType.HUMAN_APPROVAL_REQUESTED: {
            "description": "A consequential action entered the human approval queue.",
            "layer": "governance_ledger",
        },
        EventType.HUMAN_OVERRIDE_TRIGGERED: {
            "description": "A human overrode or paused automated intelligence execution.",
            "layer": "governance_ledger",
        },
        EventType.WORKFLOW_APPROVED: {
            "description": "A governed workflow reached an approval decision.",
            "layer": "governance_ledger",
        },
        EventType.GRAPH_UPDATED: {
            "description": "The living knowledge graph projection changed.",
            "layer": "living_knowledge_graph",
        },
        EventType.INSPECTOR_COLLABORATION_STARTED: {
            "description": "Multiple bounded inspectors began a collaborative run.",
            "layer": "operational_runtime",
        },
        EventType.INSPECTOR_COMPLETED: {
            "description": "A bounded ambient inspector completed a governed run.",
            "layer": "operational_runtime",
        },
        EventType.DEAD_LETTER_RECORDED: {
            "description": "A subscriber failure was captured for audit-safe recovery.",
            "layer": "operational_runtime",
        },
        EventType.FACTORY_RUN_STARTED: {
            "description": "A governed AI factory pipeline run started.",
            "layer": "operational_runtime",
        },
        EventType.FACTORY_NODE_COMPLETED: {
            "description": "A governed AI factory pipeline node completed.",
            "layer": "operational_runtime",
        },
    }


def build_event(
    *,
    event_type: EventType,
    tenant_id: UUID,
    organization_id: UUID,
    actor: Actor,
    source_service: str,
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any] | None = None,
    correlation_id: UUID | None = None,
    source_request_id: str | None = None,
) -> GovernanceEvent:
    """Build a canonical event envelope before persistence in Trust Ledger."""

    from noetfield_events.context import get_correlation_id, get_request_id

    resolved_correlation = correlation_id or get_correlation_id() or None
    resolved_request_id = source_request_id if source_request_id is not None else get_request_id()

    event_kwargs: dict[str, Any] = {}
    if resolved_correlation is not None:
        event_kwargs["correlation_id"] = resolved_correlation
    if resolved_request_id is not None:
        event_kwargs["source_request_id"] = resolved_request_id

    return GovernanceEvent(
        event_type=event_type.value,
        tenant_id=tenant_id,
        organization_id=organization_id,
        actor=actor,
        source_service=source_service,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload or {},
        **event_kwargs,
    )
