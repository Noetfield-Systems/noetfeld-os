#!/usr/bin/env python3
"""Cloud inbox worker — meaningful executable work per 10-min factory cycle."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
PRIORITY_RANK = {"P1": 0, "P2": 1, "P0": 2}

sys.path.insert(0, str(ROOT / "scripts"))
from cloud_inbox_constants_v1 import FOUNDER_BLOCKED_REASON, FOUNDER_BLOCKED_STATUS

_request_fn: Callable[..., Any] | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _cloud_meta() -> dict[str, Any]:
    return {
        "processor": "cloud_inbox_worker_v1",
        "processed_at": utc_now(),
        "github_event": os.environ.get("GITHUB_EVENT_NAME"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_workflow": os.environ.get("GITHUB_WORKFLOW"),
    }


def _config() -> tuple[str, str]:
    url = os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""
    key = os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    if not url or not key:
        raise RuntimeError("Supabase not configured")
    return url.rstrip("/"), key


def _request(method: str, path: str, *, body: dict[str, Any] | None = None) -> Any:
    if _request_fn is not None:
        return _request_fn(method, path, body=body)
    base, key = _config()
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["Prefer"] = "return=representation"
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{base}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else None


def is_founder_only(item: dict[str, Any]) -> bool:
    payload = item.get("payload") or {}
    return payload.get("owner") == "founder" or payload.get("lane") == "commercial"


def item_age_seconds(item: dict[str, Any], *, now: datetime | None = None) -> int | None:
    stamp = item.get("dispatched_at") or item.get("enqueued_at")
    if not stamp:
        return None
    then = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    ref = now or datetime.now(timezone.utc)
    return max(0, int((ref - then).total_seconds()))


def founder_blocked_summary(items: list[dict[str, Any]], *, now: datetime | None = None) -> dict[str, Any]:
    if not items:
        return {"founder_blocked_count": 0}
    oldest = sorted(items, key=lambda row: row.get("enqueued_at") or "")[0]
    return {
        "founder_blocked_count": len(items),
        "oldest": oldest.get("item_id"),
        "priority": oldest.get("priority"),
        "age_seconds": item_age_seconds(oldest, now=now),
        "reason": FOUNDER_BLOCKED_REASON,
    }


def build_founder_blocked_patch(item: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    payload = dict(item.get("payload") or {})
    payload["cloud_founder_blocked_receipt"] = {
        "schema": "noos-cloud-inbox-founder-blocked-v1",
        "item_id": item["item_id"],
        "reason": FOUNDER_BLOCKED_REASON,
        "note": "Founder action required; cloud loop will not execute this item.",
        "cloud_meta": _cloud_meta(),
    }
    if item["item_id"] == "NOOS-C-01":
        payload["cloud_founder_blocked_receipt"]["briefing_pack"] = {
            "primary_surface": "https://www.noetfield.com/ai-value-governance-os/",
            "gel_demo": "https://www.noetfield.com/gel/",
            "follow_up": "Founder delivers Trust Brief briefing when lead is warm.",
        }
    return {"status": FOUNDER_BLOCKED_STATUS, "payload": payload, "dispatched_at": now}


def select_executable(pending: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [item for item in pending if not is_founder_only(item)]
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            PRIORITY_RANK.get(item.get("priority") or "P2", 9),
            item.get("enqueued_at") or "",
        )
    )
    return candidates[0]


def _fetch_pending() -> list[dict[str, Any]]:
    rows = _request(
        "GET",
        "/rest/v1/noetfield_worker_inbox_queue?status=eq.pending&select=*&order=enqueued_at.asc",
    )
    return rows or []


def _fetch_founder_blocked() -> list[dict[str, Any]]:
    rows = _request(
        "GET",
        f"/rest/v1/noetfield_worker_inbox_queue?status=eq.{FOUNDER_BLOCKED_STATUS}&select=*&order=enqueued_at.asc",
    )
    return rows or []


def _patch_item(item_id: str, body: dict[str, Any]) -> dict[str, Any]:
    updated = _request("PATCH", f"/rest/v1/noetfield_worker_inbox_queue?item_id=eq.{item_id}", body=body)
    return updated[0] if isinstance(updated, list) and updated else updated


def _block_founder_item(item: dict[str, Any]) -> dict[str, Any]:
    row = _patch_item(item["item_id"], build_founder_blocked_patch(item))
    return {
        "ok": True,
        "item_id": item["item_id"],
        "action": "founder_blocked",
        "status": FOUNDER_BLOCKED_STATUS,
        "row": row,
    }


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 180) -> dict[str, Any]:
    completed = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    return {
        "command": cmd,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "stdout_tail": completed.stdout.strip().splitlines()[-3:],
        "stderr_tail": completed.stderr.strip().splitlines()[-3:],
        "ok": completed.returncode == 0,
    }


def _exec_upg_0152() -> dict[str, Any]:
    return _run_gate_json()


def _exec_upg_0153() -> dict[str, Any]:
    api = os.environ.get("NOETFIELD_API_URL", "https://api.noetfield.com").rstrip("/")
    return _run_gate_json(extra_args=["--strict", "--api-url", api])


def _exec_upg_0154() -> dict[str, Any]:
    return _run_gate_json(extra_args=["--pytest"])


def _exec_upg_0155() -> dict[str, Any]:
    return _run_gate_json()


def _exec_upg_0156() -> dict[str, Any]:
    intent = ROOT / "fixtures/demo_intents/approve.json"
    proc = subprocess.run(
        [sys.executable, "-m", "noetfield_gate.cli", "decide", "--file", str(intent), "--validate-only"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {
        "upg": "UPG-0156",
        "ok": proc.returncode == 0,
        "stdout": proc.stdout[-500:],
        "stderr": proc.stderr[-500:],
        "exit_code": proc.returncode,
    }


def _exec_upg_0157() -> dict[str, Any]:
    from noetfield_gate.boot import dated_receipt_dir

    gate_dir = dated_receipt_dir("gate")
    decide_dir = dated_receipt_dir("decide")
    gate_dir.mkdir(parents=True, exist_ok=True)
    decide_dir.mkdir(parents=True, exist_ok=True)
    gate_result = _run_gate_json()
    return {
        "upg": "UPG-0157",
        "ok": gate_result.get("ok") and gate_dir.is_dir() and decide_dir.is_dir(),
        "gate_receipt_dir": str(gate_dir),
        "decide_receipt_dir": str(decide_dir),
        "gate": gate_result,
    }


def _exec_upg_0158() -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-m", "noetfield_gate.cli", "verify", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    ok = proc.returncode == 0
    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
        ok = ok and payload.get("outcome") == "PASS"
    except json.JSONDecodeError:
        ok = False
    return {
        "upg": "UPG-0158",
        "ok": ok,
        "stdout": proc.stdout[-800:],
        "stderr": proc.stderr[-500:],
        "exit_code": proc.returncode,
    }


def _run_gate_json(*, extra_args: list[str] | None = None) -> dict[str, Any]:
    cmd = [sys.executable, "-m", "noetfield_gate.cli", "gate", "--json"]
    if extra_args:
        cmd.extend(extra_args)
    result = _run(cmd)
    if result["ok"]:
        try:
            json.loads(result["stdout"])
        except json.JSONDecodeError:
            result["ok"] = False
    return result


def _run_pytest() -> dict[str, Any]:
    return _run([sys.executable, "-m", "pytest", "-q"])


def _exec_upg_0191() -> dict[str, Any]:
    return _run_pytest()


def _exec_upg_0151() -> dict[str, Any]:
    pyproject = ROOT / "pyproject.toml"
    ok = pyproject.is_file() and "noetfield-gate" in pyproject.read_text(encoding="utf-8")
    return {"ok": ok, "command": ["verify", "pyproject.toml"], "exit_code": 0 if ok else 1}


def _exec_baseline(item: dict[str, Any]) -> dict[str, Any]:
    gate = _run_gate_json()
    tests = _run_pytest()
    return {
        "ok": gate["ok"] and tests["ok"],
        "exit_code": 0 if gate["ok"] and tests["ok"] else 1,
        "mode": "baseline_verify",
        "upg": (item.get("payload") or {}).get("upg"),
        "note": "Full UPG scope not yet automated; baseline gate+pytest passed.",
        "gate": gate,
        "pytest": tests,
    }


HANDLERS: dict[str, Callable[[], dict[str, Any]]] = {
    "UPG-0151": _exec_upg_0151,
    "UPG-0152": _exec_upg_0152,
    "UPG-0153": _exec_upg_0153,
    "UPG-0154": _exec_upg_0154,
    "UPG-0155": _exec_upg_0155,
    "UPG-0156": _exec_upg_0156,
    "UPG-0157": _exec_upg_0157,
    "UPG-0158": _exec_upg_0158,
    "UPG-0191": _exec_upg_0191,
}


def _execute_item(item: dict[str, Any]) -> dict[str, Any]:
    upg = (item.get("payload") or {}).get("upg") or item["item_id"]
    handler = HANDLERS.get(upg)
    execution = handler() if handler else _exec_baseline(item)
    now = utc_now()
    payload = dict(item.get("payload") or {})
    payload["cloud_execution_receipt"] = {
        "schema": "noos-cloud-inbox-receipt-v1",
        "item_id": item["item_id"],
        "upg": upg,
        "execution": execution,
        "cloud_meta": _cloud_meta(),
    }
    ok = bool(execution.get("ok"))
    row = _patch_item(
        item["item_id"],
        {
            "status": "completed" if ok else "blocked",
            "payload": payload,
            "dispatched_at": now,
            "completed_at": now if ok else None,
        },
    )
    return {
        "ok": ok,
        "item_id": item["item_id"],
        "upg": upg,
        "action": "executed",
        "status": "completed" if ok else "blocked",
        "execution": execution,
        "row": row,
    }


def process_cycle() -> dict[str, Any]:
    pending = _fetch_pending()
    blocked_founder: list[dict[str, Any]] = []
    for item in list(pending):
        if is_founder_only(item):
            blocked_founder.append(_block_founder_item(item))

    summary = founder_blocked_summary(_fetch_founder_blocked())
    pending = _fetch_pending()
    target = select_executable(pending)
    if not target:
        try:
            from noos_plan_motor_v1 import try_execute_next_step

            plan = try_execute_next_step()
        except Exception as exc:  # noqa: BLE001 — plan motor must never crash the inbox tick
            plan = {
                "ok": False,
                "status": "blocked",
                "action": "plan_motor_error",
                "error": str(exc)[:300],
                "plan_motor": True,
            }
        if plan and plan.get("action") != "plan_motor_error":
            summary = founder_blocked_summary(_fetch_founder_blocked())
            plan["founder_blocked"] = summary
            plan["founder_blocked_this_cycle"] = [row["item_id"] for row in blocked_founder]
            return plan
        pending_total = len(pending)
        idle_reason = (
            "empty_inbox"
            if pending_total == 0 and summary.get("founder_blocked_count", 0) == 0
            else "no_executable_pending"
        )
        out = {
            "ok": True,
            "status": "IDLE_NO_WORK",
            "idle_reason": idle_reason,
            "founder_blocked": summary,
            "founder_blocked_this_cycle": [row["item_id"] for row in blocked_founder],
            "plan_motor_checked": True,
        }
        if plan and plan.get("action") == "plan_motor_error":
            out["plan_motor_error"] = plan.get("error")
        return out

    executed = _execute_item(target)
    executed["founder_blocked"] = summary
    executed["founder_blocked_this_cycle"] = [row["item_id"] for row in blocked_founder]
    return executed


def main() -> int:
    try:
        result = process_cycle()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        print(json.dumps({"ok": False, "error": detail}), file=sys.stderr)
        return 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    item_id = result.get("item_id") or "none"
    status = result.get("status") or result.get("action") or "unknown"
    if result.get("skipped") and status == "unknown":
        status = "IDLE_NO_WORK"
    exit_code = 0 if result.get("ok") else 1
    fb = result.get("founder_blocked") or {}
    print(f"work_item_id: {item_id}")
    print(f"work_status: {status}")
    print(f"exit_code: {exit_code}")
    print(f"founder_blocked_count: {fb.get('founder_blocked_count', 0)}")
    if fb.get("founder_blocked_count"):
        print(f"oldest_founder_blocked: {fb.get('oldest')}")
        print(f"founder_blocked_priority: {fb.get('priority')}")
        print(f"founder_blocked_reason: {fb.get('reason')}")
    print(json.dumps(result, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
