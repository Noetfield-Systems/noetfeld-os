#!/usr/bin/env python3
"""Founder-input → Noetfield disk sync — one action patches INBOX + SHIP_NOW + receipt.

Law: founder-input-cascade newer than disk → auto-sync on nf-onboard (not chat-only).
Receipt: ~/.sina/nf-founder-disk-sync-receipt-v1.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nf_factory_lib_v1 import (
    agent_id,
    cascade_requires_disk_patch,
    iso_now,
    latest_founder_cascade,
    load_sina,
    mtime_iso,
    nf_inbox_path,
    parse_iso,
    repo_root,
    write_event,
    write_sina,
)

SHIP_MARKER = "**Founder cascade sync"


def _patch_ship_now(ship_path: Path, cascade_at: str, preview: str, source: str) -> bool:
    if not ship_path.is_file():
        return False
    text = ship_path.read_text(encoding="utf-8", errors="replace")
    if cascade_at in text and SHIP_MARKER in text:
        return False
    line = (
        f"{SHIP_MARKER} ({cascade_at}):** {preview[:200]} "
        f"— source `{source}` · synced by `nf_founder_input_sync_v1.py`\n\n"
    )
    if text.startswith("# SHIP NOW"):
        parts = text.split("\n", 1)
        new_text = parts[0] + "\n\n" + line + (parts[1] if len(parts) > 1 else "")
    else:
        new_text = line + text
    ship_path.write_text(new_text, encoding="utf-8")
    return True


def _patch_inbox(inbox_path: Path, cascade_at: str, preview: str) -> bool:
    if not inbox_path.is_file():
        return False
    text = inbox_path.read_text(encoding="utf-8", errors="replace")
    date = cascade_at[:10] if cascade_at else iso_now()[:10]
    marker = f"| {date} | Founder cascade"
    if marker in text and cascade_at in text:
        return False
    row = f"| {date} | Founder cascade: {preview[:80]} | synced {cascade_at} |\n"
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("|-------"):
            insert_at = i + 1
            break
    if insert_at:
        lines.insert(insert_at, row.rstrip())
    else:
        lines.append(row.rstrip())
    inbox_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def run_founder_input_sync(root: Path | None = None) -> dict:
    root = root or repo_root()
    cascade_at, cascade_row = latest_founder_cascade()
    prior = load_sina("nf-founder-disk-sync-receipt-v1.json") or {}
    ship_path = root / "os/SHIP_NOW.md"
    inbox_path = nf_inbox_path()

    patched_ship = False
    patched_inbox = False
    action = "noop"

    if not cascade_row:
        receipt = {
            "schema_version": "nf-founder-disk-sync-v1",
            "generated_at": iso_now(),
            "ok": True,
            "action": "no_cascade_events",
            "agent_id": agent_id(),
        }
        write_event("nf-founder-disk-sync-v1.json", receipt, root)
        write_sina("nf-founder-disk-sync-receipt-v1.json", receipt)
        return receipt

    preview = str(cascade_row.get("text_preview") or "")
    source = str(cascade_row.get("source") or "unknown")
    needs_patch = cascade_requires_disk_patch(cascade_row)
    ship_mtime = mtime_iso(ship_path)
    cascade_newer_than_ship = False
    if cascade_at and ship_mtime:
        c_dt = parse_iso(cascade_at)
        s_dt = parse_iso(ship_mtime)
        cascade_newer_than_ship = bool(c_dt and s_dt and c_dt > s_dt)

    already_synced = prior.get("cascade_at") == cascade_at and prior.get("ok")
    if already_synced and not needs_patch:
        action = "already_synced"
    elif needs_patch or cascade_newer_than_ship or prior.get("cascade_at") != cascade_at:
        patched_ship = _patch_ship_now(ship_path, cascade_at or iso_now(), preview, source)
        patched_inbox = _patch_inbox(inbox_path, cascade_at or iso_now(), preview)
        action = "patched" if (patched_ship or patched_inbox) else "receipt_only"
    else:
        action = "receipt_only"

    ok = True
    if needs_patch and cascade_newer_than_ship and not patched_ship:
        ok = False

    receipt = {
        "schema_version": "nf-founder-disk-sync-v1",
        "generated_at": iso_now(),
        "ok": ok,
        "action": action,
        "agent_id": agent_id(),
        "cascade_at": cascade_at,
        "cascade_source": source,
        "text_preview": preview[:200],
        "inbox_action": cascade_row.get("inbox_action"),
        "needs_disk_patch": needs_patch,
        "cascade_newer_than_ship": cascade_newer_than_ship,
        "patched_ship_now": patched_ship,
        "patched_inbox": patched_inbox,
        "ship_now": str(ship_path.relative_to(root)),
        "inbox": str(inbox_path),
        "heal": None if ok else "re-run nf-founder-input-sync",
    }
    write_event("nf-founder-disk-sync-v1.json", receipt, root)
    write_sina("nf-founder-disk-sync-receipt-v1.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync founder-input cascade to INBOX + SHIP_NOW")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    receipt = run_founder_input_sync()
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"nf_founder_input_sync: {'PASS' if receipt['ok'] else 'FAIL'} action={receipt.get('action')}")
        if receipt.get("patched_ship_now"):
            print("  patched SHIP_NOW.md")
        if receipt.get("patched_inbox"):
            print("  patched INBOX.md")
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
