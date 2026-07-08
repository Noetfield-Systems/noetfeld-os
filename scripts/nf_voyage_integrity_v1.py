#!/usr/bin/env python3
"""NF voyage integrity — plan.json ↔ GTM_NEXT ↔ SHIP_NOW ↔ REGISTRY alignment."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _first_pending(plan: dict) -> dict | None:
    for row in plan.get("next_tasks") or []:
        if str(row.get("status", "")).lower() == "pending":
            return row
    return None


def _ship_ids_in_gtm(text: str) -> dict[str, str]:
    """Rough map id -> mentioned as done/pending from GTM prose."""
    found: dict[str, str] = {}
    for m in re.finditer(r"\*\*(ship-[a-z0-9-]+)\*\*", text, re.I):
        found[m.group(1).lower()] = "mentioned"
    for m in re.finditer(r"(ship-[a-z0-9-]+)", text, re.I):
        tid = m.group(1).lower()
        if tid not in found:
            found[tid] = "mentioned"
    return found


def run_voyage(root: Path) -> dict:
    gates: list[dict] = []
    ok = True

    plan_path = root / "os/plan.json"
    ship_path = root / "os/SHIP_NOW.md"
    gtm_path = root / "docs/ops/plans/no-asf/GTM_NEXT.md"
    registry_path = root / "os/plan-library/noetfield-1000/REGISTRY.json"

    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else {}
    pending = _first_pending(plan)
    pid = (pending or {}).get("id", "")

    ship_text = ship_path.read_text(encoding="utf-8", errors="replace") if ship_path.is_file() else ""
    gtm_text = gtm_path.read_text(encoding="utf-8", errors="replace") if gtm_path.is_file() else ""

    if pid:
        in_ship = pid in ship_text
        in_gtm = pid.lower() in gtm_text.lower()
        gates.append({"gate": "pending_in_ship_now", "ok": in_ship, "id": pid})
        gates.append({"gate": "pending_in_gtm_next", "ok": in_gtm, "id": pid})
        if not in_ship or not in_gtm:
            ok = False
    else:
        gates.append({"gate": "pending_task_exists", "ok": True, "note": "no pending next_tasks"})

    # Duplicate ids in locked_references
    refs = plan.get("locked_references") or []
    seen: set[str] = set()
    dup = False
    for ref in refs:
        rid = ref.get("id", "")
        if rid in seen:
            dup = True
        seen.add(rid)
    gates.append({"gate": "locked_refs_unique_ids", "ok": not dup})
    if dup:
        ok = False

    # cursor-reply SHA drift (optional)
    reply_path = root / "reports/cursor-reply-latest.txt"
    sha_drift = False
    if reply_path.is_file():
        reply = reply_path.read_text(encoding="utf-8", errors="replace")
        try:
            head = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
            ).strip()
            if head and head not in reply:
                sha_drift = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    gates.append({"gate": "cursor_reply_sha_present", "ok": not sha_drift, "optional": True})

    scripts = root / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        from nf_embedding_provider_v1 import provider_payload, voyage_key_on_disk

        payload = provider_payload()
        semantic = payload.get("semantic") is True
        mode = str(payload.get("mode") or "")
        key_on_disk = voyage_key_on_disk()
        l8_ok = semantic if key_on_disk else True
        if key_on_disk and mode == "hash_local":
            l8_ok = False
        gates.append(
            {
                "gate": "l8_voyage_semantic",
                "ok": l8_ok,
                "mode": mode,
                "semantic": semantic,
                "voyage_key_on_disk": key_on_disk,
                "model": payload.get("model"),
            }
        )
        if not l8_ok:
            ok = False
        if semantic:
            proc = subprocess.run(
                [sys.executable, str(scripts / "nf_semantic_drift_v1.py"), "--json"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            drift = json.loads(proc.stdout) if proc.stdout.strip() else {}
            drift_ok = proc.returncode == 0 and bool(drift.get("ok", False))
            gates.append({"gate": "semantic_drift_anchors", "ok": drift_ok, "checks": drift.get("checks", [])})
            if not drift_ok:
                ok = False
    except Exception as exc:
        gates.append({"gate": "l8_voyage_semantic", "ok": False, "error": str(exc)})
        ok = False

    out = {
        "schema_version": "nf-voyage-integrity-v1",
        "generated_at": _iso_now(),
        "ok": ok,
        "pending_task": pending,
        "gates": gates,
    }

    events = root / "reports/agent-auto/events"
    events.mkdir(parents=True, exist_ok=True)
    (events / "nf-voyage-integrity-v1.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=None)
    args = parser.parse_args()
    root = Path(args.root or Path(__file__).resolve().parents[1])
    result = run_voyage(root)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"nf_voyage_integrity: {'PASS' if result['ok'] else 'FAIL'}")
        for g in result["gates"]:
            if not g.get("ok", True) and not g.get("optional"):
                print(f"  FAIL {g['gate']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
