#!/usr/bin/env python3
"""NOOS hourly role-circle tick — live API supervision cycle.

Triggered by CF fleet cron (interval 60m) → Railway POST /loop → this script
as the loop step for ``noos_role_circle_tick``.

Cycles every NOOS supervision role declared in ``data/noos-role-circle-v1.json``:
observe → reconcile → classify → verify → health → route → supervise_runway.

Does NOT implement Motor/Router/Runway recipes. Live HTTP probes use the locked
fleet/deadman/Railway health endpoints. Local roles invoke existing machine-loops
and health scripts. Writes one cycle receipt under ``receipts/proof/``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CIRCLE = ROOT / "data/noos-role-circle-v1.json"
PROOF_DIR = ROOT / "receipts/proof"
HTTP_TIMEOUT = 25


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_circle() -> dict[str, Any]:
    return json.loads(CIRCLE.read_text(encoding="utf-8"))


def http_json(url: str, *, timeout: int = HTTP_TIMEOUT) -> dict[str, Any]:
    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "noos-role-circle-v1"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {"ok": True, "status": resp.status, "body": body}
    except (urllib.error.HTTPError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:240]}


def run_cli(cmd: list[str], *, timeout: int = 480) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit_code": -1, "error": f"timeout_{timeout}s"}
    row: dict[str, Any] = {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "cmd": cmd,
    }
    if proc.stdout.strip():
        try:
            row["stdout_json"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            row["stdout_tail"] = proc.stdout[-600:]
    if proc.stderr.strip():
        row["stderr_tail"] = proc.stderr[-400:]
    return row


def role_observer(circle: dict[str, Any]) -> dict[str, Any]:
    apis = circle.get("live_apis") or {}
    probes = {}
    for name, url in apis.items():
        probes[name] = http_json(str(url))
    ok_count = sum(1 for p in probes.values() if p.get("ok"))
    total = len(probes)
    # Soft-ok when at least one live probe succeeds (Railway egress can miss a
    # single edge briefly). Degraded when not all probes succeed.
    return {
        "ok": ok_count > 0 if total else False,
        "degraded": ok_count < total,
        "probes": probes,
        "live_api_count": total,
        "live_api_ok_count": ok_count,
        "reason": None if ok_count == total else f"probes_ok={ok_count}/{total}",
    }


def role_route_health_incidents() -> dict[str, Any]:
    """File durable incidents from the latest stack-health receipt fix_queue."""
    import noos_health_incident_v1 as inc  # noqa: WPS433

    proof = ROOT / "receipts/proof/noos-stack-automation-health-v1.json"
    if not proof.is_file():
        return {"ok": True, "skipped": True, "reason": "no_health_receipt_yet"}
    try:
        health = json.loads(proof.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:200]}

    fix_queue = list(health.get("fix_queue") or [])
    if not fix_queue:
        return {"ok": True, "skipped": True, "reason": "empty_fix_queue", "health_ok": health.get("ok")}

    # Prefer Supabase when configured; else file transport so the circle still
    # produces durable local evidence (not the production authority).
    transport = inc.default_transport()
    transport_kind = "supabase"
    if transport is None:
        path = ROOT / ".noos-runtime/health-incident/role-circle-incidents.json"
        transport = inc.FileDurableTransport(path)
        transport_kind = "file_proof_double"

    filed = inc.file_from_fix_queue(
        fix_queue,
        source_receipt=str(proof.relative_to(ROOT)),
        source_run_url=os.environ.get("GITHUB_RUN_URL") or os.environ.get("DISPATCH_SOURCE"),
        source_sha=os.environ.get("NOOS_GIT_SHA") or os.environ.get("GITHUB_SHA"),
        transport=transport,
    )

    open_rows = inc.read_open_incidents(transport=transport)
    dispatched: list[dict[str, Any]] = []
    for row in open_rows.get("open") or []:
        if str(row.get("target_owner") or "") != "noos":
            # Cross-repo: record BLOCKED_EXTERNAL without founder spam.
            res = inc.dispatch_incident(row, transport=transport, handlers={}, owner_endpoints={})
            dispatched.append({"incident_id": row.get("incident_id"), **res})
            continue
        # Machine-safe NOOS handlers only.
        res = inc.dispatch_incident(row, transport=transport)
        dispatched.append({"incident_id": row.get("incident_id"), **res})

    after = inc.read_open_incidents(transport=transport)
    return {
        "ok": True,
        "transport": transport_kind,
        "filed": filed,
        "actionable_before": open_rows.get("actionable"),
        "dispatched": dispatched,
        "actionable_after": after.get("actionable"),
    }


def role_runway_preflight() -> dict[str, Any]:
    import noos_runway_supervision_adapter_v1 as rw  # noqa: WPS433

    pf = rw.preflight()
    # Not a circle failure — honest BLOCKED_RUNWAY_API_NOT_LIVE is expected until
    # NOETFIELD-RUNWAY is live.
    return {"ok": True, "preflight": pf, "runway_live": bool(pf.get("ok"))}


HOOKS = {
    "route_health_incidents": role_route_health_incidents,
    "runway_preflight": role_runway_preflight,
}


def run_role(role: dict[str, Any], circle: dict[str, Any]) -> dict[str, Any]:
    started = utc_now()
    kind = str(role.get("kind") or "")
    result: dict[str, Any]
    if role.get("role_id") == "noos.observer" or kind == "live_http":
        result = role_observer(circle)
    elif kind == "local_cli":
        result = run_cli(list(role.get("command") or []))
        # Health supervisor: computing RED is a successful observation (exit 1),
        # not a role-circle crash. Surface overall_status in the result.
        if role.get("role_id") == "noos.health_supervisor":
            payload = result.get("stdout_json") or {}
            proof = ROOT / "receipts/proof/noos-stack-automation-health-v1.json"
            if isinstance(payload, dict) and payload.get("schema") == "noos-stack-automation-health-v1":
                result = {
                    **result,
                    "ok": True,
                    "health_ok": bool(payload.get("ok")),
                    "overall_status": payload.get("overall_status"),
                    "fix_queue": payload.get("fix_queue") or [],
                }
            elif proof.is_file():
                try:
                    payload = json.loads(proof.read_text(encoding="utf-8"))
                    result = {
                        **result,
                        "ok": True,
                        "health_ok": bool(payload.get("ok")),
                        "overall_status": payload.get("overall_status"),
                        "fix_queue": payload.get("fix_queue") or [],
                        "reason": "read_from_receipt_file",
                    }
                except (OSError, json.JSONDecodeError):
                    result = {
                        **result,
                        "ok": True,
                        "degraded": True,
                        "reason": f"health_cli_failed:{result.get('error') or result.get('exit_code')}",
                    }
            else:
                # Observation role: a failed health CLI is a finding, not a circle crash.
                result = {
                    **result,
                    "ok": True,
                    "degraded": True,
                    "reason": f"health_cli_failed:{result.get('error') or result.get('exit_code')}",
                }
        # Reconciler/critic/auditor: tolerate missing optional runtime files on
        # slim cloud images — still report the error, but do not fail the circle
        # when the CLI produced structured JSON with ok=true, or when the only
        # failure is a known missing template/path on a partial image.
        if role.get("role_id") in {"noos.reconciler", "noos.critic", "noos.auditor"}:
            payload = result.get("stdout_json") or {}
            if isinstance(payload, dict) and payload.get("ok") is True:
                result = {**result, "ok": True}
            stderr = str(result.get("stderr_tail") or "")
            if "FileNotFoundError" in stderr and "dispatch-templates" in stderr:
                result = {
                    **result,
                    "ok": True,
                    "degraded": True,
                    "reason": "dispatch_templates_missing_on_executor",
                }
    elif kind == "python_hook":
        hook = HOOKS.get(str(role.get("hook") or ""))
        if hook is None:
            result = {"ok": False, "error": f"unknown_hook:{role.get('hook')}"}
        else:
            result = hook()
    else:
        result = {"ok": False, "error": f"unknown_kind:{kind}"}
    return {
        "role_id": role.get("role_id"),
        "title": role.get("title"),
        "category": role.get("category"),
        "kind": kind,
        "started_at": started,
        "finished_at": utc_now(),
        "ok": bool(result.get("ok")),
        "result": result,
    }


def run_circle(*, write_receipt: bool = True) -> dict[str, Any]:
    circle = load_circle()
    roles = list(circle.get("roles") or [])
    started = utc_now()
    role_rows = [run_role(r, circle) for r in roles]
    ok = all(r.get("ok") for r in role_rows)
    categories = sorted({str(r.get("category")) for r in role_rows if r.get("category")})
    expected = list(circle.get("category_coverage") or [])
    coverage_ok = all(c in categories for c in expected)

    row: dict[str, Any] = {
        "schema": "noos-role-circle-cycle-v1",
        "at": utc_now(),
        "started_at": started,
        "finished_at": utc_now(),
        "ok": ok and coverage_ok,
        "coverage_ok": coverage_ok,
        "categories_run": categories,
        "categories_expected": expected,
        "role_count": len(role_rows),
        "roles_ok": sum(1 for r in role_rows if r.get("ok")),
        "roles_failed": [r["role_id"] for r in role_rows if not r.get("ok")],
        "trigger": circle.get("trigger"),
        "roles": role_rows,
        "cost": "NO_EXTERNAL_MODEL_CALL",
        "canon_version": "FOUNDER_CANON_v1+MACHINE_LOOPS_v1",
    }
    if write_receipt:
        PROOF_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = PROOF_DIR / f"noos-role-circle-cycle-{stamp}.json"
        path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        # Stable alias for the incident router / cockpit.
        alias = PROOF_DIR / "noos-role-circle-latest.json"
        alias.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        try:
            row["receipt_path"] = str(path.relative_to(ROOT))
            row["alias_path"] = str(alias.relative_to(ROOT))
        except ValueError:
            row["receipt_path"] = str(path)
            row["alias_path"] = str(alias)
    return row


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="Print compact summary JSON (full receipt is always on disk)")
    ap.add_argument("--full-json", action="store_true", help="Print full cycle JSON to stdout (large)")
    ap.add_argument("--no-receipt", action="store_true")
    args = ap.parse_args(argv)
    row = run_circle(write_receipt=not args.no_receipt)
    summary = {
        "schema": "noos-role-circle-summary-v1",
        "ok": row.get("ok"),
        "coverage_ok": row.get("coverage_ok"),
        "roles_ok": row.get("roles_ok"),
        "role_count": row.get("role_count"),
        "roles_failed": row.get("roles_failed"),
        "categories_run": row.get("categories_run"),
        "receipt_path": row.get("receipt_path"),
        "alias_path": row.get("alias_path"),
        "cost": row.get("cost"),
        "role_briefs": [
            {
                "role_id": r.get("role_id"),
                "category": r.get("category"),
                "ok": r.get("ok"),
                "degraded": bool((r.get("result") or {}).get("degraded")),
                "reason": (r.get("result") or {}).get("reason")
                or (r.get("result") or {}).get("overall_status")
                or ((r.get("result") or {}).get("preflight") or {}).get("verdict"),
            }
            for r in (row.get("roles") or [])
        ],
    }
    if args.full_json:
        print(json.dumps(row, indent=2))
    elif args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(
            f"role_circle · ok={row.get('ok')} roles={row.get('roles_ok')}/{row.get('role_count')} "
            f"failed={row.get('roles_failed')} receipt={row.get('receipt_path')}"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
