#!/usr/bin/env python3
"""Production E2E smoke for www.noetfield.com — enforces L0-law/PUBLIC_WWW_BRAND_E2E_LAW_LOCKED_v1.md."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.environ.get("NOETFIELD_E2E_BASE", "https://www.noetfield.com")
ROOT = Path(__file__).resolve().parents[1]
DENYLIST = ROOT / "governance" / "PUBLIC_OUTPUT_DENYLIST.json"

PATHS_200 = (
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
    "/governance/",
    "/ai-factories/",
    "/ai-factories/spec/",
    "/openapi.json",
    "/config/gate-ai-factory-design.json",
    "/config/status-ai-factory.json",
    "/noetfield-ai-factory-lanes.json",
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

AI_FACTORY_NEEDLES = (
    ("/ai-factories/", ("AI factories for governed work.", "AI Factory Design", "Submit to Gate")),
    ("/ai-factories/spec/", ("YAML Factory Spec.", "Copyable deployment contract", "Submit to Gate")),
    ("/openapi.json", ("Noetfield AI Factory Layer API", "/api/gate/ai-factory-design")),
    ("/config/gate-ai-factory-design.json", ("AI Factory Design", "YAML Factory Spec")),
    ("/config/status-ai-factory.json", ("AI Factory", "ledger_complete")),
    ("/noetfield-ai-factory-lanes.json", ("AI Factory Design", "/ai-factories/")),
)

CLIENT_PAGES = ("/copilot/procurement/", "/status/", "/next/")

INTERNAL_COPY = re.compile(
    r"613 GTM|founder never|Hub approve|RESEND_API_KEY|plan-with-no-asf|AGENT_SELF_AUDIT|"
    r"/docs/ops/|services/governance/README|make nf-prove|portfolio \d+/300",
    re.I,
)


def fetch(
    url: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    timeout: float = 25.0,
) -> tuple[int, str]:
    headers = {"Accept": "text/html,application/json", "User-Agent": "noetfield-www-e2e/1"}
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


def denied_paths() -> tuple[str, ...]:
    denylist = json.loads(DENYLIST.read_text(encoding="utf-8"))
    probes = list(denylist.get("probe_paths", []))
    base_prefixes = [prefix.rstrip("/") for prefix in denylist.get("prefix_paths", [])]
    exact = list(denylist.get("exact_paths", []))
    paths = probes + exact + base_prefixes
    return tuple(dict.fromkeys(paths))


def main() -> int:
    fail = 0
    print("=== NOETFIELD.COM PRODUCTION E2E ===")
    print(f"BASE: {BASE}")
    print("LAW: L0-law/PUBLIC_WWW_BRAND_E2E_LAW_LOCKED_v1.md\n")

    code, _ = fetch("https://noetfield.com/")
    if 200 <= code < 400:
        print("OK   apex noetfield.com redirect/respond", code)
    else:
        print(f"FAIL apex noetfield.com ({code})", file=sys.stderr)
        fail += 1

    for path in PATHS_200:
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

    for path in denied_paths():
        code, _ = fetch(f"{BASE}{path}")
        if code == 404:
            print(f"OK   blocked {path} (404)")
        else:
            print(f"FAIL internal leak {path} ({code})", file=sys.stderr)
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

    for path, needles in AI_FACTORY_NEEDLES:
        code, body = fetch(f"{BASE}{path}")
        if not (200 <= code < 300):
            print(f"FAIL AI Factory path {path} ({code})", file=sys.stderr)
            fail += 1
            continue
        missing = [needle for needle in needles if needle not in body]
        if missing:
            print(f"FAIL AI Factory {path} missing: {missing}", file=sys.stderr)
            fail += 1
        else:
            print(f"OK   AI Factory contract {path}")

    for path in CLIENT_PAGES:
        _, html = fetch(f"{BASE}{path}")
        hits = INTERNAL_COPY.findall(html)
        if hits:
            print(f"FAIL client copy leak on {path}: {hits[:3]}", file=sys.stderr)
            fail += 1
        else:
            print(f"OK   client copy clean {path}")

    try:
        intake = json.loads(intake_body)
        if intake.get("www_email_configured") is True and intake.get("delivery_mode") == "resend":
            print("OK   intake resend configured")
        else:
            print("FAIL intake not fully configured (auto-heal-www gate)", file=sys.stderr)
            fail += 1
        if intake.get("platform_reachable") is False:
            print("OK   intake platform_reachable=false (www-owned spine until DNS live)")
        elif intake.get("platform_reachable") is True:
            print("OK   intake platform_reachable=true (platform proxy)")
        else:
            print("FAIL intake platform_reachable missing", file=sys.stderr)
            fail += 1
    except json.JSONDecodeError:
        print("FAIL intake health not JSON", file=sys.stderr)
        fail += 1

    chat_code, chat_body = fetch(f"{BASE}/api/public/chat/health")
    if 200 <= chat_code < 300:
        try:
            chat = json.loads(chat_body)
            if chat.get("ok") is True and chat.get("mode") in ("www-local", "platform-proxy"):
                print(f"OK   chat health mode={chat.get('mode')}")
            else:
                print(f"FAIL chat health bad contract: {chat_body[:200]}", file=sys.stderr)
                fail += 1
        except json.JSONDecodeError:
            print("FAIL chat health not JSON", file=sys.stderr)
            fail += 1
    else:
        print(f"FAIL /api/public/chat/health ({chat_code})", file=sys.stderr)
        fail += 1

    chat_post = json.dumps(
        {"message": "What should I read before applying?", "session_id": "e2e-smoke"}
    ).encode()
    chat_post_code, chat_post_body = fetch(
        f"{BASE}/api/public/chat", method="POST", data=chat_post
    )
    if 200 <= chat_post_code < 300:
        try:
            reply = json.loads(chat_post_body).get("reply", "")
            banned = (
                "move money",
                "hold custody",
                "execute transactions",
                "hardcoded faq",
                "product_brief.md",
                "positioning.md",
                "offerings_locked.md",
                "docs/",
            )
            reply_lower = reply.lower()
            if any(term in reply_lower for term in banned):
                print(f"FAIL chat reply bad framing: {reply[:200]}", file=sys.stderr)
                fail += 1
            elif reply and (
                "trust-brief" in reply_lower
                or "pricing" in reply_lower
                or "start" in reply_lower
                or "governance" in reply_lower
                or "apply" in reply_lower
                or "read" in reply_lower
                or "copilot" in reply_lower
            ):
                print("OK   POST /api/public/chat contextual reply")
            else:
                print(f"FAIL chat reply unexpected: {chat_post_body[:200]}", file=sys.stderr)
                fail += 1
        except json.JSONDecodeError:
            print("FAIL chat POST not JSON", file=sys.stderr)
            fail += 1
    else:
        print(f"FAIL POST /api/public/chat ({chat_post_code})", file=sys.stderr)
        fail += 1

    eco_code, eco_body = fetch(f"{BASE}/api/ecosystem/public")
    if 200 <= eco_code < 300:
        try:
            eco = json.loads(eco_body)
            base = eco.get("chat_api_base", "MISSING")
            if base in ("", BASE, BASE + "/"):
                print("OK   ecosystem chat_api_base same-origin")
            else:
                print(f"WARN ecosystem chat_api_base={base!r} (expected same-origin until platform DNS)")
        except json.JSONDecodeError:
            print("FAIL ecosystem/public not JSON", file=sys.stderr)
            fail += 1
    else:
        print(f"FAIL /api/ecosystem/public ({eco_code})", file=sys.stderr)
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

    factory_payload = json.dumps(
        {
            "factory_type": "Compliance Evidence Factory",
            "target_user": "Operations team",
            "output_format": "Board-ready brief",
            "payload": {"scope": "regulated workflow"},
        }
    ).encode()
    code, factory_body = fetch(
        f"{BASE}/api/gate/ai-factory-design", method="POST", data=factory_payload
    )
    if 200 <= code < 300:
        try:
            factory = json.loads(factory_body)
            if (
                factory.get("gate_lane") == "AI Factory Design"
                and factory.get("status_record", {}).get("policy_decision")
                in {"ALLOW", "BLOCK", "ESCALATE"}
            ):
                print(
                    "OK   POST /api/gate/ai-factory-design "
                    f"{factory.get('status_record', {}).get('policy_decision')}"
                )
            else:
                print(f"FAIL AI Factory gate contract: {factory_body[:200]}", file=sys.stderr)
                fail += 1
        except json.JSONDecodeError:
            print("FAIL AI Factory gate not JSON", file=sys.stderr)
            fail += 1
    else:
        print(f"FAIL POST /api/gate/ai-factory-design ({code}): {factory_body[:200]}", file=sys.stderr)
        fail += 1

    code, status_body = fetch(f"{BASE}/api/status/ai-factory?request_id=e2e-ai-factory")
    if 200 <= code < 300:
        try:
            status = json.loads(status_body)
            if (
                status.get("request_type") == "AI Factory"
                and status.get("request_id") == "e2e-ai-factory"
            ):
                print("OK   GET /api/status/ai-factory")
            else:
                print(f"FAIL AI Factory status contract: {status_body[:200]}", file=sys.stderr)
                fail += 1
        except json.JSONDecodeError:
            print("FAIL AI Factory status not JSON", file=sys.stderr)
            fail += 1
    else:
        print(f"FAIL GET /api/status/ai-factory ({code}): {status_body[:200]}", file=sys.stderr)
        fail += 1

    spine_code, spine_body = fetch(f"{BASE}/api/health")
    if 200 <= spine_code < 300:
        try:
            spine = json.loads(spine_body)
            if spine.get("status") == "ok" and spine.get("service") == "noetfield-www":
                print("OK   www spine /api/health")
            else:
                print(f"FAIL www spine contract: {spine_body[:200]}", file=sys.stderr)
                fail += 1
        except json.JSONDecodeError:
            print("FAIL www spine not JSON", file=sys.stderr)
            fail += 1
    else:
        print(f"FAIL www spine /api/health ({spine_code})", file=sys.stderr)
        fail += 1

    print(
        "INFO platform.noetfield.com + api.noetfield.com — verified by dedicated "
        "platform/GEL smoke checks, not by the public www leak-prevention E2E."
    )

    print()
    if fail:
        print(f"RESULT: E2E FAIL ({fail} issue(s))", file=sys.stderr)
        return 1
    print("RESULT: E2E PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
