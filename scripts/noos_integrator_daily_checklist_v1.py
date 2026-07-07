#!/usr/bin/env python3
"""NOOS integrator — daily mandatory checklist (live probes only, no stale disk authority)."""

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
PROOF = ROOT / "receipts/proof/noos-integrator-daily-checklist-v1.json"
RUNTIME = ROOT / ".noos-runtime/integrator/daily-checklist-v1.json"

TF_REPO = Path.home() / "Desktop/Noetfield-Systems/TrustField-Technologies"
PLAN_WORKER_HEALTH = "https://trustfield-plan-worker-production.up.railway.app/health"
CF_FLEET_HEALTH = "https://tf-cf-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
GHA_ORG = "Noetfield-Systems"
GHA_REPOS = ("TrustField-Technologies", "noetfeld-os")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_json(cmd: list[str], *, timeout: int = 180) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if not proc.stdout.strip():
        return {"ok": False, "exit_code": proc.returncode, "stderr": (proc.stderr or "")[-400:]}
    try:
        doc = json.loads(proc.stdout)
        if isinstance(doc, dict):
            doc.setdefault("exit_code", proc.returncode)
        return doc
    except json.JSONDecodeError:
        return {"ok": False, "exit_code": proc.returncode, "raw": proc.stdout[-600:]}


def http_json(url: str, *, timeout: int = 25) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "NOOS-DailyCheck/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": str(exc)[:200]}
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:200]}


def gh_runs(repo: str, *, limit: int = 8) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "gh",
            "run",
            "list",
            "--repo",
            f"{GHA_ORG}/{repo}",
            "--limit",
            str(limit),
            "--json",
            "databaseId,conclusion,status,displayTitle,createdAt,event,workflowName,updatedAt",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or proc.stdout)[-300:]}
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid gh json"}

    def run_duration_s(row: dict[str, Any]) -> float:
        created = row.get("createdAt") or ""
        updated = row.get("updatedAt") or created
        try:
            c = datetime.fromisoformat(created.replace("Z", "+00:00"))
            u = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            return max(0.0, (u - c).total_seconds())
        except ValueError:
            return 999.0

    billing_blocked = 0
    real_failures: list[str] = []
    latest_is_billing_gate = False
    if rows:
        latest = rows[0]
        if latest.get("conclusion") == "failure" and run_duration_s(latest) < 12:
            latest_is_billing_gate = True

    for row in rows:
        if row.get("conclusion") != "failure":
            continue
        duration_s = run_duration_s(row)
        title = (row.get("displayTitle") or "")[:48]
        if duration_s < 12:
            billing_blocked += 1
        else:
            real_failures.append(f"{row.get('workflowName')}: {title}")

    # Pass if newest run is not a billing gate; historical <12s fails are informational only
    ok = not latest_is_billing_gate and not real_failures
    return {
        "ok": ok,
        "billing_gate_failures_12s": billing_blocked,
        "latest_is_billing_gate": latest_is_billing_gate,
        "real_failures": real_failures[:5],
        "latest_conclusion": rows[0].get("conclusion") if rows else None,
        "recent_count": len(rows),
    }


def item(
    *,
    item_id: str,
    tier: str,
    title: str,
    ok: bool,
    evidence: Any,
    fix: str | None = None,
    owner: str = "integrator",
) -> dict[str, Any]:
    return {
        "id": item_id,
        "tier": tier,
        "title": title,
        "status": "pass" if ok else "fail",
        "evidence": evidence,
        "fix": fix,
        "owner": owner,
    }


