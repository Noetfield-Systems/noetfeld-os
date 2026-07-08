#!/usr/bin/env python3
"""NOOS GHA run health — billing-gate vs real CI failure classification (ICL-D10–D12)."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from typing import Any

GHA_ORG = "Noetfield-Systems"
GHA_REPOS = ("TrustField-Technologies", "noetfeld-os")
BILLING_GATE_MAX_SECONDS = 12.0
EARLY_WARNING_MAX_SECONDS = 12.0
ENTERPRISE_SLUG = "noetfield-systems-inc"

WITNESS_WORKFLOWS = (
    "noos-integrator-daily-witness.yml",
    "noos-autorun-witness.yml",
    "noos-motor-sustain-witness.yml",
    "noos-gha-health-witness.yml",
    "noos-stack-health-receipt.yml",
    "noos-trustfield-observe-witness.yml",
    "noos-sourcea-spine-witness.yml",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_duration_s(row: dict[str, Any]) -> float:
    created = row.get("createdAt") or ""
    updated = row.get("updatedAt") or created
    try:
        c = datetime.fromisoformat(created.replace("Z", "+00:00"))
        u = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        return max(0.0, (u - c).total_seconds())
    except ValueError:
        return 999.0


def gh_workflow_runs(
    repo: str,
    *,
    workflow: str | None = None,
    limit: int = 8,
) -> dict[str, Any]:
    cmd = [
        "gh",
        "run",
        "list",
        "--repo",
        f"{GHA_ORG}/{repo}",
        "--limit",
        str(limit),
        "--json",
        "databaseId,conclusion,status,displayTitle,createdAt,event,workflowName,updatedAt",
    ]
    if workflow:
        cmd.extend(["--workflow", workflow])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
    if proc.returncode != 0:
        return {"ok": False, "repo": repo, "workflow": workflow, "error": (proc.stderr or proc.stdout)[-300:]}
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "repo": repo, "workflow": workflow, "error": "invalid gh json"}
    return {"ok": True, "repo": repo, "workflow": workflow, "rows": rows}


def classify_runs(rows: list[dict[str, Any]]) -> dict[str, Any]:
    billing_blocked = 0
    real_failures: list[str] = []
    latest_is_billing_gate = False
    latest_real_failure = False
    if rows:
        latest = rows[0]
        duration_s = run_duration_s(latest)
        if latest.get("conclusion") == "failure" and duration_s < BILLING_GATE_MAX_SECONDS:
            latest_is_billing_gate = True
        if latest.get("conclusion") == "failure" and duration_s >= BILLING_GATE_MAX_SECONDS:
            latest_real_failure = True
    for row in rows:
        if row.get("conclusion") != "failure":
            continue
        duration_s = run_duration_s(row)
        title = (row.get("displayTitle") or "")[:48]
        wf = row.get("workflowName") or "workflow"
        if duration_s < BILLING_GATE_MAX_SECONDS:
            billing_blocked += 1
        else:
            real_failures.append(f"{wf}: {title}")
    return {
        "billing_gate_failures_12s": billing_blocked,
        "latest_is_billing_gate": latest_is_billing_gate,
        "latest_real_failure": latest_real_failure,
        "real_failures": real_failures[:8],
        "latest_conclusion": rows[0].get("conclusion") if rows else None,
        "latest_duration_s": round(run_duration_s(rows[0]), 2) if rows else None,
        "recent_count": len(rows),
    }


def gh_repo_health(repo: str, *, limit: int = 8) -> dict[str, Any]:
    base = gh_workflow_runs(repo, limit=limit)
    if not base.get("ok"):
        return base
    rows = base.get("rows") or []
    classified = classify_runs(rows)
    ok = not classified["latest_is_billing_gate"] and not classified["latest_real_failure"]
    return {"ok": ok, "repo": repo, **classified}


def org_plan_row(*, billing_gate_clear: bool) -> dict[str, Any]:
    proc = subprocess.run(
        ["gh", "api", f"orgs/{GHA_ORG}", "--jq", ".plan.name"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    plan_txt = (proc.stdout or "").strip().lower()
    enterprise_named = "enterprise" in plan_txt
    ok = proc.returncode == 0 and (enterprise_named or billing_gate_clear)
    return {
        "ok": ok,
        "plan": (proc.stdout or "").strip(),
        "enterprise_named": enterprise_named,
        "billing_gate_clear": billing_gate_clear,
        "enterprise_slug": ENTERPRISE_SLUG,
        "enterprise_url": f"https://github.com/enterprises/{ENTERPRISE_SLUG}",
        "witness_proxy": not enterprise_named and billing_gate_clear,
    }


def witness_early_warning(*, limit: int = 3) -> dict[str, Any]:
    """Flag witness workflows whose latest run failed in <12s (billing gate precursor)."""
    warnings: list[dict[str, Any]] = []
    for wf in WITNESS_WORKFLOWS:
        hit = gh_workflow_runs("noetfeld-os", workflow=wf, limit=limit)
        if not hit.get("ok"):
            warnings.append({"workflow": wf, "ok": False, "error": hit.get("error")})
            continue
        rows = hit.get("rows") or []
        if not rows:
            continue
        latest = rows[0]
        duration_s = run_duration_s(latest)
        if latest.get("conclusion") == "failure" and duration_s < EARLY_WARNING_MAX_SECONDS:
            warnings.append(
                {
                    "workflow": wf,
                    "ok": False,
                    "billing_gate_precursor": True,
                    "duration_s": round(duration_s, 2),
                    "run_id": latest.get("databaseId"),
                    "conclusion": latest.get("conclusion"),
                }
            )
        elif latest.get("conclusion") == "failure":
            warnings.append(
                {
                    "workflow": wf,
                    "ok": False,
                    "billing_gate_precursor": False,
                    "duration_s": round(duration_s, 2),
                    "run_id": latest.get("databaseId"),
                    "conclusion": latest.get("conclusion"),
                }
            )
    billing_precursors = [w for w in warnings if w.get("billing_gate_precursor")]
    return {
        "ok": not billing_precursors,
        "witness_count": len(WITNESS_WORKFLOWS),
        "warnings": warnings,
        "billing_gate_precursors": billing_precursors,
        "one_law": "Jobs failing in <12s with no step logs = billing/spending gate — not CI red",
    }


def run_gha_health() -> dict[str, Any]:
    repos: list[dict[str, Any]] = []
    billing_latest = False
    latest_real_failure = False
    real_failures: list[str] = []
    for repo in GHA_REPOS:
        row = gh_repo_health(repo)
        repos.append(row)
        billing_latest = billing_latest or bool(row.get("latest_is_billing_gate"))
        latest_real_failure = latest_real_failure or bool(row.get("latest_real_failure"))
        real_failures.extend(row.get("real_failures") or [])

    plan = org_plan_row(billing_gate_clear=not billing_latest)
    witnesses = witness_early_warning()

    checks = {
        "ICL-D10": {
            "title": "GHA secondary witness (latest run not billing-gated)",
            "ok": not billing_latest,
            "repos": repos,
        },
        "ICL-D11": {
            "title": "GHA real workflow failures (not billing)",
            "ok": not latest_real_failure,
            "failures": real_failures[:8],
        },
        "ICL-D12": {
            "title": "GitHub org on Enterprise plan",
            "ok": plan.get("ok"),
            "plan": plan,
        },
        "witness_early_warning": {
            "title": "Witness workflows not dying at billing gate (<12s)",
            "ok": witnesses.get("ok"),
            "detail": witnesses,
        },
    }
    fails = [k for k, v in checks.items() if not v.get("ok")]
    overall = "green" if not fails else ("yellow" if len(fails) == 1 else "red")
    ok = overall == "green"
    return {
        "schema": "noos-gha-run-health-v1",
        "at": utc_now(),
        "ok": ok,
        "overall_status": overall,
        "closure_token": f"NOOS_GHA_HEALTH: {overall}",
        "billing_gate_max_seconds": BILLING_GATE_MAX_SECONDS,
        "checks": checks,
        "fix_queue": [
            {
                "id": key,
                "fix": "Enterprise billing spending limit >$0; gh run rerun <id> for real CI",
            }
            for key in fails
        ],
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_gha_health()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["closure_token"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
