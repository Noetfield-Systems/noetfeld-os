#!/usr/bin/env python3
"""Pick next Noetfield 1000 prompt for PLAN WITH NO ASF. Agent-runnable backlog first."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "os" / "plan-library" / "noetfield-1000" / "REGISTRY.json"

SKIP_TASK_SNIPPETS = (
    "Founder-only:",
    "Founder: customer logo",
    "Render deploy as founder-only",
    "Reject full prod deploy execution",
    "production Azure AD secrets",
    "real Google OAuth without customer",
    "Circle prod",
    "customer logo/quote without signed",
    "commit partner PII",
)


def agent_runnable(title: str) -> bool:
    t = title.lower()
    return not any(s.lower() in t for s in SKIP_TASK_SNIPPETS)


def main() -> None:
    p = argparse.ArgumentParser(description="Pick Noetfield 1000 locked prompt")
    p.add_argument("--tier", default="T0")
    p.add_argument("--any-tier", action="store_true")
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--json", action="store_true")
    p.add_argument("--prompt", action="store_true", help="Print full agent_prompt for first pick")
    args = p.parse_args()

    if not REG.is_file():
        print(f"Missing library — run: python3 scripts/generate-noetfield-1000-prompts.py")
        raise SystemExit(1)

    data = json.loads(REG.read_text(encoding="utf-8"))
    tiers = ["T0", "T1", "T2", "T3"] if args.any_tier else [args.tier]

    picked = []
    for tier in tiers:
        for pl in data["plans"]:
            if pl["tier"] != tier or pl.get("status") != "backlog":
                continue
            if not agent_runnable(pl.get("title", "")):
                continue
            picked.append(pl)
            if len(picked) >= args.limit:
                break
        if len(picked) >= args.limit:
            break

    if args.json:
        print(json.dumps(picked, indent=2))
        return

    if not picked:
        print("No agent-runnable backlog — regenerate or mark more nf-* done")
        raise SystemExit(1)

    for pl in picked:
        print(f"{pl['id']}\t{pl['path']}\t{pl['title'][:72]}")
    print("")
    print(f"Verify: {picked[0]['verify']}")
    if args.prompt:
        print("")
        print(picked[0]["agent_prompt"])


if __name__ == "__main__":
    main()
