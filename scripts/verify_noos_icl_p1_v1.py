#!/usr/bin/env python3
"""ICL-P1 closeout verify — boot sync, GHA deploy, SourceA spine, Noetfield vault."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts/proof/noos-integrator-icl-p1-closeout-v1.json"

import os  # noqa: E402

NOETFIELD_REPO = Path(os.environ.get("NOETFIELD_REPO", str(ROOT.parent / "Noetfield")))

from noos_vault_paths_v1 import (  # noqa: E402
    NOETFIELD_LOCAL_ENV,
    NOETFIELD_PLATFORM_SECRETS,
    NOOS_LOCAL_ENV,
    parse_env_file,
    workers_api_token,
)


def _http_ok(url: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "verify-noos-icl-p1-v1"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status == 200
    except (urllib.error.HTTPError, OSError):
        return False


def _run_json(cmd: list[str], *, timeout: int = 120) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if not proc.stdout.strip():
        return {"ok": False, "exit_code": proc.returncode, "stderr": proc.stderr[-400:]}
    try:
        doc = json.loads(proc.stdout)
        if isinstance(doc, dict):
            doc.setdefault("exit_code", proc.returncode)
        return doc
    except json.JSONDecodeError:
        return {"ok": False, "exit_code": proc.returncode, "raw": proc.stdout[-500:]}


def verify_icl_p1_01() -> dict:
    boot_script = ROOT / "scripts/noos_local_boot_vault_sync_v1.sh"
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    noos = parse_env_file(NOOS_LOCAL_ENV)
    token = workers_api_token(noos)
    dupes = "CLOUDFLARE_API_TOKEN" in noos and "CF_NOETFIELD_API_TOKEN" in noos
    cf_verify = _run_json([sys.executable, str(ROOT / "scripts/verify_noos_cf_deploy_token_v1.py")])
    return {
        "id": "ICL-P1-01",
        "title": "Agentic cloud bootstrap on boot",
        "ok": bool(
            boot_script.is_file()
            and "noos_local_boot_vault_sync_v1.sh" in makefile
            and token
            and not dupes
            and cf_verify.get("ok")
        ),
        "boot_script": str(boot_script),
        "cf_token_ok": bool(cf_verify.get("ok")),
        "duplicate_cloudflare_keys": dupes,
        "platform_vault": str(NOETFIELD_PLATFORM_SECRETS),
    }


def verify_icl_p1_02() -> dict:
    wf = ROOT / ".github/workflows/deploy-noos-cloud-workers-v1.yml"
    text = wf.read_text(encoding="utf-8") if wf.is_file() else ""
    has_job_token = "CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}" in text
    has_verify_step = "verify_noos_cf_deploy_token_v1.py" in text
    fleet_ok = _http_ok("https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health")
    factory_ok = _http_ok("https://noos-factory-autorun-tick-v1.sina-kazemnezhad-ca.workers.dev/health")
    gh_run = subprocess.run(
        ["gh", "run", "list", "--workflow=deploy-noos-cloud-workers-v1.yml", "--limit", "1", "--json", "conclusion,url,databaseId"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    latest = {}
    if gh_run.returncode == 0 and gh_run.stdout.strip():
        try:
            rows = json.loads(gh_run.stdout)
            latest = rows[0] if rows else {}
        except json.JSONDecodeError:
            pass
    deploy_ok = latest.get("conclusion") == "success"
    return {
        "id": "ICL-P1-02",
        "title": "deploy-noos-cloud-workers GHA",
        "ok": bool(has_job_token and has_verify_step and fleet_ok and factory_ok and deploy_ok),
        "workflow_hardening": {
            "job_level_token": has_job_token,
            "pre_deploy_verify": has_verify_step,
        },
        "workers_health": {"fleet": fleet_ok, "factory": factory_ok},
        "latest_gha_run": latest,
    }


def verify_icl_p1_03() -> dict:
    observe = _run_json(
        [sys.executable, str(ROOT / "scripts/observe_sourcea_supabase_v1.py"), "--json"],
        timeout=60,
    )
    truth_rows = (observe.get("truth_log") or {}).get("rows") or []
    cron_fired = any(r.get("event") == "CRON_FIRED" for r in truth_rows)
    autorun = _run_json([sys.executable, str(ROOT / "scripts/autorun_status_v1.py"), "--json"], timeout=180)
    observe_running = False
    spine_fresh = False
    spine_cron = False
    for wf in autorun.get("workflows") or []:
        wid = str(wf.get("id") or wf.get("loop_id") or "")
        if wid == "noos_loop_sourcea_observe":
            observe_running = wf.get("status") == "RUNNING"
        if wid == "sourcea_cloud_queue":
            spine_cron = wf.get("heartbeat_event") == "CRON_FIRED"
            spine_fresh = wf.get("data_freshness") == "FRESH"
    return {
        "id": "ICL-P1-03",
        "title": "SourceA observe loop writes spine",
        "ok": bool(observe.get("ok") and cron_fired and observe_running and spine_fresh and spine_cron),
        "observe_ok": bool(observe.get("ok")),
        "truth_log_cron_fired": cron_fired,
        "latest_queue_head": (truth_rows[0] or {}).get("queue_head") if truth_rows else None,
        "autorun_sourcea_observe_running": observe_running,
        "sourcea_cloud_queue_fresh": spine_fresh,
        "sourcea_cloud_queue_cron_fired": spine_cron,
    }


def verify_icl_p1_04() -> dict:
    nf_script = NOETFIELD_REPO / "scripts/nf_vault_env.py"
    nf_load = NOETFIELD_REPO / "scripts/load_noetfield_vault_env.sh"
    nf_read = NOETFIELD_REPO / "scripts/read_platform_vault.sh"
    canonical_exists = NOETFIELD_LOCAL_ENV.is_file()
    legacy_not_primary = "noetfield-platform-secrets" in (
        nf_script.read_text(encoding="utf-8") if nf_script.is_file() else ""
    )
    vault_keys = 0
    if canonical_exists:
        vault_keys = len(parse_env_file(NOETFIELD_LOCAL_ENV))
    return {
        "id": "ICL-P1-04",
        "title": "Noetfield vault path migration",
        "ok": bool(
            nf_script.is_file()
            and nf_load.is_file()
            and nf_read.is_file()
            and canonical_exists
            and legacy_not_primary
            and vault_keys > 0
        ),
        "noetfield_repo": str(NOETFIELD_REPO),
        "canonical_path": str(NOETFIELD_LOCAL_ENV),
        "product_keys": vault_keys,
    }


def verify(*, write_receipt: bool = False) -> dict:
    steps = {
        "ICL-P1-01": verify_icl_p1_01(),
        "ICL-P1-02": verify_icl_p1_02(),
        "ICL-P1-03": verify_icl_p1_03(),
        "ICL-P1-04": verify_icl_p1_04(),
    }
    ok = all(s.get("ok") for s in steps.values())
    row = {
        "schema": "noos-integrator-icl-p1-closeout-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "phase": "ICL-P1",
        "status": "done" if ok else "degraded",
        "ok": ok,
        "steps": steps,
        "next_phase": "ICL-P2",
    }
    if write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT)
    return row


def main() -> int:
    write = "--write-receipt" in sys.argv
    row = verify(write_receipt=write)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
