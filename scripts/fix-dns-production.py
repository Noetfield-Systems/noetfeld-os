#!/usr/bin/env python3
"""Apply noetfield.com + trustfield.ca DNS for Vercel www + optional Resend. Uses CF API token with DNS write."""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

VAULT = Path.home() / ".sina" / "secrets.env"
WRANGLER = Path.home() / "Library/Preferences/.wrangler/config/default.toml"

NOETFIELD_ZONE = "456aeba6b1a37d1fadbf6443cb929468"
TRUSTFIELD_ZONE = "0ab53e9adedb6558e677adbf59ae4824"

VERCEL_WWW_CNAME = "d2e47b585a01bc61.vercel-dns-017.com"
VERCEL_TXT = "vc-domain-verify=www.noetfield.com,80da2e8e34431bb25d15"


def read_vault() -> dict[str, str]:
    out: dict[str, str] = {}
    if not VAULT.is_file():
        return out
    for line in VAULT.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"')
    return out


def oauth_token() -> str:
    if not WRANGLER.is_file():
        return ""
    m = re.search(r'oauth_token = "([^"]+)"', WRANGLER.read_text(encoding="utf-8"))
    return m.group(1) if m else ""


def cf_token(vault: dict[str, str]) -> str:
    return (
        vault.get("CF_NOETFIELD_API_TOKEN")
        or vault.get("CF_API_TOKEN")
        or os.environ.get("CF_NOETFIELD_API_TOKEN")
        or os.environ.get("CF_API_TOKEN")
        or ""
    )


def cf_api(token: str, method: str, path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())


def upsert_dns(
    token: str,
    zone: str,
    rtype: str,
    name: str,
    content: str,
    proxied: bool = False,
    match_content: str | None = None,
) -> dict:
    q = cf_api(token, "GET", f"/zones/{zone}/dns_records?type={urllib.parse.quote(rtype)}&name={urllib.parse.quote(name)}")
    body = {"type": rtype, "name": name, "content": content, "ttl": 1, "proxied": proxied}
    rows = q.get("result") or []
    if match_content and rtype == "TXT":
        for row in rows:
            if match_content in (row.get("content") or ""):
                return cf_api(token, "PUT", f"/zones/{zone}/dns_records/{row['id']}", body)
    if rows:
        rid = rows[0]["id"]
        return cf_api(token, "PUT", f"/zones/{zone}/dns_records/{rid}", body)
    return cf_api(token, "POST", f"/zones/{zone}/dns_records", body)


def apply_noetfield(token: str) -> bool:
    ok = True
    updates = (
        ("CNAME", "www.noetfield.com", VERCEL_WWW_CNAME, None),
        ("CNAME", "platform.noetfield.com", VERCEL_WWW_CNAME, None),
        ("TXT", "_vercel.noetfield.com", VERCEL_TXT, "vc-domain-verify=www.noetfield.com"),
    )
    for rtype, name, content, match in updates:
        res = upsert_dns(
            token, NOETFIELD_ZONE, rtype, name, content, proxied=False, match_content=match
        )
        success = res.get("success") is True
        print(f"  {rtype} {name}: {'OK' if success else 'FAIL'} {res.get('errors')}")
        ok = ok and success
    return ok


def main() -> int:
    vault = read_vault()
    token = cf_token(vault)
    if not token:
        print("FAIL: no CF_API_TOKEN in vault")
        return 1

    print("[fix-dns] noetfield.com (Vercel www + verify TXT)...")
    if apply_noetfield(token):
        print("[fix-dns] noetfield DNS OK")
    else:
        oauth = oauth_token()
        if oauth:
            print("[fix-dns] Current CF_API_TOKEN is trustfield.ca-only.")
            print("[fix-dns] Create token: Cloudflare → API Tokens → Edit zone DNS → All zones")
            print("[fix-dns] Add to ~/.sina/secrets.env as CF_NOETFIELD_API_TOKEN=...")
            print("[fix-dns] Or replace CF_API_TOKEN with an all-zones DNS token.")
            print("")
            print("Manual records (noetfield.com → DNS):")
            print(f"  CNAME www → {VERCEL_WWW_CNAME} (DNS only / grey cloud)")
            print(f"  TXT _vercel → {VERCEL_TXT}")
        return 2

    # verify Vercel
    time.sleep(5)
    vercel = cf_api("", "GET", "")  # placeholder
    try:
        vt = json.load(open(os.path.expanduser("~/Library/Application Support/com.vercel.cli/auth.json")))["token"]
        req = urllib.request.Request(
            "https://api.vercel.com/v9/projects/prj_68m1LfXo1ElhjHzAJs3VCHz4rQ79/domains/www.noetfield.com?teamId=team_DXqqstsPtLv4TVnbadi34GCN",
            headers={"Authorization": f"Bearer {vt}"},
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode())
            print(f"[fix-dns] Vercel www verified={d.get('verified')}")
    except Exception as e:
        print(f"[fix-dns] Vercel check skipped: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
