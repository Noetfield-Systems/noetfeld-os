#!/usr/bin/env python3
"""NOOS parallel agent conflict check v1 — detect duplicate territory or mutex violations.

Reads data/noos-parallel-agent-registry-v1.json + integrator runtime state.
Emits a receipt; exit 1 on conflict (L-P1/L-P2).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/noos-parallel-agent-registry-v1.json"
INTEGRATOR_STATE = ROOT / ".noos-runtime/integrator/noos-integrator-state-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    text = str(ts).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError:
        return None


def active_claims(state: dict[str, Any], *, stale_minutes: int = 30) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    out: list[dict[str, Any]] = []
    for task in state.get("tasks") or []:
        if not isinstance(task, dict):
            continue
        status = str(task.get("status") or "")
        if status not in ("claimed", "in_progress"):
            continue
        hb = _parse_iso(str(task.get("heartbeat_at") or task.get("claimed_at") or ""))
        if hb and (now - hb).total_seconds() > stale_minutes * 60:
            continue
        out.append(task)
    return out


def scope_overlap(a: list[str], b: list[str]) -> list[str]:
    a_norm = [str(p).strip().lstrip("./") for p in a if str(p).strip()]
    b_norm = [str(p).strip().lstrip("./") for p in b if str(p).strip()]
    hits: list[str] = []
    for pa in a_norm:
        for pb in b_norm:
            if pa == pb or pa.startswith(pb.rstrip("/") + "/") or pb.startswith(pa.rstrip("/") + "/"):
                hits.append(pa if pa == pb else f"{pa}∩{pb}")
    return sorted(set(hits))


def check_conflicts(*, registry: dict[str, Any], integrator: dict[str, Any]) -> dict[str, Any]:
    workers = registry.get("workers") if isinstance(registry.get("workers"), list) else []
    mutex_groups = registry.get("mutex_groups") if isinstance(registry.get("mutex_groups"), list) else []
    worker_by_id = {str(w.get("worker_id")): w for w in workers if isinstance(w, dict) and w.get("worker_id")}

    claims = active_claims(integrator)
    conflicts: list[dict[str, Any]] = []

    for i, left in enumerate(claims):
        left_scope = left.get("scope_files") if isinstance(left.get("scope_files"), list) else []
        for right in claims[i + 1 :]:
            right_scope = right.get("scope_files") if isinstance(right.get("scope_files"), list) else []
            overlap = scope_overlap(left_scope, right_scope)
            if overlap:
                conflicts.append(
                    {
                        "kind": "integrator_scope_overlap",
                        "tasks": [left.get("task_id"), right.get("task_id")],
                        "agents": [left.get("agent_id"), right.get("agent_id")],
                        "overlap": overlap,
                    }
                )

    active_by_mutex: dict[str, list[str]] = {}
    for claim in claims:
        agent = str(claim.get("agent_id") or "")
        for worker in workers:
            if not isinstance(worker, dict):
                continue
            groups = worker.get("mutex_groups") if isinstance(worker.get("mutex_groups"), list) else []
            wid = str(worker.get("worker_id") or "")
            if agent and agent in wid:
                for g in groups:
                    active_by_mutex.setdefault(str(g), []).append(wid)
        task_id = str(claim.get("task_id") or "")
        for group in mutex_groups:
            if not isinstance(group, dict):
                continue
            gid = str(group.get("id") or "")
            owners = group.get("owners") if isinstance(group.get("owners"), list) else []
            if task_id and any(o in task_id for o in owners):
                active_by_mutex.setdefault(gid, []).append(task_id)

    for gid, actors in active_by_mutex.items():
        mutating = [a for a in actors if a]
        if len(mutating) > 1:
            group_spec = next((g for g in mutex_groups if isinstance(g, dict) and g.get("id") == gid), {})
            conflicts.append(
                {
                    "kind": "mutex_group_violation",
                    "mutex_group": gid,
                    "rule": group_spec.get("rule"),
                    "actors": mutating,
                }
            )

    duplicate_territory: dict[str, list[str]] = {}
    for claim in claims:
        task_kinds = [str(claim.get("task_kind") or claim.get("title") or "")]
        for worker in workers:
            if not isinstance(worker, dict):
                continue
            kinds = worker.get("primary_task_kinds") if isinstance(worker.get("primary_task_kinds"), list) else []
            if any(k in kinds for k in task_kinds):
                terr = str(worker.get("territory") or "")
                duplicate_territory.setdefault(terr, []).append(str(claim.get("task_id") or claim.get("agent_id")))

    for terr, actors in duplicate_territory.items():
        if terr and len(actors) > 1:
            conflicts.append(
                {
                    "kind": "territory_duplicate_claim",
                    "territory": terr,
                    "actors": actors,
                }
            )

    ok = not conflicts
    return {
        "schema": "noos-parallel-agent-conflict-check-v1",
        "version": "1.0.0",
        "at": utc_now(),
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "integrator_state_present": INTEGRATOR_STATE.is_file(),
        "active_claims": len(claims),
        "conflicts": conflicts,
        "ok": ok,
        "report_line": (
            "parallel_agents_clean · no mutex or scope conflicts"
            if ok
            else f"parallel_agent_conflict · count={len(conflicts)}"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    registry = load_json(REGISTRY_PATH)
    integrator = load_json(INTEGRATOR_STATE)
    row = check_conflicts(registry=registry, integrator=integrator)

    if args.write_receipt:
        out_dir = ROOT / "receipts/proof"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = out_dir / f"noos-parallel-agent-conflict-{ts}.json"
        path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(path.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
        for c in row.get("conflicts") or []:
            print(f"  {c.get('kind')}: {c}")

    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
