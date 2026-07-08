#!/usr/bin/env python3
"""Sync trigger-registry schedules with GitHub workflow cron entries.
Reads data/trigger-registry-v1.json and updates 'schedule' for gha_schedule live_probes
when the workflow file contains a 'schedule' entry. Writes file back only if changes made.
"""
from __future__ import annotations
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data/trigger-registry-v1.json"
WFS = ROOT / ".github/workflows"


def extract_first_cron(workflow_path: Path) -> str | None:
    if not workflow_path.is_file():
        return None
    text = workflow_path.read_text(encoding="utf-8")
    # crude YAML search for schedule: - cron: "..."
    m = re.search(r"schedule:\s*\n([\s\S]*?)\n\S", text)
    if m:
        block = m.group(1)
        # find first cron: line
        cm = re.search(r"cron:\s*\"([^\"]+)\"", block)
        if cm:
            return cm.group(1).strip()
        cm = re.search(r"cron:\s*'([^']+)'", block)
        if cm:
            return cm.group(1).strip()
    # try single-line schedule: - cron: "..."
    m2 = re.search(r"-\s*cron:\s*\"([^\"]+)\"", text)
    if m2:
        return m2.group(1).strip()
    m2 = re.search(r"-\s*cron:\s*'([^']+)'", text)
    if m2:
        return m2.group(1).strip()
    return None


def main() -> int:
    if not REG.is_file():
        print("registry missing", REG)
        return 2
    reg = json.loads(REG.read_text(encoding="utf-8"))
    changed = False
    for trig in reg.get("triggers", []):
        lp = trig.get("live_probe") or {}
        if lp.get("type") == "gha_schedule":
            path = lp.get("path")
            if not path:
                continue
            wf = ROOT / path
            cron = extract_first_cron(wf)
            if cron and trig.get("schedule") != cron:
                print(f"Updating {trig.get('trigger_id')} schedule: {trig.get('schedule')} -> {cron}")
                trig["schedule"] = cron
                changed = True
    if changed:
        REG.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")
        print("registry updated")
        return 0
    print("no changes")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
