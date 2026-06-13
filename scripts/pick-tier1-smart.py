#!/usr/bin/env python3
"""Smart Tier 1 picker — dependency-aware, W3-weighted, persona-filtered."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "ops" / "plans" / "tier1-smart.json"
STATUS = ROOT / "docs" / "ops" / "plans" / "tier1-status.json"

# Bottleneck → prefer prompts with this w3_signal when backlog allows
W3_DISPATCH = {
    "demo": "demo_live",
    "export": "export_e2e",
    "www": "www_proof",
    "trust": "trust_diligence",
    "pipeline": "design_partner",
    "channel": "channel_attach",
    "ship": "ship_green",
}


def load_status() -> dict[str, str]:
    if not STATUS.is_file():
        return {}
    data = json.loads(STATUS.read_text(encoding="utf-8"))
    return data.get("status", {})


def score_prompt(p: dict, status: dict[str, str], bottleneck: str | None, cloud_only: bool) -> tuple[int, bool, bool]:
    """Returns (score, is_blocked, bottleneck_match)."""
    pid = p["id"]
    if status.get(pid) == "done":
        return (-1_000_000, False, False)
    if cloud_only and p.get("agent_mode") == "hub":
        return (-500_000, False, False)
    requires = p.get("requires") or []
    blocked = any(status.get(r) != "done" for r in requires)
    bottleneck_match = bool(
        bottleneck and p.get("w3_signal") == W3_DISPATCH.get(bottleneck)
    )

    s = 0
    s += 10 * len(p.get("unblocks") or [])
    if bottleneck_match:
        s += 500
    if pid in ("E-05", "E-06"):
        s += 150
    if pid == "E-01":
        s += 120
    default_chain = p.get("_default_rank", 999)
    s += max(0, 100 - default_chain * 10)
    effort = p.get("effort", "M")
    s += {"S": 15, "M": 10, "L": 5}.get(effort, 0)
    if blocked:
        s -= 50  # prefer unblocked, but bottleneck_match can still win with +500
    return s, blocked, bottleneck_match


def main() -> None:
    ap = argparse.ArgumentParser(description="Pick smart Tier 1 prompts")
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--id", help="Print one prompt by id (e.g. E-01)")
    ap.add_argument("--prompt", action="store_true", help="Include full agent_prompt")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--bottleneck", choices=list(W3_DISPATCH.keys()), help="W3 dispatcher hint")
    ap.add_argument("--persona", help="Filter by persona (CISO, GRC, etc.)")
    ap.add_argument("--cloud-only", action="store_true", default=True)
    ap.add_argument("--include-hub", action="store_true", help="Allow hub-only prompts")
    args = ap.parse_args()

    if not PACK.is_file():
        print("Missing tier1-smart.json — run: python3 scripts/generate-tier1-smart-pack.py")
        raise SystemExit(1)

    data = json.loads(PACK.read_text(encoding="utf-8"))
    prompts = data["prompts"]
    status = load_status()
    default_chain = data.get("default_chain", [])
    chain_rank = {pid: i for i, pid in enumerate(default_chain)}
    for p in prompts:
        p["_default_rank"] = chain_rank.get(p["id"], 999)

    if args.id:
        match = [p for p in prompts if p["id"] == args.id]
        if not match:
            print(f"Unknown id: {args.id}")
            raise SystemExit(1)
        pl = match[0]
        if args.json:
            print(json.dumps(pl, indent=2))
        else:
            print(f"{pl['id']}\t{pl['phase']}\t{pl['title']}")
            if args.prompt:
                print("")
                print(pl["agent_prompt"])
        return

    cloud_only = args.cloud_only and not args.include_hub
    scored = []
    for p in prompts:
        if args.persona and p.get("persona", "").lower() != args.persona.lower():
            continue
        sc, blocked, bmatch = score_prompt(p, status, args.bottleneck, cloud_only)
        if sc <= -100_000:
            continue
        scored.append((sc, blocked, bmatch, p))

    if args.bottleneck:
        # W3 path first: matching signal, then unblocked, then score
        scored.sort(key=lambda x: (not x[2], x[1], -x[0], x[3]["id"]))
    else:
        scored.sort(key=lambda x: (x[1], -x[0], x[3]["id"]))
    picked = [p for _, _, _, p in scored[: args.limit]]

    if not picked:
        print("No eligible Tier 1 backlog — check tier1-status.json or run generate-tier1-smart-pack.py")
        raise SystemExit(1)

    if args.json:
        print(json.dumps(picked, indent=2))
        return

    for p in picked:
        req = p.get("requires") or []
        blocked = [r for r in req if status.get(r) != "done"]
        flag = " BLOCKED" if blocked else ""
        print(f"{p['id']}\t{p['phase']}\t{p['title'][:64]}{flag}")
    print("")
    print(f"W3 north star: {data.get('w3_north_star', '')}")
    print(f"Verify: {picked[0]['verify']}")
    if args.prompt:
        print("")
        print(picked[0]["agent_prompt"])


if __name__ == "__main__":
    main()
