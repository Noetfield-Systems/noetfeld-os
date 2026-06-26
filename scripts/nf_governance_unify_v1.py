#!/usr/bin/env python3
"""NF governance unify — inventory scan + duplicate boot entry detection."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def scan(root: Path) -> dict:
    inv_path = root / "os/NF_SSOT_INVENTORY.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8")) if inv_path.is_file() else {}
    boot = inv.get("boot_entries") or []
    issues: list[str] = []
    recommendations: list[str] = []

    paths = [e["path"] for e in boot]
    if len(paths) != len(set(paths)):
        issues.append("duplicate boot path in NF_SSOT_INVENTORY.json")
        recommendations.append("MERGE duplicate boot_entries to one canonical path")

    for e in boot:
        if not (root / e["path"]).is_file():
            issues.append(f"missing inventory path: {e['path']}")
            recommendations.append(f"ADD file or REMOVE row {e['id']} from inventory")

    rules_dir = root / ".cursor/rules"
    always = []
    if rules_dir.is_dir():
        for f in rules_dir.glob("*.mdc"):
            text = f.read_text(encoding="utf-8", errors="replace")
            if "alwaysApply: true" in text and f.name.startswith(("nf-", "noetfield-ask")):
                always.append(f.name)
    expected = set(inv.get("always_apply_rules") or [])
    if set(always) != expected:
        issues.append(f"alwaysApply rules drift: {sorted(always)} vs inventory {sorted(expected)}")
        recommendations.append("SYNC always_apply_rules in NF_SSOT_INVENTORY.json")

    return {
        "schema_version": "nf-governance-unify-v1",
        "generated_at": _iso_now(),
        "ok": len(issues) == 0,
        "issues": issues,
        "recommendations": recommendations,
        "boot_count": len(boot),
        "always_apply_rules": sorted(always),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = scan(root)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"nf_governance_unify: {'PASS' if result['ok'] else 'FAIL'}")
        for i in result["issues"]:
            print(f"  - {i}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
