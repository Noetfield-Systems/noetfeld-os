#!/usr/bin/env python3
"""Mark plan IDs done/in_progress in docs/ops/plans/registry.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "docs" / "ops" / "plans" / "registry.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Update plan status in registry")
    parser.add_argument("ids", nargs="+", help="Plan IDs e.g. NF-PLAN-0042")
    parser.add_argument(
        "--status",
        default="done",
        choices=("backlog", "in_progress", "done", "cancelled"),
    )
    args = parser.parse_args()

    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in data["plans"]}
    for pid in args.ids:
        if pid not in by_id:
            raise SystemExit(f"Unknown plan id: {pid}")
        by_id[pid]["status"] = args.status
    REGISTRY.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(args.ids)} plan(s) to status={args.status}")


if __name__ == "__main__":
    main()
