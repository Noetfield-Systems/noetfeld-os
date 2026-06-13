"""Shared WISE prompt enrichment for Noetfield agent packs (v14)."""
from __future__ import annotations

FORBIDDEN_DEFAULT = [
    "vendor comparison pages",
    "fourth nf-offer-card SKU on homepage offerings grid",
    "Trust Ledger SaaS checkout or stripe-buy-button",
    "fake certs, logos, ARR, or analyst firm stats",
    "MSB/payment/custody as Noetfield www lead",
    "TrustField/VIRLUX product build scope",
    "hand-editing GTM HTML outside rebuild-www-v6.py",
    "mandatory sales call for sandbox signup",
]

W3_SIGNALS = {
    "sandbox_start": "Prospect starts /start/ without sales — 14d · 50 evaluates",
    "intake_conversion": "Trust Brief / gate intake path converts",
    "www_proof": "Public www tells receipt-first wedge story",
    "trust_diligence": "Procurement can diligence without call",
    "design_partner": "Scarcity + investor honesty without fiction",
    "demo_live": "≤5 min demo on dev or staging URL",
    "tle_artifact": "TLE samples + verify path credible",
    "export_e2e": "Board PDF + procurement ZIP reachable in product",
    "workspace_path": "Evaluate → result → workspace exports",
    "channel_attach": "MSP or federal Phase 2 narrative",
    "ship_green": "verify-gtm / e2e green after change",
}

# W3 maturity — critical path ids for auto-dispatch (v16)
W3_CRITICAL_PATH = ["S-01", "E-01", "E-04", "E-05", "E-06", "L-03", "P-01"]
W3_DEFAULT_CHAIN = ["S-01", "E-01", "E-05", "E-06", "L-02", "P-01"]

BUYER_PROOF_BY_SIGNAL = {
    "sandbox_start": "A developer signs up on /start/ and evaluates intent in sandbox without a sales call.",
    "export_e2e": "A GRC lead can download a board PDF or procurement ZIP from a real TLE path.",
    "demo_live": "A CISO completes evaluate → TLE → export in ≤5 minutes on demo URL.",
    "www_proof": "A buyer lands on www and understands: we receipt Copilot execution, not replace Purview.",
    "trust_diligence": "Procurement finds honest scope table + samples without a sales call.",
    "intake_conversion": "Primary CTA routes to Trust Brief intake with traceable RID.",
    "design_partner": "Investor/prospect sees honest scarcity — no fake logos or ARR.",
    "tle_artifact": "Sample TLE + verify page prove fail-closed export integrity.",
    "workspace_path": "Product loop shows confidence score and export links on TLE detail.",
    "channel_attach": "MSP/federal buyer sees Phase 2 attach — complement, not vendor comparison.",
    "ship_green": "verify-gtm green — ship confidence for founder demo/outreach.",
}


def buyer_proof(p: dict) -> str:
    sig = p.get("w3_signal", "")
    if sig in BUYER_PROOF_BY_SIGNAL:
        return BUYER_PROOF_BY_SIGNAL[sig]
    return f"Buyer-visible: {p.get('done_when', 'outcome matches commercial SSOT')}"


def reasoning_steps(p: dict) -> list[str]:
    return [
        "**Witness** — Read context budget only; check tier1-status.json for dependencies.",
        f"**Intent** — One artifact: {p.get('title', 'task')}. Buyer proof: {buyer_proof(p)[:100]}…",
        "**Scope** — Smallest diff; match success reference copy tone; no drive-by refactors.",
        "**Evidence** — Run verify command; if fail, recovery path below — do not widen scope.",
    ]


def self_check_rubric(p: dict) -> list[str]:
    base = [
        "Does this help W3 (sandbox start OR board PDF in meeting OR deposit ≥ CAD 2K)?",
        "Did I stay within 5-file context budget and three-SKU lock (nf-pack-card free tier OK on /start/ only)?",
        "Verify command passed without weakening assertions?",
    ]
    if p.get("agent_mode") == "hub":
        base.insert(0, "Hub-only: NF-CLOUD must NOT send email/calendar/PII.")
    if p.get("phase") == "LAND":
        base.append("No vendor compare table or certifier fiction on public www?")
    if p.get("w3_signal") == "export_e2e":
        base.append("Export path is real product/workspace — not a static fake link?")
    return base


