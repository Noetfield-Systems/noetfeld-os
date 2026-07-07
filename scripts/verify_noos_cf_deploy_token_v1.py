#!/usr/bin/env python3
"""Verify CLOUDFLARE_API_TOKEN can manage Workers on the NOOS account."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

from noos_vault_paths_v1 import workers_api_token

DEFAULT_ACCOUNT_ID = "0d0b967b77e2e5535455d39ff3dae72c"


def _get(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def verify(token: str | None = None, account_id: str | None = None) -> dict:
    tok = token or workers_api_token()
    aid = account_id or DEFAULT_ACCOUNT_ID
    row: dict[str, object] = {
        "ok": False,
        "account_id": aid,
        "token_active": False,
        "workers_scripts": False,
        "errors": [],
    }
    if not tok:
        row["errors"].append("CLOUDFLARE_API_TOKEN / CF_NOETFIELD_API_TOKEN missing")
        return row

    try:
        verify_doc = _get("https://api.cloudflare.com/client/v4/user/tokens/verify", tok)
        row["token_active"] = bool(verify_doc.get("success"))
    except urllib.error.HTTPError as exc:
        row["errors"].append(f"token verify HTTP {exc.code}")

    try:
        scripts_doc = _get(
            f"https://api.cloudflare.com/client/v4/accounts/{aid}/workers/scripts",
            tok,
        )
        row["workers_scripts"] = bool(scripts_doc.get("success"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:200]
        row["errors"].append(f"workers scripts HTTP {exc.code}: {body}")

    row["ok"] = bool(row["token_active"] and row["workers_scripts"])
    if not row["ok"] and row["token_active"] and not row["workers_scripts"]:
        row["errors"].append(
            "Token is active but lacks Account → Workers Scripts (Edit). "
            "Create a Cloudflare API token with Workers Scripts Edit for account "
            f"{aid}, set CF_NOETFIELD_API_TOKEN in ~/.noetfield-platform-secrets/noos-local.env, "
            "then run: make cloud-vault-promote && make cloud-secrets-sync"
        )
    return row


def main() -> int:
    row = verify()
    print(json.dumps(row, indent=2))
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
