#!/usr/bin/env python3
"""Reconcile NF-PLAN / nf-future status from plan.json + COMPLETED_ON_MAIN."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS_DIR = ROOT / "docs" / "ops" / "plans"
OS_PLANS_DIR = ROOT / "os" / "plans"
PLAN_JSON = ROOT / "os" / "plan.json"
COMPLETED = PLANS_DIR / "COMPLETED_ON_MAIN.md"

# Map plan.json done ids to NF-PLAN index ranges / explicit ids
SHIP_DONE_MAP: dict[str, list[int]] = {
    # Phase 0 ship ops T0 (nf-future 0001-0025 ↔ NF-PLAN 0001-0025 area rotation)
    "nf-ship-sample-ledger-017": list(range(1, 26)),
    "nf-demo-page-confidence-035": [7, 37, 57, 77, 97],
    "nf-copilot-hub-gtm-041": [6, 26, 46, 66, 86],
    "nf-homepage-design-partner-042": [5, 25, 45, 65, 85],
    "nf-gtm-pre-demo-verify-039": [1, 11, 21],
    "nf-procurement-pack-zip-034": [24, 44, 64],
    "nf-pilot-p1-9-023": [11, 111, 211],
    "ship-pilot-e2e-verify-007": [11],
    "ship-audit-export-api-e2e-008": [16],
    "ship-procurement-e2e-verify-009": [24],
    "ship-result-confidence-e2e-004": [4, 54],
    "ship-copilot-demo-links-005": [4],
    "ship-plan-with-no-asf-script-006": [5],
    "ship-audit-export-ux-001": [16],
    "ship-demo-confidence-002": [4, 54],
    "ship-www-tle-copy-003": [6, 26],
    "ship-gtm-ops-www-wire-013": [2, 21, 22, 42, 62],
    "ship-buyer-debrief-template-014": [6, 26, 46, 66, 86],
    "ship-tier-gate-verify-015": [7, 27, 47, 67, 87],
    "ship-bc-ai-for-all-outreach-016": [21, 41, 61, 81],
    "ship-registry-sync-iter6-017": [8, 28, 48, 68, 88],
    "ship-bc-ai-www-wire-018": [14, 34, 54, 74, 94],
    "ship-dual-brand-boundary-019": [3, 23, 43, 63, 83],
    "ship-registry-pattern-propagation-020": [8, 28, 48, 68, 88, 108, 128, 148, 168, 188, 208, 228, 248, 268, 288, 308, 328, 348, 368, 388, 408, 428, 448, 468, 488, 508, 528, 548, 568, 588, 608, 628, 648, 668, 688, 708, 728, 748, 768, 788, 808, 828, 848, 868, 888, 908, 928, 948, 968, 988],
    "ship-diligence-procurement-wire-021": [15, 35, 55, 75, 95, 115, 135, 155, 175, 195, 215, 235, 255, 275, 295, 315, 335, 355, 375, 395, 415, 435, 455, 475, 495, 515, 535, 555, 575, 595, 615, 635, 655, 675, 695, 715, 735, 755, 775, 795, 815, 835, 855, 875, 895, 915, 935, 955, 975, 995],
    "ship-design-partner-bc-ai-022": [1, 21, 41, 61, 81, 101, 121, 141, 161, 181, 201, 221, 241, 261, 281, 301, 321, 341, 361, 381, 401, 421, 441, 461, 481, 501, 521, 541, 561, 581, 601, 621, 641, 661, 681, 701, 721, 741, 761, 781, 801, 821, 841, 861, 881, 901, 921, 941, 961, 981],
    "ship-gtm-next-queue-023": [8, 28, 48, 68, 88],
    "ship-staging-demo-www-wire-024": [27, 47, 67, 87, 107],
    "ship-security-buyer-tle-copy-025": [14, 34, 54, 74, 94],
    "ship-procurement-one-pager-wire-027": [24, 44, 64, 84, 104],
    "ship-governance-sources-www-028": [15, 35, 55, 75, 95],
    "ship-homepage-demo-cta-029": [5, 25, 45, 65, 85],
    "ship-tunnel-smoke-verify-030": [27, 47, 67, 87],
    "ship-governance-sources-handbook-031": [15, 35, 55, 75, 95],
    "ship-copilot-hub-sources-032": [6, 26, 46, 66, 86],
    "ship-trust-brief-intake-wire-033": [9, 29, 49, 69, 89],
    "ship-drift-sources-procurement-034": [10, 30, 50, 70, 90],
    "ship-demo-rehearsal-hub-wire-035": [2, 22, 42, 62, 82],
    "ship-trust-brief-procurement-036": [9, 29, 49, 69, 89],
    "ship-drift-blueprints-procurement-037": [10, 30, 50, 70, 90],
    "ship-demo-url-verify-038": [27, 47, 67, 87],
    "ship-trust-brief-pilot-039": [9, 29, 49, 69, 89],
    "ship-procurement-cta-homepage-040": [5, 25, 45, 65, 85],
    "ship-cursor-reply-coherence-041": [8, 28, 48, 68, 88],
    "ship-trust-brief-demo-042": [9, 29, 49, 69, 89],
    "ship-demo-rehearsal-pilot-043": [2, 22, 42, 62, 82],
    "ship-open-prs-autocheck-044": [8, 28, 48, 68, 88],
    "ship-trust-brief-parity-audit-045": [9, 29, 49, 69, 89],
    "ship-merged-pr-open-prs-gate-046": [8, 28, 48, 68, 88],
    "ship-demo-rehearsal-demo-047": [2, 22, 42, 62, 82],
    "ship-blueprint-governance-console-bridge-048": [8, 28, 48, 68, 88],
    "ship-rehearsal-parity-all-pages-049": [2, 22, 42, 62, 82],
    "ship-open-prs-merged-044-gate-050": [8, 28, 48, 68, 88],
    "ship-blueprint-services-governance-bridge-051": [8, 28, 48, 68, 88],
    "ship-procurement-control-checkpoint-copy-052": [9, 29, 49, 69, 89],
    "ship-merged-pr-window-five-053": [8, 28, 48, 68, 88],
    "ship-procurement-checkpoint-verify-054": [9, 29, 49, 69, 89],
    "ship-services-governance-openapi-bridge-055": [9, 29, 49, 69, 89],
    "ship-merged-window-config-056": [8, 28, 48, 68, 88],
}

# NF-PLAN patterns that are agentic-only (R-011) — never pick for NF-CLOUD implement
AGENTIC_ONLY_PATTERNS = frozenset({"customer-outreach"})


def pattern_index(n: int) -> int:
    """0-based pattern slot in the 20-pattern × 10-phase × 5-tier grid."""
    return (n - 1) % 20


def expand_pattern_indices(pattern: str, plans: list[dict]) -> set[int]:
    """All NF-PLAN indices sharing the same work pattern."""
    return {int(p["id"].split("-")[-1]) for p in plans if p["pattern"] == pattern}


def expand_done_by_pattern(plans: list[dict], done_indices: set[int]) -> set[int]:
    """Propagate done status across phase-rotated duplicates (1000-pack grid)."""
    patterns_done = {p["pattern"] for p in plans if int(p["id"].split("-")[-1]) in done_indices}
    expanded = set(done_indices)
    for pattern in patterns_done:
        expanded.update(expand_pattern_indices(pattern, plans))
    return expanded

# Explicit COMPLETED_ON_MAIN NF-PLAN ids
COMPLETED_IDS = {
    "NF-PLAN-0001", "NF-PLAN-0016", "NF-PLAN-0022", "NF-PLAN-0023",
    "NF-PLAN-0101", "NF-PLAN-0106", "NF-PLAN-0107", "NF-PLAN-0109",
    "NF-PLAN-0116", "NF-PLAN-0121", "NF-PLAN-0136", "NF-PLAN-0301",
}


def nf_plan_id(n: int) -> str:
    return f"NF-PLAN-{n:04d}"


def nf_future_id(n: int) -> str:
    return f"nf-future-{n:04d}"


def load_registry() -> dict:
    path = PLANS_DIR / "registry.json"
    if not path.exists():
        raise SystemExit("registry.json missing — run generate-prompt-pack-v2.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def collect_done_indices() -> set[int]:
    indices: set[int] = set()
    for ids in COMPLETED_IDS:
        n = int(ids.split("-")[-1])
        indices.add(n)

    if PLAN_JSON.exists():
        data = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
        for item in data.get("done", []):
            pid = item.get("id", "")
            if pid in SHIP_DONE_MAP:
                indices.update(SHIP_DONE_MAP[pid])
        for item in data.get("next_tasks", []):
            if item.get("status") == "done":
                pid = item.get("id", "")
                if pid in SHIP_DONE_MAP:
                    indices.update(SHIP_DONE_MAP[pid])

    if COMPLETED.exists():
        text = COMPLETED.read_text(encoding="utf-8")
        for m in re.finditer(r"NF-PLAN-(\d{4})", text):
            indices.add(int(m.group(1)))

    # os/plans markdown stubs already marked done
    for md in OS_PLANS_DIR.rglob("nf-future-*.md"):
        head = md.read_text(encoding="utf-8").split("---", 2)
        if len(head) >= 2 and "status: done" in head[1]:
            n = int(md.stem.split("-")[-1])
            indices.add(n)

    return indices


def update_nf_future_markdown(done_indices: set[int], bridge: dict) -> None:
    bridge_map = {e["nf_future_id"]: e["nf_plan_id"] for e in bridge.get("entries", [])}
    for md in OS_PLANS_DIR.rglob("nf-future-*.md"):
        n = int(md.stem.split("-")[-1])
        if n not in done_indices:
            continue
        text = md.read_text(encoding="utf-8")
        if "status: done" in text.split("---", 2)[1]:
            continue
        text = re.sub(r"^status: backlog\s*$", "status: done", text, count=1, flags=re.M)
        nf_plan = bridge_map.get(nf_future_id(n), nf_plan_id(n))
        if "nf_plan_id:" not in text:
            text = text.replace(
                "generator: scripts/generate-future-plans.py",
                f"nf_plan_id: {nf_plan}\ngenerator: scripts/generate-future-plans.py",
            )
        md.write_text(text, encoding="utf-8")


def update_os_registry(done_indices: set[int]) -> None:
    reg_path = OS_PLANS_DIR / "REGISTRY.json"
    if not reg_path.exists():
        return
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    for pl in reg.get("plans", []):
        n = int(pl["id"].split("-")[-1])
        if n in done_indices:
            pl["status"] = "done"
    reg_path.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")


def regenerate_quick_pick(plans: list[dict]) -> None:
    """GTM-weighted QUICK_PICK (same logic as v2 generator)."""
    agent_plans = [
        p
        for p in plans
        if not p["asf_only"]
        and p["status"] == "backlog"
        and p["tier_gate"] != "C"
        and p.get("pattern") not in AGENTIC_ONLY_PATTERNS
        and not p.get("agentic_only")
    ]
    phase_pri = {"P7": 0, "P4": 1, "P0": 2, "P1": 3, "P2": 4, "P3": 5, "P5": 6, "P6": 7, "P8": 8, "P9": 9}
    tier_pri = {"T1": 0, "T2": 1, "T3": 2, "T4": 3, "T5": 4}

    def sort_key(p: dict) -> tuple:
        gate_pri = 0 if p["tier_gate"] == "A" else (1 if p["tier_gate"] == "none" else 2)
        return (p["gtm_priority"], gate_pri, tier_pri.get(p["tier"], 9), phase_pri.get(p["phase"], 9), p["id"])

    agent_plans.sort(key=sort_key)
    lines = [
        "# PLAN WITH NO ASF — quick pick",
        "",
        "When the founder says **PLAN WITH NO ASF**, start here. Pick the next **agent** item (not `asf_only`).",
        "",
        "**Full registry:** [registry.json](../registry.json) (1000 plans) · **Locked pack:** [PROMPT_PACK_LOCKED/](../PROMPT_PACK_LOCKED/)",
        "",
        "**Update:** `python3 scripts/sync-prompt-pack-status.py` after each ship session",
        "",
        "## Next 25 agent-ready plans (GTM-weighted)",
        "",
    ]
    if agent_plans:
        for pl in agent_plans[:25]:
            lines.append(
                f"1. **{pl['id']}** · {pl['phase']}/{pl['tier']} · {pl['title']}  \n"
                f"   Prompt: {pl['prompt'][:120]}…  \n"
                f"   Verify: `{pl['verify_command']}`"
            )
    else:
        lines.extend(
            [
                "_Registry backlog empty (1000-pack synced). Pick from "
                "[GTM_NEXT.md](./GTM_NEXT.md) or `os/plan.json` `next_tasks`._",
                "",
            ]
        )
        gtm_next_path = PLANS_DIR / "no-asf" / "GTM_NEXT.md"
        if gtm_next_path.exists():
            gtm_text = gtm_next_path.read_text(encoding="utf-8")
            if "## Next GTM Tier A" in gtm_text:
                section = gtm_text.split("## Next GTM Tier A")[1].split("\n## ")[0]
                lines.append("### GTM_NEXT (top picks)")
                lines.append("")
                picked = False
                for line in section.strip().splitlines():
                    stripped = line.strip()
                    if stripped.startswith("1."):
                        lines.append(stripped)
                        picked = True
                if not picked:
                    lines.extend(
                        [
                            "_No open NF-CLOUD disk items — see [GTM_NEXT.md](./GTM_NEXT.md)._",
                            "",
                            "**Agentic commercial P0:** ship-design-partner-outreach-026 (Hub only — not NF-CLOUD disk).",
                        ]
                    )
    lines.extend(["", "## Recently completed", "", f"Synced {sum(1 for p in plans if p['status']=='done')} plans as done.", ""])
    (PLANS_DIR / "no-asf" / "QUICK_PICK.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    registry = load_registry()
    plans = registry["plans"]
    done_indices = expand_done_by_pattern(plans, collect_done_indices())
    plan_by_id = {p["id"]: p for p in plans}

    for n in done_indices:
        pid = nf_plan_id(n)
        if pid in plan_by_id:
            plan_by_id[pid]["status"] = "done"

    done_count = sum(1 for p in plans if p["status"] == "done")
    registry["count"] = len(plans)
    (PLANS_DIR / "registry.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    bridge_path = PLANS_DIR / "BRIDGE_NF_PLAN_TO_NF_FUTURE.json"
    if bridge_path.exists():
        bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
        for e in bridge.get("entries", []):
            n = int(e["nf_plan_id"].split("-")[-1])
            if n in done_indices:
                e["status"] = "done"
        bridge_path.write_text(json.dumps(bridge, indent=2) + "\n", encoding="utf-8")
        update_nf_future_markdown(done_indices, bridge)

    update_os_registry(done_indices)
    regenerate_quick_pick(plans)

    # Refresh INDEX done count
    index_path = PLANS_DIR / "INDEX.md"
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
        text = re.sub(r"\| Done \| \d+ \|", f"| Done | {done_count} |", text)
        index_path.write_text(text, encoding="utf-8")

    print(f"sync-prompt-pack-status: marked {len(done_indices)} indices done ({done_count} in registry)")


if __name__ == "__main__":
    main()
