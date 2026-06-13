#!/usr/bin/env python3
"""WISE picker — auto W3 maturity, prerequisite chain, unified dispatch."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from wise_prompt_lib import (  # noqa: E402
    W3_CRITICAL_PATH,
    W3_DEFAULT_CHAIN,
    infer_w3_maturity,
)

PACK = ROOT / "docs" / "ops" / "plans" / "tier1-smart.json"
STATUS = ROOT / "docs" / "ops" / "plans" / "tier1-status.json"
CATALOG = ROOT / "docs" / "ops" / "plans" / "catalog-500.json"

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
    return json.loads(STATUS.read_text(encoding="utf-8")).get("status", {})


def score_prompt(p, status, bottleneck, cloud_only):
    pid = p["id"]
    if status.get(pid) == "done":
        return -1_000_000, False, False
    if cloud_only and p.get("agent_mode") == "hub":
        return -500_000, False, False
    requires = p.get("requires") or []
    blocked = any(status.get(r) != "done" for r in requires)
    bmatch = bool(bottleneck and p.get("w3_signal") == W3_DISPATCH.get(bottleneck))
    s = 10 * len(p.get("unblocks") or [])
    if bmatch:
        s += 500
    if pid in ("E-05", "E-06"):
        s += 150
    if pid == "E-01":
        s += 120
    rank = p.get("_default_rank", 999)
    s += max(0, 100 - rank * 10)
    s += {"S": 15, "M": 10, "L": 5}.get(p.get("effort", "M"), 0)
    if blocked:
        s -= 50
    return s, blocked, bmatch


def prerequisite_chain(prompt_id: str, prompts: list[dict], status: dict[str, str]) -> list[str]:
    by_id = {p["id"]: p for p in prompts}
    chain = []
    cur = prompt_id
    seen = set()
    while cur and cur not in seen:
        seen.add(cur)
        p = by_id.get(cur)
        if not p:
            break
        if status.get(cur) != "done":
            chain.append(cur)
        reqs = p.get("requires") or []
        cur = reqs[0] if reqs else None
    return list(reversed(chain))


def main() -> None:
    ap = argparse.ArgumentParser(description="WISE prompt picker (v14)")
    ap.add_argument("--limit", type=int, default=1, help="Default 1 — prefer one wise task per session")
    ap.add_argument("--id")
    ap.add_argument("--prompt", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--bottleneck", choices=list(W3_DISPATCH.keys()))
    ap.add_argument("--auto", action="store_true", default=True, help="Auto-detect bottleneck from W3 maturity")
    ap.add_argument("--no-auto", action="store_false", dest="auto")
    ap.add_argument("--maturity", action="store_true", help="Print W3 maturity only")
    ap.add_argument("--tier", type=int, default=1, choices=[1, 2])
    ap.add_argument("--include-hub", action="store_true")
    args = ap.parse_args()

    status = load_status()
    stage, label, auto_bn = infer_w3_maturity(status)
    done_n = sum(1 for i in W3_CRITICAL_PATH if status.get(i) == "done")
    critical_pct = int(100 * done_n / len(W3_CRITICAL_PATH)) if W3_CRITICAL_PATH else 0

    if args.maturity:
        print(json.dumps({
            "stage": stage,
            "label": label,
            "critical_path_pct": critical_pct,
            "critical_done": [i for i in W3_CRITICAL_PATH if status.get(i) == "done"],
            "recommended_bottleneck": auto_bn,
            "default_chain_next": next((i for i in W3_DEFAULT_CHAIN if status.get(i) != "done"), None),
        }, indent=2))
        return

    bottleneck = args.bottleneck or (auto_bn if args.auto else None)

    if args.tier == 2:
        if not CATALOG.is_file():
            print("Run: python3 scripts/generate-prompt-catalog-500.py")
            raise SystemExit(1)
        if stage < 2:
            print(f"Tier 2 gated — W3 maturity stage {stage} ({label}). Complete export path first.")
            print(f"Recommended: python3 scripts/pick-wise.py --bottleneck export --prompt")
            raise SystemExit(2)
        t2 = json.loads(CATALOG.read_text())["T2_product_backlog"][: args.limit]
        for e in t2:
            print(f"{e['id']}\tT2\t{e['title'][:64]}")
        if args.prompt and t2:
            e = t2[0]
            print(f"\n## Task\n{e.get('task', e['title'])}\n\n## Verify\n{e.get('verify', '')}")
        return

    if not PACK.is_file():
        print("Run: python3 scripts/generate-tier1-smart-pack.py")
        raise SystemExit(1)

    data = json.loads(PACK.read_text(encoding="utf-8"))
    prompts = data["prompts"]
    chain_rank = {pid: i for i, pid in enumerate(data.get("default_chain", W3_DEFAULT_CHAIN))}
    for p in prompts:
        p["_default_rank"] = chain_rank.get(p["id"], 999)

    if args.id:
        match = [p for p in prompts if p["id"] == args.id]
        if not match:
            raise SystemExit(f"Unknown id: {args.id}")
        pl = match[0]
        chain = prerequisite_chain(pl["id"], prompts, status)
        if args.json:
            print(json.dumps({**pl, "prerequisite_chain": chain}, indent=2))
        else:
            print(f"{pl['id']}\t{pl['phase']}\t{pl['title']}")
            if chain and chain != [pl["id"]]:
                print(f"Prerequisite chain: {' → '.join(chain)}")
            if args.prompt:
                print("\n" + pl["agent_prompt"])
        return

    cloud_only = not args.include_hub
    scored = []
    for p in prompts:
        sc, blocked, bmatch = score_prompt(p, status, bottleneck, cloud_only)
        if sc <= -100_000:
            continue
        scored.append((sc, blocked, bmatch, p))

    if bottleneck:
        scored.sort(key=lambda x: (not x[2], x[1], -x[0], x[3]["id"]))
    else:
        scored.sort(key=lambda x: (x[1], -x[0], x[3]["id"]))

    picked = [p for _, _, _, p in scored[: args.limit]]
    if not picked:
        print("No Tier 1 backlog — sync tier1-status or regenerate pack")
        raise SystemExit(1)

    top = picked[0]
    chain = prerequisite_chain(top["id"], prompts, status)

    if args.json:
        print(json.dumps({
            "maturity": {"stage": stage, "label": label, "critical_path_pct": critical_pct},
            "bottleneck": bottleneck,
            "picked": picked,
            "prerequisite_chain": chain,
        }, indent=2))
        return

    print(f"# WISE pick · maturity stage {stage} ({label}) · critical path {critical_pct}% · bottleneck={bottleneck or 'auto-off'}")
    print("")
    for p in picked:
        req = p.get("requires") or []
        blocked = [r for r in req if status.get(r) != "done"]
        flag = " BLOCKED" if blocked else ""
        print(f"{p['id']}\t{p['phase']}\t{p['title'][:64]}{flag}")
    if chain and chain != [top["id"]]:
        print("")
        print(f"Prerequisite chain: {' → '.join(chain)}")
        print("Tip: mark prerequisites done first, or pick the first unblocked id in chain.")
    print("")
    print(f"W3 north star: {data.get('w3_north_star', '')}")
    print(f"Verify: {top['verify']}")
    if args.prompt:
        print("\n" + top["agent_prompt"])


if __name__ == "__main__":
    main()
