"""HMAC-SHA256 signing for Trust Ledger entries."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any


def signing_key() -> bytes:
    material = os.environ.get("TLE_SIGNING_KEY", "nf-dev-signing-key-change-in-prod")
    return material.encode("utf-8")


def sign_tle_body(tle_body: dict[str, Any], *, key_id: str) -> dict[str, str]:
    digest_src = {k: v for k, v in tle_body.items() if k not in {"signatures", "audit_digest"}}
    material = json.dumps(digest_src, sort_keys=True, default=str)
    signature = hmac.new(signing_key(), material.encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "key_id": key_id,
        "algorithm": "HMAC-SHA256",
        "signature": f"sig:{signature[:32]}",
    }


def verify_tle_signature(tle_body: dict[str, Any], signature_block: dict[str, str]) -> bool:
    expected = sign_tle_body(tle_body, key_id=signature_block.get("key_id", ""))
    return hmac.compare_digest(expected["signature"], signature_block.get("signature", ""))
