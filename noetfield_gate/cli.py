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


def _cmd_gate(args: argparse.Namespace) -> int:
    report = run_gate_checks(root=Path(args.root) if args.root else None, api_url=args.api_url)
    out = write_gate_report(report, Path(args.out) if args.out else DEFAULT_RECEIPT)
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
        intent = json.loads(Path(args.file).read_text(encoding="utf-8"))
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
    decide.add_argument("--request-id", help="Optional idempotency key")
    decide.add_argument("--api-url", help="API base (default http://127.0.0.1:8001)")
    decide.add_argument("--api-key", help="X-API-Key (or NOETFIELD_API_KEY)")
    decide.add_argument("--out", help="Receipt output path")
    decide.set_defaults(func=_cmd_decide)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
