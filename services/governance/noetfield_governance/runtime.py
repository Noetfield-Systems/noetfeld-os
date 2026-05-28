"""Governance runtime execution and human approval queue."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from noetfield_events import AsyncEventBus, EventTrace, EventType, build_event
from noetfield_governance.policies import PolicyEvaluator, PolicyInput
from noetfield_types import Actor, ActorType, GovernanceBoundary


class GovernanceExecutionState(StrEnum):
    EXECUTED = "executed"
    QUEUED_FOR_APPROVAL = "queued_for_approval"
    VETOED = "vetoed"


class GovernanceActionCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    action: str
    resource_type: str
    resource_id: str
    actor_id: str
    actor_type: ActorType = ActorType.SERVICE
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    governance_boundary: GovernanceBoundary = Field(default_factory=GovernanceBoundary)
    payload: dict[str, object] = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approval_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    organization_id: UUID
    requested_by: str
    action: str
    resource_type: str
    resource_id: str
    reason: str
    payload: dict[str, object] = Field(default_factory=dict)
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApprovalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approval_id: UUID
    decided_by: str
    approved: bool
    rationale: str
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GovernanceExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: GovernanceExecutionState
    reason: str
    trace: EventTrace
    approval_id: UUID | None = None


@dataclass
class HumanApprovalQueue:
    """In-memory approval queue for audit-safe local runtime behavior."""

    pending: dict[UUID, ApprovalRequest] = field(default_factory=dict)
    decisions: list[ApprovalDecision] = field(default_factory=list)

    async def enqueue(self, request: ApprovalRequest) -> ApprovalRequest:
        self.pending[request.approval_id] = request
        return request

    async def decide(self, decision: ApprovalDecision) -> ApprovalDecision:
        self.pending.pop(decision.approval_id, None)
        self.decisions.append(decision)
        return decision

    async def list_pending(self, tenant_id: UUID | None = None) -> list[ApprovalRequest]:
        requests = list(self.pending.values())
        if tenant_id is not None:
            requests = [request for request in requests if request.tenant_id == tenant_id]
        return requests


@dataclass
class GovernanceRuntime:
    """Policy-aware execution boundary with veto and approval support."""

    event_bus: AsyncEventBus
    approvals: HumanApprovalQueue
    policy_evaluator: PolicyEvaluator = field(default_factory=PolicyEvaluator)

    async def execute(self, command: GovernanceActionCommand) -> GovernanceExecutionResult:
        actor = Actor(
            actor_type=command.actor_type,
            actor_id=command.actor_id,
            display_name=command.actor_id,
        )
        policy = self.policy_evaluator.evaluate(
            PolicyInput(
                tenant_id=command.tenant_id,
                actor_id=command.actor_id,
                action=command.action,
                resource_type=command.resource_type,
                resource_id=command.resource_id,
                context=command.payload,
            )
        )
        await self.event_bus.publish(
            build_event(
                event_type=EventType.POLICY_EVALUATED,
                tenant_id=command.tenant_id,
                organization_id=command.organization_id,
                actor=actor,
                source_service="governance",
                entity_type=command.resource_type,
                entity_id=command.resource_id,
                payload=policy.model_dump(mode="json"),
            )
        )

        if not policy.allowed or command.action in command.governance_boundary.blocked_actions:
            trace = await self.event_bus.publish(
                build_event(
                    event_type=EventType.GOVERNANCE_VETOED,
                    tenant_id=command.tenant_id,
                    organization_id=command.organization_id,
                    actor=actor,
                    source_service="governance",
                    entity_type=command.resource_type,
                    entity_id=command.resource_id,
                    payload={
                        "action": command.action,
                        "reason": policy.reason,
                        "policy_refs": policy.policy_refs,
                    },
                )
            )
            return GovernanceExecutionResult(
                state=GovernanceExecutionState.VETOED,
                reason=policy.reason,
                trace=trace,
            )

        requires_review = (
            policy.requires_human_review
            or command.governance_boundary.requires_human_review
            or command.confidence < command.governance_boundary.minimum_confidence
        )
        if requires_review:
            approval = await self.approvals.enqueue(
                ApprovalRequest(
                    tenant_id=command.tenant_id,
                    organization_id=command.organization_id,
                    requested_by=command.actor_id,
                    action=command.action,
                    resource_type=command.resource_type,
                    resource_id=command.resource_id,
                    reason="governance boundary requires human review",
                    payload=command.payload,
                )
            )
            trace = await self.event_bus.publish(
                build_event(
                    event_type=EventType.HUMAN_APPROVAL_REQUESTED,
                    tenant_id=command.tenant_id,
                    organization_id=command.organization_id,
                    actor=actor,
                    source_service="governance",
                    entity_type="approval",
                    entity_id=str(approval.approval_id),
                    payload=approval.model_dump(mode="json"),
                )
            )
            return GovernanceExecutionResult(
                state=GovernanceExecutionState.QUEUED_FOR_APPROVAL,
                reason="human approval required",
                trace=trace,
                approval_id=approval.approval_id,
            )

        trace = await self.event_bus.publish(
            build_event(
                event_type=EventType.WORKFLOW_APPROVED,
                tenant_id=command.tenant_id,
                organization_id=command.organization_id,
                actor=actor,
                source_service="governance",
                entity_type=command.resource_type,
                entity_id=command.resource_id,
                payload={"action": command.action, "payload": command.payload},
            )
        )
        return GovernanceExecutionResult(
            state=GovernanceExecutionState.EXECUTED,
            reason="policy allowed and review not required",
            trace=trace,
        )

    async def decide_approval(
        self,
        *,
        tenant_id: UUID,
        organization_id: UUID,
        decision: ApprovalDecision,
    ) -> EventTrace:
        await self.approvals.decide(decision)
        actor = Actor(
            actor_type=ActorType.HUMAN,
            actor_id=decision.decided_by,
            display_name=decision.decided_by,
        )
        return await self.event_bus.publish(
            build_event(
                event_type=EventType.HUMAN_APPROVAL_GRANTED
                if decision.approved
                else EventType.HUMAN_APPROVAL_DENIED,
                tenant_id=tenant_id,
                organization_id=organization_id,
                actor=actor,
                source_service="governance",
                entity_type="approval",
                entity_id=str(decision.approval_id),
                payload=decision.model_dump(mode="json"),
            )
        )