def run_checklist() -> dict[str, Any]:
    at = utc_now()
    checks: list[dict[str, Any]] = []

    integrator = run_json([sys.executable, str(ROOT / "scripts/noos_integrator_status_v1.py")])
    surfaces = integrator.get("surfaces") or {}
    checks.append(
        item(
            item_id="ICL-D01",
            tier="T0",
            title="NOOS vault + CF deploy token",
            ok=bool(surfaces.get("vault") and surfaces.get("cf_deploy_token")),
            evidence={"surfaces": {k: surfaces.get(k) for k in ("vault", "cf_deploy_token")}},
            fix="make cloud-vault-promote && make cloud-secrets-sync",
        )
    )
    mirror = run_json([sys.executable, str(ROOT / "scripts/noos_integrator_mirror_check_v1.py"), "--json"])
    mirror_ok = bool(surfaces.get("integrator_mirror"))
    if os.environ.get("NOOS_GHA_WITNESS") == "1" and mirror.get("reason") == "missing_home_mirror":
        mirror_ok = True
    checks.append(
        item(
            item_id="ICL-D02",
            tier="T0",
            title="Integrator mirror + agent conflicts clean",
            ok=mirror_ok and bool(surfaces.get("agent_conflicts")),
            evidence={"integrator_mirror": surfaces.get("integrator_mirror"), "agent_conflicts": surfaces.get("agent_conflicts"), "mirror": mirror},
            fix="python3 scripts/noos_integrator_mirror_check_v1.py --json && make local-sweep-stale",
        )
    )
    checks.append(
        item(
            item_id="ICL-D03",
            tier="T0",
            title="NOOS motor sustain (CF autorun tick)",
            ok=bool(surfaces.get("motor_sustain")),
            evidence=integrator.get("motor_sustain"),
            fix="make motor-sustain-verify && make integrator-repair-autorun",
        )
    )
    checks.append(
        item(
            item_id="ICL-D04",
            tier="T0",
            title="NOOS autorun critique overall green",
            ok=bool(surfaces.get("autorun")),
            evidence=integrator.get("autorun_critique"),
            fix="make integrator-repair-autorun && python3 scripts/autorun_status_v1.py --json",
        )
    )
    checks.append(
        item(
            item_id="ICL-D05",
            tier="T0",
            title="Machine loops audit chain",
            ok=bool(surfaces.get("machine_audit")),
            evidence={"line": integrator.get("machine_audit_line")},
            fix="make machine-audit && make machine-reconcile",
        )
    )

    layers = run_json([sys.executable, str(ROOT / "scripts/observe_trustfield_parallel_layers_v1.py"), "--json"])
    layer_summary = layers.get("summary") or {}
    layers_ok = layers.get("overall_status") in ("green", "yellow") and not layer_summary.get("red")
    checks.append(
        item(
            item_id="ICL-D06",
            tier="T1",
            title="TrustField 11 layers (no red)",
            ok=layers_ok,
            evidence={"closure": layers.get("closure_token"), "summary": layer_summary, "plan_worker": layers.get("plan_worker")},
            fix="make observe-trustfield-layers — route red layers to TrustField worker",
            owner="trustfield_worker",
        )
    )

    registry = run_json([sys.executable, str(ROOT / "scripts/observe_trustfield_loop_registry_v1.py"), "--json"])
    reg_summary = registry.get("summary") or {}
    reg_red = int(reg_summary.get("red") or 0)
    deadman_red = reg_summary.get("deadman_watched_red") or []
    checks.append(
        item(
            item_id="ICL-D07",
            tier="T0",
            title="TrustField loop registry (deadman motors green)",
            ok=reg_red == 0 and not deadman_red,
            evidence={"overall": registry.get("overall_status"), "summary": reg_summary},
            fix="cd TrustField-Technologies && python3 scripts/record_sg_registry_witness_v1.py && curl -sS .../tf-cf-fleet-tick-v1.../tick",
            owner="trustfield_worker",
        )
    )

    cf = http_json(CF_FLEET_HEALTH)
    cf_body = cf.get("body") or {}
    checks.append(
        item(
            item_id="ICL-D08",
            tier="T0",
            title="CF fleet tick primary motor",
            ok=bool(cf.get("ok") and cf_body.get("ok")),
            evidence=cf_body or cf,
            fix="cd TrustField-Technologies && ./scripts/cf_deploy_fleet_tick_worker.sh",
            owner="trustfield_worker",
        )
    )

    pw = http_json(PLAN_WORKER_HEALTH)
    pw_body = pw.get("body") or {}
    lane_ok = pw_body.get("lane_ok") or {}
    lanes_false = [k for k, v in lane_ok.items() if v is False]
    checks.append(
        item(
            item_id="ICL-D09",
            tier="T1",
            title="Railway plan-worker all lanes green",
            ok=bool(pw.get("ok") and pw_body.get("status") == "healthy" and not lanes_false),
            evidence={"status": pw_body.get("status"), "lanes_false": lanes_false, "cycles": pw_body.get("cycles_completed")},
            fix="cd TrustField-Technologies && ./scripts/railway_deploy_plan_worker.sh",
            owner="trustfield_worker",
        )
    )

    gha_items: list[dict[str, Any]] = []
    gha_billing_latest = False
    gha_real: list[str] = []
    for repo in GHA_REPOS:
        row = gh_runs(repo)
        gha_items.append({"repo": repo, **row})
        gha_billing_latest = gha_billing_latest or bool(row.get("latest_is_billing_gate"))
        gha_real.extend(row.get("real_failures") or [])
    checks.append(
        item(
            item_id="ICL-D10",
            tier="T1",
            title="GHA secondary witness (latest run not billing-gated)",
            ok=not gha_billing_latest,
            evidence={"repos": gha_items, "real_failures_sample": gha_real[:5]},
            fix="Enterprise billing: spending limit >$0 — then gh run rerun <id>. Real CI fails: fix workflow logs",
            owner="founder" if gha_billing_latest else "trustfield_worker",
        )
    )
    if gha_real:
        checks.append(
            item(
                item_id="ICL-D11",
                tier="T2",
                title="GHA real workflow failures (not billing)",
                ok=False,
                evidence={"failures": gha_real[:8]},
                fix="gh run view <id> --log-failed — fix script/test; do not confuse with billing",
                owner="trustfield_worker",
            )
        )

    org_plan = subprocess.run(
        ["gh", "api", f"orgs/{GHA_ORG}", "--jq", ".plan.name"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    checks.append(
        item(
            item_id="ICL-D12",
            tier="T0",
            title="GitHub org on Enterprise plan",
            ok=org_plan.returncode == 0 and "enterprise" in (org_plan.stdout or "").lower(),
            evidence={"plan": (org_plan.stdout or "").strip(), "enterprise_url": "https://github.com/enterprises/noetfield-systems-inc"},
            fix="Attach Noetfield-Systems org to enterprise noetfield-systems-inc",
            owner="founder",
        )
    )

    fails = [c for c in checks if c["status"] == "fail"]
    overall = "green" if not fails else ("yellow" if len(fails) <= 2 else "red")

    return {
        "schema": "noos-integrator-daily-checklist-v1",
        "at": at,
        "read_only": False,
        "one_law": "Daily authority = live probes at `at` — receipts on disk are snapshots only, never closure.",
        "architecture": {
            "primary": "cloudflare_workers_cron",
            "secondary": "github_actions_enterprise",
            "tertiary": "railway_plan_worker",
        },
        "overall_status": overall,
        "summary": {
            "total": len(checks),
            "pass": sum(1 for c in checks if c["status"] == "pass"),
            "fail": len(fails),
        },
        "checks": checks,
        "fix_queue": [{"id": c["id"], "fix": c["fix"], "owner": c["owner"]} for c in fails if c.get("fix")],
        "closure_token": f"NOOS_INTEGRATOR_DAILY: {overall}",
        "commands": {
            "run": "make integrator-daily",
            "status": "make integrator-status",
            "trustfield_layers": "make observe-trustfield-layers",
            "trustfield_registry": "make observe-trustfield-registry",
            "repair_autorun": "make integrator-repair-autorun",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    row = run_checklist()
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        RUNTIME.parent.mkdir(parents=True, exist_ok=True)
        RUNTIME.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        s = row["summary"]
        print(
            f"{row['closure_token']} pass={s['pass']}/{s['total']} fail={s['fail']} at={row['at']}"
        )
        for c in row["checks"]:
            if c["status"] == "fail":
                print(f"  FAIL {c['id']} {c['title']}")
                if c.get("fix"):
                    print(f"       fix: {c['fix']}")

    return 0 if row["overall_status"] == "green" else 1


if __name__ == "__main__":
    raise SystemExit(main())
