"""
Noetfield local governance scaffold — aligned to shipped policy pack vocabulary.

Use for offline demos only. Production path: platform.noetfield.com
  POST /api/v1/governance/evaluate

This example uses Copilot governance rules (human review on publish actions),
NOT payment transfer limits (out of scope for Noetfield).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Optional


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def _hash(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(obj)).hexdigest()


class PolicyViolation(Exception):
    """Raised when an action is denied pre-execution."""


@dataclass
class Decision:
    allowed: bool
    requires_human_review: bool
    reason: str
    reason_code: str


@dataclass
class Receipt:
    run_id: str
    action: str
    decision: Decision
    input_hash: str
    output_hash: Optional[str]
    ts: str
    sig: str = ""

    def verify(self, key: bytes) -> bool:
        body = {k: v for k, v in asdict(self).items() if k != "sig"}
        return hmac.compare_digest(self.sig, _seal(body, key))


def _seal(payload: dict, key: bytes) -> str:
    return "hmac:" + hmac.new(key, _canonical(payload), hashlib.sha256).hexdigest()


# Copilot governance-v1 high-impact actions (from packages/policy-packs/copilot-governance-v1.json)
COPILOT_HIGH_IMPACT = frozenset({
    "approve_workflow",
    "execute_inspector_action",
    "publish_report",
    "publish_board_report",
    "export_audit_package",
    "run_copilot_governance_demo",
})


class Governance:
    def __init__(
        self,
        policy: Optional[dict] = None,
        hub_url: Optional[str] = None,
        signing_key: Optional[str] = None,
    ):
        self.policy = policy or {}
        self.hub_url = hub_url or os.getenv("NOETFIELD_HUB_URL")
        self._key = (signing_key or os.getenv("NOETFIELD_SIGNING_KEY") or "dev-unsafe-key").encode()
        self.ledger: list[Receipt] = []

    def check(self, action: str, context: dict | None = None) -> Decision:
        ctx = context or {}
        if self.hub_url:
            raise NotImplementedError("wire to POST /api/v1/governance/evaluate on platform.noetfield.com")
        return self._local_check(action, ctx)

    def _local_check(self, action: str, ctx: dict) -> Decision:
        if action in self.policy.get("deny", []):
            return Decision(False, False, f"action '{action}' denied", "VETO_BLOCKED_ACTION")
        confidence = float(ctx.get("confidence", 1.0))
        min_conf = float(self.policy.get("minimum_confidence", 0.75))
        if confidence < min_conf:
            return Decision(True, True, "confidence below threshold", "VETO_LOW_CONFIDENCE")
        if action in COPILOT_HIGH_IMPACT and not ctx.get("approved_by"):
            return Decision(True, True, "Copilot high-impact action requires human review", "REQUIRE_HUMAN_REVIEW")
        if action in self.policy.get("blocked_autonomous", []) and not ctx.get("approved_by"):
            return Decision(False, False, "autonomous publication blocked", "VETO_AUTONOMOUS_PUBLICATION")
        return Decision(True, False, "policy allowed", "ALLOW")

    def execute(self, action: str, fn: Callable[[], Any], context: dict | None = None) -> tuple[Any, Receipt]:
        ctx = context or {}
        run_id = uuid.uuid4().hex[:12]
        decision = self.check(action, ctx)
        in_hash = _hash({"action": action, "context": ctx})

        if not decision.allowed:
            receipt = self._receipt(run_id, action, decision, in_hash, None)
            raise PolicyViolation(f"{decision.reason} [{receipt.sig[:20]}…]")

        if decision.requires_human_review:
            receipt = self._receipt(run_id, action, decision, in_hash, None)
            raise PolicyViolation(f"human review required [{receipt.sig[:20]}…]")

        result = fn()
        receipt = self._receipt(run_id, action, decision, in_hash, _hash(result))
        return result, receipt

    def _receipt(self, run_id, action, decision, in_hash, out_hash) -> Receipt:
        r = Receipt(
            run_id=run_id,
            action=action,
            decision=decision,
            input_hash=in_hash,
            output_hash=out_hash,
            ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        body = {k: v for k, v in asdict(r).items() if k != "sig"}
        r.sig = _seal(body, self._key)
        self.log(r)
        return r

    def log(self, receipt: Receipt) -> None:
        self.ledger.append(receipt)

    def audit(self, run_id: str) -> Optional[Receipt]:
        return next((r for r in self.ledger if r.run_id == run_id), None)


if __name__ == "__main__":
    gov = Governance(policy={"minimum_confidence": 0.75})

    # Allowed low-impact path
    out, ok = gov.execute("evaluate_copilot_signal", lambda: {"status": "ok"}, {"confidence": 0.82})
    print("ALLOWED", ok.run_id, ok.decision.reason_code)

    # Copilot governance: publish requires human review (real product behavior)
    try:
        gov.execute("publish_board_report", lambda: {"pdf": "board.pdf"}, {"confidence": 0.91})
    except PolicyViolation as e:
        print("REVIEW QUEUED", e)
