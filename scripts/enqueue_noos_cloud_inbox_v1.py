#!/usr/bin/env python3
"""Enqueue next NOOS UPG items into cloud worker inbox + Supabase worker_inbox_queue."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/_NOOS_AGENT/UPGRADE_MANIFEST.json"
OUT = ROOT / "data/noos-cloud-worker-inbox-v1.json"
SINA_COPY = Path.home() / ".sina/noos-cloud-worker-inbox-v1.json"
SINK = ROOT / "scripts/factory_supabase_sink_v1.py"

# Next agent-executable UPG batch (Phase 4 gate hardening + TLE lane starters)
INBOX_ITEMS = [
    {
        "item_id": "UPG-0151",
        "priority": "P1",
        "title": "PyPI package metadata polish — classifiers, project URLs",
        "source_trace": "NOOS-AGENT-20260615-014",
        "payload": {"upg": "UPG-0151", "phase": 4, "repo": "noetfeld-os"},
    },
    {
        "item_id": "UPG-0152",
        "priority": "P1",
        "title": "noetfield gate --json stdout mode for CI",
        "source_trace": "NOOS-AGENT-20260615-014",
        "payload": {"upg": "UPG-0152", "phase": 4, "repo": "noetfeld-os"},
    },
    {
        "item_id": "UPG-0153",
        "priority": "P1",
        "title": "noetfield gate --strict fails on skipped API check when URL set",
        "source_trace": "NOOS-AGENT-20260615-014",
        "payload": {"upg": "UPG-0153", "phase": 4, "repo": "noetfeld-os"},
    },
    {
        "item_id": "UPG-0156",
        "priority": "P1",
        "title": "noetfield decide --file schema validation against OpenAPI",
        "source_trace": "NOOS-AGENT-20260615-014",
        "payload": {"upg": "UPG-0156", "phase": 4, "repo": "noetfeld-os"},
    },
    {
        "item_id": "UPG-0158",
        "priority": "P1",
        "title": "noetfield verify subcommand — chain + signature + gate report",
        "source_trace": "NOOS-AGENT-20260615-014",
        "payload": {"upg": "UPG-0158", "phase": 4, "repo": "noetfeld-os"},
    },
    {
        "item_id": "UPG-0101",
        "priority": "P2",
        "title": "TLE export bundle — procurement ZIP endpoint scaffold",
        "source_trace": "NOOS-AGENT-20260615-014",
        "payload": {"upg": "UPG-0101", "phase": 3, "repo": "noetfeld-os"},
    },
    {
        "item_id": "UPG-0191",
        "priority": "P2",
        "title": "GitHub Actions — pytest on push (extend gel-ci)",
        "source_trace": "NOOS-AGENT-20260615-014",
        "payload": {"upg": "UPG-0191", "phase": 4, "repo": "noetfeld-os"},
    },
    {
        "item_id": "NOOS-C-01",
        "priority": "P0",
        "title": "Founder: first Trust Brief / AI Value OS briefing",
        "source_trace": "NOOS-AGENT-20260702-024",
        "payload": {"phase": "C", "owner": "founder", "lane": "commercial"},
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_bundle() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {
        "schema": "noos-cloud-worker-inbox-v1",
        "lane": "NOETFELD-OS",
        "saved_at": utc_now(),
        "one_law": "Cloud Workers consume worker_inbox_queue on Supabase; factory autorun every 10 min.",
        "plan_trace_id": manifest.get("plan_trace_id"),
        "completed_steps_count": len(manifest.get("completed_steps") or []),
        "items": [{**item, "status": "pending", "lane": "NOETFELD-OS"} for item in INBOX_ITEMS],
    }


def main() -> int:
    bundle = build_bundle()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    SINA_COPY.parent.mkdir(parents=True, exist_ok=True)
    SINA_COPY.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(bundle['items'])} items)")
    print(f"Mirrored {SINA_COPY}")

    if SINK.is_file():
        proc = subprocess.run(
            [sys.executable, str(SINK), "inbox", str(OUT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.stdout.strip():
            print(proc.stdout.strip())
        if proc.returncode != 0:
            print(proc.stderr.strip() or "Supabase inbox upsert failed (env missing?)", file=sys.stderr)
            return 1 if "supabase_not_configured" not in proc.stdout else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
