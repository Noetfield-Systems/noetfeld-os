#!/usr/bin/env python3
"""Read-only autorun status dashboard v1.1 — observe workflows and sandboxes.

SourceA state: Supabase only (truth_log, cycle receipts, heartbeat proxies).
NOOS never reads SourceA repo/disk or dispatches control. phase_reconciler_v1
remains sole authority (registry path only — no SourceA disk probe).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / "data/autorun-workflows-v1.json"
SANDBOXES = ROOT / "data/autorun-sandboxes-v1.json"
DEFAULT_STALE_MINUTES = 30


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


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    text = str(ts).strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def age_minutes(ts: str | None) -> float | None:
    dt = parse_iso(ts)
    if dt is None:
        return None
    return round((datetime.now(timezone.utc) - dt).total_seconds() / 60.0, 2)


def load_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    vals: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        vals[k.strip()] = v.strip().strip("'").strip('"')
    return vals


def supabase_profile_config(profile_name: str, wf_doc: dict[str, Any]) -> tuple[str, str] | None:
    profiles = wf_doc.get("supabase_profiles") or {}
    spec = profiles.get(profile_name) or {}
    env_path = expand(spec.get("env_file", ""))
    vals = load_env_file(env_path)
    url = ""
    for key in spec.get("url_env") or []:
        url = vals.get(key) or os.environ.get(key, "")
        if url:
            break
    secret = ""
    for key in spec.get("key_env") or []:
        secret = vals.get(key) or os.environ.get(key, "")
        if secret:
            break
    if url and secret:
        return url.rstrip("/"), secret
    return None


def supabase_get(
    cfg: tuple[str, str],
    table: str,
    *,
    query: str,
    prefer_count: bool = False,
) -> dict[str, Any]:
    base, key = cfg
    headers: dict[str, str] = {"apikey": key, "Authorization": f"Bearer {key}"}
    if prefer_count:
        headers["Prefer"] = "count=exact"
    req = urllib.request.Request(f"{base}/rest/v1/{table}?{query}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            rows = json.loads(raw) if raw.strip() else []
            total = None
            if prefer_count:
                cr = resp.headers.get("Content-Range", "")
                if "/" in cr:
                    try:
                        total = int(cr.split("/")[-1])
                    except ValueError:
                        total = len(rows)
            return {"ok": True, "status": resp.status, "rows": rows, "count": total}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        return {"ok": False, "status": exc.code, "error": body, "rows": [], "count": None}
    except Exception as exc:
        return {"ok": False, "status": None, "error": str(exc)[:300], "rows": [], "count": None}


def stale_wrap(
    result: dict[str, Any],
    *,
    observed_at: str | None,
    stale_minutes: float,
    source: str,
) -> dict[str, Any]:
    mins = age_minutes(observed_at)
    if mins is not None and mins > stale_minutes:
        result["data_freshness"] = "STALE_DATA"
        result["age_minutes"] = mins
        result["status"] = "BLOCKED_WITH_REASON"
        result["reason"] = "stale_supabase_row"
        result.setdefault("command", result.get("command") or f"Refresh {source} cloud writer; row older than {stale_minutes}m")
        evidence = dict(result.get("evidence") or {})
        evidence.update({"observed_at": observed_at, "age_minutes": mins, "stale_threshold_minutes": stale_minutes})
        result["evidence"] = evidence
    elif mins is not None:
        result["data_freshness"] = "FRESH"
        result["age_minutes"] = mins
    return result


def blocked(reason: str, *, command: str | None = None, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {
        "status": "BLOCKED_WITH_REASON",
        "reason": reason,
        "evidence": evidence or {},
    }
    if command:
        row["command"] = command
    return row


def fetch_truth_log_latest(cfg: tuple[str, str], table: str, event: str | None = None) -> dict[str, Any]:
    params: dict[str, str] = {
        "select": "id,recorded_at,source,event,queue_head,old_queue_head,receipt_id",
        "order": "recorded_at.desc",
        "limit": "1",
    }
    if event:
        params["event"] = f"eq.{event}"
    return supabase_get(cfg, table, query=urllib.parse.urlencode(params))


def fetch_cycle_receipt_latest(
    cfg: tuple[str, str],
    probe: dict[str, Any],
) -> dict[str, Any]:
    table = probe.get("cycle_table", "cycle_receipts")
    params = urllib.parse.urlencode(
        {
            "select": "id,created_at,cycle_id,execution_id,verdict,trigger_source,queue_head_before,queue_head_after,started_at,finished_at",
            "order": "created_at.desc",
            "limit": "5",
        }
    )
    primary = supabase_get(cfg, table, query=params)
    if primary.get("ok") and primary.get("rows"):
        return {"source_table": table, **primary}

    fb_table = probe.get("cycle_fallback_table", "telemetry_logs")
    mem_type = probe.get("cycle_fallback_memory_type", "truth_cycle_receipt")
    fb_params = urllib.parse.urlencode(
        {
            "select": "id,created_at,memory_type,metadata",
            "memory_type": f"eq.{mem_type}",
            "order": "created_at.desc",
            "limit": "20",
        }
    )
    fb = supabase_get(cfg, fb_table, query=fb_params)
    if not fb.get("ok"):
        return {"source_table": fb_table, **fb}

    needle = (probe.get("cycle_id_contains") or "").lower()
    schema = (probe.get("receipt_schema") or "").lower()
    meta_needles = [s.lower() for s in probe.get("metadata_contains") or []]
    exec_needles = [s.lower() for s in probe.get("execution_id_contains") or []]

    matched: list[dict[str, Any]] = []
    for row in fb.get("rows") or []:
        md = row.get("metadata") or {}
        blob = json.dumps(md).lower()
        cycle_id = str(md.get("cycle_id") or "").lower()
        execution_id = str(md.get("execution_id") or "").lower()
        schema_ok = not schema or str(md.get("schema") or "").lower() == schema
        contains_ok = not meta_needles or any(n in blob for n in meta_needles)
        exec_ok = not exec_needles or any(n in execution_id for n in exec_needles)
        cycle_ok = not needle or needle in cycle_id
        if schema_ok and contains_ok and exec_ok and cycle_ok:
            matched.append(
                {
                    "id": row.get("id"),
                    "created_at": row.get("created_at"),
                    "cycle_id": md.get("cycle_id"),
                    "execution_id": md.get("execution_id"),
                    "verdict": md.get("verdict"),
                    "trigger_source": md.get("trigger_source"),
                    "queue_head_before": md.get("queue_head_before"),
                    "queue_head_after": md.get("queue_head_after"),
                    "started_at": md.get("started_at"),
                    "finished_at": md.get("finished_at"),
                    "metadata": md,
                }
            )
    return {"source_table": fb_table, "ok": True, "status": 200, "rows": matched, "count": len(matched), "fallback": True}


def probe_supabase_sourcea_cloud_queue(wf: dict[str, Any], wf_doc: dict[str, Any], stale_minutes: float) -> dict[str, Any]:
    probe = wf["probe"]
    cfg = supabase_profile_config(probe.get("supabase_profile", "portfolio_spine"), wf_doc)
    if not cfg:
        return blocked(
            "supabase_not_configured",
            command=wf.get("blocked_command"),
            evidence={"profile": probe.get("supabase_profile")},
        )

    truth_table = probe.get("truth_log_table", "truth_log")
    heartbeat_events = probe.get("heartbeat_events") or ["CRON_FIRED"]
    observed_at: str | None = None
    heartbeat_event: str | None = None
    queue_head: str | None = None

    for event in heartbeat_events:
        hit = fetch_truth_log_latest(cfg, truth_table, event=event)
        if hit.get("ok") and hit.get("rows"):
            row = hit["rows"][0]
            observed_at = row.get("recorded_at")
            heartbeat_event = row.get("event")
            queue_head = row.get("queue_head")
            break
        if hit.get("status") == 404:
            break

    cycle = fetch_cycle_receipt_latest(cfg, probe)
    cycle_rows = cycle.get("rows") or []
    cycle_row = cycle_rows[0] if cycle_rows else None

    if not observed_at and cycle_row:
        observed_at = cycle_row.get("created_at") or cycle_row.get("finished_at")
        queue_head = cycle_row.get("queue_head_after") or cycle_row.get("queue_head_before")

    if not observed_at:
        if cycle.get("status") == 404 or (not cycle.get("ok") and cycle.get("status") not in (None, 200)):
            return blocked(
                "supabase_truth_tables_missing",
                command=wf.get("blocked_command"),
                evidence={"truth_log": truth_table, "cycle": cycle.get("source_table"), "http": cycle.get("status"), "error": cycle.get("error")},
            )
        return blocked(
            "no_supabase_rows",
            command=wf.get("blocked_command"),
            evidence={"truth_log_table": truth_table, "cycle_source": cycle.get("source_table")},
        )

    before = (cycle_row or {}).get("queue_head_before")
    after = (cycle_row or {}).get("queue_head_after")
    verdict = str((cycle_row or {}).get("verdict") or "").upper()
    trigger = str((cycle_row or {}).get("trigger_source") or "")

    if before and after and before != after:
        status = "RUNNING"
        reason = "queue_advancing"
    elif heartbeat_event in ("JOB_STARTED", "QUEUE_ADVANCED"):
        status = "RUNNING"
        reason = f"truth_log_{heartbeat_event.lower()}"
    elif verdict == "FAIL":
        return stale_wrap(
            {
                "status": "FAILED_WITH_RECEIPT",
                "command": wf.get("blocked_command"),
                "evidence": {
                    "queue_head": queue_head,
                    "cycle_id": (cycle_row or {}).get("cycle_id"),
                    "verdict": verdict,
                    "source_table": cycle.get("source_table"),
                },
            },
            observed_at=observed_at,
            stale_minutes=stale_minutes,
            source="sourcea_cloud_queue",
        )
    elif before and after and before == after and trigger:
        status = "IDLE_NO_WORK"
        reason = "queue_head_unchanged"
    else:
        status = "RUNNING"
        reason = "recent_cloud_cycle_receipt"

    result: dict[str, Any] = {
        "status": status,
        "reason": reason,
        "queue_head": queue_head,
        "heartbeat_event": heartbeat_event,
        "evidence": {
            "observed_at": observed_at,
            "source_table": cycle.get("source_table"),
            "cycle_id": (cycle_row or {}).get("cycle_id"),
            "trigger_source": trigger,
            "truth_log_table": truth_table,
            "fallback": cycle.get("fallback"),
        },
    }
    return stale_wrap(result, observed_at=observed_at, stale_minutes=stale_minutes, source="sourcea_cloud_queue")


def probe_supabase_sourcea_receipt(wf: dict[str, Any], wf_doc: dict[str, Any], stale_minutes: float) -> dict[str, Any]:
    probe = wf["probe"]
    cfg = supabase_profile_config(probe.get("supabase_profile", "portfolio_spine"), wf_doc)
    command = wf.get("verify_command") or wf.get("build_command")
    if not cfg:
        return blocked("supabase_not_configured", command=command, evidence={"profile": probe.get("supabase_profile")})

    cycle = fetch_cycle_receipt_latest(cfg, probe)
    rows = cycle.get("rows") or []
    if not rows:
        if cycle.get("status") == 404:
            return blocked(
                "supabase_receipt_table_missing",
                command=command,
                evidence={"table": cycle.get("source_table"), "schema": probe.get("receipt_schema")},
            )
        return blocked(
            "no_supabase_receipt",
            command=command,
            evidence={"schema": probe.get("receipt_schema"), "source_table": cycle.get("source_table")},
        )

    row = rows[0]
    observed_at = row.get("created_at") or row.get("finished_at")
    verdict = str(row.get("verdict") or (row.get("metadata") or {}).get("verdict") or "").upper()
    md = row.get("metadata") or {}

    pending = 0
    for field in probe.get("pending_metadata_fields") or []:
        val = md.get(field)
        if isinstance(val, int):
            pending = val
            break

    if wf["id"] == "sourcea_recipe_queue_builder":
        if pending > 0:
            base_status = "RUNNING"
        elif verdict == "GREEN":
            base_status = "COMPLETE"
        else:
            base_status = "IDLE_NO_WORK"
    elif verdict == "GREEN":
        base_status = "COMPLETE"
    elif verdict == "FAIL":
        base_status = "FAILED_WITH_RECEIPT"
    else:
        base_status = "IDLE_NO_WORK"

    result: dict[str, Any] = {
        "status": base_status,
        "receipt_schema": probe.get("receipt_schema"),
        "evidence": {
            "observed_at": observed_at,
            "cycle_id": row.get("cycle_id"),
            "verdict": verdict,
            "source_table": cycle.get("source_table"),
            "pending_count": pending,
            "fallback": cycle.get("fallback"),
        },
    }
    if base_status == "FAILED_WITH_RECEIPT":
        result["command"] = command
    return stale_wrap(result, observed_at=observed_at, stale_minutes=stale_minutes, source=wf["id"])


def github_latest_run(workflow_file: str, *, event: str | None = None) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return {"ok": False, "error": "github_credential_unavailable"}
    token = dict(line.split("=", 1) for line in proc.stdout.splitlines() if "=" in line).get("password")
    if not token:
        return {"ok": False, "error": "github_token_missing"}
    repo = "kazemnezhadsina144-dot/noetfeld-os"
    params: dict[str, str] = {"per_page": "5"}
    if event:
        params["event"] = event
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_file}/runs?{query}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            runs = json.loads(resp.read().decode("utf-8")).get("workflow_runs") or []
        if not runs:
            return {"ok": True, "runs": 0, "latest": None}
        latest = runs[0]
        return {
            "ok": True,
            "runs": len(runs),
            "latest": {
                "id": latest.get("id"),
                "event": latest.get("event"),
                "status": latest.get("status"),
                "conclusion": latest.get("conclusion"),
                "created_at": latest.get("created_at"),
            },
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def probe_github_schedule(wf: dict[str, Any]) -> dict[str, Any]:
    workflow_file = (wf.get("probe") or {}).get("github_workflow", "")
    sched = github_latest_run(workflow_file, event="schedule")
    any_run = github_latest_run(workflow_file)
    latest = (sched.get("latest") or any_run.get("latest")) if sched.get("ok") else None
    if not latest:
        return blocked(
            "no_github_runs",
            command=f"PUT .../workflows/enable + wait for schedule on {workflow_file}",
            evidence={"schedule_probe": sched, "any_probe": any_run},
        )
    event = latest.get("event")
    observed_at = latest.get("created_at")
    if event == "schedule" and latest.get("conclusion") == "success":
        status = "COMPLETE"
    elif event == "schedule":
        status = "RUNNING" if latest.get("status") != "completed" else "FAILED_WITH_RECEIPT"
    elif event == "repository_dispatch":
        status = "RUNNING"
    else:
        status = "BLOCKED_WITH_REASON"
    row: dict[str, Any] = {
        "status": status,
        "github_run_id": latest.get("id"),
        "github_event": event,
        "evidence": {"latest": latest, "schedule_count": sched.get("runs")},
    }
    if status == "BLOCKED_WITH_REASON":
        row["reason"] = f"latest_event_not_schedule:{event}"
    return row


def probe_supabase_noos_factory(wf: dict[str, Any], wf_doc: dict[str, Any], stale_minutes: float) -> dict[str, Any]:
    probe = wf["probe"]
    cfg = supabase_profile_config(probe.get("supabase_profile", "noetfield"), wf_doc)
    command = wf.get("run_command")
    table = probe.get("supabase_table", "noetfield_factory_cycle_runs")
    if not cfg:
        return blocked("supabase_not_configured", command=command, evidence={"table": table})

    params = urllib.parse.urlencode(
        {"select": "cycle_number,status,recorded_at,runner_output,exit_code", "order": "recorded_at.desc", "limit": "1"}
    )
    hit = supabase_get(cfg, table, query=params)
    if not hit.get("ok"):
        return blocked(
            "supabase_query_failed",
            command=command,
            evidence={"table": table, "http": hit.get("status"), "error": hit.get("error")},
        )
    rows = hit.get("rows") or []
    if not rows:
        return {
            "status": "IDLE_NO_WORK",
            "reason": "no_factory_cycles",
            "command": command,
            "evidence": {"table": table},
        }

    row = rows[0]
    observed_at = row.get("recorded_at")
    runner = row.get("runner_output") or {}
    cycle_status = str(row.get("status") or "")
    idle_statuses = {s.lower() for s in probe.get("idle_statuses") or ["idle_no_work"]}
    runner_status = str(runner.get("status") or runner.get("cycle_status") or "").lower()

    if runner_status in idle_statuses or str(runner.get("idle_reason") or ""):
        base: dict[str, Any] = {
            "status": "IDLE_NO_WORK",
            "idle_reason": runner.get("idle_reason") or "empty_inbox",
            "evidence": {
                "cycle_number": row.get("cycle_number"),
                "recorded_at": observed_at,
                "cloud_trigger": runner.get("cloud_trigger"),
                "github_event": (runner.get("cloud_meta") or {}).get("github_event"),
            },
        }
    elif cycle_status == "ok":
        base = {
            "status": "RUNNING",
            "cycle_number": row.get("cycle_number"),
            "evidence": {
                "recorded_at": observed_at,
                "exit_code": row.get("exit_code"),
                "cloud_trigger": runner.get("cloud_trigger"),
                "github_event": (runner.get("cloud_meta") or {}).get("github_event"),
            },
        }
    elif cycle_status:
        base = {
            "status": "FAILED_WITH_RECEIPT",
            "command": command,
            "evidence": {"recorded_at": observed_at, "status": cycle_status, "runner_output_keys": sorted(runner.keys())[:12]},
        }
    else:
        base = {"status": "IDLE_NO_WORK", "evidence": {"recorded_at": observed_at}}

    total = supabase_get(
        cfg,
        table,
        query="select=id",
        prefer_count=True,
    )
    base["supabase_cycle_count"] = total.get("count")
    sched_files = probe.get("github_workflows_schedule") or [probe.get("github_workflow")]
    sched_evidence = {}
    for wf_file in sched_files:
        if wf_file:
            sched_evidence[wf_file] = github_latest_run(str(wf_file), event="schedule")
    base["evidence"]["github_schedule"] = sched_evidence
    return stale_wrap(base, observed_at=observed_at, stale_minutes=stale_minutes, source="noos_factory_autorun")


def probe_supabase_noos_inbox(wf: dict[str, Any], wf_doc: dict[str, Any], stale_minutes: float) -> dict[str, Any]:
    probe = wf["probe"]
    cfg = supabase_profile_config(probe.get("supabase_profile", "noetfield"), wf_doc)
    command = wf.get("run_command")
    table = probe.get("supabase_table", "noetfield_worker_inbox_queue")
    founder_status = probe.get("founder_blocked_status", "founder_blocked")
    if not cfg:
        return blocked("supabase_not_configured", command=command, evidence={"table": table})

    pending_hit = supabase_get(
        cfg,
        table,
        query=urllib.parse.urlencode(
            {"select": "item_id,priority,payload,enqueued_at,status", "status": "eq.pending", "order": "priority.asc"}
        ),
    )
    founder_hit = supabase_get(
        cfg,
        table,
        query=urllib.parse.urlencode(
            {
                "select": "item_id,priority,enqueued_at,status",
                "status": f"eq.{founder_status}",
                "order": "enqueued_at.asc",
            }
        ),
    )
    if not pending_hit.get("ok") or not founder_hit.get("ok"):
        return blocked(
            "supabase_query_failed",
            command=command,
            evidence={"http_pending": pending_hit.get("status"), "http_founder": founder_hit.get("status")},
        )

    pending = pending_hit.get("rows") or []
    founder_rows = founder_hit.get("rows") or []
    founder_summary: dict[str, Any] = {
        "count": len(founder_rows),
        "oldest": None,
        "priority": None,
        "age_seconds": None,
        "reason": "founder_decision_required",
    }
    if founder_rows:
        oldest = founder_rows[0]
        founder_summary["oldest"] = oldest.get("item_id")
        founder_summary["priority"] = oldest.get("priority")
        dt = parse_iso(oldest.get("enqueued_at"))
        if dt:
            founder_summary["age_seconds"] = int((datetime.now(timezone.utc) - dt).total_seconds())

    executable = [
        row
        for row in pending
        if (row.get("payload") or {}).get("owner") != "founder"
        and (row.get("payload") or {}).get("lane") != "commercial"
    ]

    latest_cycle = supabase_get(
        cfg,
        table,
        query=urllib.parse.urlencode({"select": "enqueued_at,dispatched_at", "order": "enqueued_at.desc", "limit": "1"}),
    )
    observed_at = None
    if latest_cycle.get("rows"):
        row0 = latest_cycle["rows"][0]
        observed_at = row0.get("dispatched_at") or row0.get("enqueued_at")
    if pending:
        for row in pending:
            ts = row.get("enqueued_at")
            if ts and (observed_at is None or str(ts) > str(observed_at)):
                observed_at = ts

    if executable:
        base: dict[str, Any] = {
            "status": "RUNNING",
            "pending_executable": len(executable),
            "founder_blocked": founder_summary,
            "next_item": executable[0].get("item_id"),
            "evidence": {"pending_total": len(pending)},
        }
    elif pending:
        base = {
            "status": "IDLE_NO_WORK",
            "reason": "only_founder_pending",
            "founder_blocked": founder_summary,
            "evidence": {"pending_founder_only": [row.get("item_id") for row in pending]},
        }
    else:
        base = {
            "status": "IDLE_NO_WORK",
            "reason": "empty_inbox",
            "founder_blocked": founder_summary,
            "evidence": {"pending_total": 0},
        }
    return stale_wrap(base, observed_at=observed_at, stale_minutes=stale_minutes, source="noos_worker_inbox")


def probe_url_sweep_readonly(wf: dict[str, Any]) -> dict[str, Any]:
    probe = wf["probe"]
    urls = probe.get("urls") or []
    if not urls:
        return blocked("no_urls_configured", evidence={})

    fails: list[str] = []
    oks: list[str] = []
    for item in urls:
        name = item.get("name", item.get("url", "?"))
        url = item.get("url", "")
        if not url:
            fails.append(f"FAIL {name} (missing url)")
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "noos-autorun-status/1.1", "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                code = resp.status
            if 200 <= code < 300:
                oks.append(f"OK {name} ({code})")
            else:
                fails.append(f"FAIL {name} ({code})")
        except Exception as exc:
            fails.append(f"FAIL {name} ({str(exc)[:80]})")

    if fails:
        return {
            "status": "FAILED_WITH_RECEIPT",
            "command": "make urls",
            "evidence": {"fails": fails[:8], "oks": oks[:8], "checked": len(urls)},
        }
    return {"status": "COMPLETE", "evidence": {"checked": len(urls), "oks": oks}}


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


def reconciler_authority_check(wf_doc: dict[str, Any]) -> dict[str, Any]:
    sole_path = (wf_doc.get("control_authority") or {}).get("sole_reconciler")
    noos_hits = list(ROOT.glob("**/phase_reconciler_v1.py"))
    dashboard_supervisors = list(ROOT.glob("**/autorun_supervisor*.py"))
    duplicate = bool(noos_hits or dashboard_supervisors)
    return {
        "sole_authority_path": sole_path,
        "noos_reconciler_copies": len(noos_hits),
        "noos_supervisor_scripts": len(dashboard_supervisors),
        "result": "DUPLICATE" if duplicate else "ONE",
        "read_only_dashboard": True,
        "sourcea_disk_checked": False,
    }


PROBES = {
    "supabase_sourcea_cloud_queue": probe_supabase_sourcea_cloud_queue,
    "supabase_sourcea_receipt": probe_supabase_sourcea_receipt,
    "supabase_noos_factory": probe_supabase_noos_factory,
    "supabase_noos_inbox": probe_supabase_noos_inbox,
    "url_sweep_readonly": probe_url_sweep_readonly,
    "github_schedule_probe": probe_github_schedule,
}


def apply_triage(row: dict[str, Any], *, triage: bool, dirty_total: int, threshold: int) -> dict[str, Any]:
    if triage and row.get("status") not in ("FAILED_WITH_RECEIPT",):
        row = dict(row)
        row["status"] = "TRIAGE_REQUIRED"
        row["triage_reason"] = f"dirty_total={dirty_total} > {threshold}"
    return row


def build_dashboard() -> dict[str, Any]:
    wf_doc = read_json(WORKFLOWS)
    sb_doc = read_json(SANDBOXES)
    threshold = int(sb_doc.get("triage_threshold_dirty_total") or 200)
    stale_minutes = float(wf_doc.get("stale_threshold_minutes") or DEFAULT_STALE_MINUTES)

    sandbox_rows = []
    dirty_total = 0
    for sb in sb_doc.get("sandboxes") or []:
        path = expand(sb["path"]) if sb["path"] != "." else ROOT
        counts = sb.get("counts_toward_dirty_total", sb.get("git", False))
        count = dirty_count(path) if counts and sb.get("git") and path.is_dir() else 0
        if counts:
            dirty_total += count
        sandbox_rows.append(
            {
                "id": sb["id"],
                "path": str(path),
                "dirty_count": count if counts else None,
                "counts_toward_dirty_total": bool(counts),
                "observe_only": sb.get("observe_only", False),
                "dirty_source": sb.get("dirty_source", "git" if sb.get("git") else "none"),
            }
        )

    triage = dirty_total > threshold
    workflows_out = []
    for wf in wf_doc.get("workflows") or []:
        probe_type = (wf.get("probe") or {}).get("type")
        fn = PROBES.get(probe_type or "")
        row: dict[str, Any] = {"id": wf["id"], "title": wf["title"], "plane": wf.get("plane")}
        if not fn:
            row.update(
                blocked(
                    f"unknown_probe_type:{probe_type}",
                    evidence={"probe_type": probe_type},
                )
            )
        else:
            try:
                if probe_type == "url_sweep_readonly":
                    row.update(fn(wf))
                elif probe_type == "github_schedule_probe":
                    row.update(fn(wf))
                else:
                    row.update(fn(wf, wf_doc, stale_minutes))
            except Exception as exc:
                row.update(blocked(str(exc)[:200], evidence={"probe_type": probe_type}))
        row = apply_triage(row, triage=triage, dirty_total=dirty_total, threshold=threshold)
        workflows_out.append(row)

    authority = reconciler_authority_check(wf_doc)
    registered_workflows = [wf["id"] for wf in wf_doc.get("workflows") or []]
    registered_sandboxes = [sb["id"] for sb in sb_doc.get("sandboxes") or []]

    return {
        "schema": "autorun-status-dashboard-v1.2",
        "read_only": True,
        "generated_at": utc_now(),
        "dirty_total": dirty_total,
        "triage_threshold": threshold,
        "triage_required": triage,
        "stale_threshold_minutes": stale_minutes,
        "reconciler_authority": authority,
        "registered_workflows": registered_workflows,
        "registered_sandboxes": registered_sandboxes,
        "workflows": workflows_out,
        "sandboxes": sandbox_rows,
    }


def main() -> int:
    dash = build_dashboard()
    print(json.dumps(dash, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