def recovery_if_fail(p: dict) -> str:
    return (
        f"If verify fails: (1) read error output, (2) fix smallest diff in `{p.get('context_budget', ['repo'])[0]}`, "
        f"(3) re-run verify once. If still blocked → stop_if triggers → ask founder. "
        f"Do NOT pick Tier 2 or archive prompts to 'work around' this task."
    )


def infer_w3_maturity(status: dict[str, str]) -> tuple[int, str, str]:
    """Returns (stage 0-4, label, recommended bottleneck)."""
    done = {k for k, v in status.items() if v == "done"}
    if "E-05" in done and "E-06" in done and "P-01" in done:
        if len(done) >= 15:
            return 4, "EXPAND", "pipeline"
        return 3, "PROVE+", "ship"
    if "E-01" in done:
        if "E-05" not in done or "E-06" not in done:
            return 2, "EXPORT", "export"
        return 3, "TRUST", "trust"
    if "L-02" in done or "L-03" in done:
        return 1, "DEMO", "demo"
    return 0, "FOUNDATION", "www"


def build_wise_agent_prompt(p: dict) -> str:
    forbidden = p.get("forbidden", FORBIDDEN_DEFAULT)
    ctx = p.get("context_budget", [])
    preflight = p.get("preflight", [
        "Read `.cursor/agent-memory/MEMORY_LOCKED.yaml` — Noetfield only",
        "Read `docs/ops/plans/tier1-status.json` — confirm dependencies done",
        "Confirm ≤3 tasks this session (GTM 60-day lock)",
    ])
    lines = [
        "## Role",
        "NF-CLOUD-AGENT (Noetfield repo only) — Lane A. Hub-only (`agent_mode: hub`): stop and hand off.",
        "",
        "## WISE frame",
        "| Step | Rule |",
        "|------|------|",
        "| **W**itness | Repo state + deps before edits |",
        "| **I**ntent | One buyer-visible outcome |",
        "| **S**cope | Max 5 files · forbidden list |",
        "| **E**vidence | Verify command + self-check |",
        "",
        "## Context",
        f"- **W3 signal:** {W3_SIGNALS.get(p.get('w3_signal', ''), p.get('w3_signal', ''))}",
        f"- **Buyer persona:** {p.get('persona', 'Ops')}",
        f"- **Effort:** {p.get('effort', 'M')} · **Mode:** {p.get('agent_mode', 'cloud')}",
        f"- **Success reference:** {p.get('success_reference', 'Commercial SSOT')}",
        f"- **Buyer proof:** {buyer_proof(p)}",
        "",
        "## Reasoning (follow in order)",
    ]
    for i, step in enumerate(reasoning_steps(p), 1):
        lines.append(f"{i}. {step}")
    lines.extend(["", "## Preflight"])
    for x in preflight:
        lines.append(f"- {x}")
    if p.get("requires"):
        lines.extend(["", "## Dependencies", f"- Requires **done** in tier1-status: {', '.join(p['requires'])}"])
    if p.get("unblocks"):
        lines.extend(["", "## Unblocks when done", f"- {', '.join(p['unblocks'])}"])
    lines.extend(["", "## Context budget (max 5 — do not read outside)"])
    for c in ctx[:5]:
        lines.append(f"- `{c}`")
    lines.extend(["", "## Task", p.get("task", ""), "", "## Forbidden"])
    for f in forbidden:
        lines.append(f"- {f}")
    if p.get("stop_if"):
        lines.extend(["", "## Stop and ask founder if"])
        for s in p["stop_if"]:
            lines.append(f"- {s}")
    lines.extend(["", "## Verify", f"```bash\n{p.get('verify', 'make verify-gtm')}\n```", "", "## Done when", p.get("done_when", ""), "", "## Self-check (all must be yes)",])
    for q in self_check_rubric(p):
        lines.append(f"- [ ] {q}")
    lines.extend(["", "## Recovery if verify fails", recovery_if_fail(p), "", "## Closeout", "1. `python3 scripts/sync-tier1-status.py --done " + p.get("id", "ID") + "`", "2. `reports/cursor-reply-latest.txt` with verify output", "3. `make verify-gtm` or plan-with-no-asf-verify if www/API touched"])
    return "\n".join(lines)
