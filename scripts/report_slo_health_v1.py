#!/usr/bin/env python3
"""Run a command and report it against an explicit SLO budget."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", required=True, help="Human-readable workflow scope.")
    parser.add_argument("--budget-seconds", type=float, required=True, help="SLO budget in seconds.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --")
    args = parser.parse_args()

    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        print("missing command after --", file=sys.stderr)
        return 2

    started = time.monotonic()
    proc = subprocess.run(command, cwd=ROOT)
    elapsed = time.monotonic() - started
    within_slo = elapsed <= args.budget_seconds
    exit_code = proc.returncode
    ok = exit_code == 0 and within_slo

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "schema": "workflow-slo-report-v1",
                    "scope": args.scope,
                    "budget_seconds": args.budget_seconds,
                    "elapsed_seconds": round(elapsed, 3),
                    "within_slo": within_slo,
                    "exit_code": exit_code,
                    "command": command,
                },
                indent=2,
            )
        )
    else:
        status = "PASS" if ok else "FAIL"
        print(
            f"SLO {status} scope={args.scope} elapsed={elapsed:.2f}s "
            f"budget={args.budget_seconds:.2f}s exit={exit_code} command={' '.join(command)}"
        )

    if exit_code != 0:
        return exit_code
    if not within_slo:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
