#!/usr/bin/env python3
"""Prove NF-GAOS W3 factory spine — positive + negative machine proofs.

Writes: reports/agent-auto/events/nf-factory-spine-proof-v1.json
        ~/.sina/nf-factory-spine-proof-v1.json

Law: docs/ops/NF_GAOS_W3_FACTORY_SPINE_LOCKED_v1.md
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from nf_factory_lib_v1 import (
    first_pending_task,
    iso_now,
    load_event,
    load_json,
    load_sina,
    repo_root,
    write_event,
    write_sina,
)


def _run(cmd: list[str], root: Path, env: dict | None = None) -> tuple[int, str]:
    merged = {**os.environ, **(env or {})}
    try:
        out = subprocess.check_output(cmd, cwd=root, text=True, stderr=subprocess.STDOUT, env=merged)
        return 0, out.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, (e.output or "").strip()


def _proof(name: str, ok: bool, detail: str, proofs: list[dict]) -> None:
    proofs.append({"proof": name, "ok": ok, "detail": detail})
    mark = "OK" if ok else "FAIL"
    print(f"{mark}   prove: {name} — {detail}")
    if not ok:
        print(f"      {detail}", file=sys.stderr)


def prove_receipts_on_disk(root: Path, proofs: list[dict]) -> None:
    repo_files = [
        "nf-mono-nerve-v1.json",
        "nf-anti-staleness-max-v1.json",
        "nf-orient-read-chain-v1.json",
        "nf-founder-disk-sync-v1.json",
        "nf-session-gate-v1.json",
        "nf-stale-guard-v1.json",
        "nf-voyage-integrity-v1.json",
        "nf-live-routing-v1.json",
        "nf-live-surfaces-v1.json",
        "nf-receipt-cascade-v1.json",
        "nf-truth-bundle-v1.json",
        "nf-gatekeeper-v1.json",
    ]
    missing = [f for f in repo_files if not (root / "reports/agent-auto/events" / f).is_file()]
    sina_files = [
        "nf-mono-nerve-v1.json",
        "nf_session_gate_receipt_v1.json",
        "nf-live-surfaces-v1.json",
        "nf-truth-bundle-v1.json",
        "nf-receipt-cascade-v1.json",
        "nf-gatekeeper-receipt-v1.json",
    ]
    sina_missing = [f for f in sina_files if not (Path.home() / ".sina" / f).is_file()]
    ok = not missing and not sina_missing
    detail = "all receipts present" if ok else f"repo_missing={missing} sina_missing={sina_missing}"
    _proof("receipts_on_disk", ok, detail, proofs)


def prove_product_now_line_matches_plan(root: Path, proofs: list[dict]) -> None:
    plan_path = root / "os/plan.json"
    plan = load_json(plan_path) or {}
    pending = first_pending_task(plan)
    surfaces = load_event("nf-live-surfaces-v1.json", root) or load_sina("nf-live-surfaces-v1.json") or {}
    line = surfaces.get("product_now_line", "")
    if not pending:
        ok = line == "no pending next_tasks"
        _proof("product_now_line_plan", ok, f"line={line!r}", proofs)
        return
    expected = f"{pending.get('id')} — {pending.get('title')}"
    ok = line == expected
    _proof("product_now_line_plan", ok, f"expected={expected!r} got={line!r}", proofs)


def prove_stale_injection_denies(root: Path, proofs: list[dict]) -> None:
    events = root / "reports/agent-auto/events"
    stale_path = events / "nf-stale-guard-v1.json"
    backup = stale_path.read_text(encoding="utf-8") if stale_path.is_file() else None
    try:
        injected = {
            "schema_version": "nf-stale-guard-v1",
            "generated_at": iso_now(),
            "context_stale": True,
            "pending_task": {"id": "PROOF-STALE"},
            "issues": ["PROOF_INJECTED_STALE"],
            "heal": "make nf-onboard",
        }
        stale_path.write_text(json.dumps(injected, indent=2) + "\n", encoding="utf-8")

        rc_c, out_c = _run(["python3", "scripts/nf_receipt_cascade_v1.py", "--json"], root)
        cascade = load_event("nf-receipt-cascade-v1.json", root) or {}
        cascade_fail = rc_c != 0 and not cascade.get("ok", True)
        has_stale_node = "nf_stale_guard" in (cascade.get("nodes") or [])

        rc_g, out_g = _run(["python3", "scripts/nf_gatekeeper_v1.py", "--json"], root)
        gate = load_event("nf-gatekeeper-v1.json", root) or {}
        gate_denied = rc_g != 0 and not gate.get("safe_to_implement", True)
        has_stale_reason = "CONTEXT_STALE" in (gate.get("reasons") or [])

        ok = cascade_fail and has_stale_node and gate_denied and has_stale_reason
        _proof(
            "stale_injection_denies",
            ok,
            f"cascade_fail={cascade_fail} stale_node={has_stale_node} "
            f"gate_denied={gate_denied} stale_reason={has_stale_reason}",
            proofs,
        )
    finally:
        if backup is not None:
            stale_path.write_text(backup, encoding="utf-8")
        else:
            stale_path.unlink(missing_ok=True)
        _run(["make", "nf-onboard"], root)


def prove_founder_implement_required(root: Path, proofs: list[dict]) -> None:
    env = {k: v for k, v in os.environ.items() if k != "NF_FOUNDER_IMPLEMENT"}
    rc, _ = _run(
        ["python3", "scripts/nf_gatekeeper_v1.py", "--json", "--require-implement"],
        root,
        env=env,
    )
    gate = load_event("nf-gatekeeper-v1.json", root) or {}
    ok = rc != 0 and "FOUNDER_IMPLEMENT_REQUIRED" in (gate.get("reasons") or [])
    _proof("founder_implement_required", ok, f"exit={rc} reasons={gate.get('reasons')}", proofs)


def prove_founder_implement_passes(root: Path, proofs: list[dict]) -> None:
    _run(["make", "nf-onboard"], root)
    rc, _ = _run(
        ["python3", "scripts/nf_gatekeeper_v1.py", "--json", "--require-implement"],
        root,
        env={**os.environ, "NF_FOUNDER_IMPLEMENT": "1"},
    )
    gate = load_event("nf-gatekeeper-v1.json", root) or {}
    ok = rc == 0 and gate.get("safe_to_implement") is True
    _proof("founder_implement_passes", ok, f"exit={rc} safe={gate.get('safe_to_implement')}", proofs)


def prove_executor_lock(root: Path, proofs: list[dict]) -> None:
    from nf_factory_lib_v1 import load_lock, load_event

    lock_event = root / "reports/agent-auto/events/nf-executor-lock-v1.json"
    backup_sina = None
    backup_repo = lock_event.read_text(encoding="utf-8") if lock_event.is_file() else None
    sina_path = Path.home() / ".sina/nf-executor-lock-v1.json"
    if sina_path.is_file():
        backup_sina = sina_path.read_text(encoding="utf-8")
    try:
        rc_a, _ = _run(["python3", "scripts/nf_executor_lock_v1.py", "release"], root)
        rc_b, _ = _run(
            ["python3", "scripts/nf_executor_lock_v1.py", "acquire", "--task", "PROOF-LOCK"],
            root,
        )
        data = load_lock() or load_event("nf-executor-lock-v1.json", root) or {}
        rc_c, _ = _run(["python3", "scripts/nf_executor_lock_v1.py", "release"], root)
        ok = rc_a == 0 and rc_b == 0 and data.get("locked") is True and rc_c == 0
        _proof("executor_lock_acquire_release", ok, f"locked={data.get('locked')}", proofs)
    finally:
        if backup_repo is not None:
            lock_event.write_text(backup_repo, encoding="utf-8")
        elif lock_event.is_file():
            lock_event.unlink()
        if backup_sina is not None:
            sina_path.write_text(backup_sina, encoding="utf-8")
        elif sina_path.is_file():
            sina_path.unlink(missing_ok=True)


def prove_truth_bundle_keys(root: Path, proofs: list[dict]) -> None:
    _run(["python3", "scripts/nf_truth_bundle_v1.py", "--json"], root)
    bundle = load_event("nf-truth-bundle-v1.json", root) or load_sina("nf-truth-bundle-v1.json") or {}
    required = [
        "mono_nerve",
        "ecosystem_nerve",
        "session_gate",
        "stale_guard",
        "voyage_integrity",
        "live_surfaces",
        "product_now_line",
        "email_send_defer_line",
        "ecosystem_nerve",
        "portfolio",
    ]
    missing = [k for k in required if not bundle.get(k) and k != "portfolio"]
    # portfolio optional if registry absent
    if bundle.get("portfolio") is None:
        required = [k for k in required if k != "portfolio"]
        missing = [k for k in required if not bundle.get(k)]
    ok = not missing and bool(bundle.get("product_now_line"))
    _proof("truth_bundle_keys", ok, f"missing={missing} line={bundle.get('product_now_line')!r}", proofs)


def prove_onboard_pipeline(root: Path, proofs: list[dict]) -> None:
    rc, _ = _run(["make", "nf-onboard"], root)
    ok = rc == 0
    _proof("onboard_pipeline_exit_0", ok, f"exit={rc}", proofs)


def prove_mono_nerve_wired(root: Path, proofs: list[dict]) -> None:
    mono = load_event("nf-mono-nerve-v1.json", root) or load_sina("nf-mono-nerve-v1.json") or {}
    ok = bool(mono.get("ok")) and bool(mono.get("email_send_defer_line"))
    _proof("mono_nerve_wired", ok, f"line={mono.get('email_send_defer_line')!r}", proofs)


def prove_email_defer_line_on_surfaces(root: Path, proofs: list[dict]) -> None:
    surfaces = load_event("nf-live-surfaces-v1.json", root) or load_sina("nf-live-surfaces-v1.json") or {}
    line = surfaces.get("email_send_defer_line") or ""
    ok = bool(line) and "email-defer" in line
    _proof("email_defer_line_surfaces", ok, f"line={line!r}", proofs)


def prove_email_task_denied_when_defer(root: Path, proofs: list[dict]) -> None:
    events = root / "reports/agent-auto/events"
    plan_path = root / "os/plan.json"
    plan = load_json(plan_path) or {}
    backup_plan = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else None
    try:
        injected = dict(plan)
        injected["next_tasks"] = [
            {
                "id": "PROOF-RESEND-WIRE",
                "title": "Wire Resend auto-notify on www intake",
                "status": "pending",
            }
        ]
        plan_path.write_text(json.dumps(injected, indent=2) + "\n", encoding="utf-8")
        _run(["python3", "scripts/nf_live_surfaces_v1.py", "--json"], root)
        _run(["python3", "scripts/nf_gatekeeper_v1.py", "--json"], root)
        gate = load_event("nf-gatekeeper-v1.json", root) or {}
        surfaces = load_event("nf-live-surfaces-v1.json", root) or {}
        denied = "EMAIL_SEND_DEFERRED" in (gate.get("reasons") or [])
        defer_on = bool(surfaces.get("defer_active"))
        ok = denied if defer_on else True
        _proof("email_task_denied_when_defer", ok, f"denied={denied} defer={defer_on}", proofs)
    finally:
        if backup_plan is not None:
            plan_path.write_text(backup_plan, encoding="utf-8")
        _run(["make", "nf-onboard"], root)


def prove_ecosystem_nerve_linked(root: Path, proofs: list[dict]) -> None:
    eco = load_sina("ecosystem-live-nerve-v1.json") or {}
    ok = bool(eco.get("ok")) and bool(eco.get("email_send_defer_line"))
    planes = eco.get("planes") or {}
    nf_ok = (planes.get("noetfield") or {}).get("ok")
    ok = ok and bool(nf_ok)
    _proof("ecosystem_nerve_linked", ok, f"line={eco.get('email_send_defer_line')!r}", proofs)


def prove_anti_staleness_max(root: Path, proofs: list[dict]) -> None:
    max_r = load_event("nf-anti-staleness-max-v1.json", root) or load_sina("nf-anti-staleness-max-v1.json") or {}
    ok = bool(max_r.get("ok")) and bool(max_r.get("email_send_defer_line"))
    _proof("anti_staleness_max", ok, f"checks={len(max_r.get('checks') or [])}", proofs)


def prove_orient_read_chain(root: Path, proofs: list[dict]) -> None:
    orient = load_event("nf-orient-read-chain-v1.json", root) or load_sina("nf-orient-read-chain-v1.json") or {}
    ok = bool(orient.get("ok")) and not orient.get("missing")
    _proof("orient_read_chain", ok, f"{orient.get('present')}/{orient.get('total')}", proofs)


def prove_cascade_ssot_shape(root: Path, proofs: list[dict]) -> None:
    ssot = load_json(root / "data/nf_orient_routing_v1.json") or {}
    sources = ssot.get("receipt_cascade_sources") or []
    has_mono = any(s.get("id") == "nf_mono_nerve" for s in sources)
    has_founder = any(s.get("id") == "nf_founder_disk_sync" for s in sources)
    has_orient = any(s.get("id") == "nf_orient_read_chain" for s in sources)
    ok = len(sources) >= 8 and bool(ssot.get("session_start_rule")) and has_mono and has_founder and has_orient
    _proof("cascade_ssot_shape", ok, f"sources={len(sources)} mono={has_mono} founder={has_founder} orient={has_orient}", proofs)


def run_all_proofs(root: Path | None = None) -> dict:
    root = root or repo_root()
    proofs: list[dict] = []

    prove_cascade_ssot_shape(root, proofs)
    prove_onboard_pipeline(root, proofs)
    prove_mono_nerve_wired(root, proofs)
    prove_ecosystem_nerve_linked(root, proofs)
    prove_email_defer_line_on_surfaces(root, proofs)
    prove_orient_read_chain(root, proofs)
    prove_anti_staleness_max(root, proofs)
    prove_receipts_on_disk(root, proofs)
    prove_product_now_line_matches_plan(root, proofs)
    prove_truth_bundle_keys(root, proofs)
    prove_stale_injection_denies(root, proofs)
    prove_email_task_denied_when_defer(root, proofs)
    prove_founder_implement_required(root, proofs)
    prove_founder_implement_passes(root, proofs)
    prove_executor_lock(root, proofs)

    ok = all(p["ok"] for p in proofs)
    report = {
        "schema_version": "nf-factory-spine-proof-v1",
        "generated_at": iso_now(),
        "ok": ok,
        "proof_count": len(proofs),
        "passed": sum(1 for p in proofs if p["ok"]),
        "failed": sum(1 for p in proofs if not p["ok"]),
        "proofs": proofs,
        "product_now_line": (load_sina("nf-live-surfaces-v1.json") or {}).get("product_now_line"),
    }
    write_event("nf-factory-spine-proof-v1.json", report, root)
    write_sina("nf-factory-spine-proof-v1.json", report)
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Prove NF factory spine (machine)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    print("=== prove-nf-factory-spine-v1 ===")
    report = run_all_proofs()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("")
        print(f"prove-nf-factory-spine-v1: {'PASS' if report['ok'] else 'FAIL'} "
              f"({report['passed']}/{report['proof_count']})")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
