"""
noetfield — minimal governance SDK (scaffold)

Deterministic control-plane client. The contract:

    check policy  ->  execute under that decision  ->  sign a receipt

The model never makes the rules. It runs a contract you own. Policy is
evaluated deterministically from a plain dict (or your Hub), and every run
produces a tamper-evident, signed receipt.

Pure stdlib. Works fully offline against a local policy dict. Set
NOETFIELD_HUB_URL to enforce centrally instead, and NOETFIELD_SIGNING_KEY
to seal receipts with your own key.

This is a scaffold: wire `_hub_check` / `_hub_log` to your real endpoints,
and swap the HMAC seal for asymmetric signing before production.
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
    """Deterministic bytes for any JSON-able object: sorted keys, no spaces."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def _hash(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(obj)).hexdigest()


class PolicyViolation(Exception):
    """Raised when an action is denied pre-execution."""


@dataclass
class Decision:
    allowed: bool
    reason: str
    policy: str  # which rule decided


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
        self.ledger: list[Receipt] = []  # in-memory; swap for Supabase / Hub

    # --- policy ---------------------------------------------------------
    def check(self, action: str, context: dict | None = None) -> Decision:
        ctx = context or {}
        if self.hub_url:
            return self._hub_check(action, ctx)
        return self._local_check(action, ctx)

    def _local_check(self, action: str, ctx: dict) -> Decision:
        p = self.policy
        if action in p.get("deny", []):
            return Decision(False, f"action '{action}' is on the deny list", "deny")
        if action in p.get("approval", {}).get("human_required", []) and not ctx.get("approved_by"):
            return Decision(False, "human approval required, none present", "approval")
        amt = ctx.get("amount")
        cap = p.get("transfer", {}).get("max_amount")
        if amt is not None and cap is not None and amt > cap:
            return Decision(False, f"amount {amt} exceeds max_amount {cap}", "transfer.max_amount")
        cost = ctx.get("cost")
        budget = p.get("budget", {}).get("max_cost")
        if cost is not None and budget is not None and cost > budget:
            return Decision(False, f"cost {cost} exceeds max_cost {budget}", "budget.max_cost")
        return Decision(True, "no policy matched; allowed", "default-allow")

    def _hub_check(self, action: str, ctx: dict) -> Decision:
        # TODO: POST {action, ctx} to f"{self.hub_url}/check"; parse Decision.
        raise NotImplementedError("wire _hub_check to your Hub /check endpoint")

    # --- execution ------------------------------------------------------
    def execute(self, action: str, fn: Callable[[], Any], context: dict | None = None) -> tuple[Any, Receipt]:
        ctx = context or {}
        run_id = uuid.uuid4().hex[:12]
        decision = self.check(action, ctx)
        in_hash = _hash({"action": action, "context": ctx})

        if not decision.allowed:
            receipt = self._receipt(run_id, action, decision, in_hash, None)
            raise PolicyViolation(f"{decision.reason}  [{receipt.sig}]")

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

    # --- ledger ---------------------------------------------------------
    def log(self, receipt: Receipt) -> None:
        self.ledger.append(receipt)  # TODO: also POST to f"{self.hub_url}/ledger"

    def audit(self, run_id: str) -> Optional[Receipt]:
        return next((r for r in self.ledger if r.run_id == run_id), None)


if __name__ == "__main__":
    gov = Governance(policy={"transfer": {"max_amount": 10_000}})

    # allowed
    out, ok = gov.execute("transfer", lambda: {"status": "sent"}, {"amount": 4_000})
    print("ALLOWED ", ok.run_id, ok.decision.reason, ok.sig[:24], "...")
    print("verify  ", ok.verify(gov._key))

    # blocked pre-execution (the banner's $48k case, as real logic)
    try:
        gov.execute("transfer", lambda: {"status": "sent"}, {"amount": 48_000})
    except PolicyViolation as e:
        print("BLOCKED ", e)
