#!/usr/bin/env python3
"""Mint a local API key for Noetfield OS development (Phase 2)."""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from auth import ApiKeyStore, _hash_key


def main() -> None:
    parser = argparse.ArgumentParser(description="Mint Noetfield OS API key")
    parser.add_argument("--output", default="api_keys.local.json")
    parser.add_argument("--key-id", default="dev-decision")
    parser.add_argument("--tenant-id", default="tenant-demo")
    parser.add_argument("--org-id", default="org-demo")
    args = parser.parse_args()

    salt = secrets.token_hex(16)
    raw_key = ApiKeyStore.generate_key()
    key_hash = _hash_key(raw_key, salt=salt)

    payload = {
        "salt": salt,
        "keys": [
            {
                "key_id": args.key_id,
                "key_hash": key_hash,
                "tenant_id": args.tenant_id,
                "org_id": args.org_id,
                "scopes": ["decision:write", "audit:read"],
            }
        ],
    }

    out = Path(args.output)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    print(f"X-API-Key: {raw_key}")


if __name__ == "__main__":
    main()
