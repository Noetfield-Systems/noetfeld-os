#!/usr/bin/env python3
"""Mark Tier 1 SMART prompt ids done/backlog in tier1-status.json."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "ops" / "plans" / "tier1-status.json"
PACK = ROOT / "docs" / "ops" / "plans" / "tier1-smart.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--done", nargs="*", help="Mark ids done (e.g. E-01 L-02)")
    ap.add_argument("--backlog", nargs="*", help="Mark ids backlog")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not STATUS.is_file():
        print("Run generate-tier1-smart-pack.py first")
        raise SystemExit(1)

    data = json.loads(STATUS.read_text(encoding="utf-8"))
    st = data.setdefault("status", {})
    valid = set()
    if PACK.is_file():
        valid = {p["id"] for p in json.loads(PACK.read_text())["prompts"]}

    for pid in args.done or []:
        if valid and pid not in valid:
            print(f"warn: unknown id {pid}")
        st[pid] = "done"
    for pid in args.backlog or []:
        st[pid] = "backlog"

    data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.dry_run:
        print(json.dumps(data, indent=2))
        return
    STATUS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {STATUS}")


if __name__ == "__main__":
    main()
