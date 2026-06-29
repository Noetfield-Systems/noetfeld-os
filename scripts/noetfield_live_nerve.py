#!/usr/bin/env python3
"""Noetfield live nerve receipt: one machine truth for public output and chatbot knowledge."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "governance" / "NOETFIELD_LIVE_NERVE_RECEIPT.json"
DENYLIST = ROOT / "governance" / "PUBLIC_OUTPUT_DENYLIST.json"
PUBLIC_OUTPUT_SCRIPT = ROOT / "scripts" / "verify-public-output-allowlist.py"
ROUTE_NAV_SCRIPT = ROOT / "scripts" / "verify-route-nav-truth.py"
WWW_BASE = "https://www.noetfield.com"
PLATFORM_BASE = "https://platform.noetfield.com"
GEL_BASE = "https://api.noetfield.com"

STALE_CHAT_TERMS = (
    "governance execution infrastructure",
    "compliance log",
    "allow or deny",
    "offerings_locked",
    "product_brief",
    "positioning.md",
    "docs/",
    "source:",
    "move money",
    "hold custody",
    "execute transactions",
)


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_denylist() -> dict[str, Any]:
    return json.loads(DENYLIST.read_text(encoding="utf-8"))


def git_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    except Exception:
        return None
    return result.stdout.strip()


def load_public_output_module() -> Any:
    spec = importlib.util.spec_from_file_location("verify_public_output_allowlist", PUBLIC_OUTPUT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load verify-public-output-allowlist.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public_output_status() -> dict[str, Any]:
    module = load_public_output_module()
    output = ROOT / ".vercel" / "output" / "static"
    findings = module.scan(output)
    return {
        "ok": not findings,
        "output": str(output),
        "blocked_count": len(findings),
        "findings": findings[:50],
    }


def fetch_url(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> tuple[int | str, str]:
    data = None
    headers = {"User-Agent": "NoetfieldLiveNerve/1.0"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.status, res.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:
        return type(exc).__name__, str(exc)


def live_www_status() -> dict[str, Any]:
    blocked: list[dict[str, Any]] = []
    leaks: list[dict[str, Any]] = []
    denylist = public_denylist()
    for path in denylist.get("probe_paths", []):
        code, _body = fetch_url(WWW_BASE + path)
        row = {"path": path, "status": code}
        blocked.append(row)
        if code != 404:
            leaks.append(row)
    health_code, health_body = fetch_url(WWW_BASE + "/health")
    return {
        "ok": not leaks and health_code == 200,
        "base": WWW_BASE,
        "health_status": health_code,
        "health_preview": health_body[:200],
        "blocked_count": len(blocked),
        "denylist_hash": sha256_file(DENYLIST),
        "leaks": leaks,
    }


def chat_semantic_status(base: str) -> dict[str, Any]:
    code, body = fetch_url(
        base + "/api/public/chat",
        method="POST",
        payload={"message": "Executive overview", "session_id": "live-nerve"},
    )
    provider = None
    reply = body
    try:
        parsed = json.loads(body)
        provider = parsed.get("provider")
        reply = str(parsed.get("reply") or "")
    except json.JSONDecodeError:
        pass
    lower = reply.lower()
    stale_hits = [term for term in STALE_CHAT_TERMS if term in lower]
    return {
        "ok": code == 200 and not stale_hits,
        "base": base,
        "status": code,
        "provider": provider,
        "stale_hits": stale_hits,
        "reply_preview": reply[:240],
    }


def gel_status() -> dict[str, Any]:
    health_code, health_body = fetch_url(GEL_BASE + "/health")
    readiness_code, readiness_body = fetch_url(GEL_BASE + "/readiness")
    return {
        "ok": health_code == 200 and readiness_code == 200 and '"ready":true' in readiness_body,
        "base": GEL_BASE,
        "health_status": health_code,
        "readiness_status": readiness_code,
        "health_preview": health_body[:200],
        "readiness_preview": readiness_body[:200],
    }


def route_nav_status() -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(ROUTE_NAV_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "ok": result.returncode == 0,
        "command": f"{sys.executable} {ROUTE_NAV_SCRIPT.relative_to(ROOT).as_posix()}",
        "stdout": result.stdout[-1200:],
        "stderr": result.stderr[-1200:],
    }


def chatbot_status() -> dict[str, Any]:
    for rel in (
        ".",
        "packages/types",
        "packages/config",
        "packages/sdk",
        "services/events",
        "services/ledger",
        "services/graph",
        "services/governance",
        "services/signals",
        "services/workflow",
        "services/ai-runtime",
        "services/inspectors",
        "services/identity",
        "services/copilot-governance",
        "services/factories",
        "services/trust-brief",
        "services/legal-review",
        "services/aml-trace",
    ):
        sys.path.insert(0, str(ROOT / rel))
    from noetfield_governance.chatbot_knowledge import (  # type: ignore
        knowledge_bundle_version,
        knowledge_context_stats,
        knowledge_manifest_violations,
    )

    violations = knowledge_manifest_violations()
    return {
        "ok": not violations,
        "bundle_version": knowledge_bundle_version(),
        "manifest_hash": sha256_file(ROOT / "data" / "chatbot" / "MANIFEST.json"),
        "stats": knowledge_context_stats() if not violations else {},
        "violations": violations,
    }


def public_doc_freshness() -> dict[str, Any]:
    # First cut: public markdown must stay in explicitly allowed public folders.
    allowed_prefixes = (
        "docs/api/",
        "docs/copilot/",
        "docs/diligence/",
        "docs/federal/",
        "docs/msp/",
        "docs/runtime/",
        "docs/templates/",
        "docs/trust-brief/",
    )
    public_md = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob("docs/**/*.md")
        if any(path.relative_to(ROOT).as_posix().startswith(prefix) for prefix in allowed_prefixes)
    ]
    return {
        "ok": True,
        "public_markdown_count": len(public_md),
        "contract": "public markdown requires generated metadata in phase 2; raw internal docs are blocked from output now",
    }


def build_receipt() -> dict[str, Any]:
    public_output = public_output_status()
    chatbot = chatbot_status()
    docs = public_doc_freshness()
    www_live = live_www_status()
    www_chat = chat_semantic_status(WWW_BASE)
    platform_chat = chat_semantic_status(PLATFORM_BASE)
    gel_live = gel_status()
    route_nav = route_nav_status()
    ok = bool(
        public_output["ok"]
        and chatbot["ok"]
        and docs["ok"]
        and www_live["ok"]
        and www_chat["ok"]
        and platform_chat["ok"]
        and gel_live["ok"]
        and route_nav["ok"]
    )
    return {
        "schema": "noetfield-live-nerve-receipt-v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repo": str(ROOT),
        "git_sha": git_sha(),
        "ok": ok,
        "gate": "PASS" if ok else "FAIL",
        "next_safe_action": (
            "use this receipt as current truth before docs or chat summaries"
            if ok
            else "repair failed local/live nerve surfaces before using docs as truth"
        ),
        "nodes": {
            "N1_PUBLIC_OUTPUT": public_output,
            "N2_CHAT_TRUTH": chatbot,
            "N3_DOC_FRESHNESS": docs,
            "N4_WWW_LIVE_OUTPUT": www_live,
            "N5_WWW_CHAT_SEMANTIC": www_chat,
            "N6_PLATFORM_CHAT_SEMANTIC": platform_chat,
            "N7_GEL_LIVE_RUNTIME": gel_live,
            "N8_ROUTE_NAV_TRUTH": route_nav,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = build_receipt()
    if args.write:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"NOETFIELD_LIVE_NERVE {receipt['gate']} receipt={RECEIPT}")
        for node, status in receipt["nodes"].items():
            print(f"{node} ok={status['ok']}")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
