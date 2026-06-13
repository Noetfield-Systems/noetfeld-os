#!/usr/bin/env python3
"""Generate MARKET_SUCCESS_1000_ROADMAP_LOCKED_v3.md — founder/agent only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from market_success_1000_data import (  # noqa: E402
    COMPANIES,
    COMPANY_PROFILES,
    all_phases_steps,
)

OUT = ROOT / "ops" / "private" / "MARKET_SUCCESS_1000_ROADMAP_LOCKED_v3.md"
LEGACY_PATHS = [
    ROOT / "ops" / "private" / "MARKET_SUCCESS_1000_ROADMAP_LOCKED_v1.md",
    ROOT / "ops" / "private" / "MARKET_SUCCESS_1000_ROADMAP_LOCKED_v2.md",
]

GOLDEN_RULES = [
    "**Copy success models, not product scope** — receipt wedge, not SOC2 CCM platform.",
    "**Proof before pitch** — forwardable PDF · ZIP · YAML · verify walkthrough beats deck.",
    "**Complement the stack** — attach inside Purview / CCS / ITSM procurement rails.",
    "**Continuous beats annual** — export_integrity fail-closed today; TLE refresh honest Roadmap.",
    "**Policy packs follow regulation dates** — EU AI Act **2 Aug 2026** orientation on TLE rows.",
    "**Agents do chores internally** — triage · verify · demo prep; never public chatbot SKU.",
    "**Channel beats solo founder** — MSP Phase 2 + one live tenant parallel to direct W3.",
    "**Three SKUs forever** — Trust Brief · Copilot Governance Pack · Bank Pilot only.",
    "**Honest scope is a moat** — Shipped / Orientation / Roadmap / N/A on every hub.",
    "**W3 is economic** — board PDF in governance meeting or deposit ≥ CAD 2K.",
    "**No vendor names on www** — ten models live in ops/private; public copy is pattern-only.",
    "**Pre-execution is the gap** — none of the ten productize signed receipt before Copilot act.",
    "**Board PDF closes regulated buyers** — MetricStream + Vanta proof moment in one artifact.",
    "**Slice under umbrella** — OneTrust lesson: fit GRC budget line, don't become platform.",
    "**Services cash funds product** — Trust Brief 6-week delivery before MRR fiction.",
]

GOLDEN_SUGGESTIONS = [
    "**Start Vancouver, not global.** Trust Brief wedge in healthcare or legal/accounting beats spray outreach.",
    "**Sell Phase 2 to MSPs.** Let CSPs own Purview readiness; Noetfield owns TLE attach after sign-off.",
    "**Run verify-gtm before every external demo.** Green gate is cheaper than reputation repair.",
    "**One design partner deep.** Complyance F500 lesson: depth + reference beats three shallow pilots.",
    "**Use EU AI Act clock in Q2 2026.** Credo/Modulos pattern: regulation date → policy orientation row → intake question.",
    "**Never claim FedRAMP, ISO, SOC2, or EU compliant.** Orientation rows only — honesty converts procurement.",
    "**Forward the ZIP, not the pitch.** Credo portable bundle pattern: procurement persona self-serves in Teams.",
    "**Minutes-to-first-TLE is your KPI.** RegScale velocity mindset: measure evaluate → signed TLE time.",
    "**Defer Governance Monitor MRR.** Drata CCM aspiration is Roadmap until W3 proves receipt demand.",
    "**Capital story = distribution.** You are not inventing AI governance — you are exporting what Microsoft buyers still lack.",
]


def main() -> None:
    lines: list[str] = [
        "# Market Success Models — 1000-Step Roadmap (LOCKED v3)",
        "",
        "| Field | Value |",
        "|-------|--------|",
        "| **Status** | LOCKED founder/agent roadmap — **never public www** |",
        "| **Version** | v3 — full rewrite · unique steps · deep company analysis · golden suggestions |",
        "| **Audience** | Founders · NF-CLOUD-AGENT · investors (private brief only) |",
        "| **Sources** | Ten June 2026 market success models (public positioning · funding · analyst signals) |",
        "| **Not for** | Battlecards · `/compare/` · vendor names on noetfield.com |",
        "| **Parent** | [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](../../docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md) · [WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md](../../docs/WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md) |",
        "| **Verify** | `make verify-market-roadmap` · `make verify-www` · `make verify-gtm` |",
        "",
        "---",
        "",
        "## Golden rules (apply every phase)",
        "",
    ]
    for i, rule in enumerate(GOLDEN_RULES, 1):
        lines.append(f"{i}. {rule}")

    lines.extend(["", "---", "", "## Golden suggestions (founder wisdom)", ""])
    for s in GOLDEN_SUGGESTIONS:
        lines.append(f"- {s}")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Ten market success models (June 2026)",
            "",
            "| # | Company | Archetype | Primary buyer | Proof artifact | GTM motion | 2026 signal | Noetfield tier |",
            "|---|---------|-----------|---------------|----------------|------------|-------------|----------------|",
        ]
    )

    for i, profile in enumerate(COMPANY_PROFILES):
        name, arch, tier, wins, buyer, proof, gtm, signal, _copy, _ignore, _insight = profile
        lines.append(
            f"| {i + 1} | {name} | {arch} | {buyer} | {proof} | {gtm} | {signal} | {tier} |"
        )

    lines.extend(
        [
            "",
            "**Noetfield-only gap:** signed RID-keyed **TLE exported before Copilot operational act** — none of the ten productize this receipt layer.",
            "",
            "---",
            "",
            "## Deep analysis — what to copy vs ignore (per company)",
            "",
        ]
    )

    for i, profile in enumerate(COMPANY_PROFILES, 1):
        name, arch, tier, wins, buyer, proof, gtm, signal, copy, ignore, insight = profile
        lines.extend(
            [
                f"### {i}. {name} (Archetype {arch} · {tier})",
                "",
                f"| Lens | Detail |",
                f"|------|--------|",
                f"| **Wins** | {wins} |",
                f"| **Buyer** | {buyer} |",
                f"| **Proof moment** | {proof} |",
                f"| **GTM motion** | {gtm} |",
                f"| **2026 signal** | {signal} |",
                f"| **Copy for Noetfield** | {copy} |",
                f"| **Do NOT build** | {ignore} |",
                f"| **Golden insight** | *{insight}* |",
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "",
            "## Five archetypes",
            "",
            "| Archetype | Examples | Buyer pays for | Proof moment | Noetfield adaptation |",
            "|-----------|----------|----------------|--------------|----------------------|",
            "| **A — Trust unlock** | Vanta · Drata | Faster sales · fewer questionnaires | Prospect self-serves diligence | Trust center + procurement rail + board PDF |",
            "| **B — AI policy product** | Credo AI · Modulos | Regulatory readiness without bespoke policy | Activated crosswalk + evidence bundle | NIST/EU/AIA orientation rows on TLE |",
            "| **C — Incumbent attach** | IBM · ServiceNow · OneTrust | Govern inside existing procurement | Dashboard in current stack | Phase 2 after readiness · RID handoff |",
            "| **D — Continuous assurance** | RegScale | Always audit-ready vs point-in-time | Live control / export state | YAML + export_integrity + API evaluate |",
            "| **E — Agentic GRC** | Complyance | Agents per workflow chore | Hours saved on evidence tasks | Internal triage/demo/verify agents only |",
            "",
            "---",
            "",
            "## Noetfield tier map (S0–S8)",
            "",
            "| Tier | Name | Market proof | Primary phase |",
            "|------|------|--------------|---------------|",
            "| **S0** | Board PDF moment | Vanta trust · MetricStream board reporting | II · VII · IX |",
            "| **S2** | Complement not replace | IBM/ServiceNow attach · Microsoft CCS | IV |",
            "| **S3** | MSP channel | CSP readiness → Phase 2 TLE | VIII |",
            "| **S4** | Trust center grid | OneTrust/Vanta self-serve diligence | II |",
            "| **S5** | Federal / regulated | watsonx FedRAMP path · GC ADM | IV · VII |",
            "| **S6** | Receipt export wedge | Credo/RegScale portable evidence | III · V · IX |",
            "| **S7** | Automation / CCM | RegScale live controls · Drata rhythm | II · V |",
            "| **S8** | Agentic ops (internal) | Complyance workflow agents | VI |",
            "",
            "---",
            "",
            "## Market context (June 2026)",
            "",
            "- AI governance/compliance ~**$2.5B** category — buyers want **proof**, not platforms.",
            "- **EU AI Act** high-risk obligations **2 Aug 2026** — policy orientation sells before product features.",
            "- **Shadow AI** (~87% without active audit) — sanctioned Copilot + receipted decisions is the wedge.",
            "- **Agentic GRC** — agents per workflow (Complyance), not generic chatbot SKU.",
            "- **Microsoft CSP** 3-year Copilot (May 2026) + Purview promo through **Jun 30 2026** → MSP attach window.",
            "- **GC Canada ADS deadline** **June 24, 2026** — federal Trust Brief attach timing.",
            "",
            "---",
            "",
            "## Phase overview",
            "",
            "| Phase | Steps | Focus | Companies / archetypes |",
            "|-------|-------|-------|------------------------|",
            "| **I** | 1–100 | Market truth lock | All 10 × 10 analysis steps |",
            "| **II** | 101–200 | Trust unlock | Vanta · Drata |",
            "| **III** | 201–300 | AI policy product | Credo AI · Modulos |",
            "| **IV** | 301–400 | Incumbent attach | IBM · ServiceNow · OneTrust |",
            "| **V** | 401–500 | Continuous assurance | RegScale |",
            "| **VI** | 501–600 | Agentic GRC (internal) | Complyance |",
            "| **VII** | 601–700 | Enterprise regulated | MetricStream · watsonx |",
            "| **VIII** | 701–800 | MSP channel | CSP · partners |",
            "| **IX** | 801–900 | Receipt wedge product | Noetfield-only synthesis |",
            "| **X** | 901–1000 | W3 · capital readiness | All archetypes closeout |",
            "",
            "---",
            "",
            "## Full e2e verify gate (run from scratch before external demo)",
            "",
            "```bash",
            "cd Noetfield",
            "make dev-local-down 2>/dev/null || true",
            "make verify-all-static",
            "cd governance-console/backend && PYTHONPATH=. python3 -m pytest tests/test_tle_flow.py tests/test_audit_events.py -q",
            "cd ../..",
            "NF_DEV_FORCE_DASHBOARD_BUILD=1 make dev-local-pro",
            "make verify-ui-e2e",
            "make verify-gtm",
            "```",
            "",
            "---",
            "",
        ]
    )

    step_num = 0
    outcomes: list[tuple[str, str, str]] = []

    for pid, title, steps in all_phases_steps():
        start = step_num + 1
        end = step_num + 100
        step_num = end
        short = title.split("(")[0].strip() if "(" in title else title
        outcomes.append((pid, f"{start}–{end}", short))

        lines.extend(
            [
                f"## Phase {pid} — {title} (Steps {start}–{end})",
                "",
                "| # | Step | Archetype | Tier | Done when |",
                "|---|------|-----------|------|-----------|",
            ]
        )
        for i, (step, arch, tier, done) in enumerate(steps, start=start):
            lines.append(f"| {i} | {step} | {arch} | {tier} | {done} |")
        lines.extend(["", "---", ""])

    lines.extend(
        [
            "## Execution index",
            "",
            "| Phase | Steps | Primary outcome |",
            "|-------|-------|-----------------|",
        ]
    )
    for pid, span, outcome in outcomes:
        lines.append(f"| {pid} | {span} | {outcome} |")

    lines.extend(
        [
            "",
            "## Regenerate",
            "",
            "```bash",
            "python3 scripts/generate-market-success-1000-roadmap.py",
            "make verify-market-roadmap",
            "```",
            "",
            "_Generated by `scripts/generate-market-success-1000-roadmap.py` + `scripts/market_success_1000_data.py` (v3)_",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    for legacy in LEGACY_PATHS:
        if legacy.exists() and legacy != OUT:
            legacy.unlink()
    print(f"Wrote {OUT} (1000 unique steps)")


if __name__ == "__main__":
    main()
