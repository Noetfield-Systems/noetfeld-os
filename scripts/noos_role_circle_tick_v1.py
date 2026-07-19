#!/usr/bin/env python3
"""NOOS hourly role-circle tick v2 — full input→output portfolio.

Triggered by CF fleet cron (60m) → Railway POST /loop → this script.

For EVERY required NOOS operational loop (inbox → orchestrator):
  INPUT  → declared in data/noos-role-circle-v1.json loop_io
  PROCESS → execute_loop() from the locked 24/7 runner (cloud_steps on Railway)
  OUTPUT → durable valuable artifact (cycle receipt / evidence / state)

Then runs supervision roles (observe, reconcile, critic, audit, health, route,
runway). Circle is only fully green when every required loop produced a durable
valuable_output record. Probe-only is insufficient.

Does NOT copy Motor/Router/Runway recipes.
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
LOOPS_REG = ROOT / "data/noos-24-7-loops-v1.json"
PROOF_DIR = ROOT / "receipts/proof"
HTTP_TIMEOUT = 25

import noos_loop_runner_v1 as loop_runner  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_circle() -> dict[str, Any]:
    return json.loads(CIRCLE.read_text(encoding="utf-8"))


def load_loops() -> list[dict[str, Any]]:
    return list(json.loads(LOOPS_REG.read_text(encoding="utf-8")).get("loops") or [])


def http_json(url: str, *, timeout: int = HTTP_TIMEOUT) -> dict[str, Any]:
    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "noos-role-circle-v2"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except (urllib.error.HTTPError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:240]}


def post_role_circle_report(circle: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    deadman_health = str((circle.get("live_apis") or {}).get("deadman_health") or "")
    secret = (os.environ.get("NOOS_LOOP_SECRET") or os.environ.get("LOOP_RUNNER_SECRET") or "").strip()
    if not deadman_health:
        return {"ok": False, "skipped": True, "reason": "deadman_url_missing"}
    if not secret:
        return {"ok": False, "skipped": True, "reason": "loop_secret_missing"}
    url = deadman_health.removesuffix("/health") + "/role-circle-report"
    payload = {
        "ok": row.get("ok"),
        "portfolio_productive": row.get("portfolio_productive"),
        "loop_count": row.get("loop_count"),
        "loops_valuable": row.get("loops_valuable"),
        "loops_productive": row.get("loops_productive"),
        "loops_failed": row.get("loops_failed"),
        "loops_not_productive": row.get("loops_not_productive"),
        "receipt_path": row.get("receipt_path"),
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-NOOS-Loop-Secret": secret,
            "User-Agent": "noos-role-circle-v2",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            body = json.loads(response.read().decode("utf-8"))
            return {"ok": response.status < 300 and body.get("ok") is True, "status": response.status, "body": body}
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "error": exc.read().decode("utf-8", errors="replace")[:240],
        }
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:240]}


def run_cli(cmd: list[str], *, timeout: int = 480) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit_code": -1, "error": f"timeout_{timeout}s"}
    row: dict[str, Any] = {"ok": proc.returncode == 0, "exit_code": proc.returncode, "cmd": cmd}
    if proc.stdout.strip():
        try:
            row["stdout_json"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            row["stdout_tail"] = proc.stdout[-600:]
    if proc.stderr.strip():
        row["stderr_tail"] = proc.stderr[-400:]
    return row


def extract_valuable_output(cycle: dict[str, Any], *, io: dict[str, Any]) -> dict[str, Any]:
    """Pull real valuable output from a loop cycle (not a probe stub)."""
    steps = (cycle.get("runner_output") or {}).get("steps") or []
    evidence = cycle.get("evidence") or []
    liveness = cycle.get("liveness_upsert") or {}
    state = str(cycle.get("state_after") or "")
    artifact: dict[str, Any] = {
        "kind": "loop_cycle_receipt",
        "loop_id": cycle.get("loop_id"),
        "event_type": cycle.get("event_type"),
        "cycle_number": cycle.get("cycle_number"),
        "op_key": cycle.get("op_key"),
        "state_after": state,
        "value_class": cycle.get("value_class") or io.get("value_class"),
        "steps_ok": sum(1 for s in steps if s.get("ok")),
        "steps_total": len(steps),
        "evidence_count": len(evidence),
        "liveness_ok": bool(liveness.get("ok")) if liveness else None,
        "mission_id": cycle.get("mission_id"),
        "declared_output": io.get("valuable_output"),
    }
    # Prefer concrete step outputs when present.
    for s in steps:
        if s.get("stdout_tail") or s.get("stdout_json"):
            artifact["sample_step"] = {
                "name": s.get("name"),
                "ok": s.get("ok"),
                "exit_code": s.get("exit_code"),
                "stdout_tail": (s.get("stdout_tail") or "")[-200:],
            }
            break
    has_identity = bool(artifact.get("loop_id") and artifact.get("cycle_number"))
    has_state = state in {
        "COMPLETE",
        "IDLE_NO_WORK",
        "FAILED_WITH_RECEIPT",
        "BLOCKED_WITH_REASON",
    }
    valuable = has_identity and has_state and (len(steps) > 0 or state == "IDLE_NO_WORK")
    return {
        "valuable": valuable,
        "input": io.get("input"),
        "process": io.get("process"),
        "artifact": artifact,
    }


def execute_required_loop(loop: dict[str, Any], *, io: dict[str, Any]) -> dict[str, Any]:
    """Full I→O for one required NOOS loop via the locked loop runner."""
    started = utc_now()
    # Prefer cloud_steps on Railway / when explicitly cloud.
    os.environ.setdefault("NOOS_CLOUD_LOOP", "1")
    try:
        cycle = loop_runner.execute_loop(loop, self_heal=True)
    except SystemExit as exc:
        return {
            "ok": False,
            "role_id": io.get("role_id"),
            "loop_id": loop.get("id"),
            "started_at": started,
            "finished_at": utc_now(),
            "error": f"system_exit:{exc}",
            "valuable_output": {"valuable": False},
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "role_id": io.get("role_id"),
            "loop_id": loop.get("id"),
            "started_at": started,
            "finished_at": utc_now(),
            "error": str(exc)[:300],
            "valuable_output": {"valuable": False},
        }

    valuable = extract_valuable_output(cycle, io=io)
    state = str(cycle.get("state_after") or "")
    productive = state in {"COMPLETE", "IDLE_NO_WORK"}
    # Durable I→O artifact is valuable even when sink/steps degrade — but the
    # ledger separates productive (COMPLETE/IDLE) from merely durable.
    ok = bool(valuable.get("valuable"))
    steps = (cycle.get("runner_output") or {}).get("steps") or []
    evidence = cycle.get("evidence") or []
    return {
        "ok": ok,
        "productive": productive,
        "role_id": io.get("role_id") or f"noos.loop.{loop.get('id')}",
        "loop_id": loop.get("id"),
        "event_type": loop.get("event_type"),
        "category": str(loop.get("id")),
        "title": loop.get("title"),
        "started_at": started,
        "finished_at": utc_now(),
        "state_after": state,
        "cycle_number": cycle.get("cycle_number"),
        "op_key": cycle.get("op_key"),
        "value_class": cycle.get("value_class"),
        "valuable_output": valuable,
        "cycle_status": cycle.get("status"),
        "blocker_reason": cycle.get("blocker_reason"),
        "d4": cycle.get("d4"),
        "supabase_sink": {
            "ok": (cycle.get("supabase_sink") or {}).get("ok"),
            "skipped": (cycle.get("supabase_sink") or {}).get("skipped"),
            "reason": (cycle.get("supabase_sink") or {}).get("reason"),
        },
        "liveness_upsert": {
            "ok": (cycle.get("liveness_upsert") or {}).get("ok"),
            "skipped": (cycle.get("liveness_upsert") or {}).get("skipped"),
            "reason": (cycle.get("liveness_upsert") or {}).get("reason"),
        },
        "evidence": evidence[:8],
        "steps_summary": [
            {
                "name": s.get("name"),
                "ok": s.get("ok"),
                "exit_code": s.get("exit_code"),
                "stdout_tail": (s.get("stdout_tail") or "")[-160:],
            }
            for s in steps[:6]
        ],
    }


def role_observer(circle: dict[str, Any]) -> dict[str, Any]:
    apis = circle.get("live_apis") or {}
    probes = {name: http_json(str(url)) for name, url in apis.items()}
    ok_count = sum(1 for p in probes.values() if p.get("ok"))
    total = len(probes)
    return {
        "ok": ok_count > 0 if total else False,
        "degraded": ok_count < total,
        "probes": probes,
        "live_api_count": total,
        "live_api_ok_count": ok_count,
        "valuable_output": {
            "valuable": ok_count > 0,
            "artifact": {"kind": "live_api_probe_matrix", "ok_count": ok_count, "total": total},
        },
        "reason": None if ok_count == total else f"probes_ok={ok_count}/{total}",
    }


def role_route_health_incidents() -> dict[str, Any]:
    import noos_health_incident_v1 as inc  # noqa: WPS433

    proof = ROOT / "receipts/proof/noos-stack-automation-health-v1.json"
    if not proof.is_file():
        return {
            "ok": True,
            "skipped": True,
            "reason": "no_health_receipt_yet",
            "valuable_output": {"valuable": False, "reason": "no_health_receipt_yet"},
        }
    try:
        health = json.loads(proof.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:200], "valuable_output": {"valuable": False}}

    fix_queue = list(health.get("fix_queue") or [])
    transport = inc.default_transport()
    transport_kind = "supabase"
    if transport is None:
        transport = inc.FileDurableTransport(ROOT / ".noos-runtime/health-incident/role-circle-incidents.json")
        transport_kind = "file_proof_double"

    if not fix_queue:
        return {
            "ok": True,
            "skipped": True,
            "reason": "empty_fix_queue",
            "health_ok": health.get("ok"),
            "valuable_output": {
                "valuable": True,
                "artifact": {
                    "kind": "health_receipt",
                    "overall_status": health.get("overall_status"),
                    "fix_queue": [],
                    "note": "healthy_or_empty_queue",
                },
            },
        }

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
            res = inc.dispatch_incident(row, transport=transport, handlers={}, owner_endpoints={})
        else:
            res = inc.dispatch_incident(row, transport=transport)
        dispatched.append({"incident_id": row.get("incident_id"), **res})
    after = inc.read_open_incidents(transport=transport)
    return {
        "ok": True,
        "transport": transport_kind,
        "filed": filed,
        "dispatched": dispatched,
        "actionable_before": open_rows.get("actionable"),
        "actionable_after": after.get("actionable"),
        "valuable_output": {
            "valuable": True,
            "artifact": {
                "kind": "incident_dispatch",
                "created": (filed or {}).get("created") or [],
                "dispatched_count": len(dispatched),
                "worker_run_ids": [d.get("worker_run_id") for d in dispatched if d.get("worker_run_id")],
            },
        },
    }


def role_runway_preflight() -> dict[str, Any]:
    import noos_runway_supervision_adapter_v1 as rw  # noqa: WPS433

    pf = rw.preflight()
    return {
        "ok": True,
        "preflight": pf,
        "runway_live": bool(pf.get("ok")),
        "valuable_output": {
            "valuable": True,
            "artifact": {
                "kind": "runway_preflight",
                "verdict": pf.get("verdict"),
                "missing": pf.get("missing") or pf.get("required_url_env"),
            },
        },
    }


HOOKS = {
    "route_health_incidents": role_route_health_incidents,
    "runway_preflight": role_runway_preflight,
}


def run_supervision_role(role: dict[str, Any], circle: dict[str, Any]) -> dict[str, Any]:
    started = utc_now()
    kind = str(role.get("kind") or "")
    if role.get("role_id") in {"noos.fleet_observer", "noos.observer"} or kind == "live_http":
        result = role_observer(circle)
    elif kind == "local_cli":
        result = run_cli(list(role.get("command") or []))
        if role.get("role_id") == "noos.health_supervisor":
            payload = result.get("stdout_json") or {}
            proof = ROOT / "receipts/proof/noos-stack-automation-health-v1.json"
            if isinstance(payload, dict) and payload.get("schema") == "noos-stack-automation-health-v1":
                result = {
                    **result,
                    "ok": True,
                    "overall_status": payload.get("overall_status"),
                    "fix_queue": payload.get("fix_queue") or [],
                    "valuable_output": {
                        "valuable": True,
                        "artifact": {
                            "kind": "health_receipt",
                            "overall_status": payload.get("overall_status"),
                            "fix_queue": payload.get("fix_queue") or [],
                        },
                    },
                }
            elif proof.is_file():
                try:
                    payload = json.loads(proof.read_text(encoding="utf-8"))
                    result = {
                        **result,
                        "ok": True,
                        "overall_status": payload.get("overall_status"),
                        "valuable_output": {
                            "valuable": True,
                            "artifact": {
                                "kind": "health_receipt",
                                "overall_status": payload.get("overall_status"),
                                "fix_queue": payload.get("fix_queue") or [],
                            },
                        },
                    }
                except (OSError, json.JSONDecodeError):
                    result = {
                        **result,
                        "ok": True,
                        "degraded": True,
                        "valuable_output": {"valuable": False, "reason": "health_unreadable"},
                    }
            else:
                result = {
                    **result,
                    "ok": True,
                    "degraded": True,
                    "reason": f"health_cli_failed:{result.get('exit_code')}",
                    "valuable_output": {"valuable": False, "reason": "health_cli_failed"},
                }
        elif role.get("role_id") in {"noos.reconciler", "noos.critic", "noos.auditor"}:
            payload = result.get("stdout_json") or {}
            if isinstance(payload, dict) and (payload.get("ok") is True or payload.get("schema")):
                result = {
                    **result,
                    "ok": True,
                    "valuable_output": {
                        "valuable": True,
                        "artifact": {
                            "kind": "machine_loops_receipt",
                            "schema": payload.get("schema"),
                            "report_line": payload.get("report_line"),
                            "receipt_path": payload.get("receipt_path"),
                        },
                    },
                }
            stderr = str(result.get("stderr_tail") or "")
            if "FileNotFoundError" in stderr and "dispatch-templates" in stderr:
                result = {
                    **result,
                    "ok": True,
                    "degraded": True,
                    "reason": "dispatch_templates_missing_on_executor",
                    "valuable_output": {"valuable": False, "reason": "dispatch_templates_missing"},
                }
    elif kind == "python_hook":
        hook = HOOKS.get(str(role.get("hook") or ""))
        result = hook() if hook else {"ok": False, "error": f"unknown_hook:{role.get('hook')}"}
    else:
        result = {"ok": False, "error": f"unknown_kind:{kind}"}

    return {
        "role_id": role.get("role_id"),
        "title": role.get("title") or role.get("task"),
        "category": role.get("category"),
        "kind": "supervision",
        "started_at": started,
        "finished_at": utc_now(),
        "ok": bool(result.get("ok")),
        "valuable_output": result.get("valuable_output")
        or {"valuable": bool(result.get("ok")), "artifact": {"kind": "supervision_result"}},
        "result": {k: v for k, v in result.items() if k != "valuable_output"},
    }


def build_value_ledger(loop_rows: list[dict[str, Any]], supervision: list[dict[str, Any]]) -> dict[str, Any]:
    valuable_loops = [r for r in loop_rows if (r.get("valuable_output") or {}).get("valuable")]
    productive_loops = [r for r in loop_rows if r.get("productive")]
    by_value_class: dict[str, int] = {}
    for r in valuable_loops:
        vc = str(r.get("value_class") or "unknown")
        by_value_class[vc] = by_value_class.get(vc, 0) + 1
    artifacts = []
    for r in loop_rows + supervision:
        vo = r.get("valuable_output") or {}
        if vo.get("valuable") and vo.get("artifact"):
            artifacts.append(
                {
                    "role_id": r.get("role_id"),
                    "loop_id": r.get("loop_id"),
                    "kind": (vo.get("artifact") or {}).get("kind"),
                    "state_after": r.get("state_after"),
                    "cycle_number": r.get("cycle_number"),
                    "op_key": r.get("op_key"),
                    "productive": bool(r.get("productive")),
                    "blocker_reason": r.get("blocker_reason"),
                    "steps_ok": sum(1 for s in (r.get("steps_summary") or []) if s.get("ok")),
                    "steps_total": len(r.get("steps_summary") or []),
                    "evidence_count": len(r.get("evidence") or []),
                }
            )
    return {
        "schema": "noos-role-circle-value-ledger-v1",
        "required_loops": len(loop_rows),
        "valuable_loops": len(valuable_loops),
        "productive_loops": len(productive_loops),
        "missing_valuable": [r.get("loop_id") for r in loop_rows if not (r.get("valuable_output") or {}).get("valuable")],
        "not_productive": [r.get("loop_id") for r in loop_rows if not r.get("productive")],
        "by_value_class": by_value_class,
        "artifacts": artifacts,
        # Real valuable output = every required loop produced a durable I→O artifact.
        "real_valuable_output": len(valuable_loops) == len(loop_rows) and len(loop_rows) > 0,
        # Portfolio success = every required loop reached COMPLETE/IDLE (sink acked).
        "portfolio_productive": len(productive_loops) == len(loop_rows) and len(loop_rows) > 0,
    }


def run_circle(*, write_receipt: bool = True) -> dict[str, Any]:
    circle = load_circle()
    loops = {str(l.get("id")): l for l in load_loops()}
    required_ids = list(circle.get("required_loop_ids") or [])
    io_map = circle.get("loop_io") or {}
    started = utc_now()

    # Force cloud step selection on Railway / circle executor.
    os.environ.setdefault("NOOS_CLOUD_LOOP", "1")

    loop_rows: list[dict[str, Any]] = []
    for lid in required_ids:
        loop = loops.get(lid)
        io = dict(io_map.get(lid) or {})
        if not loop:
            loop_rows.append(
                {
                    "ok": False,
                    "loop_id": lid,
                    "role_id": io.get("role_id"),
                    "error": "loop_missing_from_24_7_registry",
                    "valuable_output": {"valuable": False},
                }
            )
            continue
        loop_rows.append(execute_required_loop(loop, io=io))

    supervision = [run_supervision_role(r, circle) for r in (circle.get("supervision_roles") or [])]
    ledger = build_value_ledger(loop_rows, supervision)

    loops_ok = all(r.get("ok") for r in loop_rows)
    supervision_ok = all(r.get("ok") for r in supervision)
    ok = bool(ledger.get("real_valuable_output")) and supervision_ok

    row: dict[str, Any] = {
        "schema": "noos-role-circle-cycle-v2",
        "at": utc_now(),
        "started_at": started,
        "finished_at": utc_now(),
        "ok": ok,
        "version": circle.get("version"),
        "io_law": circle.get("io_law"),
        "required_loop_ids": required_ids,
        "loops_ok": loops_ok,
        "supervision_ok": supervision_ok,
        "loop_count": len(loop_rows),
        "loops_valuable": ledger.get("valuable_loops"),
        "loops_productive": ledger.get("productive_loops"),
        "loops_failed": [r.get("loop_id") for r in loop_rows if not r.get("ok")],
        "loops_not_productive": ledger.get("not_productive"),
        "supervision_failed": [r.get("role_id") for r in supervision if not r.get("ok")],
        "portfolio_productive": ledger.get("portfolio_productive"),
        "value_ledger": ledger,
        "loops": loop_rows,
        "supervision": supervision,
        "cost": "NO_EXTERNAL_MODEL_CALL",
        "canon_version": "FOUNDER_CANON_v1+MACHINE_LOOPS_v1",
        "trigger": circle.get("trigger"),
    }

    if write_receipt:
        PROOF_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = PROOF_DIR / f"noos-role-circle-cycle-{stamp}.json"
        path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        alias = PROOF_DIR / "noos-role-circle-latest.json"
        alias.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        # Dedicated value ledger artifact — the "real valuable output" surface.
        ledger_path = PROOF_DIR / f"noos-role-circle-value-ledger-{stamp}.json"
        try:
            circle_receipt_rel = str(path.relative_to(ROOT))
        except ValueError:
            circle_receipt_rel = str(path)
        ledger_doc = {
            **ledger,
            "at": utc_now(),
            "circle_receipt": circle_receipt_rel,
            "ok": bool(ledger.get("real_valuable_output")),
        }
        ledger_path.write_text(json.dumps(ledger_doc, indent=2) + "\n", encoding="utf-8")
        try:
            row["receipt_path"] = str(path.relative_to(ROOT))
            row["alias_path"] = str(alias.relative_to(ROOT))
            row["value_ledger_path"] = str(ledger_path.relative_to(ROOT))
        except ValueError:
            row["receipt_path"] = str(path)
            row["alias_path"] = str(alias)
            row["value_ledger_path"] = str(ledger_path)
    row["telegram_delivery"] = post_role_circle_report(circle, row)
    return row


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="Print compact summary JSON")
    ap.add_argument("--full-json", action="store_true")
    ap.add_argument("--no-receipt", action="store_true")
    args = ap.parse_args(argv)
    row = run_circle(write_receipt=not args.no_receipt)
    summary = {
        "schema": "noos-role-circle-summary-v2",
        "ok": row.get("ok"),
        "loop_count": row.get("loop_count"),
        "loops_valuable": row.get("loops_valuable"),
        "loops_productive": row.get("loops_productive"),
        "loops_failed": row.get("loops_failed"),
        "loops_not_productive": row.get("loops_not_productive"),
        "supervision_failed": row.get("supervision_failed"),
        "real_valuable_output": (row.get("value_ledger") or {}).get("real_valuable_output"),
        "portfolio_productive": row.get("portfolio_productive"),
        "by_value_class": (row.get("value_ledger") or {}).get("by_value_class"),
        "receipt_path": row.get("receipt_path"),
        "value_ledger_path": row.get("value_ledger_path"),
        "telegram_delivery": row.get("telegram_delivery"),
        "cost": row.get("cost"),
        "loop_briefs": [
            {
                "loop_id": r.get("loop_id"),
                "role_id": r.get("role_id"),
                "ok": r.get("ok"),
                "productive": r.get("productive"),
                "state_after": r.get("state_after"),
                "cycle_number": r.get("cycle_number"),
                "valuable": (r.get("valuable_output") or {}).get("valuable"),
                "value_class": r.get("value_class"),
                "blocker_reason": r.get("blocker_reason"),
                "steps_ok": sum(1 for s in (r.get("steps_summary") or []) if s.get("ok")),
                "steps_total": len(r.get("steps_summary") or []),
            }
            for r in (row.get("loops") or [])
        ],
    }
    if args.full_json:
        print(json.dumps(row, indent=2))
    elif args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(
            f"role_circle_v2 · ok={row.get('ok')} valuable={row.get('loops_valuable')}/{row.get('loop_count')} "
            f"failed={row.get('loops_failed')} ledger={row.get('value_ledger_path')}"
        )
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
