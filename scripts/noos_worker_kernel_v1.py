#!/usr/bin/env python3
"""NOOS Cheap Worker Kernel v1 — headless governed task router (not IDE/UI).

Routes tasks to T0 deterministic tools or T1–T3 model tiers under config/model-router.yml.
AI proposes patches only inside sandbox; deterministic checks decide pass/fail.
Every run writes a receipt. T3 requires founder approval. No secrets to model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_model_router_v1 import (  # noqa: E402
    enforce_budget,
    estimate_cost,
    load_router_config,
    redact_secrets,
    route_task,
)
from noos_patch_sandbox_v1 import (  # noqa: E402
    validate_patch_proposal,
    write_sandbox_patch,
)
from noos_receipt_writer_v1 import write_receipt  # noqa: E402

try:
    from noos_tool_broker_v1 import invoke as broker_invoke  # noqa: E402
except ImportError:
    broker_invoke = None  # type: ignore


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def op_key(*, task_kind: str, payload_hash: str) -> str:
    return hashlib.sha256(f"{task_kind}:{payload_hash}".encode()).hexdigest()[:24]


def _payload_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def execute_t0(task_kind: str, payload: dict[str, Any], *, agent_id: str = "noos-worker-kernel") -> dict[str, Any]:
    """T0 tools execute only via tool broker (M1)."""
    tool_map = {"grep": "grep", "check": "check", "validate": "pytest_q", "lint": "pytest_q"}
    tool = tool_map.get(task_kind, task_kind)
    if broker_invoke is None:
        return {"ok": False, "error": "tool_broker_unavailable"}
    broker_params = dict(payload)
    if task_kind in ("validate", "lint") and "paths" not in broker_params:
        broker_params["paths"] = broker_params.get("paths") or ["tests/"]
    row = broker_invoke(agent_id=agent_id, tool=tool, params=broker_params, dry_run=False)
    return {
        "ok": row.get("ok"),
        "broker": True,
        "tool": tool,
        "result": row.get("result"),
        "receipt_path": row.get("receipt_path"),
        "cost": row.get("cost"),
    }


def execute_t1(task_kind: str, payload: dict[str, Any], *, routing: dict[str, Any]) -> dict[str, Any]:
    """Stub proposal — real OpenRouter/DeepSeek calls are founder-gated network; kernel records intent."""
    text = str(payload.get("text") or payload.get("content") or "")
    redacted, redactions = redact_secrets(text)
    return {
        "mode": "llm_proposal_stub",
        "task_kind": task_kind,
        "tier": routing.get("tier"),
        "model_id": routing.get("model_id"),
        "provider": routing.get("provider"),
        "redactions": redactions,
        "proposal": {
            "summary": f"[T1 stub] classify/summarize len={len(redacted)}",
            "labels": payload.get("labels") or ["unclassified"],
        },
        "ok": True,
        "note": "Network LLM call not executed in kernel v1 — receipt records routing intent only",
    }


def execute_t2(payload: dict[str, Any], *, routing: dict[str, Any], op_key_val: str) -> dict[str, Any]:
    proposal = payload.get("patch") if isinstance(payload.get("patch"), dict) else payload
    verdict = validate_patch_proposal(proposal)
    sandbox = write_sandbox_patch(proposal, op_key=op_key_val)
    return {
        "mode": "bounded_patch_proposal",
        "tier": routing.get("tier"),
        "verdict": verdict,
        "sandbox": sandbox,
        "ok": verdict.get("verdict") == "PASS",
    }


def execute_t3(payload: dict[str, Any], *, routing: dict[str, Any]) -> dict[str, Any]:
    if routing.get("blocked"):
        return {"ok": False, "blocker_reason": routing.get("blocker_reason")}
    redacted, redactions = redact_secrets(json.dumps(payload))
    cost = estimate_cost(tier="T3", tokens_in=len(redacted) // 4, tokens_out=500)
    budget = enforce_budget(cost)
    if not budget.get("ok"):
        return {"ok": False, "blocker_reason": budget.get("blocker_reason")}
    return {
        "mode": "premium_exception_stub",
        "tier": "T3",
        "founder_approved": True,
        "cost_estimate": cost,
        "redactions": redactions,
        "proposal": {"analysis": "[T3 stub] premium analysis placeholder"},
        "ok": True,
    }


def run_task(
    *,
    task_kind: str,
    payload: dict[str, Any] | None = None,
    founder_approval_token: str | None = None,
    dry_run: bool = False,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = config or load_router_config()
    body = payload if isinstance(payload, dict) else {}
    safe_payload = json.loads(redact_secrets(json.dumps(body))[0])
    ph = _payload_hash(safe_payload)
    ok = op_key(task_kind=task_kind, payload_hash=ph)

    routing = route_task(
        task_kind=task_kind,
        founder_approval_token=founder_approval_token,
        config=cfg,
    )

    started_at = utc_now()
    result: dict[str, Any]
    cost_row = estimate_cost(tier=str(routing.get("tier") or "T0"))

    if routing.get("blocked"):
        result = {"ok": False, "blocker_reason": routing.get("blocker_reason"), "routing": routing}
    elif routing.get("tier") == "T0":
        result = execute_t0(task_kind, safe_payload)
        result["routing"] = routing
    elif routing.get("tier") == "T1":
        result = execute_t1(task_kind, safe_payload, routing=routing)
        result["routing"] = routing
        cost_row = estimate_cost(tier="T1", tokens_in=len(json.dumps(safe_payload)) // 4, tokens_out=200)
    elif routing.get("tier") == "T2":
        result = execute_t2(safe_payload, routing=routing, op_key_val=ok)
        result["routing"] = routing
        cost_row = estimate_cost(tier="T2", tokens_in=500, tokens_out=800)
    elif routing.get("tier") == "T3":
        result = execute_t3(safe_payload, routing=routing)
        result["routing"] = routing
        cost_row = estimate_cost(tier="T3", tokens_in=1000, tokens_out=1500)
    else:
        result = {"ok": False, "error": "unknown_tier", "routing": routing}

    budget = enforce_budget(cost_row, config=cfg)
    if not budget.get("ok") and result.get("ok"):
        result = {"ok": False, "blocker_reason": budget.get("blocker_reason"), "prior": result}

    finished_at = utc_now()
    status = "ok" if result.get("ok") else "blocked"
    receipt_body = {
        "op_key": ok,
        "task_kind": task_kind,
        "mission_id": "M4",
        "value_class": "hygiene",
        "started_at": started_at,
        "finished_at": finished_at,
        "status": status,
        "routing": routing,
        "cost": {
            "provider": routing.get("provider"),
            "model": routing.get("model_id") or "none",
            "total_usd": cost_row.get("total_usd", 0),
            "within_budget": budget.get("ok"),
        },
        "result": result,
        "dry_run": dry_run,
        "governance": {
            "no_secrets_to_model": True,
            "deterministic_verdict": routing.get("tier") in ("T0", "T2"),
        },
    }
    if not dry_run:
        receipt_body = write_receipt(receipt_body, op_key=ok)
    return receipt_body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task-kind", required=True, help="grep|check|summarize|patch_proposal|premium_analysis|...")
    ap.add_argument("--payload", default="{}", help="JSON payload")
    ap.add_argument("--payload-file", type=Path, help="JSON file payload")
    ap.add_argument("--founder-approval-token", default="", help="FOUNDER_APPROVED_T3 for T3")
    ap.add_argument("--dry-run", action="store_true", help="Skip receipt write")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.payload_file:
        payload = json.loads(args.payload_file.read_text(encoding="utf-8"))
    else:
        payload = json.loads(args.payload)

    row = run_task(
        task_kind=args.task_kind,
        payload=payload,
        founder_approval_token=args.founder_approval_token or None,
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(
            f"kernel task={args.task_kind} tier={row.get('routing', {}).get('tier')} "
            f"status={row.get('status')} receipt={row.get('receipt_path', 'dry-run')}"
        )
    return 0 if row.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
