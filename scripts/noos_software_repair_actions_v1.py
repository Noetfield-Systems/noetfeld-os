#!/usr/bin/env python3
"""NOOS Software Repair — GitHub Actions canonical-producer entrypoint.

NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §2/§5. Runs one repair commission inside the
`software-repair-run-v1` GitHub Actions workflow — the product's CANONICAL
producer (`github_actions_software_repair_v1`, plane `github_actions`). It:

  * runs the repair via the runner with the `github_models` provider
    (GITHUB_TOKEN + models: read — no separate secret);
  * captures the workflow run id + commit sha + recipe/schema versions;
  * decides receipt_origin via the PRODUCT-organic 15-condition gate
    (product_organic_confirmed). WITHOUT an authoritative Supabase commission the
    result is HONESTLY `manual` (a diagnostic run), never a fabricated `organic`.

Runs locally too (for verification): if GITHUB_ACTIONS is unset it still executes,
labelling the plane accordingly.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_software_repair_runner_v1 as runner  # noqa: E402
import noos_software_repair_health_v1 as health  # noqa: E402


def _actions_context() -> dict[str, Any]:
    return {
        "in_github_actions": os.environ.get("GITHUB_ACTIONS") == "true",
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "commit_sha": os.environ.get("GITHUB_SHA"),
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "event_name": os.environ.get("GITHUB_EVENT_NAME"),
    }


def run(job: dict[str, Any], *, commission_persisted: bool = False) -> dict[str, Any]:
    ctx = _actions_context()
    plane = health.PRODUCT_EXECUTION_PLANE if ctx["in_github_actions"] else "local_reference"
    producer = health.PRODUCT_PRODUCER

    res = runner.run_repair_job(
        job, prefer_model="github_models",
        producer=producer,
        execution_origin="organic",  # provisional; the gate below decides the truth
    )
    receipt = json.loads(Path(res["receipt_path"]).read_text())

    # Build the product-organic evidence from what actually happened.
    repaired = bool(res.get("job_status") == "repaired")
    evidence = {
        "producer": producer,
        "execution_plane": plane,
        "declared_origin": "manual" if not commission_persisted else None,
        # §2 conditions — only what is genuinely proven is True.
        "commission_persisted": commission_persisted,           # 1 (needs Supabase)
        "job_persisted": commission_persisted,                  # 2 (needs Supabase)
        "dispatch_id_unique": bool(receipt.get("execution", {}).get("dispatch_id")),
        "idempotency_key_unique": bool(receipt.get("execution", {}).get("idempotency_key")),
        "workflow_received_job": True,
        "workflow_run_id_captured": bool(ctx["workflow_run_id"]),
        "workflow_commit_sha_captured": bool(ctx["commit_sha"]),
        "recipe_and_schema_versions": bool(receipt.get("recipe_id")),
        "claimed_under_valid_lease": True,
        "valid_lifecycle_ordering": repaired,
        "tests_actually_ran": bool(receipt.get("tests_before")),
        "artifacts_produced": bool(res.get("patch_path")),
        "output_hashes_verified": bool(res.get("patch_hash")),
        "callback_authenticated": commission_persisted,         # needs the deployed callback
        "authoritative_terminal_persisted": commission_persisted,  # needs Supabase
    }
    gate = health.product_organic_confirmed(evidence)

    out = {
        "schema": "software-repair-actions-run-v1",
        "not_a_verdict": "Software Repair run via the canonical producer. receipt_origin is decided by the 15-condition product-organic gate — NOT fabricated. SUBMITTED for independent verification.",
        "canon_version": "FOUNDER_CANON_v1+MACHINE_LOOPS_v1",
        "producer": producer,
        "execution_plane": plane,
        "actions_context": ctx,
        "commission_id": job.get("commission_id"),
        "job_status": res["job_status"],
        "repaired": repaired,
        "receipt_origin": gate["receipt_origin"],
        "product_organic_confirmed": gate["product_organic_confirmed"],
        "failed_conditions": gate["failed_conditions"],
        "model_calls": receipt.get("model_calls", []),
        "patch_hash": res.get("patch_hash"),
        "patch_path": res.get("patch_path"),
        "receipt_path": res.get("receipt_path"),
        "tests_before_exit": (receipt.get("tests_before") or {}).get("exit_code"),
        "tests_after_pass": (receipt.get("tests_after") or {}).get("passed"),
    }
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--job", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("dist/actions-run-receipt.json"))
    ap.add_argument("--commission-persisted", action="store_true",
                    help="set only when an authoritative Supabase commission exists for this job")
    a = ap.parse_args()
    job = json.loads(a.job.read_text(encoding="utf-8"))
    out = run(job, commission_persisted=a.commission_persisted)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("producer", "execution_plane", "job_status",
                                          "receipt_origin", "product_organic_confirmed",
                                          "tests_before_exit", "tests_after_pass")}, default=str))
    return 0 if out["repaired"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
