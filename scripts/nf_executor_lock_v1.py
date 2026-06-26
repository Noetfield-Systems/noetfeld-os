#!/usr/bin/env python3
"""NF executor lock — one implementer per plane (optional)."""

from __future__ import annotations

import argparse
import json
import sys

from nf_factory_lib_v1 import agent_id, iso_now, load_lock, repo_root, write_lock


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["acquire", "release", "status"])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--task", default=None)
    args = parser.parse_args()

    root = repo_root()
    lock = load_lock() or {}
    aid = agent_id()

    if args.action == "status":
        out = {"locked": bool(lock.get("locked")), "lock": lock}
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"locked={out['locked']} holder={lock.get('agent_id')}")
        return 0

    if args.action == "release":
        if lock.get("agent_id") == aid or not lock.get("locked"):
            write_lock({"locked": False, "released_at": iso_now(), "agent_id": aid}, root)
            if args.json:
                print(json.dumps({"ok": True}))
            else:
                print("released")
        else:
            print(f"denied: lock held by {lock.get('agent_id')}", file=sys.stderr)
            return 1
        return 0

    if lock.get("locked") and lock.get("agent_id") != aid:
        print(f"denied: lock held by {lock.get('agent_id')}", file=sys.stderr)
        return 1
    payload = {
        "locked": True,
        "agent_id": aid,
        "task_id": args.task,
        "acquired_at": iso_now(),
    }
    write_lock(payload, root)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"acquired task={args.task}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
