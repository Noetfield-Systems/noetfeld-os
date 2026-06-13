#!/usr/bin/env python3
"""Generate prompt-ready 1000-plan pack (docs/ops/plans). Preserves done statuses."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS_DIR = ROOT / "docs" / "ops" / "plans"

PHASES = {
    "P0": "Foundation — ship, dev stack, ops locks, CI",
    "P1": "Trust Ledger — TLE lifecycle, evidence, export",
    "P2": "Governance API — evaluate, audit, pilot auth, webhooks",
    "P3": "Connectors live — Purview, Entra, M365 audit sync",
    "P4": "Workspace & GTM — UI, www, procurement assets",
    "P5": "Enterprise — multi-tenant, RBAC, KMS signing",
    "P6": "Compliance — append-only proofs, retention, SOC narratives",
    "P7": "Customer & demo GTM — design partners, outreach, demo rehearsal",
    "P8": "Integrations — MSB channel, partners, API marketplace",
    "P9": "Horizon — research, critic, ML confidence, cross-product bridges",
}

TIERS = {
    "T1": "Critical — unblocks revenue or production ship",
    "T2": "Near-term — next 1–2 sprints",
    "T3": "Medium — quarters 2–4",
    "T4": "Strategic — 12–24 month capability",
    "T5": "Horizon — experimental / optional",
}

AREAS = [
    "trust-ledger",
    "governance-api",
    "evidence",
    "connectors",
    "workspace-ui",
    "www-gtm",
    "customer-acquisition",
    "demo-ops",
    "agent-ops",
    "governance-drift",
    "critic-research",
    "devex",
    "ci-cd",
    "security",
    "data-migrations",
    "testing",
    "docs-diligence",
    "msb-partner",
    "observability",
    "performance",
]

# 20 patterns × 10 phases × 5 tiers = 1000 (8 GTM-first patterns replace low-GTM infra patterns)
WORK_PATTERNS = [
    ("customer-outreach", "Design-partner outreach and pipeline for {area}"),
    ("demo-rehearsal", "5-minute demo rehearsal script and buyer checklist for {area}"),
    ("scope-gate-drill", "Agent scope-gate drill and verify for {area}"),
    ("drift-impl", "Governance drift implementation slice for {area}"),
    ("verdict-review", "Architecture verdict review and ship gate for {area}"),
    ("buyer-debrief", "Buyer interview debrief and evidence capture for {area}"),
    ("tier-gate-check", "Tier A/B/C gate validation before {area} work"),
    ("registry-reconcile", "Registry reconcile and plan.json sync for {area}"),
    ("api-endpoint", "Add or extend API endpoint for {area}"),
    ("integration-test", "Integration tests covering {area} happy path and 409 guards"),
    ("openapi-sync", "Align OpenAPI spec with implemented {area} routes"),
    ("smoke-script", "Extend plan-with-no-asf-verify check for {area}"),
    ("console-ui", "Governance console surface for {area} read-only v0"),
    ("www-copy", "WWW / trust-ledger copy block for {area} buyer line"),
    ("diligence-doc", "Diligence one-pager evidence for {area} controls"),
    ("audit-export", "Audit-export field bundle for {area} decisions"),
    ("schema-validate", "Request validation against locked schema for {area}"),
    ("examples-pack", "YAML/JSON examples pack under docs/spec/examples"),
    ("runbook", "RUNBOOK section for operating {area} in production"),
    ("performance", "Load test baseline and p95 budget for {area}"),
]

VERIFY_DEFAULT = "./scripts/plan-with-no-asf-verify.sh"

BASE_SOURCES = [
    "docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md",
    "docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md",
    "docs/ops/NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md",
    "docs/WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md",
    "docs/GTM_COPYBOOK.md",
    "docs/ops/NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md",
    ".cursor/agent-memory/MEMORY_LOCKED.yaml",
    "os/SHIP_NOW.md",
]

GTM_PATTERNS = {
    "customer-outreach",
    "demo-rehearsal",
    "buyer-debrief",
    "www-copy",
    "diligence-doc",
}

AGENT_OPS_PATTERNS = {"scope-gate-drill", "registry-reconcile"}

DRIFT_PATTERNS = {"drift-impl", "verdict-review"}

TIER_B_AREAS = {"connectors", "security", "data-migrations"}
TIER_C_AREAS = {"security", "observability", "performance"}


def plan_id(n: int) -> str:
    return f"NF-PLAN-{n:04d}"


def nf_future_id(n: int) -> str:
    return f"nf-future-{n:04d}"


def gtm_priority(phase: str, tier: str, area: str, pattern: str) -> int:
    if pattern in GTM_PATTERNS or area in ("customer-acquisition", "demo-ops", "www-gtm"):
        return 1
    if pattern in AGENT_OPS_PATTERNS or area == "agent-ops":
        return 2
    if phase in ("P4", "P7"):
        return 2
    if pattern in DRIFT_PATTERNS or area in ("governance-drift", "critic-research"):
        return 3
    if phase == "P9":
        return 4
    if tier in ("T4", "T5"):
        return 5
    return 3


def tier_gate(area: str, phase: str) -> str:
    if area in TIER_C_AREAS and phase in ("P5", "P8"):
        return "C"
    if area in TIER_B_AREAS and phase == "P3":
        return "B"
    if area in ("customer-acquisition", "demo-ops", "www-gtm", "agent-ops"):
        return "A"
    return "none"


def tier_gate_note(gate: str) -> str:
    if gate == "B":
        return "Blocked until first contracted customer (GTM Tier B)."
    if gate == "C":
        return "Blocked until 3+ customers and Tier A+B live (GTM Tier C)."
    return ""


def plan_sources(area: str, pattern: str) -> list[str]:
    sources = list(BASE_SOURCES)
    if area in ("governance-drift",) or pattern == "drift-impl":
        sources.append("docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md")
    if pattern == "verdict-review":
        sources.append(
            "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-010/noetfield-architecture-verdict-postgres-first-fa.md"
        )
    if area == "customer-acquisition" or pattern == "customer-outreach":
        sources.append("docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md")
    if area == "demo-ops" or pattern == "demo-rehearsal":
        sources.append("copilot/demo/index.html")
    if pattern == "scope-gate-drill":
        sources.append("docs/ops/AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md")
    return sources


def build_prompt(area: str, pattern: str, title: str, phase: str, tier: str) -> str:
    area_label = area.replace("-", " ")
    if pattern == "customer-outreach":
        return (
            f"As NF-CLOUD-AGENT (Noetfield only), agentic layer only — maintain pipeline copy on disk "
            f"(not send/call): {title}. Read R-011 + AGENTIC_COMMERCIAL_HANDOFF. "
            f"Prefer Tier 1 WISE id L-15 via pick-wise.py. "
            f"Area={area_label}; pattern={pattern}; phase={phase}; tier={tier}."
        )
    return (
        f"As NF-CLOUD-AGENT (Noetfield only): {title}. "
        f"Use SMART wrapper (docs/ops/NOETFIELD_PROMPT_PACK_V13_SMART_LOCKED_v1.md). "
        f"Prefer pick-wise.py over raw NF-PLAN grid. Lane A only. "
        f"Area={area_label}; pattern={pattern}; phase={phase}; tier={tier}. "
        f"Max 5 source files · one verify command · update tier1-status on done."
    )


def critic_note(area: str, pattern: str, gate: str) -> str:
    if gate in ("B", "C"):
        return tier_gate_note(gate)
    if pattern == "verdict-review":
        return "Postgres-first architecture verdict — ship only what supports pilot proof."
    if pattern in GTM_PATTERNS:
        return "GTM scorecard: validation 2/10 until one contracted pilot uses board PDF."
    if pattern == "scope-gate-drill":
        return "Best-practice: scope gate before work (MEMORY v5 + verify-agent-scope)."
    return "Align with ≤3 next_tasks; no infra sprawl per GTM 60-day lock."


def build_plans() -> list[dict]:
    plans: list[dict] = []
    n = 1
    for phase_code, phase_desc in PHASES.items():
        for tier_code, tier_desc in TIERS.items():
            for pattern_key, pattern_tpl in WORK_PATTERNS:
                area = AREAS[(n - 1) % len(AREAS)]
                area_label = area.replace("-", " ")
                title = pattern_tpl.format(area=area_label)
                gate = tier_gate(area, phase_code)
                gtm_pri = gtm_priority(phase_code, tier_code, area, pattern_key)
                agentic_only = pattern_key == "customer-outreach"
                plans.append(
                    {
                        "id": plan_id(n),
                        "nf_future_id": nf_future_id(n),
                        "phase": phase_code,
                        "phase_name": phase_desc,
                        "tier": tier_code,
                        "tier_name": tier_desc,
                        "area": area,
                        "pattern": pattern_key,
                        "agentic_only": agentic_only,
                        "title": title,
                        "outcome": f"Shippable increment for {area_label} in {phase_code} at {tier_code} priority.",
                        "verify": f"{VERIFY_DEFAULT}; area={area}; pattern={pattern_key}",
                        "verify_command": VERIFY_DEFAULT,
                        "prompt": build_prompt(area, pattern_key, title, phase_code, tier_code),
                        "sources": plan_sources(area, pattern_key),
                        "gtm_priority": gtm_pri,
                        "tier_gate": gate,
                        "tier_gate_note": tier_gate_note(gate),
                        "shipped_ref": "",
                        "critic_note": critic_note(area, pattern_key, gate),
                        "model_benchmark": "scope_gate + verify_bundle + locked_memory",
                        "no_asf": tier_code != "T1" or pattern_key not in ("runbook",),
                        "asf_only": pattern_key == "runbook" and tier_code == "T1",
                        "status": "backlog",
                        "blocks": [],
                    }
                )
                n += 1
                if n > 1000:
                    return plans
    return plans


def write_bridge(plans: list[dict]) -> None:
    bridge = {
        "schema_version": 1,
        "count": len(plans),
        "mapping_rule": "NF-PLAN-NNNN ↔ nf-future-NNNN (same sequence index)",
        "entries": [
            {
                "nf_plan_id": p["id"],
                "nf_future_id": p["nf_future_id"],
                "status": p["status"],
                "gtm_priority": p["gtm_priority"],
            }
            for p in plans
        ],
    }
    (PLANS_DIR / "BRIDGE_NF_PLAN_TO_NF_FUTURE.json").write_text(
        json.dumps(bridge, indent=2) + "\n", encoding="utf-8"
    )


def write_by_phase(plans: list[dict]) -> None:
    by_phase: dict[str, list[dict]] = {p: [] for p in PHASES}
    for pl in plans:
        by_phase[pl["phase"]].append(pl)
    phase_dir = PLANS_DIR / "by-phase"
    phase_dir.mkdir(parents=True, exist_ok=True)
    for code, desc in PHASES.items():
        lines = [
            f"# Plans — {code}: {desc}",
            "",
            f"**Count:** {len(by_phase[code])} · **Lane:** `noetfield_cloud`",
            "",
        ]
        for pl in by_phase[code]:
            flag = "ASF" if pl["asf_only"] else "agent"
            lines.append(
                f"- **{pl['id']}** [{pl['tier']}] ({flag}) GTM={pl['gtm_priority']} {pl['title']} — `{pl['status']}`"
            )
        lines.append("")
        (phase_dir / f"{code.lower()}.md").write_text("\n".join(lines), encoding="utf-8")


def write_by_tier(plans: list[dict]) -> None:
    by_tier: dict[str, list[dict]] = {t: [] for t in TIERS}
    for pl in plans:
        by_tier[pl["tier"]].append(pl)
    tier_dir = PLANS_DIR / "by-tier"
    tier_dir.mkdir(parents=True, exist_ok=True)
    for code, desc in TIERS.items():
        lines = [f"# Plans — {code}: {desc}", "", f"**Count:** {len(by_tier[code])}", ""]
        for pl in by_tier[code]:
            lines.append(f"- **{pl['id']}** [{pl['phase']}] {pl['title']}")
        lines.append("")
        (tier_dir / f"{code.lower()}.md").write_text("\n".join(lines), encoding="utf-8")


def write_quick_pick(plans: list[dict]) -> None:
    agent_plans = [
        p
        for p in plans
        if not p["asf_only"]
        and p["status"] == "backlog"
        and p["tier_gate"] != "C"
    ]
    phase_pri = {"P7": 0, "P4": 1, "P0": 2, "P1": 3, "P2": 4, "P3": 5, "P5": 6, "P6": 7, "P8": 8, "P9": 9}
    tier_pri = {"T1": 0, "T2": 1, "T3": 2, "T4": 3, "T5": 4}

    def sort_key(p: dict) -> tuple:
        gate_pri = 0 if p["tier_gate"] == "A" else (1 if p["tier_gate"] == "none" else 2)
        return (
            p["gtm_priority"],
            gate_pri,
            tier_pri.get(p["tier"], 9),
            phase_pri.get(p["phase"], 9),
            p["id"],
        )

    agent_plans.sort(key=sort_key)
    lines = [
        "# PLAN WITH NO ASF — quick pick",
        "",
        "When the founder says **PLAN WITH NO ASF**, start here. Pick the next **agent** item (not `asf_only`).",
        "",
        "**Full registry:** [registry.json](../registry.json) (1000 plans) · **Locked pack:** [PROMPT_PACK_LOCKED/](../PROMPT_PACK_LOCKED/)",
        "",
        "**Update:** `python3 scripts/generate-prompt-pack-v2.py` then `python3 scripts/sync-prompt-pack-status.py`",
        "",
        "## Next 25 agent-ready plans (GTM-weighted)",
        "",
    ]
    for pl in agent_plans[:25]:
        lines.append(
            f"1. **{pl['id']}** · {pl['phase']}/{pl['tier']} · {pl['title']}  \n"
            f"   Prompt: {pl['prompt'][:120]}…  \n"
            f"   Verify: `{pl['verify_command']}`"
        )
    lines.extend(
        [
            "",
            "## Recently completed",
            "",
            "Run `python3 scripts/sync-prompt-pack-status.py` after each ship session.",
            "",
        ]
    )
    (PLANS_DIR / "no-asf" / "QUICK_PICK.md").write_text("\n".join(lines), encoding="utf-8")


def write_slice_docs(plans: list[dict]) -> None:
    slice_dir = PLANS_DIR / "PROMPT_PACK_LOCKED"
    slice_dir.mkdir(parents=True, exist_ok=True)

    backlog = [p for p in plans if p["status"] == "backlog" and not p["asf_only"]]

    def top_n(pred, n: int) -> list[dict]:
        items = [p for p in backlog if pred(p)]
        items.sort(key=lambda p: (p["gtm_priority"], p["id"]))
        return items[:n]

    gtm100 = top_n(
        lambda p: p["gtm_priority"] <= 2
        or p["area"] in ("customer-acquisition", "demo-ops", "www-gtm"),
        100,
    )
    agent50 = top_n(
        lambda p: p["area"] == "agent-ops" or p["pattern"] in AGENT_OPS_PATTERNS,
        50,
    )
    drift100 = top_n(
        lambda p: p["area"] in ("governance-drift", "critic-research")
        or p["pattern"] in DRIFT_PATTERNS
        or p["phase"] == "P9",
        100,
    )
    tier_bc = [p for p in plans if p["tier_gate"] in ("B", "C")]

    def write_list(path: Path, title: str, items: list[dict], extra: str = "") -> None:
        lines = [f"# {title}", "", f"**Count:** {len(items)}", ""]
        if extra:
            lines.extend([extra, ""])
        for p in items:
            prefix = "**AGENTIC ONLY — skip NF-CLOUD** · " if p.get("agentic_only") else ""
            lines.append(
                f"- {prefix}**{p['id']}** ({p['nf_future_id']}) · {p['phase']}/{p['tier']} · {p['title']}"
            )
            lines.append(f"  - Prompt: `{p['prompt'][:100]}…`")
            lines.append(f"  - Critic: {p['critic_note']}")
        lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")

    write_list(slice_dir / "GTM_PRIORITY_100.md", "GTM priority 100", gtm100)
    write_list(slice_dir / "AGENT_OPS_50.md", "Agent ops 50", agent50)
    write_list(slice_dir / "DRIFT_AND_RESEARCH_100.md", "Drift and research 100", drift100)
    write_list(
        slice_dir / "TIER_GATES.md",
        "Tier B/C gates",
        tier_bc,
        "Do not implement until GTM tier unlock conditions are met.",
    )


def _load_existing_status() -> dict[str, str]:
    path = PLANS_DIR / "registry.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {p["id"]: p.get("status", "backlog") for p in data.get("plans", [])}


def main() -> None:
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    (PLANS_DIR / "no-asf").mkdir(exist_ok=True)
    existing_status = _load_existing_status()
    plans = build_plans()
    assert len(plans) == 1000, len(plans)

    for pl in plans:
        if pl["id"] in existing_status and existing_status[pl["id"]] != "backlog":
            pl["status"] = existing_status[pl["id"]]

    registry = {
        "version": 2,
        "count": 1000,
        "generated_by": "scripts/generate-prompt-pack-v2.py",
        "lane": "noetfield_cloud",
        "thread": "THREAD-PORTFOLIO",
        "locked_doc": "docs/ops/NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md",
        "phases": PHASES,
        "tiers": TIERS,
        "update_policy": "generate-prompt-pack-v2.py preserves done; sync-prompt-pack-status.py reconciles plan.json.",
        "plans": plans,
    }
    (PLANS_DIR / "registry.json").write_text(
        json.dumps(registry, indent=2) + "\n", encoding="utf-8"
    )

    write_bridge(plans)
    write_by_phase(plans)
    write_by_tier(plans)
    write_quick_pick(plans)
    write_slice_docs(plans)

    agent_count = sum(1 for p in plans if not p["asf_only"])
    done_count = sum(1 for p in plans if p["status"] == "done")
    index = [
        "# Plan registry index (1000 plans — prompt-ready v2)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total plans | {len(plans)} |",
        f"| Agent (`no_asf`) | {agent_count} |",
        f"| Done | {done_count} |",
        f"| ASF-only flagged | {len(plans) - agent_count} |",
        "",
        "## Organization",
        "",
        "- **Locked pack:** [PROMPT_PACK_LOCKED/](./PROMPT_PACK_LOCKED/)",
        "- **Bridge:** [BRIDGE_NF_PLAN_TO_NF_FUTURE.json](./BRIDGE_NF_PLAN_TO_NF_FUTURE.json)",
        "- **By phase:** [by-phase/](./by-phase/)",
        "- **By tier:** [by-tier/](./by-tier/)",
        "- **No ASF quick pick:** [no-asf/QUICK_PICK.md](./no-asf/QUICK_PICK.md)",
        "- **Machine registry:** [registry.json](./registry.json)",
        "",
    ]
    (PLANS_DIR / "INDEX.md").write_text("\n".join(index), encoding="utf-8")
    print(f"Wrote {len(plans)} prompt-ready plans to {PLANS_DIR} (done={done_count})")


if __name__ == "__main__":
    main()
