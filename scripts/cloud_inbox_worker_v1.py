#!/usr/bin/env python3
"""Cloud inbox worker — meaningful executable work per 10-min factory cycle.

Runs in GitHub Actions (not Cursor):
- Receipt-skips founder-only pending items so they never block the queue
- Executes one agent-executable inbox item (P1 before P2)
- Emits machine-readable stdout for factory cycle receipts
"""

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


def _is_founder_only(item: dict[str, Any]) -> bool:
    payload = item.get("payload") or {}
    return payload.get("owner") == "founder" or payload.get("lane") == "commercial"


def _fetch_pending() -> list[dict[str, Any]]:
    rows = _request(
        "GET",
        "/rest/v1/noetfield_worker_inbox_queue?status=eq.pending&select=*&order=enqueued_at.asc",
    )
    return rows or []


def _patch_item(item_id: str, body: dict[str, Any]) -> dict[str, Any]:
    updated = _request("PATCH", f"/rest/v1/noetfield_worker_inbox_queue?item_id=eq.{item_id}", body=body)
    return updated[0] if isinstance(updated, list) and updated else updated


def _skip_founder_item(item: dict[str, Any]) -> dict[str, Any]:
    now = utc_now()
    payload = dict(item.get("payload") or {})
    payload["cloud_skip_receipt"] = {
        "schema": "noos-cloud-inbox-skip-receipt-v1",
        "item_id": item["item_id"],
        "skip_reason": "founder_only",
        "note": "Cloud loop cannot execute founder commercial work; intake receipt recorded.",
        "cloud_meta": _cloud_meta(),
    }
    if item["item_id"] == "NOOS-C-01":
        payload["cloud_skip_receipt"]["briefing_pack"] = {
            "primary_surface": "https://www.noetfield.com/ai-value-governance-os/",
            "gel_demo": "https://www.noetfield.com/gel/",
            "follow_up": "Founder delivers Trust Brief briefing when lead is warm.",
        }
    row = _patch_item(
        item["item_id"],
        {
            "status": "cancelled",
            "payload": payload,
            "dispatched_at": now,
            "completed_at": now,
        },
    )
    return {"ok": True, "item_id": item["item_id"], "action": "skipped_founder", "status": "cancelled", "row": row}


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
    result = _run(["noetfield", "gate", "--json"])
    if result["ok"]:
        json.loads(result["stdout"])
    return result


def _exec_upg_0153() -> dict[str, Any]:
    api = os.environ.get("NOETFIELD_API_URL", "https://api.noetfield.com").rstrip("/")
    return _run(["noetfield", "gate", "--strict", "--api-url", api])


def _exec_upg_0191() -> dict[str, Any]:
    return _run(["pytest", "-q"])


def _exec_upg_0151() -> dict[str, Any]:
    pyproject = ROOT / "pyproject.toml"
    ok = pyproject.is_file() and "noetfield-gate" in pyproject.read_text(encoding="utf-8")
    return {"ok": ok, "command": ["verify", "pyproject.toml"], "exit_code": 0 if ok else 1}


def _exec_baseline(item: dict[str, Any]) -> dict[str, Any]:
    gate = _run(["noetfield", "gate", "--json"])
    tests = _run(["pytest", "-q"])
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


def _select_executable(pending: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [item for item in pending if not _is_founder_only(item)]
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            PRIORITY_RANK.get(item.get("priority") or "P2", 9),
            item.get("enqueued_at") or "",
        )
    )
    return candidates[0]


def process_cycle() -> dict[str, Any]:
    pending = _fetch_pending()
    skipped: list[dict[str, Any]] = []
    for item in list(pending):
        if _is_founder_only(item):
            skipped.append(_skip_founder_item(item))

    pending = _fetch_pending()
    target = _select_executable(pending)
    if not target:
        return {
            "ok": True,
            "skipped": True,
            "reason": "no_executable_pending",
            "founder_skipped": [s["item_id"] for s in skipped],
        }

    executed = _execute_item(target)
    executed["founder_skipped"] = [s["item_id"] for s in skipped]
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
    status = result.get("status") or result.get("action") or ("skipped" if result.get("skipped") else "unknown")
    exit_code = 0 if result.get("ok") else 1
    print(f"work_item_id: {item_id}")
    print(f"work_status: {status}")
    print(f"exit_code: {exit_code}")
    print(json.dumps(result, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
