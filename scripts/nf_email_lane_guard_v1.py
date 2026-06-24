#!/usr/bin/env python3
"""Email lane edit guard — block Resend/intake wiring when defer ON."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from nf_factory_lib_v1 import iso_now, load_json, load_sina, repo_root, write_event, write_sina
from nf_mono_nerve_v1 import task_touches_email_lane


def _email_lane_paths(root: Path) -> list[str]:
    cfg = load_json(root / "data/nf_anti_staleness_max_v1.json") or {}
    return list(cfg.get("email_lane_paths") or [
        "api/_lib/intake-email.js",
        "api/intake.js",
        "scripts/setup-resend-domain.sh",
        "scripts/auto-heal-www.sh",
        "docs/ops/VERCEL_INTAKE_SETUP.md",
    ])


def run_email_lane_guard(*, paths: list[str] | None = None) -> dict:
    root = repo_root()
    mono = load_sina("nf-mono-nerve-v1.json") or {}
    defer = load_sina("commercial-email-send-defer-receipt-v1.json") or {}
    defer_active = mono.get("defer_active")
    if defer_active is None:
        defer_active = defer.get("defer_active", True)

    check_paths = paths or []
    if not check_paths:
        env_paths = os.environ.get("NF_EMAIL_LANE_PATHS", "").strip()
        task = os.environ.get("NF_TASK_ID", "").strip()
        require = os.environ.get("NF_EMAIL_LANE_EDIT", "").strip().lower() in ("1", "true", "yes")
        if env_paths:
            check_paths = [p.strip() for p in env_paths.split(",") if p.strip()]
        elif require or task:
            blocked = defer_active and task_touches_email_lane(
                {"id": task or "resend-wiring", "title": task or "resend-wiring"}
            )
        else:
            blocked = False
        receipt = {
            "schema_version": "nf-email-lane-guard-v1",
            "generated_at": iso_now(),
            "ok": not blocked,
            "defer_active": defer_active,
            "email_send_defer_line": mono.get("email_send_defer_line") or defer.get("email_send_defer_line"),
            "task_checked": task or None,
            "email_lane_paths": _email_lane_paths(root),
            "blocked": blocked,
            "reason": "EMAIL_LANE_EDIT_BLOCKED" if blocked else None,
            "law": "Resend/form auto-send DEFERRED post-factory — see COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md",
        }
        write_event("nf-email-lane-guard-v1.json", receipt, root)
        write_sina("nf-email-lane-guard-v1.json", receipt)
        return receipt

    hits = [p for p in check_paths if (root / p).is_file() or Path(p).is_file()]
    blocked = defer_active and bool(hits)
    receipt = {
        "schema_version": "nf-email-lane-guard-v1",
        "generated_at": iso_now(),
        "ok": not blocked,
        "defer_active": defer_active,
        "paths_checked": check_paths,
        "paths_hit": hits,
        "blocked": blocked,
        "reason": "EMAIL_LANE_EDIT_BLOCKED" if blocked else None,
    }
    write_event("nf-email-lane-guard-v1.json", receipt, root)
    write_sina("nf-email-lane-guard-v1.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--path", action="append", default=[], help="Path(s) about to be edited")
    args = parser.parse_args()
    require = os.environ.get("NF_EMAIL_LANE_EDIT", "").strip().lower() in ("1", "true", "yes")
    receipt = run_email_lane_guard(paths=args.path or None)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        if receipt.get("blocked"):
            print(f"BLOCKED: {receipt.get('reason')} — defer ON")
            print(f"  {receipt.get('email_send_defer_line')}")
        else:
            print("OK: email lane edit allowed (defer lifted or non-email path)")
    if require and receipt.get("blocked"):
        return 2
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
