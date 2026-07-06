#!/usr/bin/env python3
"""Read-only automation surface verifier.

This is the repo-safe subset of the Noetfield OS autorun model:
observe the automation inventory, do not assume control of any external
runtime, and fail closed when the repo state drifts from the locked manifest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "governance" / "AUTOMATION_SURFACES_LOCKED.json"
MAKEFILE = ROOT / "Makefile"
HEARTBEAT = ROOT / ".github" / "workflows" / "supabase-heartbeat.yml"
DAILY_HEARTBEAT = ROOT / ".github" / "workflows" / "nf-daily-heartbeat.yml"
KAIZEN_NIGHTLY = ROOT / ".github" / "workflows" / "nf-kaizen-nightly.yml"
COPILOT_DISABLED = ROOT / "governance" / "COPILOT_SCHEDULED_AUTOMATIONS_LOCKED.json"


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--check", action="store_true", help="Exit non-zero on drift.")
    args = parser.parse_args()

    manifest = load_manifest()
    failures: list[str] = []
    checks: list[dict[str, str]] = []

    require(manifest.get("schema_version") == "automation-surfaces-locked-v1", "bad schema_version", failures)
    require(manifest.get("repo") == "Noetfield-Systems/Noetfield", "bad repo", failures)

    surfaces = manifest.get("surfaces", [])
    require(isinstance(surfaces, list) and len(surfaces) >= 7, "expected at least 7 surfaces", failures)

    for surface in surfaces:
        sid = str(surface.get("id", "<missing>"))
        path = str(surface.get("path", ""))
        kind = str(surface.get("kind", ""))
        full_path = ROOT / path
        exists = full_path.exists()
        checks.append({"id": sid, "kind": kind, "path": path, "exists": str(exists).lower()})
        require(exists, f"missing surface path: {path}", failures)

    makefile_text = MAKEFILE.read_text(encoding="utf-8")
    for target in (
        "verify-live-nerve",
        "verify-www-e2e",
        "verify-ui-e2e",
        "verify-ui-visual",
        "verify-platform-health",
        "verify-route-nav-truth",
        "verify-validator-node-registry",
        "verify-automation-surfaces",
    ):
        require(f"{target}:" in makefile_text, f"missing Makefile target: {target}", failures)

    heartbeat_text = HEARTBEAT.read_text(encoding="utf-8")
    require('cron: "0 14 * * 1"' in heartbeat_text, "missing heartbeat cron", failures)
    require("verify_supabase_heartbeat_v1.py" in heartbeat_text, "heartbeat does not invoke heartbeat verifier", failures)
    require("report_slo_health_v1.py" in heartbeat_text, "heartbeat does not invoke SLO reporter", failures)

    daily_text = DAILY_HEARTBEAT.read_text(encoding="utf-8")
    require('cron: "0 14 * * *"' in daily_text, "missing daily heartbeat cron (07:00 Pacific)", failures)
    require("nf_daily_heartbeat_v1.py" in daily_text, "daily heartbeat does not invoke nf_daily_heartbeat_v1", failures)

    kaizen_text = KAIZEN_NIGHTLY.read_text(encoding="utf-8")
    require('cron: "0 9 * * *"' in kaizen_text, "missing kaizen nightly cron", failures)
    require("nf_kaizen_nightly_tick_v1.py" in kaizen_text, "kaizen nightly does not invoke tick script", failures)

    copilot = json.loads(COPILOT_DISABLED.read_text(encoding="utf-8"))
    require(copilot.get("policy") == "all_disabled", "copilot scheduled automations not all_disabled", failures)
    for auto in copilot.get("automations", []):
        require(auto.get("enabled") is False, f"copilot automation still enabled: {auto.get('id')}", failures)

    adopted = {
        item.get("id"): item.get("fit")
        for item in manifest.get("noos_reference_patterns", [])
        if isinstance(item, dict)
    }
    require(adopted.get("read_only_autorun_status") == "adopted", "read-only status pattern not adopted", failures)
    require(adopted.get("scheduled_heartbeat") == "adopted", "scheduled heartbeat pattern not adopted", failures)
    require(adopted.get("deterministic_receipts") == "adopted", "deterministic receipts pattern not adopted", failures)

    if args.json:
        payload = {
            "schema": "automation-surface-verifier-v1",
            "ok": not failures,
            "failures": failures,
            "checks": checks,
        }
        print(json.dumps(payload, indent=2))
    else:
        print("=== automation surfaces ===")
        for check in checks:
            print(f"{check['id']}: {check['exists']} {check['kind']} {check['path']}")
        if failures:
            print("\nFAIL:")
            for failure in failures:
                print(f"- {failure}")
        else:
            print("\nPASS")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
