#!/usr/bin/env python3
"""Generate os/plans library (1000 future plans by phase × tier). Re-run to refresh stubs."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS_DIR = ROOT / "os" / "plans"
CURSOR_MIRROR = Path.home() / ".cursor" / "plans" / "noetfield-os"

PHASES = [
    ("phase-0-ship-ops", "Ship ops, ingest, agent read-order, plan.json hygiene"),
    ("phase-1-tle-core", "Trust Ledger core, digests, exports, workspace"),
    ("phase-2-evidence-connectors", "Evidence index, M365/Google connectors, intake"),
    ("phase-3-workspace-enterprise", "RBAC, SSO, multi-tenant, audit export"),
    ("phase-4-agents-automation", "Agent manifests, workflows, copilot governance runs"),
    ("phase-5-knowledge-rag", "RAG, knowledge ingestion, policy packs"),
    ("phase-6-compliance-scale", "Controls catalog, risk registers, compliance dashboard"),
    ("phase-7-pilot-gtm", "Design partners, procurement, demos, pricing narrative"),
    ("phase-8-staging-prod", "Staging, Render/CF deploy, observability, SLOs"),
    ("phase-9-ecosystem-bridge", "SourceA sync, Prompt OS ingest, mono/hub bridges"),
]

TIERS = [
    ("T0", "Critical — blocks ship or pilot"),
    ("T1", "High — next sprint candidate"),
    ("T2", "Medium — quarterly"),
    ("T3", "Low — research / optional"),
]

DOMAINS = [
    "tle", "evidence", "connectors", "workspace", "rbac", "export", "audit",
    "copilot", "workflow", "agent", "rag", "policy", "risk", "staging", "ops",
    "ingest", "docs", "api", "ui", "security", "tenant", "pilot", "procurement",
    "sample", "kms",
]

ACTIONS = [
    "harden", "extend", "document", "automate", "validate", "expose",
    "integrate", "migrate", "optimize", "instrument", "test", "ship",
]


def plan_title(phase_slug: str, tier: str, domain: str, action: str, n: int) -> str:
    phase_short = phase_slug.split("-", 2)[-1].replace("-", " ")
    return f"{action.title()} {domain} for {phase_short} ({tier}, #{n:04d})"


def plan_body(plan_id: str, phase_slug: str, phase_desc: str, tier: str, tier_desc: str,
              domain: str, action: str, seq: int, status: str = "backlog") -> str:
    title = plan_title(phase_slug, tier, domain, action, seq)
    priority = {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}[tier]
    nf_plan = f"NF-PLAN-{seq:04d}"
    return f"""---
id: {plan_id}
phase: {phase_slug}
tier: {tier}
priority: {priority}
status: {status}
lane: lane_a
domain: {domain}
no_asf: true
nf_plan_id: {nf_plan}
generator: scripts/generate-future-plans.py
---

# {title}

**Phase:** {phase_slug} — {phase_desc}  
**Tier:** {tier} — {tier_desc}  
**Lane:** A (Copilot governance & evidence). Lane C (payments/custody) out of scope.

## Outcome

{action.title()} **{domain}** capabilities so Noetfield moves toward long-term Trust Ledger + Copilot readiness without waiting for external dispatch.

## Build (stub)

- Identify touchpoints under `governance-console/`, `scripts/`, `docs/spec/`, or `copilot/`.
- Add or extend API/UI/tests only in `~/Desktop/Noetfield`.
- Do not edit `SinaPromptOS` or Desktop `SourceA`.

## Verify

```bash
./scripts/plan-with-no-asf-verify.sh
```

## Agent closeout (no ASF)

1. Read `docs/ops/AGENT_READ_LINKS_LOCKED_v1.md` → `os/SHIP_NOW.md`.
2. Implement; run verify; update this plan `status: done` in front matter.
3. `reports/cursor-reply-latest.txt` + `ingest-cursor-reply.sh noetfield`.
4. `./scripts/sync-sourceA-desktop.sh`; commit on `cursor/bank-grade-fullstack-37f0`.

## Dependencies

