"""Golden Edge v3 — pre-execution evaluate pipeline and agent loop.

Evaluates policy before any governed action proceeds. REJECT (VETO) blocks execution
and emits audit events via the governance runtime.
"""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from noetfield_governance.ledger_digest import policy_version_hash
from noetfield_governance.policies import PolicyEvaluator, PolicyInput
from noetfield_governance.policy_pack import PolicyDecisionCode
from noetfield_governance.control_plane import ControlPlaneState
from noetfield_governance.runtime import (
    GovernanceActionCommand,
    GovernanceExecutionResult,
    GovernanceExecutionState,
    GovernanceRuntime,
)
from noetfield_types import ActorType


class AgentLoopDecision(StrEnum):
    REJECT = "REJECT"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    PROCEED = "PROCEED"


class GoldenEdgeEvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    organization_id: UUID
    action: str
    resource_type: str
    resource_id: str
    actor_id: str = "golden-edge-v3"
    actor_type: ActorType = ActorType.SERVICE
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    payload: dict[str, object] = Field(default_factory=dict)


class GoldenEdgeEvaluateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: AgentLoopDecision
    allowed: bool
    reason: str
    reason_code: str
    execution_state: str | None = None
    policy_refs: list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)
    policy_version_hash: str | None = None
    control_plane_state: str = ControlPlaneState.GOVERNANCE_CHECKED.value
    ledger_event_id: str | None = None


class GoldenEdgeV3Engine:
    """Async evaluate + agent loop over GovernanceRuntime."""

    def __init__(
        self,
        *,
        governance_runtime: GovernanceRuntime,
        policy_evaluator: PolicyEvaluator | None = None,
    ) -> None:
        self.governance_runtime = governance_runtime
        self.policy_evaluator = policy_evaluator or PolicyEvaluator()

    def _enrich(self, evaluation: object, response: GoldenEdgeEvaluateResponse) -> GoldenEdgeEvaluateResponse:
        refs = getattr(evaluation, "policy_refs", response.policy_refs)
        return response.model_copy(
            update={
                "policy_version_hash": policy_version_hash(list(refs)),
                "control_plane_state": ControlPlaneState.GOVERNANCE_CHECKED.value,
            }
        )

    async def evaluate(self, request: GoldenEdgeEvaluateRequest) -> GoldenEdgeEvaluateResponse:
        """Policy-only evaluate (no side effects)."""
        pack = self.policy_evaluator.policy_pack
        evaluation = self.policy_evaluator.evaluate(
            PolicyInput(
                tenant_id=request.tenant_id,
                actor_id=request.actor_id,
                action=request.action,
                resource_type=request.resource_type,
                resource_id=request.resource_id,
                context={
                    **request.payload,
                    "actor_type": request.actor_type.value,
                    "confidence": request.confidence,
                    "blocked_actions": list(pack.forbidden_financial_actions),
                },
            )
        )
        if not evaluation.allowed:
            return self._enrich(
                evaluation,
                GoldenEdgeEvaluateResponse(
                    decision=AgentLoopDecision.REJECT,
                    allowed=False,
                    reason=evaluation.reason,
                    reason_code=evaluation.reason_code.value,
                    policy_refs=evaluation.policy_refs,
                    obligations=evaluation.obligations,
                ),
            )
        if evaluation.requires_human_review:
            return self._enrich(
                evaluation,
                GoldenEdgeEvaluateResponse(
                    decision=AgentLoopDecision.REQUIRE_HUMAN_REVIEW,
                    allowed=True,
                    reason=evaluation.reason,
                    reason_code=evaluation.reason_code.value,
                    policy_refs=evaluation.policy_refs,
                    obligations=evaluation.obligations,
                ),
            )
        return self._enrich(
            evaluation,
            GoldenEdgeEvaluateResponse(
                decision=AgentLoopDecision.PROCEED,
                allowed=True,
                reason=evaluation.reason,
                reason_code=evaluation.reason_code.value,
                policy_refs=evaluation.policy_refs,
                obligations=evaluation.obligations,
            ),
        )

    async def agent_loop(self, request: GoldenEdgeEvaluateRequest) -> GoldenEdgeEvaluateResponse:
        """Evaluate first; REJECT stops before governance execute."""
        preview = await self.evaluate(request)
        if preview.decision == AgentLoopDecision.REJECT:
            return preview

        command = GovernanceActionCommand(
            tenant_id=request.tenant_id,
            organization_id=request.organization_id,
            action=request.action,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            actor_id=request.actor_id,
            actor_type=request.actor_type,
            confidence=request.confidence,
            payload=request.payload,
        )
        result: GovernanceExecutionResult = await self.governance_runtime.execute(command)
        if result.state == GovernanceExecutionState.VETOED:
            return GoldenEdgeEvaluateResponse(
                decision=AgentLoopDecision.REJECT,
                allowed=False,
                reason=result.reason,
                reason_code=PolicyDecisionCode.VETO_BLOCKED_ACTION.value,
                execution_state=result.state.value,
                policy_version_hash=preview.policy_version_hash,
                control_plane_state=result.control_plane_state.value,
                ledger_event_id=str(result.trace.event_id),
            )
        if result.state == GovernanceExecutionState.QUEUED_FOR_APPROVAL:
            return GoldenEdgeEvaluateResponse(
                decision=AgentLoopDecision.REQUIRE_HUMAN_REVIEW,
                allowed=True,
                reason=result.reason,
                reason_code=PolicyDecisionCode.REQUIRE_HUMAN_REVIEW.value,
                execution_state=result.state.value,
                policy_version_hash=preview.policy_version_hash,
                control_plane_state=result.control_plane_state.value,
                ledger_event_id=str(result.trace.event_id),
            )
        return GoldenEdgeEvaluateResponse(
            decision=AgentLoopDecision.PROCEED,
            allowed=True,
            reason=result.reason,
            reason_code=PolicyDecisionCode.ALLOW.value,
            execution_state=result.state.value,
            policy_refs=preview.policy_refs,
            obligations=preview.obligations,
            policy_version_hash=preview.policy_version_hash,
            control_plane_state=result.control_plane_state.value,
            ledger_event_id=str(result.trace.event_id),
        )
