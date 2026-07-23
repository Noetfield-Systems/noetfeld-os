#!/usr/bin/env python3
"""Plan motor — dequeue machine_safe upgrade-plane steps and execute verify_cmd.

When the Supabase inbox is empty, cloud_inbox_worker calls try_execute_next_step()
so the 24/7 motor advances the plan SSOT (upgrade planes + manifest) deterministically.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

WIRING = ROOT / "data/noos-plan-motor-wiring-v1.json"
PLANES = ROOT / "data/noos-upgrade-planes-v1.json"
MANIFEST = ROOT / "docs/_NOOS_AGENT/UPGRADE_MANIFEST.json"
STATE_PATH = ROOT / "data/noos-plan-motor-state-v1.json"
PROOF_DIR = ROOT / "receipts/proof"
PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
STEP_COOLDOWN_MINUTES = 30


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return {
            "schema": "noos-plan-motor-state-v1",
            "version": "1.0.0",
            "submitted_steps": {},
            "last_step_id": None,
            "last_cycle_at": None,
        }
    return _load_json(STATE_PATH)


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = utc_now()
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _blocked_ids(manifest: dict[str, Any]) -> set[str]:
    blocked = set((manifest.get("blocked_steps") or {}).keys())
    blocked.update((manifest.get("deferred_to_founder") or {}).keys())
    completed = set(manifest.get("completed_steps") or [])
    in_progress = set(manifest.get("in_progress_steps") or [])
    return blocked | completed | in_progress


def _step_key(plane_id: str, step: dict[str, Any]) -> str:
    return f"{plane_id}:{step.get('id') or step.get('step')}"


def iter_open_steps(*, planes: dict[str, Any], manifest: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any]]]:
    blocked = _blocked_ids(manifest)
    rows: list[tuple[int, int, str, dict[str, Any]]] = []
    for plane in planes.get("planes") or []:
        plane_id = str(plane.get("id") or "")
        for step in plane.get("steps") or []:
            if step.get("status") != "open":
                continue
            verify_cmd = str(step.get("verify_cmd") or "").strip()
            if not verify_cmd:
                continue
            step_id = str(step.get("id") or "")
            backlog_ids = step.get("backlog_ids") or []
            if step_id in blocked or any(bid in blocked for bid in backlog_ids):
                continue
            pri = PRIORITY_RANK.get(str(step.get("priority") or "P2"), 9)
            rows.append((pri, int(step.get("step") or 0), plane_id, step))
    rows.sort(key=lambda row: (row[0], row[1], row[2]))
    for _pri, _ord, plane_id, step in rows:
        yield plane_id, step


def _recently_submitted(state: dict[str, Any], key: str) -> bool:
    row = (state.get("submitted_steps") or {}).get(key)
    if not row:
        return False
    if row.get("last_status") != "ok":
        return False
    at = row.get("last_at")
    if not at:
        return False
    then = datetime.fromisoformat(str(at).replace("Z", "+00:00"))
    age_min = (datetime.now(timezone.utc) - then).total_seconds() / 60.0
    return age_min < STEP_COOLDOWN_MINUTES


def select_next_step(*, planes: dict[str, Any] | None = None, manifest: dict[str, Any] | None = None, state: dict[str, Any] | None = None) -> tuple[str, dict[str, Any]] | None:
    planes_doc = planes or _load_json(PLANES)
    manifest_doc = manifest or _load_json(MANIFEST)
    state_doc = state or load_state()
    for plane_id, step in iter_open_steps(planes=planes_doc, manifest=manifest_doc):
        key = _step_key(plane_id, step)
        if _recently_submitted(state_doc, key):
            continue
        return plane_id, step
    return None


def run_verify_cmd(verify_cmd: str, *, timeout: int = 600) -> dict[str, Any]:
    proc = subprocess.run(
        verify_cmd,
        shell=True,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    return {
        "verify_cmd": verify_cmd,
        "exit_code": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-800:],
    }


def write_step_receipt(*, plane_id: str, step: dict[str, Any], execution: dict[str, Any]) -> str:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    step_id = str(step.get("id") or "unknown")
    path = PROOF_DIR / f"noos-plan-motor-step-{plane_id}-{step_id}-{utc_now().replace(':', '').replace('-', '')}.json"
    body = {
        "schema": "noos-plan-motor-step-receipt-v1",
        "at": utc_now(),
        "plane_id": plane_id,
        "step_id": step_id,
        "action": step.get("action"),
        "success_check": step.get("success_check"),
        "execution": execution,
        "not_a_verdict": "SUBMITTED for independent verification (author != subject)",
        "canon_version": "FOUNDER_CANON_v1+MACHINE_LOOPS_v1",
    }
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return str(path.relative_to(ROOT))


def try_execute_next_step(*, dry_run: bool = False) -> dict[str, Any] | None:
    """Execute one machine_safe plan step. Returns None when no eligible work."""
    if not PLANES.is_file() or not MANIFEST.is_file():
        return None
    state = load_state()
    picked = select_next_step(state=state)
    if not picked:
        return None
    plane_id, step = picked
    key = _step_key(plane_id, step)
    verify_cmd = str(step.get("verify_cmd") or "")
    if dry_run:
        return {
            "ok": True,
            "status": "DRY_RUN",
            "plane_id": plane_id,
            "step_id": step.get("id"),
            "verify_cmd": verify_cmd,
            "action": "plan_motor_dequeue",
        }
    execution = run_verify_cmd(verify_cmd)
    receipt_path = write_step_receipt(plane_id=plane_id, step=step, execution=execution)
    state.setdefault("submitted_steps", {})[key] = {
        "last_at": utc_now(),
        "last_status": "ok" if execution.get("ok") else "fail",
        "verify_cmd": verify_cmd,
        "receipt_path": receipt_path,
    }
    state["last_step_id"] = str(step.get("id"))
    state["last_cycle_at"] = utc_now()
    save_state(state)
    return {
        "ok": bool(execution.get("ok")),
        "status": "completed" if execution.get("ok") else "blocked",
        "item_id": f"PLAN-{plane_id}-{step.get('id')}",
        "upg": (step.get("backlog_ids") or [step.get("id")])[0],
        "action": "plan_motor_executed",
        "plane_id": plane_id,
        "step_id": step.get("id"),
        "execution": execution,
        "receipt_path": receipt_path,
        "plan_motor": True,
    }


def burn_down_summary() -> dict[str, Any]:
    planes = _load_json(PLANES)
    manifest = _load_json(MANIFEST)
    open_count = sum(1 for _ in iter_open_steps(planes=planes, manifest=manifest))
    state = load_state()
    submitted_ok = sum(1 for row in (state.get("submitted_steps") or {}).values() if row.get("last_status") == "ok")
    return {
        "open_machine_safe_steps": open_count,
        "submitted_ok_count": submitted_ok,
        "last_step_id": state.get("last_step_id"),
        "last_cycle_at": state.get("last_cycle_at"),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.summary:
        row = burn_down_summary()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(json.dumps(row))
        return 0

    row = try_execute_next_step(dry_run=args.dry_run)
    if row is None:
        out = {"ok": True, "status": "IDLE_NO_WORK", "idle_reason": "no_open_plan_steps", "plan_motor": True}
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(json.dumps(out))
        return 0
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"plan_motor step={row.get('step_id')} ok={row.get('ok')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
