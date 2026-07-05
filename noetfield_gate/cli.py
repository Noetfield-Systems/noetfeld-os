"""CLI: noetfield gate | noetfield decide"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from noetfield_gate import __version__
from noetfield_gate.boot import DEFAULT_RECEIPT, resolve_root, run_gate_checks, write_gate_report
from noetfield_gate.decide import (
    SAMPLE_BLOCK_INTENT,
    SAMPLE_INTENT,
    build_receipt,
    default_out_path,
    post_decision,
    write_receipt,
)
from noetfield_gate.intent_validate import validate_intent_file
from noetfield_gate.verify import verify_chain


def _cmd_deploy(args: argparse.Namespace) -> int:
    import subprocess

    cmd = [sys.executable, "scripts/noetfield_deploy_v1.py", "deploy", "--scope", args.scope]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.write_receipt:
        cmd.append("--write-receipt")
    if args.json:
        cmd.append("--json")
    proc = subprocess.run(cmd, cwd=resolve_root(), check=False)
    return proc.returncode


def _cmd_gate(args: argparse.Namespace) -> int:
    report = run_gate_checks(
        root=Path(args.root) if args.root else None,
        api_url=args.api_url,
        strict=bool(args.strict),
        include_pytest=bool(args.pytest),
    )
    out = write_gate_report(report, Path(args.out) if args.out else DEFAULT_RECEIPT)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['outcome']} — gate report -> {out}")
    if report["outcome"] == "BLOCK":
        for reason in report.get("block_reasons", []):
            print(f"  BLOCK: {reason}", file=sys.stderr)
        return 1
    return 0


def _cmd_decide(args: argparse.Namespace) -> int:
    if args.sample_block:
        intent = dict(SAMPLE_BLOCK_INTENT)
    elif args.sample:
        intent = dict(SAMPLE_INTENT)
    elif args.file:
        file_path = Path(args.file)
        validation = validate_intent_file(file_path)
        if args.validate_only:
            print(json.dumps(validation, indent=2))
            return 0
        intent = json.loads(file_path.read_text(encoding="utf-8"))
    else:
        print("Provide --sample, --sample-block, or --file intent.json", file=sys.stderr)
        return 2
    if args.request_id:
        intent["request_id"] = args.request_id
    resp = post_decision(intent, api_url=args.api_url, api_key_value=args.api_key)
    receipt = build_receipt(resp, intent=intent)
    out = write_receipt(receipt, Path(args.out) if args.out else default_out_path())
    decision = resp.get("decision", "UNKNOWN")
    print(f"OK — {decision} score={resp.get('composite_score')} receipt -> {out}")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    report = verify_chain(
        root=Path(args.root) if args.root else None,
        gate_report=Path(args.gate_report) if args.gate_report else None,
        receipt_path=Path(args.receipt) if args.receipt else None,
        api_url=args.api_url,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['outcome']} — verify chain ({len(report.get('checks', []))} checks)")
    return 0 if report["outcome"] == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="noetfield",
        description="Noetfield chain tools — gate before execution, decide with receipt",
    )
    parser.add_argument("--version", action="version", version=f"noetfield-gate {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    gate = sub.add_parser("gate", help="4+ checks → PASS/BLOCK + GATE_REPORT on disk")
    gate.add_argument("--root", help="Noetfield OS repo root (auto-detect if omitted)")
    gate.add_argument("--api-url", help="Probe GET /readiness (or NOETFIELD_API_URL)")
    gate.add_argument("--json", action="store_true", help="Print gate report JSON on stdout (UPG-0152)")
    gate.add_argument(
        "--strict",
        action="store_true",
        help="Fail on skipped checks when API URL is set (UPG-0153)",
    )
    gate.add_argument(
        "--pytest",
        action="store_true",
        help="Include G6 pytest suite check (UPG-0154)",
    )
    gate.add_argument("--out", help=f"JSON report path (default {DEFAULT_RECEIPT})")
    gate.set_defaults(func=_cmd_gate)

    decide = sub.add_parser("decide", help="POST /v1/decision → receipt JSON")
    decide.add_argument("--sample", action="store_true", help="Use built-in sample credit intent (APPROVE path)")
    decide.add_argument(
        "--sample-block",
        action="store_true",
        help="Use built-in extreme-DTI intent (DECLINE corridor path)",
    )
    decide.add_argument("--file", help="Path to intent JSON")
    decide.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate intent JSON against DecisionRequest schema only (UPG-0156)",
    )
    decide.add_argument("--request-id", help="Optional idempotency key")
    decide.add_argument("--api-url", help="API base (default http://127.0.0.1:8001)")
    decide.add_argument("--api-key", help="X-API-Key (or NOETFIELD_API_KEY)")
    decide.add_argument("--out", help="Receipt output path")
    decide.set_defaults(func=_cmd_decide)

    verify = sub.add_parser("verify", help="Gate report + optional receipt chain (UPG-0158)")
    verify.add_argument("--root", help="Noetfield OS repo root")
    verify.add_argument("--gate-report", help="Existing gate report JSON path")
    verify.add_argument("--receipt", help="Decision receipt JSON to validate")
    verify.add_argument("--api-url", help="Probe GET /readiness")
    verify.add_argument("--json", action="store_true")
    verify.set_defaults(func=_cmd_verify)

    deploy = sub.add_parser("deploy", help="Unified deploy by scope (UPG-0203)")
    deploy.add_argument(
        "--scope",
        required=True,
        choices=["fly-inbox", "fly-self-heal", "gel-api", "www"],
    )
    deploy.add_argument("--dry-run", action="store_true")
    deploy.add_argument("--write-receipt", action="store_true")
    deploy.add_argument("--json", action="store_true")
    deploy.set_defaults(func=_cmd_deploy)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
