#!/usr/bin/env python3
"""Verify Noetfield validator registry and node catalog wiring."""

from __future__ import annotations

import json
import re
import argparse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATORS = ROOT / "governance" / "VALIDATOR_REGISTRY.json"
NODES = ROOT / "governance" / "NODE_CATALOG.json"
LIVE_RECEIPT = ROOT / "governance" / "NOETFIELD_LIVE_NERVE_RECEIPT.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def is_live_receipt_node(node_id: str) -> bool:
    match = re.match(r"^N(\d+)_", node_id)
    return bool(match and int(match.group(1)) <= 9)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-live-receipt", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []
    validator_doc = load_json(VALIDATORS)
    node_doc = load_json(NODES)
    receipt = {} if args.skip_live_receipt else (load_json(LIVE_RECEIPT) if LIVE_RECEIPT.exists() else {})

    validators = validator_doc.get("validators", [])
    nodes = node_doc.get("nodes", [])
    validator_ids = {row.get("id") for row in validators}
    node_ids = {row.get("id") for row in nodes}
    active_node_ids = {row.get("id") for row in nodes if row.get("status") == "active"}

    if validator_doc.get("schema") != "noetfield-validator-registry-v1":
        failures.append("VALIDATOR_REGISTRY.json has wrong schema")
    if node_doc.get("schema") != "noetfield-node-catalog-v1":
        failures.append("NODE_CATALOG.json has wrong schema")

    if len(validator_ids) != len(validators):
        failures.append("duplicate validator id found")
    if len(node_ids) != len(nodes):
        failures.append("duplicate node id found")

    for validator in validators:
        validator_id = validator.get("id")
        script = validator.get("script")
        if not validator_id:
            failures.append("validator missing id")
        if not script or not file_exists(script):
            failures.append(f"validator {validator_id} missing script: {script}")
        for node_id in validator.get("node_ids", []):
            if node_id not in node_ids:
                failures.append(f"validator {validator_id} references unknown node: {node_id}")
        receipt_path = validator.get("receipt")
        if receipt_path and not file_exists(receipt_path):
            failures.append(f"validator {validator_id} missing receipt: {receipt_path}")

    for node in nodes:
        node_id = node.get("id")
        status = node.get("status")
        validator_refs = set(node.get("validator_ids", []))
        if status == "active" and not validator_refs:
            failures.append(f"active node {node_id} has no validators")
        for validator_id in validator_refs:
            if validator_id not in validator_ids:
                failures.append(f"node {node_id} references unknown validator: {validator_id}")
        for rel_path in node.get("files", []):
            if not file_exists(rel_path):
                failures.append(f"node {node_id} missing file: {rel_path}")

    for validator in validators:
        validator_id = validator.get("id")
        for node_id in validator.get("node_ids", []):
            node = next((row for row in nodes if row.get("id") == node_id), None)
            if node and validator_id not in set(node.get("validator_ids", [])):
                failures.append(f"validator/node reverse link missing: {validator_id} -> {node_id}")

    live_nodes = set((receipt.get("nodes") or {}).keys())
    if not args.skip_live_receipt:
        for node_id in live_nodes:
            if node_id not in node_ids:
                failures.append(f"live receipt has node missing from catalog: {node_id}")
        for node_id in active_node_ids:
            if isinstance(node_id, str) and is_live_receipt_node(node_id) and node_id not in live_nodes:
                failures.append(f"active live node missing from receipt: {node_id}")

    if failures:
        print("verify-validator-node-registry: FAIL")
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    print("verify-validator-node-registry: PASS")
    mode = "structural" if args.skip_live_receipt else "full"
    print(f"mode={mode} validators={len(validators)} nodes={len(nodes)} live_nodes={len(live_nodes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
