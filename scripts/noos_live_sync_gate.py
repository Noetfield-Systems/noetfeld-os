#!/usr/bin/env python3
"""Noetfield OS live sync gate.

This is the NOOS-side nerve reader. It does not replace the website repo's
`make verify-live-nerve`; the wrapper refreshes that receipt, this script
consumes it, checks GEL/API health, reads SourceA live surfaces, and writes a
local NOOS receipt so this repo has fresh machine truth before agents update docs
or answer from memory. Use `--scope` to focus runtime, public, studio,
foundation, ecosystem, or all nodes without pretending a narrow check proves the
whole ecosystem.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "_NOOS_AGENT" / "live_sync" / "NOOS_LIVE_SYNC_RECEIPT.json"

WEBSITE_ROOT = Path("/Users/sinakazemnezhad/Desktop/Noetfield/Noetfield-All-Documents/Noetfield")
WEBSITE_NERVE_RECEIPT = WEBSITE_ROOT / "governance" / "NOETFIELD_LIVE_NERVE_RECEIPT.json"
STUDIO_ROOT = Path("/Users/sinakazemnezhad/Desktop/Noetfield/noetfield-studio-ide")
SOURCEA_ROOT = Path("/Users/sinakazemnezhad/Desktop/SourceA")
SOURCEA_LIVE_SURFACES = Path.home() / ".sina" / "agent-live-surfaces-v1.json"
SOURCEA_SESSION_RECEIPT = Path.home() / ".sina" / "agent_session_gate_receipt_v1.json"

SCOPE_REQUIRED_NODES = {
    "runtime": ("NOOS_REPO", "GEL_RUNTIME"),
    "public": ("NOOS_REPO", "WEBSITE_LIVE_NERVE", "PUBLIC_WEBSITE"),
    "studio": ("NOOS_REPO", "STUDIO_SUPABASE_BOUNDARY"),
    "foundation": ("NOOS_REPO", "SOURCEA_NERVE"),
    "ecosystem": (
        "NOOS_REPO",
        "WEBSITE_LIVE_NERVE",
        "GEL_RUNTIME",
        "PUBLIC_WEBSITE",
        "STUDIO_SUPABASE_BOUNDARY",
    ),
    "all": (
        "NOOS_REPO",
        "WEBSITE_LIVE_NERVE",
        "GEL_RUNTIME",
        "PUBLIC_WEBSITE",
        "SOURCEA_NERVE",
        "STUDIO_SUPABASE_BOUNDARY",
    ),
}

SCOPE_WARNING_NAMES = {
    "runtime": (),
    "public": ("website_intelligence_page_404",),
    "studio": (),
    "foundation": ("sourcea_session_gate_not_green",),
    "ecosystem": ("sourcea_session_gate_not_green", "website_intelligence_page_404"),
    "all": ("sourcea_session_gate_not_green", "website_intelligence_page_404"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"_error": f"json_decode:{exc}"}


def run_command(command: list[str], *, cwd: Path, timeout: int = 30) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:240]}
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-1200:],
        "stderr": result.stderr[-1200:],
    }


def fetch_json_or_text(url: str, *, timeout: int = 15) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "noos-live-sync-gate/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(1000).decode("utf-8", "replace")
            parsed: Any = None
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = None
            return {
                "ok": 200 <= response.status < 300,
                "status": response.status,
                "content_type": response.headers.get("content-type"),
                "json": parsed,
                "body_preview": body[:300],
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": "HTTPError"}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:240]}


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def age_hours(value: str | None) -> float | None:
    parsed = parse_time(value)
    if not parsed:
        return None
    return (datetime.now(timezone.utc) - parsed).total_seconds() / 3600


def noos_repo_status(*, full: bool) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "agent_docs": run_command(["bash", "scripts/check_noos_agent_docs.sh"], cwd=ROOT),
        "manifest_json": run_command(
            [
                "python3",
                "-c",
                "import json; json.load(open('docs/_NOOS_AGENT/MANIFEST.json')); print('manifest json ok')",
            ],
            cwd=ROOT,
        ),
    }
    if full:
        checks["pytest"] = run_command([".venv/bin/python", "-m", "pytest", "-q"], cwd=ROOT, timeout=120)
    ok = all(row.get("ok") for row in checks.values())
    return {"ok": ok, "checks": checks}


def website_live_nerve_status(*, refresh: bool, max_age_hours: float) -> dict[str, Any]:
    refresh_result = None
    if refresh:
        refresh_result = run_command(["make", "verify-live-nerve"], cwd=WEBSITE_ROOT, timeout=180)
    receipt = read_json(WEBSITE_NERVE_RECEIPT)
    receipt_age = age_hours(receipt.get("generated_at")) if receipt else None
    fresh = receipt_age is not None and receipt_age <= max_age_hours
    ok = receipt.get("ok") is True and receipt.get("gate") == "PASS" and fresh
    return {
        "ok": ok,
        "fresh": fresh,
        "age_hours": receipt_age,
        "path": str(WEBSITE_NERVE_RECEIPT),
        "refresh": refresh_result,
        "gate": receipt.get("gate"),
        "generated_at": receipt.get("generated_at"),
        "nodes": receipt.get("nodes") or {},
    }


def gel_runtime_status() -> dict[str, Any]:
    health = fetch_json_or_text("https://api.noetfield.com/health")
    readiness = fetch_json_or_text("https://api.noetfield.com/readiness")
    ready_json = readiness.get("json") if isinstance(readiness.get("json"), dict) else {}
    return {
        "ok": health.get("ok") is True and readiness.get("ok") is True and ready_json.get("ready") is True,
        "health": health,
        "readiness": readiness,
    }


def public_website_status() -> dict[str, Any]:
    urls = {
        "www": "https://www.noetfield.com/",
        "platform": "https://platform.noetfield.com/health",
    }
    checks = {name: fetch_json_or_text(url) for name, url in urls.items()}
    intelligence = fetch_json_or_text("https://www.noetfield.com/intelligence/")
    intake = fetch_json_or_text("https://www.noetfield.com/intelligence/intake/")
    checks["intelligence_page"] = intelligence
    checks["intelligence_intake"] = intake
    intelligence_404 = intelligence.get("status") == 404
    intake_ok = intake.get("ok") is True
    return {
        "ok": checks["www"].get("ok") is True and checks["platform"].get("ok") is True,
        "checks": checks,
        "known_drift": {
            "intelligence_page_404": intelligence_404 and not intake_ok,
            "intelligence_hub_deferred": intelligence_404 and intake_ok,
            "meaning": "Intelligence hub may defer to /intelligence/intake/ until website repo builds /intelligence/.",
        },
    }


def sourcea_nerve_status() -> dict[str, Any]:
    live = read_json(SOURCEA_LIVE_SURFACES)
    session = read_json(SOURCEA_SESSION_RECEIPT)
    session_failures = [
        {
            "step": row.get("step"),
            "exit": row.get("exit"),
            "incident": row.get("incident"),
            "poison_hits": row.get("poison_hits"),
        }
        for row in session.get("steps", [])
        if row.get("ok") is False
    ]
    live_ok = bool(live) and "ADMIT" in str(live.get("sascip_line") or live.get("sascip_safety_line") or "")
    return {
        "ok": live_ok,
        "session_gate_ok": session.get("ok") is True,
        "session_gate_failures": session_failures,
        "live_surfaces_path": str(SOURCEA_LIVE_SURFACES),
        "session_receipt_path": str(SOURCEA_SESSION_RECEIPT),
        "factory_now_line": live.get("factory_now_line"),
        "sascip_line": live.get("sascip_line") or live.get("sascip_safety_line"),
        "nerve_system_line": live.get("nerve_system_line"),
        "ui_upgrade_first_check_line": live.get("ui_upgrade_first_check_line"),
        "form_official_line": live.get("form_official_line"),
    }


def studio_boundary_status(*, full: bool) -> dict[str, Any]:
    boundary_module = STUDIO_ROOT / "src" / "lib" / "noetfield-supabase-boundary.ts"
    sql_policy = STUDIO_ROOT / "supabase" / "noetfield-studio-boundary.sql"
    if not STUDIO_ROOT.is_dir():
        return {
            "ok": True,
            "skipped": True,
            "reason": "studio_repo_absent",
            "repo": str(STUDIO_ROOT),
            "boundary_module_exists": False,
            "sql_policy_exists": False,
            "boundary_check": None,
        }
    result = None
    if full:
        result = run_command(["npm", "run", "boundary:check"], cwd=STUDIO_ROOT, timeout=120)
    return {
        "ok": boundary_module.is_file() and sql_policy.is_file() and (result is None or result.get("ok") is True),
        "repo": str(STUDIO_ROOT),
        "boundary_module_exists": boundary_module.is_file(),
        "sql_policy_exists": sql_policy.is_file(),
        "boundary_check": result,
    }


def build_receipt(*, scope: str, refresh_website_nerve: bool, full: bool, max_age_hours: float) -> dict[str, Any]:
    nodes = {
        "NOOS_REPO": noos_repo_status(full=full),
        "WEBSITE_LIVE_NERVE": website_live_nerve_status(
            refresh=refresh_website_nerve,
            max_age_hours=max_age_hours,
        ),
        "GEL_RUNTIME": gel_runtime_status(),
        "PUBLIC_WEBSITE": public_website_status(),
        "SOURCEA_NERVE": sourcea_nerve_status(),
        "STUDIO_SUPABASE_BOUNDARY": studio_boundary_status(full=full),
    }
    required_nodes = SCOPE_REQUIRED_NODES[scope]
    required_ok = all(nodes[name]["ok"] for name in required_nodes)
    warning_names = set(SCOPE_WARNING_NAMES[scope])
    warnings: list[str] = []
    if "sourcea_session_gate_not_green" in warning_names and not nodes["SOURCEA_NERVE"].get("session_gate_ok"):
        warnings.append("sourcea_session_gate_not_green")
    if (
        "website_intelligence_page_404" in warning_names
        and nodes["PUBLIC_WEBSITE"].get("known_drift", {}).get("intelligence_page_404")
    ):
        warnings.append("website_intelligence_page_404")
    gate = "PASS" if required_ok and not warnings else "DEGRADED" if required_ok else "FAIL"
    return {
        "schema": "noos-live-sync-receipt-v1",
        "generated_at": utc_now(),
        "repo": str(ROOT),
        "scope": scope,
        "required_nodes": list(required_nodes),
        "gate": gate,
        "ok": required_ok,
        "warnings": warnings,
        "next_safe_action": (
            "use this receipt as current NOOS truth; repair warnings before claiming full ecosystem green"
            if required_ok
            else "repair failed required nodes before updating public or runtime truth"
        ),
        "nodes": nodes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build NOOS live sync receipt")
    parser.add_argument("--write", action="store_true", help="write receipt into docs/_NOOS_AGENT/live_sync")
    parser.add_argument("--json", action="store_true", help="print full receipt JSON")
    parser.add_argument("--refresh-website-nerve", action="store_true", help="run website make verify-live-nerve first")
    parser.add_argument("--full", action="store_true", help="run heavier local pytest and Studio boundary command")
    parser.add_argument("--max-age-hours", type=float, default=24.0)
    parser.add_argument(
        "--scope",
        choices=sorted(SCOPE_REQUIRED_NODES),
        default="ecosystem",
        help="focus the required live nodes for the current task",
    )
    parser.add_argument("--strict", action="store_true", help="exit non-zero on DEGRADED as well as FAIL")
    args = parser.parse_args()

    receipt = build_receipt(
        scope=args.scope,
        refresh_website_nerve=args.refresh_website_nerve,
        full=args.full,
        max_age_hours=args.max_age_hours,
    )
    if args.write:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"NOOS_LIVE_SYNC {receipt['gate']} scope={receipt['scope']} receipt={RECEIPT}")
        for node, status in receipt["nodes"].items():
            print(f"{node} ok={status.get('ok')}")
        if receipt["warnings"]:
            print("WARNINGS " + ",".join(receipt["warnings"]))

    if not receipt["ok"]:
        return 1
    if args.strict and receipt["gate"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
