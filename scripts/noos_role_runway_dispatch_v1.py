#!/usr/bin/env python3
"""Typed role → Runway intake adapters (replaces mock researcher/specialist/self-heal/orchestrator LLM).

Each role emits a durable dispatch artifact + optional dry-run/live intake.
NOOS does not call DeepSeek; Runway ResilientRouter owns model execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_plan_completion_dispatch_v1 as dispatch  # noqa: E402
import noos_runway_supervision_adapter_v1 as runway  # noqa: E402

CONTRACT = ROOT / "data/noetfield-runway-contract-v1.json"
PROOF = ROOT / "receipts/proof"

ROLE_SPECS = {
    "research": {
        "value_class": "risk_reduction",
        "artifact_kind": "research_memo",
        "acceptance": ["cited_sources", "schema_valid_memo", "no_state_mutation"],
    },
    "specialist": {
        "value_class": "risk_reduction",
        "artifact_kind": "patch_proposal",
        "acceptance": ["scoped_paths", "proposal_schema_valid", "no_direct_apply"],
    },
    "self_heal": {
        "value_class": "risk_reduction",
        "artifact_kind": "repair_attempt",
        "acceptance": ["sandbox_only", "before_after_evidence", "independent_verify"],
    },
    "orchestrator": {
        "value_class": "risk_reduction",
        "artifact_kind": "cross_repo_health",
        "acceptance": ["aggregate_receipt", "no_cross_repo_disk_read", "sink_via_shared_db"],
    },
    "incident_diagnose": {
        "value_class": "proof_asset",
        "artifact_kind": "incident_diagnosis",
        "acceptance": ["diagnosis_receipt", "no_execution_restart"],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def role_op_key(role: str, subject: str) -> str:
    material = f"role-dispatch|{role}|{subject}|{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def dispatch_role(role: str, *, subject: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    if role not in ROLE_SPECS:
        return {"ok": False, "error": f"unknown_role:{role}"}
    spec = ROLE_SPECS[role]
    contract = load_contract()
    mapped = (contract.get("role_recipe_map") or {}).get(role) or {}
    op = role_op_key(role, subject)
    intake = {
        "runway_id": mapped.get("runway_id") or "research",
        "recipe_id": mapped.get("recipe_id") or "noos-research-memo",
        "recipe_version": mapped.get("recipe_version") or "1.0.0",
        "idempotency_key": op,
        "requested_at": utc_now(),
        "budget_usd": 0.25,
        "input": {
            "goal": {
                "role": role,
                "subject": subject,
                "artifact_kind": spec["artifact_kind"],
                "acceptance_checks": spec["acceptance"],
                "value_class": spec["value_class"],
                "context": context or {},
            }
        },
    }
    pf = runway.preflight()
    if pf.get("ok") and __import__("os").environ.get("NOOS_PLAN_COMPLETION_LIVE_INTAKE", "").strip() in ("1", "true", "yes"):
        ack = runway.submit_intake(intake)
    else:
        ack = dispatch.dry_run_ack(intake)

    artifact = {
        "schema": "noos-role-runway-dispatch-artifact-v1",
        "at": utc_now(),
        "role": role,
        "subject": subject,
        "op_key": op,
        "artifact_kind": spec["artifact_kind"],
        "value_class": spec["value_class"],
        "acceptance_checks": spec["acceptance"],
        "recipe": {
            "runway_id": intake["runway_id"],
            "recipe_id": intake["recipe_id"],
            "recipe_version": intake["recipe_version"],
        },
        "ack": {"ok": ack.get("ok"), "status": ack.get("status"), "dry_run": ack.get("dry_run"), "job_id": (ack.get("body") or {}).get("job_id")},
        "productive": bool(ack.get("ok")) and spec["value_class"] != "none",
        "ok": bool(ack.get("ok")),
        "report_line": f"role_dispatch · {role} · productive={bool(ack.get('ok'))} dry_run={bool(ack.get('dry_run'))}",
    }
    PROOF.mkdir(parents=True, exist_ok=True)
    out = PROOF / f"noos-role-dispatch-{role}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    artifact["receipt_path"] = str(out.relative_to(ROOT))
    return artifact


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--role", required=True, choices=sorted(ROLE_SPECS))
    p.add_argument("--subject", default="portfolio")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    row = dispatch_role(args.role, subject=args.subject)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
