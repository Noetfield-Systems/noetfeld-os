#!/usr/bin/env python3
"""sandbox_health_sweep_v1 — diff live triggers vs data/trigger-registry-v1.json (NOETFIELD P1)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "trigger-registry-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_wrangler_crons(text: str) -> list[str]:
    crons: list[str] = []
    in_triggers = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[triggers]"):
            in_triggers = True
            continue
        if in_triggers and stripped.startswith("["):
            break
        if in_triggers and stripped.startswith("crons"):
            match = re.search(r"\[(.*)\]", line.split("=", 1)[-1])
            if match:
                inner = match.group(1)
                for part in re.findall(r'"([^"]+)"|\'([^\']+)\'', inner):
                    cron = part[0] or part[1]
                    if cron:
                        crons.append(cron.strip())
    return crons


def _parse_gha_workflow(text: str) -> dict[str, Any]:
    events: list[str] = []
    schedules: list[str] = []
    if re.search(r"^\s*workflow_dispatch\s*:", text, re.MULTILINE):
        events.append("workflow_dispatch")
    if re.search(r"^\s*push\s*:", text, re.MULTILINE):
        events.append("push")
    if re.search(r"^\s*pull_request\s*:", text, re.MULTILINE):
        events.append("pull_request")
    if re.search(r"^\s*schedule\s*:", text, re.MULTILINE):
        events.append("schedule")
        for match in re.finditer(r"cron:\s*['\"]([^'\"]+)['\"]", text):
            schedules.append(match.group(1).strip())
    return {"events": sorted(set(events)), "schedules": schedules}


def _discover_live_wrangler_triggers() -> list[dict[str, Any]]:
    live: list[dict[str, Any]] = []
    workers = ROOT / "cloud" / "workers"
    if not workers.is_dir():
        return live
    for wrangler in sorted(workers.glob("*/wrangler.toml")):
        text = wrangler.read_text(encoding="utf-8", errors="replace")
        crons = _parse_wrangler_crons(text)
        if not crons:
            continue
        rel = str(wrangler.relative_to(ROOT))
        for cron in crons:
            live.append(
                {
                    "signature": f"wrangler:{rel}:{cron}",
                    "type": "wrangler_cron",
                    "path": rel,
                    "schedule": cron,
                }
            )
    return live


def _discover_live_gha_triggers() -> list[dict[str, Any]]:
    live: list[dict[str, Any]] = []
    workflows = ROOT / ".github" / "workflows"
    if not workflows.is_dir():
        return live
    for wf in sorted(workflows.glob("*.yml")) + sorted(workflows.glob("*.yaml")):
        text = wf.read_text(encoding="utf-8", errors="replace")
        parsed = _parse_gha_workflow(text)
        rel = str(wf.relative_to(ROOT))
        if parsed["schedules"]:
            for cron in parsed["schedules"]:
                live.append(
                    {
                        "signature": f"gha_schedule:{rel}:{cron}",
                        "type": "gha_schedule",
                        "path": rel,
                        "schedule": cron,
                    }
                )
        for event in parsed["events"]:
            if event == "schedule":
                continue
            live.append(
                {
                    "signature": f"gha:{rel}:{event}",
                    "type": "gha_workflow",
                    "path": rel,
                    "event": event,
                }
            )
    return live


def _probe_registry_entry(entry: dict[str, Any]) -> dict[str, Any]:
    probe = entry.get("live_probe") if isinstance(entry.get("live_probe"), dict) else {}
    rel_path = str(probe.get("path") or "")
    path = ROOT / rel_path
    trigger_id = str(entry.get("trigger_id") or "")
    if not rel_path or not path.is_file():
        return {
            "trigger_id": trigger_id,
            "ok": False,
            "reason": "probe_path_missing",
            "path": rel_path,
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    probe_type = str(probe.get("type") or "")
    if probe_type == "wrangler_cron":
        crons = _parse_wrangler_crons(text)
        expected = str(entry.get("schedule") or "")
        ok = expected in crons
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": rel_path,
            "expected_schedule": expected,
            "live_schedules": crons,
            "reason": None if ok else "schedule_mismatch",
        }
    if probe_type == "gha_schedule":
        parsed = _parse_gha_workflow(text)
        expected = str(entry.get("schedule") or "")
        ok = expected in parsed["schedules"]
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": rel_path,
            "expected_schedule": expected,
            "live_schedules": parsed["schedules"],
            "reason": None if ok else "schedule_mismatch",
        }
    if probe_type == "gha_workflow":
        parsed = _parse_gha_workflow(text)
        expects = probe.get("expects") if isinstance(probe.get("expects"), list) else []
        missing = [e for e in expects if e not in parsed["events"]]
        ok = not missing
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": rel_path,
            "expects": expects,
            "live_events": parsed["events"],
            "reason": None if ok else f"missing_events:{','.join(missing)}",
        }
    if probe_type == "pg_cron_migration":
        expected = str(entry.get("schedule") or "")
        ok = expected in text and "noetfield_detect_stale_lanes_v1" in text
        return {
            "trigger_id": trigger_id,
            "ok": ok,
            "path": rel_path,
            "expected_schedule": expected,
            "reason": None if ok else "pg_cron_migration_mismatch",
        }
    return {"trigger_id": trigger_id, "ok": False, "reason": "unknown_probe_type", "path": rel_path}


def run_sweep(*, repo_root: Path | None = None) -> dict[str, Any]:
    global ROOT, REGISTRY_PATH  # noqa: PLW0603
    if repo_root is not None:
        ROOT = repo_root
        REGISTRY_PATH = ROOT / "data" / "trigger-registry-v1.json"

    registry = _read_json(REGISTRY_PATH)
    triggers = registry.get("triggers") if isinstance(registry.get("triggers"), list) else []
    probe_results = [_probe_registry_entry(t) for t in triggers if isinstance(t, dict)]
    dead_or_mismatch = [r for r in probe_results if not r.get("ok")]

    live_all = _discover_live_wrangler_triggers() + _discover_live_gha_triggers()
    claimed: set[str] = set()
    for entry in triggers:
        if not isinstance(entry, dict):
            continue
        probe = entry.get("live_probe") if isinstance(entry.get("live_probe"), dict) else {}
        rel = str(probe.get("path") or "")
        probe_type = str(probe.get("type") or "")
        if probe_type == "wrangler_cron":
            claimed.add(f"wrangler:{rel}:{entry.get('schedule')}")
        elif probe_type == "gha_schedule":
            claimed.add(f"gha_schedule:{rel}:{entry.get('schedule')}")
        elif probe_type == "gha_workflow":
            for event in probe.get("expects") or []:
                claimed.add(f"gha:{rel}:{event}")
        elif probe_type == "pg_cron_migration":
            claimed.add(f"pg_cron:{rel}:{entry.get('schedule')}")

    unregistered = [row for row in live_all if row["signature"] not in claimed]

    ok = not dead_or_mismatch and not unregistered
    return {
        "schema": "sandbox-health-sweep-v1",
        "version": "1.0.0",
        "at": _now(),
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "registry_trigger_count": len(triggers),
        "live_trigger_count": len(live_all),
        "probe_results": probe_results,
        "dead_or_mismatch": dead_or_mismatch,
        "unregistered_live": unregistered,
        "ok": ok,
        "drift": not ok,
        "report_line": (
            "trigger_sweep_clean · registry matches live"
            if ok
            else f"trigger_drift · dead={len(dead_or_mismatch)} unregistered={len(unregistered)}"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff live triggers vs trigger-registry-v1.json")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    row = run_sweep(repo_root=args.repo_root)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
