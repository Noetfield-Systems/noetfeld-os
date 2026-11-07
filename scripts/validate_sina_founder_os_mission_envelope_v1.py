#!/usr/bin/env python3
"""Fail-closed validator for the post-Governor SINA Founder OS -> NOOS envelope."""
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "noetfield-org/sina-founder-os-mission-envelope-v1.json"
REQUIRED = {
    "schema", "envelope_id", "company_id", "project_id", "origin", "objective",
    "scope", "constraints", "acceptance_criteria", "priority", "requested_by",
    "decision_record_ref", "workpacket_ref", "authority_level", "budget_limit",
    "expires_at", "idempotency_key",
}
SECRET_KEYS = {"api_key", "token", "secret", "password", "credential", "private_key"}

def reject_secret_fields(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in SECRET_KEYS or any(word in key.lower() for word in ("secret", "token", "api_key", "password", "credential", "private_key")):
                raise ValueError(f"secret-like field is forbidden at {path}.{key}")
            reject_secret_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_secret_fields(child, f"{path}[{index}]")

def validate(payload):
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("envelope must be a JSON object")
    missing = REQUIRED - payload.keys()
    if missing:
        raise ValueError("missing fields: " + ", ".join(sorted(missing)))
    if payload.get("schema") != contract["schema"]:
        raise ValueError("unknown schema version")
    if payload.get("company_id") != "noetfield-systems-inc":
        raise ValueError("tenant mismatch: this NOOS adapter accepts only noetfield-systems-inc")
    for key in ("envelope_id", "company_id", "project_id", "objective", "requested_by", "decision_record_ref", "workpacket_ref", "idempotency_key"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    if not isinstance(payload["acceptance_criteria"], list) or not payload["acceptance_criteria"]:
        raise ValueError("acceptance_criteria must be a non-empty array")
    if payload.get("priority") not in {"P0", "P1", "P2", "P3", "P4"}:
        raise ValueError("invalid priority")
    if payload.get("authority_level") not in {"A0", "A1", "A2", "A3"}:
        raise ValueError("A4 or unknown authority is forbidden for digital workers")
    if not isinstance(payload.get("budget_limit"), dict):
        raise ValueError("budget_limit must be an object")
    expires = payload.get("expires_at")
    if not isinstance(expires, str):
        raise ValueError("expires_at must be an ISO-8601 timestamp")
    try:
        expiry = datetime.fromisoformat(expires.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("expires_at must be an ISO-8601 timestamp") from exc
    if expiry.tzinfo is None or expiry <= datetime.now(timezone.utc):
        raise ValueError("mandate is expired or has no explicit timezone")
    reject_secret_fields(payload)
    # No dispatch side effect: validation only. Caller must still check DecisionRecord/WorkPacket
    # cryptographic and policy validity against the authoritative Governor/verifier services.
    return {"valid": True, "schema": contract["schema"], "company_id": payload["company_id"], "project_id": payload["project_id"], "dispatch": "NOT_PERFORMED", "reason": "contract_validation_only"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to a JSON mission envelope")
    args = parser.parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        print(json.dumps(validate(payload), indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
