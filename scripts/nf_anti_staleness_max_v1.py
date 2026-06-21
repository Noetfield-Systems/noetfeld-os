#!/usr/bin/env python3
"""NF anti-staleness maximum — orchestrate all layers; single superset receipt."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from nf_factory_lib_v1 import agent_id, iso_now, load_event, load_json, load_sina, repo_root, write_event, write_sina


def _run(cmd: list[str], root: Path) -> tuple[int, dict]:
    try:
        out = subprocess.check_output(cmd, cwd=root, text=True, stderr=subprocess.STDOUT)
        try:
            return 0, json.loads(out)
        except json.JSONDecodeError:
            return 0, {"raw": out[:500]}
    except subprocess.CalledProcessError as exc:
        try:
            return exc.returncode, json.loads(exc.output or "{}")
        except json.JSONDecodeError:
            return exc.returncode, {"error": (exc.output or str(exc))[:300]}


def run_anti_staleness_max(*, execute: bool = False) -> dict:
    root = repo_root()
    cfg = load_json(root / "data/nf_anti_staleness_max_v1.json") or {}
    checks: list[dict] = []
    ok = True

    def record(layer: str, passed: bool, detail: str = "", data: dict | None = None) -> None:
        nonlocal ok
        checks.append({"layer": layer, "ok": passed, "detail": detail, "data": data or {}})
        if not passed:
            ok = False

    if execute:
        steps = [
            ("L0_mono", ["python3", "scripts/nf_mono_nerve_v1.py", "--json"]),
            ("L0_founder", ["python3", "scripts/nf_founder_input_sync_v1.py", "--json"]),
            ("L1_stale", ["python3", "scripts/nf_stale_guard_v1.py", "--json"]),
            ("L2_surfaces", ["python3", "scripts/nf_live_surfaces_v1.py", "--json"]),
            ("L2_cascade", ["python3", "scripts/nf_receipt_cascade_v1.py", "--json"]),
            ("L3_orient_chain", ["python3", "scripts/nf_orient_read_chain_v1.py", "--json"]),
        ]
        for layer, cmd in steps:
            rc, data = _run(cmd, root)
            record(layer, rc == 0 and bool(data.get("ok", rc == 0)), f"exit={rc}", data)

    mono = load_event("nf-mono-nerve-v1.json", root) or load_sina("nf-mono-nerve-v1.json") or {}
    record("L0_mono_receipt", bool(mono.get("ok")), mono.get("email_send_defer_line", ""), mono)

    founder = load_event("nf-founder-disk-sync-v1.json", root) or load_sina("nf-founder-disk-sync-receipt-v1.json") or {}
    record("L0_founder_receipt", bool(founder.get("ok")), founder.get("action", ""), founder)

    stale = load_event("nf-stale-guard-v1.json", root) or {}
    record("L1_stale_receipt", not stale.get("context_stale"), str(stale.get("issues")), stale)

    surfaces = load_event("nf-live-surfaces-v1.json", root) or load_sina("nf-live-surfaces-v1.json") or {}
    has_line = bool(surfaces.get("email_send_defer_line"))
    record("L2_surfaces_line", has_line, surfaces.get("email_send_defer_line", ""), surfaces)

    cascade = load_event("nf-receipt-cascade-v1.json", root) or load_sina("nf-receipt-cascade-v1.json") or {}
    record("L2_cascade", bool(cascade.get("ok")), ",".join(cascade.get("nodes") or []), cascade)

    orient = load_event("nf-orient-read-chain-v1.json", root) or load_sina("nf-orient-read-chain-v1.json") or {}
    if orient:
        record("L3_orient_chain", bool(orient.get("ok")), f"{orient.get('present')}/{orient.get('total')}", orient)
    else:
        rc, orient = _run(["python3", "scripts/nf_orient_read_chain_v1.py", "--json"], root)
        record("L3_orient_chain", rc == 0 and orient.get("ok"), "", orient)

    eco = load_sina("ecosystem-live-nerve-v1.json") or {}
    record("L3_ecosystem", bool(eco.get("ok")), eco.get("sequencing_law", ""), eco)

    ops = load_sina("noetfield-operations-inbox-active-v1.json") or {}
    defer = load_sina("commercial-email-send-defer-receipt-v1.json") or {}
    record("L3_inbox_receive", bool(ops.get("ok")), ops.get("gw_status", ""), ops)
    record("L3_outbound_defer", bool(defer.get("email_send_defer_line")), defer.get("email_send_defer_line", ""), defer)

    tf = load_sina("tf-live-surfaces-v1.json") or {}
    record("L3_trustfield_wire", bool(tf.get("email_send_defer_line")), tf.get("email_send_defer_line", ""), tf)

    email_guard = load_event("nf-email-lane-guard-v1.json", root) or load_sina("nf-email-lane-guard-v1.json") or {}
    if not email_guard:
        rc, email_guard = _run(["python3", "scripts/nf_email_lane_guard_v1.py", "--json"], root)
        record("L4_email_lane", email_guard.get("ok", True), email_guard.get("reason", ""), email_guard)
    else:
        record("L4_email_lane", email_guard.get("ok", True), "", email_guard)

    reply_path = root / "reports/cursor-reply-latest.txt"
    if reply_path.is_file():
        rc, lang = _run(
            ["python3", "scripts/nf_agent_report_language_gate_v1.py", "--scan-file", str(reply_path), "--json"],
            root,
        )
        record("L5_language", rc == 0 and lang.get("ok"), f"score={lang.get('score')}", lang)
    else:
        record("L5_language", True, "skip:no cursor-reply", {})

    receipt = {
        "schema_version": "nf-anti-staleness-max-v1",
        "generated_at": iso_now(),
        "ok": ok,
        "agent_id": agent_id(),
        "law_doc": cfg.get("law_doc"),
        "checks": checks,
        "product_now_line": surfaces.get("product_now_line"),
        "email_send_defer_line": surfaces.get("email_send_defer_line") or mono.get("email_send_defer_line"),
        "defer_active": surfaces.get("defer_active") if surfaces.get("defer_active") is not None else mono.get("defer_active"),
        "heal": None if ok else "make nf-onboard",
    }
    write_event("nf-anti-staleness-max-v1.json", receipt, root)
    write_sina("nf-anti-staleness-max-v1.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--execute", action="store_true", help="Re-run layer scripts before assess")
    args = parser.parse_args()
    receipt = run_anti_staleness_max(execute=args.execute)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        status = "PASS" if receipt["ok"] else "FAIL"
        print(f"nf_anti_staleness_max: {status}")
        print(f"  defer: {receipt.get('email_send_defer_line')}")
        for c in receipt.get("checks") or []:
            if not c.get("ok"):
                print(f"  FAIL {c['layer']}: {c.get('detail')}")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