- Prior phase items in same domain may be required.
- Locked positioning: `docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md`.
"""


def _read_existing_status(path: Path) -> str:
    if not path.exists():
        return "backlog"
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 2:
        return "backlog"
    for line in parts[1].splitlines():
        if line.strip().startswith("status:"):
            return line.split(":", 1)[1].strip()
    return "backlog"


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries: list[dict] = []
    seq = 0
    for phase_slug, phase_desc in PHASES:
        for tier, tier_desc in TIERS:
            tier_dir = PLANS_DIR / phase_slug / tier
            tier_dir.mkdir(parents=True, exist_ok=True)
            for i in range(25):
                seq += 1
                domain = DOMAINS[(seq + i) % len(DOMAINS)]
                action = ACTIONS[(seq * 3 + i) % len(ACTIONS)]
                plan_id = f"nf-future-{seq:04d}"
                rel_path = f"os/plans/{phase_slug}/{tier}/{plan_id}.md"
                path = ROOT / rel_path
                status = _read_existing_status(path)
                content = plan_body(
                    plan_id, phase_slug, phase_desc, tier, tier_desc,
                    domain, action, seq, status=status,
                )
                path.write_text(content, encoding="utf-8")
                entries.append({
                    "id": plan_id,
                    "nf_plan_id": f"NF-PLAN-{seq:04d}",
                    "phase": phase_slug,
                    "tier": tier,
                    "priority": {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}[tier],
                    "domain": domain,
                    "title": plan_title(phase_slug, tier, domain, action, seq),
                    "path": rel_path,
                    "status": status,
                })

    registry = {
        "schema_version": 1,
        "repo": "noetfield",
        "count": len(entries),
        "generated_at": now,
        "no_asf_rule": "When user says 'plan with no ASF', pick from this registry; update plan status after ship.",
        "phases": [{"id": p, "description": d} for p, d in PHASES],
        "tiers": [{"id": t, "description": d} for t, d in TIERS],
        "plans": entries,
    }
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    (PLANS_DIR / "REGISTRY.json").write_text(
        json.dumps(registry, indent=2) + "\n", encoding="utf-8"
    )

    # Compact YAML index for humans
    lines = [
        "# Noetfield future plans registry",
        f"",
        f"**Count:** {len(entries)} | **Generated:** {now}",
        f"",
        "## Phases",
        "",
    ]
    for p, d in PHASES:
        lines.append(f"- `{p}` — {d}")
    lines.append("\n## Tiers\n")
    for t, d in TIERS:
        lines.append(f"- `{t}` — {d}")
    lines.append("\n## Sample IDs (first per phase/T0)\n")
    for phase_slug, _ in PHASES:
        hit = next(e for e in entries if e["phase"] == phase_slug and e["tier"] == "T0")
        lines.append(f"- [{hit['id']}]({hit['path']}) — {hit['title']}")
    (PLANS_DIR / "REGISTRY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Mirror lightweight index for Cursor plans folder
    CURSOR_MIRROR.mkdir(parents=True, exist_ok=True)
    mirror_readme = CURSOR_MIRROR / "README.md"
    mirror_readme.write_text(
        f"# Noetfield OS plans mirror\n\n"
        f"Canonical library: `~/Desktop/Noetfield/os/plans/` ({len(entries)} plans).\n\n"
        f"Regenerate: `python3 scripts/generate-future-plans.py`\n\n"
        f"Full registry: [REGISTRY.json](file:///Users/sinakazemnezhad/Desktop/Noetfield/os/plans/REGISTRY.json)\n",
        encoding="utf-8",
    )
    (CURSOR_MIRROR / "REGISTRY.json").write_text(
        json.dumps({"count": len(entries), "generated_at": now, "canonical": str(PLANS_DIR)}, indent=2),
        encoding="utf-8",
    )

    print(f"Generated {len(entries)} plans under {PLANS_DIR}")
    print(f"Registry: {PLANS_DIR / 'REGISTRY.json'}")
    print(f"Cursor mirror: {CURSOR_MIRROR}")


if __name__ == "__main__":
    main()
