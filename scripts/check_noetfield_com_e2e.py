#!/usr/bin/env python3
"""Production E2E smoke for www.noetfield.com (read-only)."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("NOETFIELD_E2E_BASE", "https://www.noetfield.com")
CANONICAL = os.environ.get(
    "NOETFIELD_CANONICAL_BASE", "https://www.noetfield.com"
)

PATHS = (
    "/",
    "/start/",
    "/pricing/",
    "/copilot/",
    "/copilot/pilot/",
    "/copilot/demo/",
    "/copilot/proof-case/",
    "/trust/",
    "/trust-brief/intake/",
    "/trust-ledger/sample-report/",
    "/investors/",
    "/work-with-us/",
    "/health",
)

API_PATHS = ("/api/intake/health", "/api/public/chat/health")

HOME_NEEDLES = (
    "Apply for pilot",
    "Copilot Governance Pack",
    "Trust Brief",
    "Board-grade trust",
    "operations@noetfield.com",
)

PILOT_NEEDLES = ("nfPilotApplyForm", "Copilot Governance Pack", "tamper-evident")


def fetch(url: str, *, method: str = "GET", data: bytes | None = None, timeout: float = 25.0) -> tuple[int, str]:
    headers = {"Accept": "text/html,application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, str(exc.reason)


def main() -> int:
    fail = 0
    print("=== NOETFIELD.COM PRODUCTION E2E ===")
    print(f"BASE: {BASE}\n")

    code, _ = fetch("https://noetfield.com/")
    if 200 <= code < 400:
        print("OK   apex noetfield.com redirect/respond", code)
    else:
        print(f"FAIL apex noetfield.com ({code})", file=sys.stderr)
        fail += 1

    for path in PATHS:
        code, _ = fetch(f"{BASE}{path}")
        label = f"{path} ({code})"
        if path == "/health" and code == 404:
            code2, _ = fetch(f"{BASE}/api/health")
            if 200 <= code2 < 300:
                print(f"OK   /health via /api/health ({code2})")
                continue
        if 200 <= code < 300:
            print(f"OK   {label}")
        else:
            print(f"FAIL {label}", file=sys.stderr)
            fail += 1

    intake_body = ""
    for path in API_PATHS:
        code, body = fetch(f"{BASE}{path}")
        if 200 <= code < 300:
            print(f"OK   {path} ({code})")
            try:
                print(json.dumps(json.loads(body), indent=2)[:800])
            except json.JSONDecodeError:
                print(body[:400])
        else:
            print(f"FAIL {path} ({code})", file=sys.stderr)
            fail += 1
        if path == "/api/intake/health":
            intake_body = body

    _, home = fetch(f"{BASE}/")
    for needle in HOME_NEEDLES:
        if needle in home:
            print(f"OK   homepage: {needle}")
        else:
            print(f"FAIL homepage missing: {needle}", file=sys.stderr)
            fail += 1

    _, pilot = fetch(f"{BASE}/copilot/pilot/")
    for needle in PILOT_NEEDLES:
        if needle in pilot:
            print(f"OK   pilot: {needle}")
        else:
            print(f"FAIL pilot missing: {needle}", file=sys.stderr)
            fail += 1

    try:
        intake = json.loads(intake_body)
        if intake.get("www_email_configured") is True and intake.get("delivery_mode") == "resend":
            print("OK   intake resend configured")
        else:
            print("FAIL intake not fully configured (auto-heal-www gate)", file=sys.stderr)
            fail += 1
    except json.JSONDecodeError:
        print("FAIL intake health not JSON", file=sys.stderr)
        fail += 1

    eval_payload = json.dumps(
        {"actor": "e2e-check", "action": "smoke", "context": "production e2e", "metadata": {}}
    ).encode()
    code, eval_body = fetch(f"{BASE}/evaluate", method="POST", data=eval_payload)
    if not (200 <= code < 300):
        code, eval_body = fetch(f"{BASE}/api/demo/evaluate", method="POST", data=eval_payload)
    if 200 <= code < 300:
        try:
            rid = json.loads(eval_body).get("rid", "")
        except json.JSONDecodeError:
            rid = ""
        if rid:
            print(f"OK   POST /evaluate rid={rid}")
        else:
            print(f"FAIL POST /evaluate no rid: {eval_body[:200]}", file=sys.stderr)
            fail += 1
    else:
        print(f"FAIL POST /evaluate ({code}): {eval_body[:200]}", file=sys.stderr)
        fail += 1

    for host, note in (
        ("https://platform.noetfield.com/health", "platform spine"),
        ("https://api.noetfield.com/health", "GEL lane (noetfeld-os)"),
    ):
        code, _ = fetch(host, timeout=15.0)
        if 200 <= code < 300:
            print(f"OK   {host} ({code})")
        else:
            print(f"WARN {host} ({code}) — {note}")

    print()
    if fail:
        print(f"RESULT: E2E FAIL ({fail} issue(s))", file=sys.stderr)
        return 1
    print("RESULT: E2E PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
