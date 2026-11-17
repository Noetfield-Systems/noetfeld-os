#!/usr/bin/env python3
"""Fail closed only on loss of the mandatory agent recovery instructions.

This is a CI wiring check, not a new runtime/customer admission gate.
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RULE=".cursor/rules/010-execution-first-alternatives.mdc"


def require(checked: bool, message: str) -> None:
    if not checked:
        raise SystemExit("FAIL alternative-first agent policy: "+message)


def main() -> int:
    root=(ROOT/"AGENTS.md").read_text(encoding="utf-8")
    law=(ROOT/RULE).read_text(encoding="utf-8")
    require(RULE in root, "root AGENTS.md does not activate the law")
    require("alwaysApply: true" in law, "Cursor automatic agent activation missing")
    require("FAILURE -> DISCOVER -> SELECT -> EXECUTE -> VERIFY -> LEARN" in law,
            "mandatory execute/verify/learn loop weakened")
    for fragment in (
        "Before writing a blocker report",
        "currently configured alternatives",
        "cost per verified useful outcome",
        "failing free API to block a viable paid model",
        "Select and **execute**",
        "same identity, acceptance criteria, spend limits and idempotency",
        "independent verification",
        "No speculative status noise",
    ):
        require(fragment in law, "missing "+fragment)
    require("Founder goal" in law, "founder priority omitted")
    print("PASS: NOOS alternative-first mandatory execution law is live in AGENTS + Cursor rules")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
