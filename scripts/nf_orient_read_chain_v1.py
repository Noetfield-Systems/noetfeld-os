#!/usr/bin/env python3
"""Validate orient read chain — every path in nf_orient_routing must exist."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nf_factory_lib_v1 import iso_now, load_json, repo_root, write_event, write_sina


def _expand(path: str, root: Path) -> Path:
    raw = path.strip()
    if raw.startswith("~/"):
        return Path.home() / raw[2:]
    return root / raw


def run_orient_read_chain(root: Path | None = None) -> dict:
    root = root or repo_root()
    ssot = load_json(root / "data/nf_orient_routing_v1.json") or {}
    chain = ssot.get("orient_read_chain") or []
    missing: list[str] = []
    present: list[str] = []

    for rel in chain:
        path = _expand(rel, root)
        if path.is_file():
            present.append(rel)
        else:
            missing.append(rel)

    ok = not missing
    receipt = {
        "schema_version": "nf-orient-read-chain-v1",
        "generated_at": iso_now(),
        "ok": ok,
        "total": len(chain),
        "present": len(present),
        "missing": missing,
        "present_paths": present,
        "heal": None if ok else "fix missing orient read chain paths",
    }
    write_event("nf-orient-read-chain-v1.json", receipt, root)
    write_sina("nf-orient-read-chain-v1.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = run_orient_read_chain()
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        status = "PASS" if receipt["ok"] else "FAIL"
        print(f"nf_orient_read_chain: {status} ({receipt['present']}/{receipt['total']})")
        for m in receipt.get("missing") or []:
            print(f"  MISSING {m}")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
