#!/usr/bin/env python3
"""NOOS Motor v1 — local reference executor (offline sellable vertical slice).

NF-NOOS-MOTOR-V1-FULL-RUNWAY, Phase 5. This is the end-to-end product path that
runs WITHOUT any cloud dependency, so the motor can be demonstrated, verified,
and sold today:

    CUSTOMER INPUT -> VALIDATION -> PLAN -> MOTOR EXECUTION (FSM) ->
    REAL OUTPUT ARTIFACT -> AUTHORITATIVE RECEIPT -> RETRIEVAL -> REPLAY

PROVENANCE HONESTY (CORRECTED, NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §2): this
executor performs REAL work, but it is NOT the production canonical producer, so
its receipts carry ``receipt_origin=local_reference`` (NOT ``organic``),
``producer=noos-motor-local-executor-v1`` and ``execution_plane=local_reference``.
A local_reference receipt proves product BEHAVIOR; it can NEVER establish
deployed-system liveness (see production_running_confirmed in the classifier).
The cloud canonical ``http_loop`` cycles remain a separate production step.

The representative product task is ``digest``: given a set of records it computes
a deterministic, integrity-hashed summary artifact (real customer value) — a
normalized JSON output plus a human-readable Markdown report.
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

import noos_motor_state_machine_v1 as fsm  # noqa: E402

PRODUCER = "noos-motor-local-executor-v1"
EXECUTION_PLANE = "local_reference"
DEFAULT_ARTIFACT_DIR = ROOT / "receipts" / "runway" / "artifacts"
DEFAULT_RECEIPT_DIR = ROOT / "receipts" / "runway" / "executions"
SUPPORTED_TASKS = ("digest",)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


# ---- Phase 5 step 2: validation --------------------------------------------
def validate_input(job: Any) -> list[str]:
    """Return a list of human-readable validation errors ([] => valid)."""
    errors: list[str] = []
    if not isinstance(job, dict):
        return ["input must be a JSON object"]
    task = job.get("task_kind")
    if task not in SUPPORTED_TASKS:
        errors.append(f"task_kind must be one of {SUPPORTED_TASKS}, got {task!r}")
    if task == "digest":
        records = job.get("records")
        if not isinstance(records, list) or not records:
            errors.append("digest requires a non-empty 'records' list")
        elif not all(isinstance(r, dict) for r in records):
            errors.append("every record must be a JSON object")
    return errors


# ---- Phase 5 step 3: deterministic plan ------------------------------------
def build_plan(job: dict[str, Any]) -> dict[str, Any]:
    task = job["task_kind"]
    if task == "digest":
        steps = ["validate", "normalize_records", "aggregate", "render_report", "hash_and_commit"]
    else:  # pragma: no cover - guarded by validate_input
        steps = ["validate", "execute", "hash_and_commit"]
    plan = {"task_kind": task, "steps": steps, "record_count": len(job.get("records", []))}
    plan["plan_hash"] = fsm.payload_hash(plan)
    return plan


# ---- Phase 5 step 6: the real work + real artifact -------------------------
def _run_digest(job: dict[str, Any]) -> dict[str, Any]:
    """Deterministic transform: normalized aggregate over the records."""
    records = job["records"]
    keys: dict[str, int] = {}
    numeric_sums: dict[str, float] = {}
    for r in records:
        for k, v in r.items():
            keys[k] = keys.get(k, 0) + 1
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                numeric_sums[k] = numeric_sums.get(k, 0.0) + float(v)
    canonical = json.dumps(records, sort_keys=True, default=str)
    return {
        "title": job.get("title", "NOOS digest"),
        "record_count": len(records),
        "field_frequency": dict(sorted(keys.items())),
        "numeric_totals": {k: numeric_sums[k] for k in sorted(numeric_sums)},
        "records_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def _render_markdown(output: dict[str, Any], ex: "fsm.MotorExecution") -> str:
    lines = [
        f"# {output['title']}",
        "",
        f"- Execution ID: `{ex.execution_id}`",
        f"- Correlation ID: `{ex.correlation_id}`",
        f"- Producer: `{PRODUCER}` (plane: {EXECUTION_PLANE})",
        f"- Records: **{output['record_count']}**",
        f"- Records SHA-256: `{output['records_sha256']}`",
        "",
        "## Field frequency",
        "",
        "| field | count |",
        "|---|---:|",
    ]
    for k, v in output["field_frequency"].items():
        lines.append(f"| {k} | {v} |")
    if output["numeric_totals"]:
        lines += ["", "## Numeric totals", "", "| field | total |", "|---|---:|"]
        for k, v in output["numeric_totals"].items():
            lines.append(f"| {k} | {v} |")
    lines.append("")
    return "\n".join(lines)


# ---- Phase 5 steps 1-11: the full product path -----------------------------
def run_job(
    job: Any,
    *,
    now: str | None = None,
    artifact_dir: Path | None = None,
    receipt_dir: Path | None = None,
    ledger: "fsm.MotorLedger | None" = None,
    execution_origin: str = fsm.ORIGIN_LOCAL_REFERENCE,
) -> dict[str, Any]:
    """Drive one customer input through the entire organic motor path.

    Returns a result dict with the execution record, artifact paths and status.
    A truthful FAILED result (no artifact) is returned for invalid input."""
    now = now or utc_now()
    artifact_dir = artifact_dir or DEFAULT_ARTIFACT_DIR
    receipt_dir = receipt_dir or DEFAULT_RECEIPT_DIR
    ledger = ledger if ledger is not None else fsm.MotorLedger()

    errors = validate_input(job)
    task_kind = job.get("task_kind", "invalid") if isinstance(job, dict) else "invalid"
    payload = job if isinstance(job, dict) else {"raw": job}

    ex, created = ledger.submit(
        task_kind=task_kind, payload=payload, now=now,
        producer=PRODUCER, execution_origin=execution_origin,
    )
    if not created:
        # Idempotency: same input already ran; return the existing terminal run
        # rather than executing a duplicate logical job (Phase 5 step 11).
        return _result(ex, artifact_dir, receipt_dir, deduplicated=True)

    if errors:
        # Truthful failure — validation rejects before any plan/dispatch.
        ex.fail(now=now, error_code="invalid_input", error_summary="; ".join(errors))
        return _result(ex, artifact_dir, receipt_dir, validation_errors=errors)

    # Plan -> dispatch -> claim -> run
    plan = build_plan(payload)
    ex.plan(now=now, dispatch_id=f"dsp_{ex.execution_id[4:12]}")
    ex.dispatch(now=now)
    ex.claim(now=now, owner="local-worker-1", lease_ttl_seconds=120)
    ex.start(now=now)

    try:
        output = _run_digest(payload) if task_kind == "digest" else {"echo": payload}
    except Exception as exc:  # pragma: no cover - defensive
        ex.fail(now=now, error_code="execution_error", error_summary=str(exc))
        return _result(ex, artifact_dir, receipt_dir)

    # Commit the REAL output artifact (JSON + Markdown), bound to the execution.
    artifact_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifact_dir / f"{ex.execution_id}.output.json"
    md_path = artifact_dir / f"{ex.execution_id}.report.md"
    json_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifact_uri = json_path.as_uri()
    ex.commit_output(now=now, output=output, artifact_uri=artifact_uri)
    md_path.write_text(_render_markdown(output, ex), encoding="utf-8")
    ex.complete(now=now)

    return _result(ex, artifact_dir, receipt_dir, output=output)


def _result(
    ex: "fsm.MotorExecution",
    artifact_dir: Path,
    receipt_dir: Path,
    *,
    output: dict[str, Any] | None = None,
    validation_errors: list[str] | None = None,
    deduplicated: bool = False,
) -> dict[str, Any]:
    receipt = build_receipt(ex, deduplicated=deduplicated, validation_errors=validation_errors)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipt_dir / f"{ex.execution_id}.receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return {
        "execution_id": ex.execution_id,
        "status": ex.state,
        "ok": ex.state == fsm.COMPLETED,
        "deduplicated": deduplicated,
        "artifact_uri": ex.artifact_uri,
        "json_artifact": str((artifact_dir / f"{ex.execution_id}.output.json")) if ex.artifact_uri else None,
        "md_artifact": str((artifact_dir / f"{ex.execution_id}.report.md")) if ex.artifact_uri else None,
        "output_hash": ex.output_hash,
        "receipt_path": str(receipt_path),
        "output": output,
        "validation_errors": validation_errors or [],
        "record": ex.to_record(),
    }


def build_receipt(
    ex: "fsm.MotorExecution",
    *,
    deduplicated: bool = False,
    validation_errors: list[str] | None = None,
) -> dict[str, Any]:
    """Provenance-aware lifecycle receipt (directive Phase 4 field set)."""
    rec = ex.to_record()
    return {
        "schema": "noos-motor-execution-receipt-v1",
        "not_a_verdict": "Local reference execution receipt. receipt_origin=local_reference (NOT organic, NOT cloud http_loop); proves product behavior, never deployed liveness. SUBMITTED for independent verification.",
        "canon_version": "FOUNDER_CANON_v1+MACHINE_LOOPS_v1",
        "receipt_origin": fsm.ORIGIN_LOCAL_REFERENCE,
        "execution_plane": EXECUTION_PLANE,
        "producer": PRODUCER,
        "deduplicated": deduplicated,
        "validation_errors": validation_errors or [],
        **rec,
    }


def retrieve(execution_id: str, *, receipt_dir: Path | None = None, artifact_dir: Path | None = None) -> dict[str, Any]:
    """Phase 5 steps 9-10: customer retrieval of output + receipt + provenance."""
    receipt_dir = receipt_dir or DEFAULT_RECEIPT_DIR
    artifact_dir = artifact_dir or DEFAULT_ARTIFACT_DIR
    receipt_path = receipt_dir / f"{execution_id}.receipt.json"
    if not receipt_path.is_file():
        return {"ok": False, "error": f"no receipt for {execution_id}"}
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    json_path = artifact_dir / f"{execution_id}.output.json"
    output = json.loads(json_path.read_text(encoding="utf-8")) if json_path.is_file() else None
    integrity_ok = None
    if output is not None and receipt.get("output_hash"):
        integrity_ok = fsm.payload_hash(output) == receipt["output_hash"]
    return {
        "ok": True,
        "execution_id": execution_id,
        "status": receipt.get("state"),
        "receipt": receipt,
        "output": output,
        "artifact_uri": receipt.get("artifact_uri"),
        "output_integrity_ok": integrity_ok,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, help="JSON job file")
    ap.add_argument("--input-json", help="inline JSON job")
    ap.add_argument("--status", help="retrieve an execution_id instead of running")
    ap.add_argument("--artifact-dir", type=Path, default=None)
    ap.add_argument("--receipt-dir", type=Path, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.status:
        res = retrieve(args.status, receipt_dir=args.receipt_dir, artifact_dir=args.artifact_dir)
        print(json.dumps(res, indent=2) if args.json else f"{args.status}: {res.get('status')} integrity={res.get('output_integrity_ok')}")
        return 0 if res.get("ok") else 1

    if args.input:
        job = json.loads(args.input.read_text(encoding="utf-8"))
    elif args.input_json:
        job = json.loads(args.input_json)
    else:
        ap.error("one of --input / --input-json / --status is required")
        return 2

    res = run_job(job, artifact_dir=args.artifact_dir, receipt_dir=args.receipt_dir)
    if args.json:
        print(json.dumps({k: v for k, v in res.items() if k != "record"}, indent=2))
    else:
        print(
            f"execution={res['execution_id']} status={res['status']} "
            f"artifact={res['json_artifact']} output_hash={res['output_hash']}"
        )
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
