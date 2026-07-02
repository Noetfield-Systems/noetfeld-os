#!/usr/bin/env python3
"""Verify TLE audit_digest integrity — or demonstrate tamper FAIL."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def _sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def expected_digest(tle: dict[str, Any], *, record: dict[str, Any]) -> str:
    import json as _json

    input_payload = record.get("input_payload") or {}
    payload_hash = _sha256_hex(_json.dumps(input_payload, sort_keys=True))
    base_hash = str(record.get("policy_base_hash") or "")
    corridor_hash = str(record.get("policy_corridor_hash") or "")
    rule_set_version = str(record.get("rule_set_version") or "0.0.0")
    request_id = str(record.get("request_id") or tle.get("source_rid") or "")
    decision = str(record.get("decision") or "UNKNOWN")
    digest_material = _json.dumps(
        {
            "tle_id": tle["tle_id"],
            "source_rid": request_id,
            "decision": decision,
            "rule_set_version": rule_set_version,
            "payload_hash": payload_hash,
            "base_hash": base_hash,
            "corridor_hash": corridor_hash,
        },
        sort_keys=True,
    )
    return f"sha256:{_sha256_hex(digest_material)}"


def bundle_from_path(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_bundle(bundle: dict[str, Any]) -> tuple[bool, str]:
    tle = bundle.get("tle_v1")
    audit = bundle.get("audit")
    if not isinstance(tle, dict) or not isinstance(audit, dict):
        return False, "bundle missing tle_v1 or audit"
    record = {
        "id": audit.get("id"),
        "request_id": audit.get("request_id"),
        "decision": audit.get("decision"),
        "rule_set_version": bundle.get("rule_set_version"),
        "input_payload": audit.get("input_payload"),
        "policy_base_hash": (bundle.get("policy_hashes") or {}).get("base"),
        "policy_corridor_hash": (bundle.get("policy_hashes") or {}).get("corridor"),
    }
    expected = expected_digest(tle, record=record)
    actual = str(tle.get("audit_digest") or "")
    if actual == expected:
        return True, expected
    return False, f"expected {expected} got {actual}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify TLE audit_digest in export bundle")
    parser.add_argument("bundle", type=Path, help="Path to export JSON bundle")
    parser.add_argument(
        "--mutate",
        action="store_true",
        help="Mutate decision field before verify (expect FAIL)",
    )
    args = parser.parse_args()
    bundle = bundle_from_path(args.bundle)
    if args.mutate and isinstance(bundle.get("audit"), dict):
        bundle["audit"]["decision"] = "APPROVE"
        if isinstance(bundle.get("tle_v1"), dict):
            bundle["tle_v1"]["decision"] = "Go — tampered"
    ok, detail = verify_bundle(bundle)
    if ok:
        print(f"PASS — audit_digest ok ({detail})")
        return 0
    print(f"FAIL — audit_digest mismatch ({detail})", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
