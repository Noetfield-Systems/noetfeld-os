#!/usr/bin/env python3
"""Read-only autorun status dashboard v1 — observe workflows and sandboxes."""

from __future__ import annotations

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
WORKFLOWS = ROOT / "data/autorun-workflows-v1.json"
SANDBOXES = ROOT / "data/autorun-sandboxes-v1.json"
SOURCEA_ROOT = Path.home() / "Desktop/SourceA"
SINA = Path.home() / ".sina"
RECONCILER = SOURCEA_ROOT / "scripts/phase_reconciler_v1.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def expand(path: str) -> Path:
    return Path(os.path.expanduser(path)).resolve()


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def http_json(url: str, *, timeout: float = 12.0) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "noos-autorun-status/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            body = json.loads(raw) if raw.strip() else {}
            return {"ok": resp.status == 200, "status": resp.status, "body": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:300], "url": url}


def supabase_config() -> tuple[str, str] | None:
    url = os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return url.rstrip("/"), key
    env_path = Path.home() / ".sourcea-secrets/noetfield.env"
    if not env_path.is_file():
        return None
    vals: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        vals[k] = v.strip().strip("'").strip('"')
    url = vals.get("NOETFIELD_SUPABASE_URL") or vals.get("SUPABASE_URL")
    key = vals.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or vals.get("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        return url.rstrip("/"), key
    return None


def supabase_count(table: str, *, query: str = "select=id") -> int | None:
    cfg = supabase_config()
    if not cfg:
        return None
    base, key = cfg
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "count=exact"}
    req = urllib.request.Request(f"{base}/rest/v1/{table}?{query}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return int(resp.headers.get("Content-Range", "*/0").split("/")[-1])
    except Exception:
        return None


def supabase_rows(table: str, *, query: str) -> list[dict[str, Any]] | None:
    cfg = supabase_config()
    if not cfg:
        return None
    base, key = cfg
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    req = urllib.request.Request(f"{base}/rest/v1/{table}?{query}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def dirty_count(path: Path) -> int:
    if not path.is_dir():
        return 0
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        if proc.returncode != 0:
            return 0
        return len([line for line in proc.stdout.splitlines() if line.strip()])
    except Exception:
        return 0


def reconciler_authority_check() -> dict[str, Any]:
    noos_hits = list(ROOT.glob("**/phase_reconciler_v1.py"))
    sourcea_ok = RECONCILER.is_file()
    dashboard_supervisors = list(ROOT.glob("**/autorun_supervisor*.py"))
    return {
        "sole_authority_path": str(RECONCILER) if sourcea_ok else None,
        "noos_reconciler_copies": len(noos_hits),
        "noos_supervisor_scripts": len(dashboard_supervisors),
        "result": "ONE" if sourcea_ok and not noos_hits and not dashboard_supervisors else "DUPLICATE",
        "read_only_dashboard": True,
    }


def probe_sourcea_cloud_queue(wf: dict[str, Any]) -> dict[str, Any]:
    probe = wf["probe"]
    base = os.environ.get(probe.get("url_env", ""), probe["url_default"]).rstrip("/")
    if base.endswith("/api/cloud-forge-run/queue/v1"):
        url = base
    else:
        url = f"{base}{probe.get('url_suffix', '/api/cloud-forge-run/queue/v1')}"
    row = http_json(url)
    if not row.get("ok"):
        return {
            "status": "BLOCKED_WITH_REASON",
            "reason": row.get("error") or f"HTTP {row.get('status')}",
            "command": wf.get("blocked_command", f"curl -fsS {url}"),
            "evidence": {"url": url, "probe": row},
        }
    body = row.get("body") or {}
    pending = 0
    for field in probe.get("pending_fields") or []:
        if isinstance(body.get(field), int):
            pending = int(body[field])
            break
    head = None
    for field in probe.get("head_fields") or []:
        if body.get(field):
            head = body[field]
            break
    if pending > 0 or (head and body.get("auto_proceed_ready")):
        return {
            "status": "RUNNING",
            "queue_head": head,
            "pending_count": pending,
            "evidence": {"url": url, "body_keys": sorted(body.keys())[:12]},
        }
    return {
        "status": "IDLE_NO_WORK",
        "queue_head": head,
        "pending_count": pending,
        "evidence": {"url": url},
    }


def probe_receipt(wf: dict[str, Any]) -> dict[str, Any]:
    path = expand(wf["probe"]["receipt_path"])
    receipt = read_json(path)
    if not receipt:
        return {
            "status": "IDLE_NO_WORK",
            "reason": "no_receipt_on_disk",
            "command": wf.get("verify_command"),
            "evidence": {"path": str(path), "exists": False},
        }
    if receipt.get(wf["probe"].get("ok_field", "ok")):
        return {"status": "COMPLETE", "receipt_path": str(path), "at": receipt.get("at"), "evidence": {"ok": True}}
    return {
        "status": "FAILED_WITH_RECEIPT",
        "receipt_path": str(path),
        "at": receipt.get("at"),
        "command": wf.get("verify_command"),
        "evidence": receipt,
    }


def probe_queue_file(wf: dict[str, Any]) -> dict[str, Any]:
    path = expand(wf["probe"]["queue_path"])
    doc = read_json(path)
    items = doc.get(wf["probe"].get("items_field", "items")) or []
    pending_statuses = set(wf["probe"].get("pending_statuses") or ["pending"])
    pending = [item for item in items if item.get("status") in pending_statuses]
    if not items:
        return {"status": "IDLE_NO_WORK", "evidence": {"path": str(path), "total": 0}}
    if pending:
        return {
            "status": "RUNNING",
            "pending_count": len(pending),
            "total": len(items),
            "evidence": {"path": str(path), "proven_live_count": doc.get("proven_live_count")},
        }
    return {
        "status": "COMPLETE",
        "total": len(items),
        "evidence": {"path": str(path), "generated_at": doc.get("generated_at")},
    }


def probe_noos_factory(wf: dict[str, Any]) -> dict[str, Any]:
    runtime = ROOT / wf["probe"]["runtime_state"]
    state = read_json(runtime)
    cycles = supabase_count(wf["probe"]["supabase_table"])
    if state.get("last_cycle_result", {}).get("status") == "ok":
        return {
            "status": "RUNNING",
            "factory_id": state.get("factory_id"),
            "supabase_cycle_count": cycles,
            "evidence": {"runtime_state": str(runtime), "last_heartbeat": state.get("last_heartbeat_at")},
        }
    if cycles is not None and cycles > 0:
        return {
            "status": "RUNNING",
            "supabase_cycle_count": cycles,
            "evidence": {"runtime_state_exists": runtime.is_file()},
        }
    if cycles is None:
        return {
            "status": "BLOCKED_WITH_REASON",
            "reason": "supabase_not_configured",
            "command": wf.get("run_command"),
            "evidence": {"runtime_state": str(runtime)},
        }
    return {
        "status": "IDLE_NO_WORK",
        "supabase_cycle_count": cycles,
        "command": wf.get("run_command"),
        "evidence": {"runtime_state_exists": runtime.is_file()},
    }


def probe_noos_inbox(wf: dict[str, Any]) -> dict[str, Any]:
    pending = supabase_rows(
        wf["probe"]["supabase_table"],
        query="status=eq.pending&select=item_id,priority,payload&order=priority.asc",
    )
    founder_blocked = supabase_count(
        wf["probe"]["supabase_table"],
        query=f"status=eq.{wf['probe'].get('founder_blocked_status', 'founder_blocked')}&select=id",
    )
    if pending is None:
        return {
            "status": "BLOCKED_WITH_REASON",
            "reason": "supabase_not_configured",
            "command": wf.get("run_command"),
            "evidence": {},
        }
    executable = [
        row
        for row in pending
        if (row.get("payload") or {}).get("owner") != "founder"
        and (row.get("payload") or {}).get("lane") != "commercial"
    ]
    if executable:
        return {
            "status": "RUNNING",
            "pending_executable": len(executable),
            "founder_blocked_count": founder_blocked or 0,
            "next_item": executable[0].get("item_id"),
            "evidence": {"pending_total": len(pending)},
        }
    if pending:
        return {
            "status": "IDLE_NO_WORK",
            "reason": "only_founder_pending",
            "founder_blocked_count": founder_blocked or 0,
            "evidence": {"pending_founder_only": [row.get("item_id") for row in pending]},
        }
    return {
        "status": "IDLE_NO_WORK",
        "founder_blocked_count": founder_blocked or 0,
        "evidence": {"pending_total": 0},
    }


def probe_url_sweep(wf: dict[str, Any]) -> dict[str, Any]:
    script = ROOT / wf["probe"]["script"]
    if not script.is_file():
        return {
            "status": "BLOCKED_WITH_REASON",
            "reason": "sweep_script_missing",
            "command": f"bash {script}",
            "evidence": {"path": str(script)},
        }
    proc = subprocess.run(["bash", str(script)], cwd=ROOT, capture_output=True, text=True, check=False, timeout=60)
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    fails = [line for line in lines if line.startswith("FAIL")]
    if proc.returncode == 0 and not fails:
        return {"status": "COMPLETE", "evidence": {"checked": len(lines), "script": str(script)}}
    if fails:
        return {
            "status": "FAILED_WITH_RECEIPT",
            "command": f"bash {script}",
            "evidence": {"fails": fails[:6], "stdout_tail": lines[-6:]},
        }
    return {
        "status": "BLOCKED_WITH_REASON",
        "reason": proc.stderr.strip()[:200] or "sweep_error",
        "command": f"bash {script}",
        "evidence": {"exit_code": proc.returncode},
    }


PROBES = {
    "http_json": probe_sourcea_cloud_queue,
    "receipt_json": probe_receipt,
    "queue_file": probe_queue_file,
    "noos_factory": probe_noos_factory,
    "noos_inbox": probe_noos_inbox,
    "url_sweep": probe_url_sweep,
}


def build_dashboard() -> dict[str, Any]:
    wf_doc = read_json(WORKFLOWS)
    sb_doc = read_json(SANDBOXES)
    threshold = int(sb_doc.get("triage_threshold_dirty_total") or 200)

    sandbox_rows = []
    dirty_total = 0
    for sb in sb_doc.get("sandboxes") or []:
        path = expand(sb["path"]) if sb["path"] != "." else ROOT
        count = dirty_count(path) if sb.get("git") and path.is_dir() else 0
        dirty_total += count
        sandbox_rows.append({"id": sb["id"], "path": str(path), "dirty_count": count, "observe_only": sb.get("observe_only", False)})

    triage = dirty_total > threshold
    workflows_out = []
    for wf in wf_doc.get("workflows") or []:
        probe_type = (wf.get("probe") or {}).get("type")
        fn = PROBES.get(probe_type or "")
        row = {"id": wf["id"], "title": wf["title"], "plane": wf.get("plane")}
        if not fn:
            row.update(
                {
                    "status": "BLOCKED_WITH_REASON",
                    "reason": f"unknown_probe_type:{probe_type}",
                    "evidence": {},
                }
            )
        else:
            try:
                row.update(fn(wf))
            except Exception as exc:
                row.update(
                    {
                        "status": "BLOCKED_WITH_REASON",
                        "reason": str(exc)[:200],
                        "evidence": {"probe_type": probe_type},
                    }
                )
        if triage and row.get("status") not in ("FAILED_WITH_RECEIPT",):
            row["status"] = "TRIAGE_REQUIRED"
            row["triage_reason"] = f"dirty_total={dirty_total} > {threshold}"
        workflows_out.append(row)

    authority = reconciler_authority_check()
    return {
        "schema": "autorun-status-dashboard-v1",
        "read_only": True,
        "generated_at": utc_now(),
        "dirty_total": dirty_total,
        "triage_threshold": threshold,
        "triage_required": triage,
        "reconciler_authority": authority,
        "workflows": workflows_out,
        "sandboxes": sandbox_rows,
    }


def main() -> int:
    dash = build_dashboard()
    print(json.dumps(dash, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
