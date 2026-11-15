#!/usr/bin/env python3
"""UOS-RI commissioning against the EXISTING Company OS -> Runway HMAC adapter.

No new queue, executor, broker, auth surface, or invented paid-cost/ROI metrics.
Requires a real, already authorized Runway intake packet and configured HMAC.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import noos_runway_supervision_adapter_v1 as runway

SCHEMA = "uos-ri.commissioning-observation.v1"
TERMINAL = {"SUCCEEDED", "COMPLETE", "DONE", "FAILED", "FAILED_WITH_RECEIPT", "BLOCKED", "BLOCKED_WITH_REASON", "CANCELLED"}
SHA256 = re.compile(r"^[a-f0-9]{64}$")
JOB_ID = re.compile(r"^[A-Za-z0-9._:-]{3,128}$")


def _body(reply: dict[str, Any]) -> dict[str, Any]:
    value: Any = reply.get("body", reply)
    if isinstance(value, dict) and isinstance(value.get("data"), dict):
        value = value["data"]
    return value if isinstance(value, dict) else {}


def _job_id(reply: dict[str, Any]) -> str | None:
    body = _body(reply)
    nested = body.get("job")
    for value in (body.get("job_id"), body.get("id"), nested.get("job_id") if isinstance(nested, dict) else None):
        if isinstance(value, str) and JOB_ID.fullmatch(value):
            return value
    return None


def _state(reply: dict[str, Any]) -> str:
    body = _body(reply)
    job = body.get("job")
    source = job if isinstance(job, dict) else body
    value = source.get("state", source.get("status", "UNKNOWN"))
    return str(value).upper()


def _packet_ok(packet: Any) -> bool:
    if not isinstance(packet, dict):
        return False
    required = ("tenant_id", "entitlement_id", "runway_id", "recipe_id", "recipe_version", "idempotency_key", "input")
    if any(not packet.get(k) for k in required):
        return False
    if not isinstance(packet["input"], dict):
        return False
    key = packet["idempotency_key"]
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{16,128}", key):
        return False
    budget = packet.get("budget_usd")
    return isinstance(budget, (int, float)) and not isinstance(budget, bool) and math.isfinite(budget) and budget > 0


def _verified_result(reply: dict[str, Any]) -> dict[str, Any]:
    """A runtime self-report or model result is NOT independent acceptance."""
    body = _body(reply)
    receipt = body.get("receipt")
    if not isinstance(receipt, dict):
        receipt = body.get("verification") if isinstance(body.get("verification"), dict) else {}
    verifier = receipt.get("verifier_id")
    builder = receipt.get("builder_id")
    digest = receipt.get("artifact_sha256")
    verified = (
        receipt.get("independent") is True
        and receipt.get("verdict") == "PASS"
        and isinstance(verifier, str) and bool(verifier)
        and isinstance(builder, str) and bool(builder) and verifier != builder
        and isinstance(digest, str) and bool(SHA256.fullmatch(digest))
    )
    cost = body.get("billing")
    billed = cost.get("billed_usd") if isinstance(cost, dict) else None
    billed_ok = (
        isinstance(cost, dict) and cost.get("billing_reconciled") is True
        and isinstance(billed, (int, float)) and not isinstance(billed, bool)
        and math.isfinite(billed) and billed >= 0
    )
    return {
        "independent_verdict": "PASS" if verified else "UNVERIFIED",
        "verifier_id": verifier if verified else None,
        "artifact_sha256": digest if verified else None,
        "billed_cost_usd": float(billed) if billed_ok else None,
        "cost_source": "RECONCILED_PROVIDER_BILL" if billed_ok else "UNKNOWN_NOT_ZERO",
        "realized_roi": None,
    }


def commission(
    packet: dict[str, Any],
    *,
    max_observations: int = 24,
    poll_seconds: float = 10,
    sleeper: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Submit once, reconcile duplicate intake, observe Runtime and separate proof.

    Running this function is an ACTIVE external dispatch, not a dry run.
    Replay validates intake idempotency ONLY, not worker crash/restart recovery.
    """
    proof: dict[str, Any] = {
        "schema": SCHEMA,
        "at": datetime.now(timezone.utc).isoformat(),
        "mode": "LIVE_ONLY_NO_MOCK",
        "workpacket_idempotency_sha256": hashlib.sha256(str(packet.get("idempotency_key", "")).encode()).hexdigest(),
        "runtime_job_id": None,
        "provider_execution_verified": False,
        "runtime_terminal_state": None,
        "replay_idempotent": None,
        "worker_restart_recovery_verified": False,
        "independent_verdict": "UNVERIFIED",
        "billed_cost_usd": None,
        "realized_roi": None,
        "status": "NOT_STARTED",
    }
    if not _packet_ok(packet):
        return {**proof, "status": "INVALID_AUTHORIZED_INTAKE", "error_code": "EXPLICIT_PACKET_FIELDS_REQUIRED"}
    preflight = runway.preflight()
    if not preflight.get("ok"):
        return {**proof, "status": "NOT_CONFIGURED", "error_code": str(preflight.get("verdict", "HMAC_PREFLIGHT_FAILED"))}

    first = runway.submit_intake(packet)
    job_id = _job_id(first) if first.get("ok") else None
    if not job_id:
        body = _body(first)
        raw_code = body.get("error") or first.get("error") or "NO_JOB_ID"
        code = str(raw_code)
        # Only machine-shaped codes and HTTP status are logged. Never raw
        # response bodies, credentials, host secrets or model output.
        safe_code = code if re.fullmatch(r"[A-Za-z0-9_:-]{1,90}", code) else "NONSTANDARD_ERROR"
        status = first.get("status")
        http_status = status if type(status) is int and 100 <= status <= 599 else None
        detail = str(body.get("detail") or "")
        # Database and provider error text may contain URLs, SQL, headers or
        # identifiers. Classify locally; never emit arbitrary upstream text.
        lowered = detail.lower()
        if "consume_runway_runtime_nonce_v1" in lowered and (
            "pgrst202" in lowered or "could not find" in lowered
            or "does not exist" in lowered or "not found" in lowered
        ):
            backend_category = "NONCE_RPC_MISSING"
        elif "consume_runway_runtime_nonce_v1" in lowered and "permission denied" in lowered:
            backend_category = "NONCE_RPC_PERMISSION_DENIED"
        elif "consume_runway_runtime_nonce_v1" in lowered:
            backend_category = "NONCE_RPC_FAILED"
        elif "supabase" in lowered and ("401" in lowered or "403" in lowered or "jwt" in lowered):
            backend_category = "SUPABASE_AUTH_ERROR"
        elif "supabase" in lowered and "timeout" in lowered:
            backend_category = "SUPABASE_TIMEOUT"
        elif "supabase" in lowered:
            backend_category = "SUPABASE_OTHER_ERROR"
        elif detail:
            backend_category = "UNCLASSIFIED_GATEWAY_EXCEPTION"
        else:
            backend_category = "DETAIL_UNAVAILABLE"
        return {**proof, "status": "INTAKE_UNCONFIRMED",
                "error_code": "NO_RUNTIME_JOB_ID", "intake_http_status": http_status,
                "intake_error_code": safe_code,
                "auth_backend_category": backend_category}
    proof["runtime_job_id"] = job_id
    proof["status"] = "DISPATCHED"

    # Distinct HMAC nonce, same semantic intake/idempotency key; never create another job.
    repeated = runway.submit_intake({**packet, "requested_at": first["intake"]["requested_at"]})
    duplicate_job_id = _job_id(repeated) if repeated.get("ok") else None
    if duplicate_job_id != job_id:
        return {**proof, "status": "IDEMPOTENCY_RECONCILIATION_FAILED", "error_code": "REPLAY_JOB_ID_MISMATCH"}
    proof["replay_idempotent"] = True

    for i in range(max(1, max_observations)):
        observed = runway.get_job(job_id)
        if not observed.get("ok"):
            return {**proof, "status": "RUNTIME_READBACK_FAILED", "error_code": "JOB_READBACK_ERROR"}
        state = _state(observed)
        proof["runtime_terminal_state"] = state
        if state in TERMINAL:
            break
        if i < max_observations - 1:
            sleeper(max(0, poll_seconds))
    else:
        return {**proof, "status": "PENDING_NOT_TERMINAL"}

    event_resp = runway.hmac_request("GET", f"/v1/jobs/{job_id}/events")
    result_resp = runway.hmac_request("GET", f"/v1/jobs/{job_id}/result")
    proof["events_readback"] = bool(event_resp.get("ok"))
    proof["result_readback"] = bool(result_resp.get("ok"))
    if not event_resp.get("ok") or not result_resp.get("ok"):
        proof["status"] = "TERMINAL_WITHOUT_COMPLETE_EVIDENCE"
        return proof

    proof.update(_verified_result(result_resp))
    result_body = _body(result_resp)
    artifacts = result_body.get("artifacts")
    if isinstance(artifacts, list):
        proof["runtime_artifact_digests"] = [
            {"artifact_id": item.get("artifact_id"), "sha256": item.get("content_sha256")}
            for item in artifacts
            if isinstance(item, dict) and isinstance(item.get("artifact_id"), str)
            and isinstance(item.get("content_sha256"), str) and SHA256.fullmatch(item["content_sha256"])
        ]
    proof["runtime_result_readback"] = True
    usage = result_body.get("usage")
    if isinstance(usage, dict):
        # The provider request ID is essential for correlation with HDIR Attempt/Evidence.
        # A model name or token counter alone is NOT evidence of a real API call.
        request_id = usage.get("provider_request_id") or usage.get("request_id")
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        proof["observed_usage"] = {
            "model": usage.get("model") if isinstance(usage.get("model"), str) else None,
            "provider_request_id": request_id if isinstance(request_id, str) and request_id.strip() else None,
            "input_tokens": input_tokens if type(input_tokens) is int and input_tokens >= 0 else None,
            "output_tokens": output_tokens if type(output_tokens) is int and output_tokens >= 0 else None,
            "usage_source": usage.get("usage_source") if isinstance(usage.get("usage_source"), str) else None,
        }
    reported = proof.get("observed_usage")
    proof["provider_execution_verified"] = (
        isinstance(reported, dict)
        and bool(reported.get("model"))
        and bool(reported.get("provider_request_id"))
        and reported.get("input_tokens") is not None
        and reported.get("output_tokens") is not None
        and reported.get("usage_source") in {"DEEPSEEK_API_USAGE", "CLOUDFLARE_API_USAGE", "PROVIDER_API_USAGE"}
    )
    terminal_ok = proof["runtime_terminal_state"] in {"SUCCEEDED", "COMPLETE", "DONE"}
    verifier_ok = proof["independent_verdict"] == "PASS"
    proof["status"] = (
        "VERIFIED_TECHNICAL_SUCCESS" if terminal_ok and verifier_ok and proof["provider_execution_verified"]
        else "MODEL_EXECUTION_EVIDENCE_MISSING" if terminal_ok and verifier_ok
        else "TERMINAL_UNVERIFIED_OR_FAILED"
    )
    return proof


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True, help="Existing authorized Runway intake JSON")
    parser.add_argument("--output", type=Path, help="Local non-authoritative observation export")
    parser.add_argument("--checks", type=int, default=24)
    parser.add_argument("--poll-seconds", type=float, default=10)
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
        result = commission(packet, max_observations=args.checks, poll_seconds=args.poll_seconds)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {"schema": SCHEMA, "status": "COMMISSIONING_ERROR", "error_code": type(exc).__name__}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "VERIFIED_TECHNICAL_SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
