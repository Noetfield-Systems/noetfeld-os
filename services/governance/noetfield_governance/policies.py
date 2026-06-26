"""Policy evaluation contracts for workflow-first governance."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .policy_loader import load_default_policy_pack
from .policy_pack import (
    GovernancePolicyPack,
    PolicyDecisionCode,
    context_float,
    context_int,
)


class PolicyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    context: dict[str, object] = Field(default_factory=dict)


class PolicyEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    requires_human_review: bool
    reason: str
    reason_code: PolicyDecisionCode
    policy_refs: list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)


class PolicyEvaluator:
    """Deterministic governance policy evaluator.

    This class is OPA-ready but does not require OPA to enforce baseline
    runtime rules. Every decision includes a reason code, policy refs, and
    obligations so it can be audited and replayed.
    """

    def __init__(self, policy_pack: GovernancePolicyPack | None = None) -> None:
        self.policy_pack = policy_pack or load_default_policy_pack()

    def evaluate(self, policy_input: PolicyInput) -> PolicyEvaluation:
        context = policy_input.context
        actor_type = str(context.get("actor_type", "service"))
        confidence = context_float(context, "confidence", 1.0)
        blocked_actions = set(context.get("blocked_actions", []) or [])
        inspector_count = context_int(context, "inspector_count", 0)
        module = str(context.get("module", ""))

        if policy_input.action in self.policy_pack.forbidden_financial_actions:
            return self._decision(
                allowed=False,
                requires_human_review=False,
                reason="Financial execution actions are forbidden for Noetfield runtime (GCIP alignment).",
                reason_code=PolicyDecisionCode.VETO_BLOCKED_ACTION,
            )

        if policy_input.action in blocked_actions:
            return self._decision(
                allowed=False,
                requires_human_review=False,
                reason="Action is explicitly blocked by the governance boundary.",
                reason_code=PolicyDecisionCode.VETO_BLOCKED_ACTION,
            )

        if (
            actor_type in {"ai", "service", "inspector"}
            and policy_input.action in self.policy_pack.blocked_autonomous_actions
        ):
            return self._decision(
                allowed=False,
                requires_human_review=False,
                reason="Autonomous actors cannot silently publish, export, or approve governed artifacts.",
                reason_code=PolicyDecisionCode.VETO_AUTONOMOUS_PUBLICATION,
            )

        if inspector_count > self.policy_pack.inspector_execution_limit:
            return self._decision(
                allowed=False,
                requires_human_review=False,
                reason="Inspector execution exceeds bounded collaboration limit.",
                reason_code=PolicyDecisionCode.VETO_INSPECTOR_LIMIT,
            )

        if confidence < self.policy_pack.minimum_confidence:
            return self._decision(
                allowed=True,
                requires_human_review=True,
                reason="Confidence is below the governance threshold and requires human review.",
                reason_code=PolicyDecisionCode.VETO_LOW_CONFIDENCE,
            )

        requires_review = policy_input.action in self.policy_pack.high_impact_actions
        if module == "copilot_governance":
            requires_review = True

        if requires_review:
            return self._decision(
                allowed=True,
                requires_human_review=True,
                reason="High-impact governance action requires human review.",
                reason_code=PolicyDecisionCode.REQUIRE_HUMAN_REVIEW,
            )

        return self._decision(
            allowed=True,
            requires_human_review=False,
            reason="Policy allowed action without additional review.",
            reason_code=PolicyDecisionCode.ALLOW,
        )

    def _decision(
        self,
        *,
        allowed: bool,
        requires_human_review: bool,
        reason: str,
        reason_code: PolicyDecisionCode,
    ) -> PolicyEvaluation:
        return PolicyEvaluation(
            allowed=allowed,
            requires_human_review=requires_human_review,
            reason=reason,
            reason_code=reason_code,
            policy_refs=self.policy_pack.policy_refs(),
            obligations=self.policy_pack.obligations_for(requires_human_review=requires_human_review),
        )
