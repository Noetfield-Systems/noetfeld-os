#!/usr/bin/env python3
"""Verify public route inventory shape and optional live status."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "governance" / "ROUTE_INVENTORY.json"
DEFAULT_BASE = "https://www.noetfield.com"


def load_inventory() -> dict[str, Any]:
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def fetch_status(url: str) -> int | str:
    req = urllib.request.Request(url, headers={"User-Agent": "NoetfieldRouteInventory/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception as exc:
        return type(exc).__name__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="also verify live HTTP status")
    parser.add_argument("--base", default=DEFAULT_BASE)
    args = parser.parse_args()

    inventory = load_inventory()
    failures: list[str] = []

    if inventory.get("schema") != "noetfield-route-inventory-v1":
        failures.append("wrong schema")

    routes = inventory.get("routes")
    if not isinstance(routes, list) or not routes:
        failures.append("routes must be a non-empty list")
        routes = []

    seen: set[str] = set()
    for row in routes:
        path = row.get("path")
        expected = row.get("expected_status")
        source = row.get("source")
        owner = row.get("owner")
        purpose = row.get("purpose")

        if not isinstance(path, str) or not path.startswith("/"):
            failures.append(f"invalid route path: {path}")
            continue
        if path in seen:
            failures.append(f"duplicate route path: {path}")
        seen.add(path)
        if expected != 200:
            failures.append(f"{path} expected_status must be 200")
        if not owner:
            failures.append(f"{path} missing owner")
        if not purpose:
            failures.append(f"{path} missing purpose")
        if not source or not (ROOT / source).exists():
            failures.append(f"{path} missing source file: {source}")

        if args.live:
            status = fetch_status(args.base.rstrip("/") + path)
            if status != expected:
                failures.append(f"{path} live status {status}, expected {expected}")

    if failures:
        print("verify-route-inventory: FAIL")
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    mode = "live" if args.live else "structural"
    print(f"verify-route-inventory: PASS mode={mode} routes={len(routes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
