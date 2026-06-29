#!/usr/bin/env python3
"""Validate the machine-readable Noetfield OS repo policy."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "repo-policy.json"

REQUIRED_FIELDS = {
    "repo_name",
    "repo_role",
    "allowed_ownership",
    "forbidden_ownership",
    "dirty_file_states",
    "cross_lane_quarantine_paths",
    "generated_artifact_policy",
    "evidence_policy",
    "cursor_performance_policy",
    "max_files_per_pass",
    "required_prework_commands",
    "required_final_report",
}

REQUIRED_DIRTY_STATES = {
    "COMMIT",
    "RESTORE",
    "DELETE",
    "SNAPSHOT",
    "QUARANTINE",
    "LEAVE",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    missing = sorted(REQUIRED_FIELDS - set(policy))
    require(not missing, f"repo-policy.json missing fields: {', '.join(missing)}")

    require(policy["repo_name"] == "noetfeld-os", "repo_name must be noetfeld-os")
    require(isinstance(policy["max_files_per_pass"], int), "max_files_per_pass must be an integer")
    require(1 <= policy["max_files_per_pass"] <= 40, "max_files_per_pass must be between 1 and 40")
    require(
        set(policy["dirty_file_states"]) == REQUIRED_DIRTY_STATES,
        "dirty_file_states must match the required state set",
    )
    require(
        policy["generated_artifact_policy"].get("mode") == "snapshot_plus_manifest",
        "generated_artifact_policy.mode must be snapshot_plus_manifest",
    )
    require(
        policy["evidence_policy"].get("mode") == "snapshot_plus_manifest",
        "evidence_policy.mode must be snapshot_plus_manifest",
    )

    for command in ("git status --short", "git branch --show-current"):
        require(command in policy["required_prework_commands"], f"missing prework command: {command}")

    print("OK: repo-policy.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
