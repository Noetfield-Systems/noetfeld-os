#!/usr/bin/env python3
"""Regenerate Noetfield GTM www pages — v6 ground-up rebuild."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WWW_VER = "30"

# Copilot Governance Pack — locked lead SKU ($2k–10k · 90 days · board PDF success signal)
PILOT_SKU = "Copilot Governance Pack"
PILOT_BAND = "$2k–10k · 90 days"
PILOT_SUCCESS = "board PDF in a real governance meeting"
PILOT_INTAKE = "/trust-brief/intake/?interest=pilot&vector=copilot-governance"
TRUST_BRIEF_INTAKE = "/trust-brief/intake/"
WORK_WITH_US_INTAKE = "/trust-brief/intake/?interest=partner&vector=work-with-us"
MEGA_CTA_TITLE = "Board PDF in your next governance meeting"

# Lane-native north star (docs/strategy/NOETFIELD_DIGITAL_TRUST_LANE_LOCKED_v1.md)
LANE_NORTH_STAR = (
    "For regulated EU and US institutions rolling out Microsoft 365 Copilot: Noetfield produces "
    "board-grade, tamper-evident go/no-go receipts — signed Trust Ledger Entries, confidence scores, "
    "and procurement exports — before production scope opens."
)

# Above-fold regulatory marquee — EU + US institutional lane (orientation only)
HERO_MARQUEE = ["EU AI Act Art. 12", "ISO 42001", "DORA orientation", "NIST AI RMF"]

FONT_LINK = (
    ' <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    ' <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    ' <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400..700;1,14..32,400..700&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap" />'
)

SCOPE_LABELS = {
    "available": "Available",
    "orientation": "Orientation",
    "roadmap": "Planned",
    "na": "Out of scope",
}
SCOPE_BADGES = {
    "available": "nf-signal-badge--available",
    "orientation": "nf-signal-badge--orientation",
    "roadmap": "nf-signal-badge--roadmap",
    "na": "nf-signal-badge--na",
}

# Commercial narrative — SSOT: docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md · docs/GTM_COPYBOOK.md
COPY = {
    "meta_home": "Board-grade Copilot governance for EU and US regulated institutions — tamper-evident decision records, signed TLE receipts, fail-closed export. Copilot Governance Pack $2k–10k.",
    "hero_h1": "The audit trail your Copilot deployment will be asked for later",
    "hero_lead": (
        "Noetfield is the <strong>AI Governance &amp; Evidence</strong> layer for Microsoft 365 Copilot — "
        "<strong>board-grade, tamper-evident decision records</strong> for <strong>EU and US regulated institutions</strong>. "
        "Every go/no-go produces a signed Trust Ledger Entry — a record <strong>independent of the app under audit</strong> — "
        "invalid changes <strong>blocked</strong>, allowed decisions <strong>receipted</strong>, export <strong>fail closed</strong> on tamper. "
        "Metadata-only M365 · evaluate → record → export before production scope opens."
    ),
    "demo_sentence": "Show the record your auditor would accept before Copilot touches production data.",
    "mega_sub": (
        "Non-confidential intake · include your Request ID · Copilot Governance Pack ($2k–10k · 90 days · board PDF), "
        "Trust Brief ($10k), federal or MSP lane · operations@noetfield.com"
    ),
    "scope_lead": "Honest scope for procurement — what you can demo, export, and defend today.",
    "footer_note": (
        "AI Governance &amp; Evidence for Microsoft 365 Copilot. Govern execution before production scope opens — "
        "signed TLE v1, board PDF, procurement ZIP. Invalid changes blocked · allowed decisions receipted · export fails closed on tamper."
    ),
    "sandbox_limits": "14-day sandbox · 50 evaluate calls · mock M365 connectors · no sales call",
    "m365_position": (
        "Metadata-only M365 evidence index on every Trust Ledger Entry — Purview · Entra · audit references "
        "plus signed execution receipts, board PDF, and procurement exports."
    ),
    "production_upgrade": (
        "Production tenant, real metadata connectors, and board PDF export unlock via "
        "<strong>Copilot Governance Pack ($2k–10k)</strong> or Trust Brief SOW."
    ),
    "first_receipt_promise": (
        "Run one evaluate · get one signed receipt · <strong>before your next Copilot standup</strong> "
        "(~5 minutes in sandbox)."
    ),
    "closing_competitive": (
        "Roll out Copilot with <strong>signed receipts</strong> — board PDF, procurement ZIP, and verified export integrity."
    ),
}

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>{title}</title>
 <meta name="description" content="{desc}" />
 <meta name="robots" content="index,follow" />
 <meta name="theme-color" content="#f4f5f8" />
 <link rel="canonical" href="https://www.noetfield.com{canonical}" />
 <link rel="icon" href="/noetfield-favicon-512.png" type="image/png" />
{font_link}
 <link rel="stylesheet" href="/assets/noetfield-tokens.css" />
 <link rel="stylesheet" href="/assets/noetfield-shell.css" />
 <link rel="stylesheet" href="/assets/noetfield-www.css?v={www_ver}" />
 <link rel="stylesheet" href="/assets/noetfield-print.css?v={www_ver}" media="print" />
 <script src="/assets/noetfield-shell.js?v={www_ver}" defer></script>
</head>
<body class="{body_class}">
 <div class="bg" aria-hidden="true"></div>
 <a class="skip" href="#main">Skip to content</a>
 <header id="nfHeader"></header>
 <main id="main" class="nf-main nf-page">
"""

FOOT = """
 </main>
 <footer id="nfFooter"></footer>
</body>
</html>
"""


def receipt(rid: str = "RID-2026-0602-HOME", footer: str = "Live sample · <a href=\"/trust-ledger/sample-report/\">Download TLE YAML</a>") -> str:
    return f"""
 <div class="nf-artifact-panel">
 <div class="nf-artifact-panel-chrome">
 <span class="nf-artifact-panel-dots" aria-hidden="true"><i></i><i></i><i></i></span>
 <span class="nf-artifact-panel-file">tle-receipt.yaml</span>
 <span class="nf-artifact-panel-badge">Verified</span>
 </div>
 <aside class="nf-receipt-mock" aria-label="Trust Ledger Entry receipt">
 <dl class="nf-receipt-mock-body">
 <div class="nf-receipt-row"><dt>tle_id</dt><dd>TLE-015DCFB8B953</dd></div>
 <div class="nf-receipt-row"><dt>decision</dt><dd>allow</dd></div>
 <div class="nf-receipt-row"><dt>confidence_score</dt><dd>0.82</dd></div>
 <div class="nf-receipt-row"><dt>rid</dt><dd>{rid}</dd></div>
 <div class="nf-receipt-row"><dt>evidence_index</dt><dd>purview · entra · audit</dd></div>
 <div class="nf-receipt-row"><dt>export_integrity</dt><dd class="nf-receipt-ok">PASS · fail closed on tamper</dd></div>
 </dl>
 <p class="nf-receipt-mock-footer">{footer}</p>
 </aside>
 </div>"""


def live_proof_panel() -> str:
    """UI-01 Governance Playground — scenario picker + mini evaluate + scorecard receipt."""
    return f"""
 <div id="nfLiveProofHero" class="nf-live-proof-panel" data-live-proof-hero="live-proof-hero" aria-label="Governance playground">
 <form id="nfLiveProofForm" class="nf-live-proof-form">
 <h3>Governance playground</h3>
 <p id="nfScenarioOfDay" class="nf-scenario-of-day" aria-live="polite"></p>
 <p class="nf-scorecard-hint">Every go/no-go gets a <strong>confidence score</strong> + evidence index — not a black-box AI yes.</p>
 <label>Scenario
 <select name="scenario" id="nfLiveProofScenario" aria-label="Evaluate scenario">
 <option value="copilot_rollout" selected>Copilot rollout · production scope</option>
 <option value="guest_access">Guest access · external sharing</option>
 <option value="data_export">Bulk export · high sensitivity</option>
 </select>
 </label>
 <label>Actor<input type="text" name="actor" value="security-team" autocomplete="off" /></label>
 <label>Action<input type="text" name="action" value="copilot_rollout" autocomplete="off" /></label>
 <label>Context<textarea name="context">Copilot rollout governance check — homepage playground</textarea></label>
 <button type="submit" class="btn btn-primary">Evaluate intent</button>
 </form>
 <div id="nfLiveProofReceipt" class="nf-live-proof-receipt-host" aria-live="polite">
 {receipt()}
 </div>
 </div>
 <script src="/assets/noetfield-live-proof.js?v={WWW_VER}" defer></script>"""


def trial_os_wizard() -> str:
    """UI-02 Trial OS — Sumsub-class sandbox wizard."""
    return f"""
 <div id="nfTrialOs" class="nf-trial-os" data-trial-os-flow="trial-os-flow" aria-label="Trial OS wizard">
 <p class="nf-trial-os__usage" data-nf-usage-chip hidden>0/50 evaluates · 14 days left</p>
 <ol class="nf-trial-os__stepper" aria-label="Sandbox setup steps">
 <li class="nf-trial-os__step is-active"><span class="nf-trial-os__step-num">1</span> Account</li>
 <li class="nf-trial-os__step"><span class="nf-trial-os__step-num">2</span> Environment</li>
 <li class="nf-trial-os__step"><span class="nf-trial-os__step-num">3</span> Connect M365</li>
 <li class="nf-trial-os__step"><span class="nf-trial-os__step-num">4</span> First evaluate</li>
 <li class="nf-trial-os__step"><span class="nf-trial-os__step-num">5</span> Receipt + export</li>
 </ol>
 <div class="nf-trial-os__panel is-active" data-step="0">
 <form id="nfTrialAccountForm" class="nf-sandbox-form" aria-labelledby="trial-account-title">
 <h3 id="trial-account-title">Create your developer sandbox</h3>
 <p class="nf-section-lead">No credit card · no sales call · {COPY["sandbox_limits"]}</p>
 <label>Work email<input type="email" name="email" required autocomplete="email" placeholder="you@company.com" /></label>
 <label>Organization (optional)<input type="text" name="org" autocomplete="organization" placeholder="Your team or company" /></label>
 <div class="nf-trial-os__actions"><button type="submit" class="btn btn-primary">Continue</button></div>
 </form>
 </div>
 <div class="nf-trial-os__panel" data-step="1">
 <h3>Environment mode</h3>
 <div class="nf-trial-os__env">
 <article class="nf-trial-os__env-tile is-active"><strong>Sandbox</strong><p>Mock M365 · 50 evaluate calls · 14-day trial · active now.</p></article>
 <article class="nf-trial-os__env-tile is-locked"><strong>Production</strong><p>Real metadata index · board PDF · Governance Pack production keys.</p><span class="nf-trial-os__lock">🔒 <a href="/copilot/pilot/">Apply for Governance Pack</a></span></article>
 </div>
 <div class="nf-trial-os__actions"><button type="button" class="btn btn-primary" data-trial-next="2">Continue in sandbox</button></div>
 </div>
 <div class="nf-trial-os__panel" data-step="2">
 <h3>Connect mock M365</h3>
 <p class="nf-section-lead">One-click OAuth success UI — metadata-only Purview · Entra · audit (sandbox simulation).</p>
 <div class="nf-trial-os__mock-oauth"><button type="button" id="nfTrialMockOAuth" class="btn btn-primary">Register + mock connect (M365)</button></div>
 <p id="nfTrialOAuthStatus" class="nf-callout" hidden role="status"></p>
 <div class="nf-trial-os__actions"><button type="button" class="btn btn-primary" data-trial-next="3">Continue</button></div>
 </div>
 <div class="nf-trial-os__panel" data-step="3">
 <h3>First evaluate</h3>
 <form id="nfTrialEvaluateForm"><p class="nf-section-lead">Submit operational intent — confidence score · RID-threaded audit log.</p><div class="nf-trial-os__actions"><button type="submit" class="btn btn-primary">Run first evaluate</button></div></form>
 </div>
 <div class="nf-trial-os__panel" data-step="4">
 <h3>Receipt + export orientation</h3>
 <p class="nf-section-lead">RID <code data-trial-rid>RID-pending</code> · sample TLE YAML · board PDF path · procurement ZIP orientation.</p>
 <div class="nf-trial-os__api-drawer">
 <strong>API drawer</strong> · key preview <code data-api-key>nf_sbx_…</code> · <a href="/docs/api/">API reference</a>
 <pre data-curl-example>curl example loads after signup</pre>
 </div>
 <div class="nf-trial-os__actions">
 <button type="button" id="nfTrialFinish" class="btn btn-primary">Open Governance Console</button>
 <a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for Governance Pack · $2k–10k</a>
 <a class="btn btn-secondary" href="/trust-ledger/sample-report/">Download sample export orientation</a>
 </div>
 </div>
 </div>
 <script src="/assets/noetfield-sandbox.js?v={WWW_VER}" defer></script>"""


def sticky_mobile_cta() -> str:
    return f"""
 <div class="nf-sticky-mobile-cta" aria-label="Quick start">
 <a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for pilot · $2k–10k</a>
 <a class="btn btn-secondary" href="/copilot/demo/">5-minute demo</a>
 </div>"""


def panel(label: str, items: list[str], btn: str = "") -> str:
    lis = "".join(f"<li>{i}</li>" for i in items)
    b = f'<a class="btn btn-secondary" href="{btn}">Trust Ledger Workspace</a>' if btn else ""
    return f"""
 <aside class="nf-hero-panel" aria-label="{label}">
 <p class="nf-hero-panel-label">{label}</p>
 <ul class="nf-hero-panel-list">{lis}</ul>
 {b}
 </aside>"""


def hero(kicker: str, eyebrow: str, h1: str, lead: str, badges: list[tuple[str, bool]], actions: list[tuple[str, str, bool]], tags: list[str], side: str, *, h1_class: str = "") -> str:
    badge_html = "".join(
        f'<span class="nf-badge-pill{" nf-badge-pill--gold" if gold else ""}">{t}</span>' for t, gold in badges
    )
    act_html = "".join(
        f'<a class="btn btn-{"primary" if pri else "secondary"}" href="{href}">{label}</a>' for href, label, pri in actions
    )
    tag_html = "".join(f"<li>{t}</li>" for t in tags)
    kick = f'<p class="nf-hero-kicker"><span class="nf-hero-kicker-dot" aria-hidden="true"></span> {kicker}</p>' if kicker else ""
    eye = f'<p class="nf-eyebrow">{eyebrow}</p>' if eyebrow else ""
    h1_attr = f' class="{h1_class}"' if h1_class else ""
    return f"""
 <header class="nf-hero-cinematic">
 <div>
 {kick}
 {eye}
 <h1{h1_attr}>{h1}</h1>
 <p class="nf-lead">{lead}</p>
 <div class="nf-hero-badges">{badge_html}</div>
 <div class="nf-cta-actions">{act_html}</div>
 <ul class="nf-marquee" aria-label="Framework alignment">{tag_html}</ul>
 </div>
 {side}
 </header>"""


def scope_rows_html() -> str:
    items = [
        ("Pre-execution evaluate", "available"),
        ("TLE v1 + workspace UI", "available"),
        ("Board PDF · procurement ZIP", "available"),
        ("M365 metadata connectors", "available"),
        ("Framework citations", "orientation"),
        ("Payment rails / MSB execution", "na"),
    ]
    labels = SCOPE_LABELS
    return "".join(
        f'<div class="nf-trust-signal"><span class="nf-trust-signal-label">{l}</span>'
        f'<span class="nf-signal-badge {SCOPE_BADGES[k]}">{labels[k]}</span></div>'
        for l, k in items
    )


def scope_block() -> str:
    return f"""
 <section class="nf-trust-signals" aria-labelledby="scope-title">
 <h2 id="scope-title">Available now — capability scope</h2>
 <p class="nf-trust-signals-lead">{COPY["scope_lead"]}</p>
 <div class="nf-trust-signals-grid">{scope_rows_html()}</div>
 </section>"""


def scope_block_inner() -> str:
    return f"""
 <div class="nf-trust-signals nf-block-inner" id="scope-title">
 <h3>Available now — capability scope</h3>
 <p class="nf-trust-signals-lead">{COPY["scope_lead"]}</p>
 <div class="nf-trust-signals-grid">{scope_rows_html()}</div>
 </div>"""


def stat_bar() -> str:
    return outcome_stat_bar()


def outcome_stat_bar() -> str:
    return """
 <div class="nf-stat-bar nf-stat-bar--outcome" role="region" aria-label="Outcome metrics">
 <div class="nf-stat-bar-item"><strong>$2k–10k</strong><span>Copilot Governance Pack · 90 days · board PDF</span></div>
 <div class="nf-stat-bar-item"><strong>1 RID</strong><span>Intake → evaluate → export on one thread</span></div>
 <div class="nf-stat-bar-item"><strong>4 exports</strong><span>TLE · board PDF · procurement ZIP · audit</span></div>
 <div class="nf-stat-bar-item"><strong>EU + US</strong><span>Regulated institutions · metadata-only M365</span></div>
 </div>"""


def investor_stat_bar() -> str:
    return """
 <div class="nf-stat-bar" role="region" aria-label="Investor metrics">
 <div class="nf-stat-bar-item"><strong>Live</strong><span>Evaluate · TLE · export available</span></div>
 <div class="nf-stat-bar-item"><strong>$10k</strong><span>Trust Brief land wedge</span></div>
 <div class="nf-stat-bar-item"><strong>90d</strong><span>Governance Pack pilot</span></div>
 <div class="nf-stat-bar-item"><strong>3</strong><span>Locked SKUs only</span></div>
 </div>"""


def mega_cta(title: str = MEGA_CTA_TITLE, sub: str | None = None, primary: tuple[str, str] = (PILOT_INTAKE, "Apply for pilot ($2k–10k)"), secondary: tuple[str, str] | None = ("/trust-brief/intake/", "Request Trust Brief ($10k)")) -> str:
    sub_text = sub if sub is not None else COPY["mega_sub"]
    sec = f'<a class="btn btn-secondary" href="{secondary[0]}">{secondary[1]}</a>' if secondary else ""
    return f"""
 <section class="nf-cta-mega" aria-labelledby="cta-h">
 <h2 id="cta-h">{title}</h2>
 <p>{sub_text}</p>
 <div class="nf-cta-actions">
 <a class="btn btn-primary" href="{primary[0]}">{primary[1]}</a>
 {sec}
 </div>
 </section>"""


def hero_artifacts(*parts: str) -> str:
    return f'<div class="nf-hero-artifacts">{"".join(parts)}</div>'


def procurement_rail() -> str:
    return """
 <nav class="nf-procurement-rail" aria-label="Procurement diligence path">
 <p class="nf-procurement-rail__label">Procurement</p>
 <a href="/trust/">Trust center</a>
 <a href="/copilot/procurement/">Diligence pack</a>
 <a href="/trust-ledger/sample-report/">TLE samples</a>
 <a href="/trust-ledger/verify/">Verify export</a>
 </nav>"""


def self_serve_rail() -> str:
    return f"""
 <nav class="nf-self-serve-rail" aria-label="Self-serve product access">
 <p class="nf-self-serve-rail__label">Try without a sales call</p>
 <a href="/copilot/pilot/">Copilot Governance Pack</a>
 <a href="/start/">Developer sandbox</a>
 <a href="/copilot/demo/">5-minute demo</a>
 <a href="/docs/api/">Governance API</a>
 <a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for pilot</a>
 <a class="btn btn-secondary" href="/start/">Start sandbox</a>
 </nav>"""


def revenue_path_ladder_inner() -> str:
    """Commercial path ladder — embed inside a parent section (homepage compression)."""
    return f"""
 <div class="nf-block-inner nf-revenue-path" id="revenue-path" aria-labelledby="revenue-path-label">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">$</span><div>
 <p class="nf-eyebrow" id="revenue-path-label">Commercial path</p>
 <h3>Learn in sandbox · earn with Governance Pack · expand on proof</h3>
 <p class="nf-section-lead">Fixed-fee entry · board PDF success signal · same evaluate → TLE → export spine at every tier.</p>
 </div></div>
 <div class="nf-revenue-ladder">
 <a class="nf-revenue-step" href="/start/"><span class="nf-revenue-step__num">Try</span><strong>Free sandbox</strong><span>14 days · 50 evaluates · mock M365 · no sales call</span></a>
 <span class="nf-milestone-arrow" aria-hidden="true">→</span>
 <a class="nf-revenue-step nf-revenue-step--gold" href="{PILOT_INTAKE}"><span class="nf-revenue-step__num">Lead</span><strong>Copilot Governance Pack</strong><span>$2k–10k · 90 days · board PDF in governance meeting</span></a>
 <span class="nf-milestone-arrow" aria-hidden="true">→</span>
 <a class="nf-revenue-step" href="/trust-brief/"><span class="nf-revenue-step__num">Land</span><strong>Trust Brief</strong><span>$10k · 6 weeks · policy map before scale</span></a>
 <span class="nf-milestone-arrow" aria-hidden="true">→</span>
 <span class="nf-revenue-step"><span class="nf-revenue-step__num">Expand</span><strong>Seats + export cadence</strong><span>Production keys · MSP attach · enterprise SOW</span></span>
 </div>
 <aside class="nf-callout nf-callout--urgency"><p><strong>W3 economic signal:</strong> deposit ≥ CAD 2K or signed LOI on Copilot Governance Pack — one org uses board PDF in a real governance meeting.</p></aside>
 </div>"""


def homepage_depth_links() -> str:
    """Compact links to full buyer depth on pilot landing."""
    return """
 <nav class="nf-depth-links" aria-label="Deeper buyer resources on pilot page">
 <p class="nf-depth-links__label">Full buyer depth</p>
 <a href="/copilot/pilot/#digital-trust-lane">Digital trust lane</a>
 <a href="/copilot/pilot/#buyer-triggers">Regulated buyer map</a>
 <a href="/copilot/pilot/#governance-gaps">Governance gaps</a>
 <a href="/copilot/pilot/#buyer-voices">Buyer voices</a>
 <a href="/copilot/pilot/#automation-title">Automated governance</a>
 </nav>"""


def revenue_path_strip() -> str:
    """Commercial earn path — learn in sandbox · contract via Governance Pack."""
    return f"""
 <section class="nf-section-block nf-section--elevated" aria-labelledby="revenue-path">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">$</span><div>
 <p class="nf-eyebrow" id="revenue-path">Commercial path</p>
 <h2>Learn in sandbox · earn with Governance Pack · expand on proof</h2>
 <p class="nf-section-lead">Fixed-fee entry · board PDF success signal · same evaluate → TLE → export spine at every tier.</p>
 </div></div>
 <div class="nf-revenue-ladder">
 <a class="nf-revenue-step" href="/start/"><span class="nf-revenue-step__num">Try</span><strong>Free sandbox</strong><span>14 days · 50 evaluates · mock M365 · no sales call</span></a>
 <span class="nf-milestone-arrow" aria-hidden="true">→</span>
 <a class="nf-revenue-step nf-revenue-step--gold" href="{PILOT_INTAKE}"><span class="nf-revenue-step__num">Lead</span><strong>Copilot Governance Pack</strong><span>$2k–10k · 90 days · board PDF in governance meeting</span></a>
 <span class="nf-milestone-arrow" aria-hidden="true">→</span>
 <a class="nf-revenue-step" href="/trust-brief/"><span class="nf-revenue-step__num">Land</span><strong>Trust Brief</strong><span>$10k · 6 weeks · policy map before scale</span></a>
 <span class="nf-milestone-arrow" aria-hidden="true">→</span>
 <span class="nf-revenue-step"><span class="nf-revenue-step__num">Expand</span><strong>Seats + export cadence</strong><span>Production keys · MSP attach · enterprise SOW</span></span>
 </div>
 <aside class="nf-callout nf-callout--urgency"><p><strong>W3 economic signal:</strong> deposit ≥ CAD 2K or signed LOI on Copilot Governance Pack — one org uses board PDF in a real governance meeting.</p></aside>
 </section>"""


def production_upgrade_callout() -> str:
    return f"""
 <aside class="nf-callout"><p><strong>Production evidence path:</strong> {COPY["production_upgrade"]}</p></aside>"""


def copilot_governance_gaps_section() -> str:
    """Three governance gaps — problem framing without vendor comparison."""
    return """
 <section class="nf-section-block nf-section--elevated" aria-labelledby="governance-gaps">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">!</span><div>
 <p class="nf-eyebrow" id="governance-gaps">Governance gaps</p>
 <h2>Three gaps regulated Copilot rollouts must close before production</h2>
 <p class="nf-section-lead">Policy readiness alone does not produce a signed go/no-go record your board and auditors can inspect.</p>
 </div></div>
 <div class="nf-traps-grid">
 <article class="nf-trap-card"><p class="nf-trap-card__label">Gap 01</p><h3>No signed execution receipt per go/no-go</h3><p>Labels and policies exist — but audit asks for a tamper-evident decision record tied to each Copilot rollout decision.</p></article>
 <article class="nf-trap-card"><p class="nf-trap-card__label">Gap 02</p><h3>Evidence scattered across inboxes and decks</h3><p>When risk committee asks who approved production scope, the thread is not exportable for diligence.</p></article>
 <article class="nf-trap-card"><p class="nf-trap-card__label">Gap 03</p><h3>Audit discovery after rollout — not before</h3><p>Boards and regulators ask for records <em>after</em> Copilot touched production data unless you receipt decisions upfront.</p></article>
 </div>
 </section>"""


def digital_trust_lane_block() -> str:
    """Noetfield lane definition — Copilot rollout trust (no vendor names)."""
    return f"""
 <section class="nf-section-block nf-section--elevated" aria-labelledby="digital-trust-lane">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">◎</span><div>
 <p class="nf-eyebrow" id="digital-trust-lane">Digital trust lane</p>
 <h2>Trust at Copilot rollout decisions — not identity onboarding, not generic LLM proxy</h2>
 <p class="nf-section-lead">{LANE_NORTH_STAR}</p>
 </div></div>
 <div class="nf-lane-grid">
 <article class="nf-lane-card"><p class="nf-lane-card__tag">Noetfield wedge</p><h3>Copilot go/no-go evidence</h3><p>Evaluate operational intent → signed TLE → board PDF + procurement ZIP. Metadata-only M365 stack.</p></article>
 <article class="nf-lane-card"><p class="nf-lane-card__tag">Buyer</p><h3>CISO · GRC · procurement · board</h3><p>EU and US regulated institutions rolling out Microsoft 365 Copilot under audit scrutiny.</p></article>
 <article class="nf-lane-card nf-lane-card--gold"><p class="nf-lane-card__tag">Trust mechanism</p><h3>Signed receipt + export integrity</h3><p>Tamper-evident decision records · confidence score · fail-closed export · independent of the app under audit.</p></article>
 </div>
 <aside class="nf-callout nf-callout--urgency"><p><strong>EU AI Act Art. 12 orientation (Aug 2026):</strong> High-risk logging expectations are accelerating board demand for automatic, tamper-evident decision records — orientation only, not legal advice or certifier claims.</p></aside>
 </section>"""


def regulated_buyer_triggers_block() -> str:
    """Regulated buyer trigger map — EU + US institutional lanes."""
    rows = [
        ("EU AI Act Art. 12", "EU", "Automatic tamper-evident decision records", "TLE v1 + fail-closed export"),
        ("DORA / NIS2", "EU financial", "Incident evidence · audit trails", "Board PDF + procurement ZIP"),
        ("NIST AI RMF / ISO 42001", "US", "Govern · manage · evidence mapping", "Framework orientation in exports"),
        ("FFIEC / OSFI / GC ADM", "US/CA · public &amp; bank", "Board oversight · metadata-only", "Federal + bank-pilot lanes"),
        ("Copilot enterprise rollout", "EU + US", "Signed go/no-go before production scope", f"<a href=\"{PILOT_INTAKE}\">Copilot Governance Pack</a>"),
    ]
    body = "".join(f"<tr><td><strong>{t}</strong></td><td>{r}</td><td>{n}</td><td>{f}</td></tr>" for t, r, n, f in rows)
    return f"""
 <section class="nf-section-block" aria-labelledby="buyer-triggers">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">EU+US</span><div>
 <p class="nf-eyebrow" id="buyer-triggers">Regulated buyer map</p>
 <h2>What triggers institutional buyers — and what Noetfield delivers</h2>
 <p class="nf-section-lead">Orientation for CISO, GRC, legal, and procurement — not legal advice.</p>
 </div></div>
 <div class="nf-table-wrap"><table class="nf-table nf-table--compact"><thead><tr><th>Trigger</th><th>Region / sector</th><th>Buyer need</th><th>Noetfield deliverable</th></tr></thead><tbody>{body}</tbody></table></div>
 </section>"""


def honest_moat_inner() -> str:
    """Honest moat body — embed inside Trust act (homepage compression)."""
    claims = [
        ("Signed go/no-go receipt per Copilot decision", "TLE v1 + evaluate API", "available"),
        ("Board + procurement exports", "Board PDF · procurement ZIP", "available"),
        ("M365-native evidence index", "Purview · Entra · audit metadata", "available"),
        ("Fail-closed export integrity", "/trust-ledger/verify/", "available"),
        ("Fixed-fee institutional pilot", "Copilot Governance Pack $2k–10k", "available"),
        ("Ed25519 / Merkle transparency log", "Roadmap · orientation on verify page", "roadmap"),
    ]
    dont = [
        "ISO / SOC / eIDAS certification from Noetfield",
        "Identity verification or KYC at onboarding",
        "Payment custody · MSB execution · money transmission",
        "Full Article 12 compliance certifier claims",
        "Platform ARR · logo wall · inflated references",
    ]
    items = "".join(
        f'<article class="nf-moat-item"><h3>{c}</h3><p>{e}</p><span class="nf-signal-badge nf-signal-badge--{s}">{SCOPE_LABELS[s]}</span></article>'
        for c, e, s in claims
    )
    dont_li = "".join(f"<li>{d}</li>" for d in dont)
    return f"""
 <div class="nf-block-inner" id="honest-moat">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">✓</span><div>
 <p class="nf-eyebrow">Honest scope</p>
 <h3>What you can claim in diligence today</h3>
 <p class="nf-section-lead">Available now with demo and export walkthrough — Planned and out-of-scope labeled honestly.</p>
 </div></div>
 <div class="nf-moat-grid">{items}</div>
 <aside class="nf-callout"><p><strong>Do not claim:</strong></p><ul class="nf-hero-panel-list">{dont_li}</ul></aside>
 </div>"""


def honest_moat_grid() -> str:
    """Honest capability claims — evidence and do-not-claim boundaries."""
    claims = [
        ("Signed go/no-go receipt per Copilot decision", "TLE v1 + evaluate API", "available"),
        ("Board + procurement exports", "Board PDF · procurement ZIP", "available"),
        ("M365-native evidence index", "Purview · Entra · audit metadata", "available"),
        ("Fail-closed export integrity", "/trust-ledger/verify/", "available"),
        ("Fixed-fee institutional pilot", "Copilot Governance Pack $2k–10k", "available"),
        ("Ed25519 / Merkle transparency log", "Roadmap · orientation on verify page", "roadmap"),
    ]
    dont = [
        "ISO / SOC / eIDAS certification from Noetfield",
        "Identity verification or KYC at onboarding",
        "Payment custody · MSB execution · money transmission",
        "Full Article 12 compliance certifier claims",
        "Platform ARR · logo wall · inflated references",
    ]
    items = "".join(
        f'<article class="nf-moat-item"><h3>{c}</h3><p>{e}</p><span class="nf-signal-badge nf-signal-badge--{s}">{SCOPE_LABELS[s]}</span></article>'
        for c, e, s in claims
    )
    dont_li = "".join(f"<li>{d}</li>" for d in dont)
    return f"""
 <section class="nf-section-block" aria-labelledby="honest-moat">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">✓</span><div>
 <p class="nf-eyebrow" id="honest-moat">Honest scope</p>
 <h2>What you can claim in diligence today</h2>
 <p class="nf-section-lead">Available now with demo and export walkthrough — Planned and out-of-scope labeled honestly.</p>
 </div></div>
 <div class="nf-moat-grid">{items}</div>
 <aside class="nf-callout"><p><strong>Do not claim:</strong></p><ul class="nf-hero-panel-list">{dont_li}</ul></aside>
 </section>"""


def _buyer_delivery_outcomes_body() -> str:
    return """
 <div class="nf-table-wrap">
 <table class="nf-table nf-table--compact">
 <thead><tr><th>Buyer need</th><th>Noetfield deliverable</th></tr></thead>
 <tbody>
 <tr><td><strong>Signed go/no-go per Copilot decision</strong></td><td>TLE v1 · confidence score · Request ID lineage</td></tr>
 <tr><td><strong>Board and risk committee evidence</strong></td><td>Board PDF used in governance meeting — pilot success signal</td></tr>
 <tr><td><strong>Procurement and legal diligence</strong></td><td>Procurement ZIP · fail-closed export integrity verification</td></tr>
 <tr><td><strong>M365 metadata evidence index</strong></td><td>Purview · Entra · audit connectors — read-only · metadata-only</td></tr>
 <tr><td><strong>Fixed-fee institutional entry</strong></td><td>Copilot Governance Pack · $2k–10k · 90 days · QuickScan to Readiness Pilot bands</td></tr>
 </tbody>
 </table>
 </div>"""


def buyer_delivery_outcomes_inner() -> str:
    return f"""
 <div class="nf-block-inner" id="delivery-outcomes">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">→</span><div>
 <p class="nf-eyebrow">Delivery outcomes</p>
 <h3>What regulated buyers receive from Noetfield</h3>
 <p class="nf-section-lead">Same evaluate → TLE → export spine from sandbox through Copilot Governance Pack production tenant.</p>
 </div></div>
 {_buyer_delivery_outcomes_body()}
 </div>"""


def buyer_delivery_outcomes_table() -> str:
    """Positive delivery map — no competitor or approach comparison."""
    return f"""
 <section class="nf-section-block" aria-labelledby="delivery-outcomes">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">→</span><div>
 <p class="nf-eyebrow" id="delivery-outcomes">Delivery outcomes</p>
 <h2>What regulated buyers receive from Noetfield</h2>
 <p class="nf-section-lead">Same evaluate → TLE → export spine from sandbox through Copilot Governance Pack production tenant.</p>
 </div></div>
 {_buyer_delivery_outcomes_body()}
 </section>"""


def hero_regulatory_chips() -> str:
    """Compact above-fold regulatory orientation — not legal advice."""
    chips = [
        ("EU AI Act Art. 12", "Tamper-evident decision record orientation"),
        ("ISO 42001", "AI management system evidence mapping"),
        ("DORA", "Incident evidence · audit trail exports"),
        ("NIST AI RMF", "Govern · Map · Measure · Manage"),
    ]
    items = "".join(
        f'<div class="nf-trust__item"><strong>{label}</strong><span>{desc}</span></div>'
        for label, desc in chips
    )
    return f"""
 <div class="nf-trust nf-trust--hero" role="region" aria-label="Regulatory orientation above fold">
 {items}
 </div>
 <p class="nf-section-lead" style="margin-top:8px;font-size:0.875rem">Orientation only — not legal advice · Noetfield produces governance artifacts, not certification.</p>"""


def pilot_success_criteria_block() -> str:
    return """
 <section class="nf-section-block nf-section--elevated" aria-labelledby="pilot-success">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">✓</span><div>
 <p class="nf-eyebrow" id="pilot-success">Success criteria</p>
 <h2>GTM-locked pilot success signals</h2>
 <p class="nf-section-lead">Fixed-fee Copilot Governance Pack ($2k–10k) — one org uses a board PDF in a real governance meeting.</p>
 </div></div>
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">1</p><h3>Evidence connected</h3><p>Partner uploads or connects M365 metadata evidence (Purview · Entra · audit).</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">2</p><h3>Approved TLE</h3><p>At least one approved Trust Ledger Entry with visible confidence score and tamper-evident export.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">3</p><h3>Board PDF in meeting</h3><p>Board pack PDF used in a governance meeting — board, risk, or legal session.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">4</p><h3>Procurement ZIP</h3><p>Optional: procurement ZIP shared with diligence reviewers before production scope opens.</p></article>
 </div>
 </section>"""


def buyer_journey_strip() -> str:
    return f"""
 <nav class="nf-journey-strip" aria-label="Buyer journey — Pilot Prove Package Trust">
 <a class="nf-journey-step" href="{PILOT_INTAKE}"><span class="nf-journey-step__num">01 · Pilot</span><strong>Copilot Governance Pack</strong><span>$2k–10k · 90 days · board PDF in governance meeting</span></a>
 <a class="nf-journey-step" href="/copilot/demo/"><span class="nf-journey-step__num">02 · Prove</span><strong>5-minute demo</strong><span>Evaluate → confidence score → export</span></a>
 <a class="nf-journey-step" href="/start/"><span class="nf-journey-step__num">03 · Try</span><strong>Start free sandbox</strong><span>~5 min · mock M365 · no sales call</span></a>
 <a class="nf-journey-step" href="/trust/"><span class="nf-journey-step__num">04 · Trust</span><strong>Trust center</strong><span>Procurement pack · verify export</span></a>
 </nav>"""


def social_proof_industry_strip() -> str:
    """Sumsub/Stripe-style industry strip — no fake logos."""
    industries = [
        ("Financial services", "Copilot rollout under DORA · FFIEC scrutiny"),
        ("Insurance &amp; health", "Board-grade exports · metadata-only M365"),
        ("Professional services", "Client-data boundaries · Purview + TLE"),
        ("Public sector", "ADM · AIA · Copilot PIN orientation"),
    ]
    items = "".join(
        f'<div class="nf-social-proof__item"><strong>{name}</strong><span>{desc}</span></div>'
        for name, desc in industries
    )
    return f"""
 <div class="nf-social-proof" role="region" aria-label="Regulated industries">
 <p class="nf-social-proof__label">Built for regulated EU and US institutions</p>
 <div class="nf-social-proof__grid">{items}</div>
 </div>"""


def role_testimonials_strip() -> str:
    """Anonymous buyer-role quotes — orientation only, no fake logos (Wave 2)."""
    quotes = [
        ("CISO · EU regulated financial institution", "We needed a tamper-evident go/no-go record before Copilot touched production — beyond policy decks alone."),
        ("GRC lead · US insurer", "The board asked for evidence, not slides. The pilot delivered a PDF we used in risk committee."),
        ("Procurement · professional services", "Fixed-fee Governance Pack delivered board PDF we used in risk committee within 90 days."),
    ]
    cards = "".join(
        f'<blockquote class="nf-testimonial"><p class="nf-testimonial__quote">{q}</p><footer><cite>{role}</cite></footer></blockquote>'
        for role, q in quotes
    )
    return f"""
 <section class="nf-section-block nf-section--elevated" aria-labelledby="buyer-voices">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">"</span><div>
 <p class="nf-eyebrow" id="buyer-voices">Buyer voices</p>
 <h2>What regulated teams say they need before Copilot production</h2>
 <p class="nf-section-lead">Anonymous role orientation from governance pilot conversations — not paid testimonials or logo claims.</p>
 </div></div>
 <div class="nf-testimonial-grid">{cards}</div>
 </section>"""


def assurance_levels_inner() -> str:
    return """
 <div class="nf-block-inner" id="assurance-levels">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">A</span><div>
 <p class="nf-eyebrow">Export assurance</p>
 <h3>TLE export integrity levels — orientation for diligence reviewers</h3>
 <p class="nf-section-lead">Orientation for diligence reviewers — Available · Planned · Per SOW. Not eIDAS or ISO certification.</p>
 </div></div>
 <div class="nf-assurance-ladder">
 <article class="nf-assurance-step"><p class="nf-assurance-step__level">Baseline</p><h3>Sandbox · sample YAML</h3><p>Mock evaluate · orientation TLE · export walkthrough · no production tenant.</p><span class="nf-signal-badge nf-signal-badge--available">Available</span></article>
 <article class="nf-assurance-step nf-assurance-step--gold"><p class="nf-assurance-step__level">Substantial</p><h3>Governance Pack · signed TLE</h3><p>Live evaluate · approved TLE · confidence score · board PDF in governance meeting.</p><span class="nf-signal-badge nf-signal-badge--available">Pilot $2k–10k</span></article>
 <article class="nf-assurance-step"><p class="nf-assurance-step__level">High</p><h3>Production · procurement ZIP</h3><p>Fail-closed export verify · procurement ZIP · audit bundle · tenant-scoped keys.</p><span class="nf-signal-badge nf-signal-badge--orientation">Per SOW</span></article>
 </div>
 </div>"""


def assurance_levels_block() -> str:
    """ShareID-inspired export assurance levels — orientation only."""
    return """
 <section class="nf-section-block" aria-labelledby="assurance-levels">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">A</span><div>
 <p class="nf-eyebrow" id="assurance-levels">Export assurance</p>
 <h2>TLE export integrity levels — orientation for diligence reviewers</h2>
 <p class="nf-section-lead">Orientation for diligence reviewers — Available · Planned · Per SOW. Not eIDAS or ISO certification.</p>
 </div></div>
 <div class="nf-assurance-ladder">
 <article class="nf-assurance-step"><p class="nf-assurance-step__level">Baseline</p><h3>Sandbox · sample YAML</h3><p>Mock evaluate · orientation TLE · export walkthrough · no production tenant.</p><span class="nf-signal-badge nf-signal-badge--available">Available</span></article>
 <article class="nf-assurance-step nf-assurance-step--gold"><p class="nf-assurance-step__level">Substantial</p><h3>Governance Pack · signed TLE</h3><p>Live evaluate · approved TLE · confidence score · board PDF in governance meeting.</p><span class="nf-signal-badge nf-signal-badge--available">Pilot $2k–10k</span></article>
 <article class="nf-assurance-step"><p class="nf-assurance-step__level">High</p><h3>Production · procurement ZIP</h3><p>Fail-closed export verify · procurement ZIP · audit bundle · tenant-scoped keys.</p><span class="nf-signal-badge nf-signal-badge--orientation">Per SOW</span></article>
 </div>
 </section>"""


def milestone_pricing_ladder() -> str:
    """Sumsub-class milestone pricing — lead → land → expand."""
    return f"""
 <section class="nf-section-block" aria-labelledby="milestone-pricing">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">$</span><div>
 <p class="nf-eyebrow" id="milestone-pricing">Milestone pricing</p>
 <h2>Lead → land → expand — no SKU creep</h2>
 <p class="nf-section-lead">Same spine at every tier: evaluate → signed TLE → export. Price follows proof, not platform shelfware.</p>
 </div></div>
 <div class="nf-milestone-ladder">
 <a class="nf-milestone-step nf-milestone-step--active" href="{PILOT_INTAKE}"><span class="nf-milestone-step__tag">Lead</span><strong>$2k–10k</strong><span>Copilot Governance Pack · 90 days · board PDF</span></a>
 <span class="nf-milestone-arrow" aria-hidden="true">→</span>
 <a class="nf-milestone-step" href="/trust-brief/"><span class="nf-milestone-step__tag">Land</span><strong>$10k</strong><span>Trust Brief · 6 weeks · policy map + risk exposure</span></a>
 <span class="nf-milestone-arrow" aria-hidden="true">→</span>
 <a class="nf-milestone-step" href="/bank-pilot/"><span class="nf-milestone-step__tag">Expand</span><strong>Custom</strong><span>Bank Pilot · enterprise SOW · shadow → enforce</span></a>
 </div>
 </section>"""


def pilot_apply_form() -> str:
    """Sumsub-class inline pilot apply — routes to Governance Pack intake."""
    return f"""
 <section class="nf-section-block nf-section--elevated" id="pilot-apply" aria-labelledby="pilot-apply-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">→</span><div>
 <p class="nf-eyebrow" id="pilot-apply-title">Apply online</p>
 <h2>Start your Copilot Governance Pack intake</h2>
 <p class="nf-section-lead">Non-confidential · include your Request ID from the footer · operations@noetfield.com</p>
 </div></div>
 <form id="nfPilotApplyForm" class="nf-pilot-apply-form" data-intake="{PILOT_INTAKE}" aria-label="Copilot Governance Pack intake">
 <div class="nf-pilot-apply-grid">
 <label>Work email<input type="email" name="email" required autocomplete="email" placeholder="you@institution.com" /></label>
 <label>Organization<input type="text" name="org" required autocomplete="organization" placeholder="Regulated institution name" /></label>
 <label>Your role
 <select name="role" required>
 <option value="">Select role</option>
 <option value="ciso">CISO / Security</option>
 <option value="grc">GRC / Compliance</option>
 <option value="legal">Legal / Procurement</option>
 <option value="board">Board / Risk committee</option>
 <option value="it">IT / Copilot owner</option>
 </select>
 </label>
 <label>Pilot band
 <select name="band">
 <option value="quickscan">QuickScan · $2,000 · 4 weeks</option>
 <option value="readiness" selected>Readiness Pilot · $5k–10k · 90 days (recommended)</option>
 </select>
 </label>
 </div>
 <label>Scope notes (optional)<textarea name="notes" rows="3" placeholder="Copilot rollout timeline · EU/US · unclassified only"></textarea></label>
 <div class="nf-cta-actions">
 <button type="submit" class="btn btn-primary">Submit pilot intake</button>
 <a class="btn btn-secondary" href="/copilot/demo/">5-minute demo first</a>
 </div>
 <p class="nf-section-lead" style="margin-top:12px">Fixed fee · metadata-only M365 · board PDF success signal · <a href="/copilot/procurement/">procurement pack</a></p>
 </form>
 </section>
 <script src="/assets/noetfield-pilot-intake.js?v={WWW_VER}" defer></script>"""


def work_with_us_intake(role: str = "") -> str:
    base = WORK_WITH_US_INTAKE
    if role:
        return f"{base}&role={role}"
    return base


def work_with_us_roles_grid() -> str:
    roles = [
        (
            "connector",
            "Connector",
            "Introduce regulated EU and US institutions rolling out Microsoft 365 Copilot.",
            "Warm intros to CISO, GRC, or procurement · referral path after signed Copilot Governance Pack.",
            "Intro fee · co-marketing orientation",
        ),
        (
            "facilitator",
            "Facilitator",
            "Lead buyer workshops, pilot kickoffs, and governance enablement sessions.",
            "Fixed-fee adjunct delivery · board PDF success signal in client governance meeting.",
            "Workshop + kickoff delivery",
        ),
        (
            "co-partner",
            "Co-partner",
            "Co-deliver Copilot Governance Pack pilots under a joint SOW.",
            "Shared delivery scope · live TLE · metadata-only M365 evidence · procurement ZIP.",
            "Joint SOW · $2k–10k pilot bands",
        ),
        (
            "partner",
            "Partner",
            "MSP, SI, or advisory firm — Phase 2 attach after Purview readiness.",
            "Readiness → Record handoff · multi-tenant enablement · Governance Pack attach.",
            "MSP · SI · advisory lane",
        ),
    ]
    cards = []
    for key, title, h3, p, tag in roles:
        cards.append(
            f'<article class="nf-offer-card nf-offer-card--featured">'
            f'<p class="meta">{tag}</p>'
            f"<h3>{title}</h3><p>{h3} {p}</p>"
            f'<a class="btn btn-primary" href="{work_with_us_intake(key)}">Apply as {title.lower()}</a>'
            f"</article>"
        )
    return f"""
 <section class="nf-section-block nf-section--elevated" aria-labelledby="wwu-roles">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="wwu-roles">Program lanes</p>
 <h2>Connector · Facilitator · Co-partner · Partner</h2>
 <p class="nf-section-lead">Four ways to work with Noetfield on regulated Copilot governance — pick the lane that matches how you go to market.</p>
 </div></div>
 <div class="nf-offerings-v5">{"".join(cards)}</div>
 </section>"""


def partner_apply_form() -> str:
    return f"""
 <section class="nf-section-block" id="partner-apply" aria-labelledby="partner-apply-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">→</span><div>
 <p class="nf-eyebrow" id="partner-apply-title">Apply</p>
 <h2>Work with Noetfield — ecosystem application</h2>
 <p class="nf-section-lead">Non-confidential · operations@noetfield.com · include your Request ID from the site footer.</p>
 </div></div>
 <form id="nfPartnerApplyForm" class="nf-pilot-apply-form" data-intake="{WORK_WITH_US_INTAKE}" aria-label="Work with Noetfield application">
 <div class="nf-pilot-apply-grid">
 <label>Work email<input type="email" name="email" required autocomplete="email" placeholder="you@firm.com" /></label>
 <label>Organization<input type="text" name="org" required autocomplete="organization" placeholder="Firm or practice name" /></label>
 <label>Program lane
 <select name="role" required>
 <option value="">Select lane</option>
 <option value="connector">Connector — warm intros to regulated buyers</option>
 <option value="facilitator">Facilitator — workshops &amp; pilot kickoffs</option>
 <option value="co-partner">Co-partner — joint Copilot Governance Pack delivery</option>
 <option value="partner">Partner — MSP / SI / advisory (Phase 2 attach)</option>
 </select>
 </label>
 <label>Primary geography
 <select name="region">
 <option value="eu-us" selected>EU + US</option>
 <option value="ca">Canada</option>
 <option value="eu">EU</option>
 <option value="us">US</option>
 </select>
 </label>
 </div>
 <label>How you want to work together (optional)<textarea name="notes" rows="3" placeholder="Existing Copilot/Purview practice · target sectors · unclassified only"></textarea></label>
 <div class="nf-cta-actions">
 <button type="submit" class="btn btn-primary">Submit application</button>
 <a class="btn btn-secondary" href="/copilot/demo/">See 5-minute demo first</a>
 <a class="btn btn-secondary" href="/msp/">MSP lane overview</a>
 </div>
 </form>
 </section>
 <script src="/assets/noetfield-partner-apply.js?v={WWW_VER}" defer></script>"""


def work_with_us_page_body() -> str:
    return hero(
        "Work with Noetfield · Ecosystem",
        "Connectors · facilitators · co-partners · partners",
        "Help regulated institutions get board-grade Copilot governance receipts",
        "Noetfield is the <strong>governance execution layer</strong> for Microsoft 365 Copilot rollouts — signed Trust Ledger Entries, board PDF, procurement ZIP. "
        "We partner with people and firms who <strong>connect buyers</strong>, <strong>facilitate rollout</strong>, <strong>co-deliver pilots</strong>, or <strong>attach after Purview readiness</strong> — same evaluate → TLE → export spine.",
        [("Copilot Governance Pack attach", True), ("EU + US regulated lane", True), ("No custody · no MSB", False)],
        [(WORK_WITH_US_INTAKE, "Apply to work with us", True), ("/copilot/demo/", "5-minute demo", False), ("/msp/", "MSP program", False)],
        ["Connector", "Facilitator", "Co-partner", "Partner"],
        panel("What you help deliver", [
            "Copilot Governance Pack pilots · $2k–10k",
            "Board PDF in client governance meeting",
            "Metadata-only M365 evidence index",
            "Honest scope — no certifier claims",
        ]),
    ) + work_with_us_roles_grid() + f"""
 <section class="nf-section-block" aria-labelledby="wwu-model">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="wwu-model">How the program works</p>
 <h2>Apply → enable → earn on proof</h2>
 <p class="nf-section-lead">Channel economics follow the same milestone path as direct GTM — lead with Governance Pack, expand on board PDF success.</p>
 </div></div>
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">1</p><h3>Apply</h3><p>Tell us your lane — connector, facilitator, co-partner, or MSP/SI partner. Non-confidential intake only.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">2</p><h3>Enable</h3><p>Sandbox demo · delivery playbook orientation · co-marketing kit for your lane (per agreement).</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">3</p><h3>Earn</h3><p>Attach Copilot Governance Pack pilots · referral or delivery fee per SOW · expand to Trust Brief or enterprise cadence.</p></article>
 </div>
 </section>
 {partner_apply_form()}
 <section class="nf-section-block nf-section--elevated" aria-labelledby="wwu-fit">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">✓</span><div>
 <p class="nf-eyebrow" id="wwu-fit">Fit</p>
 <h2>Built for ecosystem players in regulated digital trust</h2>
 </div></div>
 {fit_qualification_body()}
 </section>
""" + mega_cta(
        "Ready to connect buyers to Copilot governance receipts?",
        "Apply online · include Request ID · operations@noetfield.com",
        (WORK_WITH_US_INTAKE, "Apply to work with us"),
        ("/contact/", "Contact operations"),
    )


def pilot_hero_wedge() -> str:
    """Above-fold pilot wedge — links to full pilot page."""
    return f"""
 <aside class="nf-callout" aria-label="Copilot Governance Pack wedge">
 <p><strong>Lead program · $2k–10k · 90 days</strong> — Copilot Governance Pack for EU and US regulated institutions. Fixed fee · production tenant · board PDF in your next governance meeting.</p>
 <div class="nf-cta-actions" style="margin-top:12px">
 <a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for pilot</a>
 <a class="btn btn-secondary" href="/copilot/pilot/">Pilot overview</a>
 <a class="btn btn-secondary" href="/start/">Try sandbox first</a>
 </div>
 </aside>"""


def _governance_output_suite_body() -> str:
    return """
 <div class="nf-export-suite" role="list">
 <article class="nf-export-suite__item" role="listitem"><span class="nf-export-suite__icon">TLE</span><h3>TLE v1 YAML</h3><p>Signed decision · confidence score · approval chain · evidence index.</p></article>
 <article class="nf-export-suite__item" role="listitem"><span class="nf-export-suite__icon">PDF</span><h3>Board PDF</h3><p>Executive-ready digest for governance and budget conversations.</p></article>
 <article class="nf-export-suite__item" role="listitem"><span class="nf-export-suite__icon">ZIP</span><h3>Procurement ZIP</h3><p>Buyer diligence bundle · fail-closed integrity on tamper.</p></article>
 <article class="nf-export-suite__item is-roadmap" role="listitem"><span class="nf-export-suite__icon">API</span><h3>Audit export <span class="nf-signal-badge nf-signal-badge--roadmap">Planned</span></h3><p>Tenant audit bundle · SIEM / GRC webhooks — planned capability, orientation only.</p></article>
 </div>"""


def governance_output_suite_inner() -> str:
    return f"""
 <div class="nf-block-inner" id="export-suite-title" aria-labelledby="export-suite-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">↗</span><div>
 <p class="nf-eyebrow">Governance Output Suite</p>
 <h3>One evaluate · four exports</h3>
 <p class="nf-section-lead">Buyers file artifacts — not API access alone. Same spine from sandbox to production tenant.</p>
 </div></div>
 {_governance_output_suite_body()}
 </div>"""


def governance_output_suite() -> str:
    return f"""
 <section class="nf-section-block" aria-labelledby="export-suite-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">↗</span><div>
 <p class="nf-eyebrow" id="export-suite-title">Governance Output Suite</p>
 <h2>One evaluate · four exports</h2>
 <p class="nf-section-lead">Buyers file artifacts — not API access alone. Same spine from sandbox to production tenant.</p>
 </div></div>
 {_governance_output_suite_body()}
 </section>"""


def contrast_table_section() -> str:
    """Legacy alias — positive delivery outcomes only (no comparison framing)."""
    return buyer_delivery_outcomes_table()


def fit_qualification_body() -> str:
    return """
 <div class="nf-fit-grid">
 <article class="nf-fit-card nf-fit-card--yes"><h3>This is for you if</h3><ul>
 <li>You are a <strong>regulated EU or US institution</strong> rolling out Microsoft 365 Copilot under board, legal, or procurement scrutiny</li>
 <li>You need <strong>board-grade tamper-evident receipts</strong> — signed TLE v1, not spreadsheet approvals alone</li>
 <li>You need <strong>metadata-only</strong> M365 evidence — no mailbox custody</li>
 <li>You want <strong>honest scope</strong> — Available · Planned · Out of scope badges, not certifier claims</li>
 </ul></article>
 <article class="nf-fit-card nf-fit-card--no"><h3>This is not for you if</h3><ul>
 <li>You need payment rails, custody, MSB execution, or transaction processing</li>
 <li>You want full mailbox/content surveillance — we index metadata only</li>
 <li>You need ISO/SOC <strong>certification</strong> from us — we produce governance artifacts, not company certification</li>
 <li>You want a generic AI chatbot catalog — three contract SKUs only</li>
 </ul></article>
 </div>"""


def institution_icp_strip() -> str:
    """Regulated buyer personas — EU + US institutions."""
    personas = [
        ("CISO / Security", "Copilot rollout under audit scrutiny — signed go/no-go before production scope opens."),
        ("GRC / Compliance", "EU AI Act Art. 12 orientation · NIST AI RMF · ISO 42001 evidence mapping — not legal advice."),
        ("Legal / Procurement", "Board PDF + procurement ZIP with fail-closed export integrity for diligence reviewers."),
        ("Board / Risk committee", "One approved TLE and board pack used in a real governance meeting — pilot success signal."),
    ]
    cards = "".join(
        f'<article class="nf-persona"><p class="nf-persona-role">{role}</p><h3>{role.split(" / ")[0]}</h3><p>{p}</p></article>'
        for role, p in personas
    )
    return f"""
 <section class="nf-section-block nf-section--elevated" aria-labelledby="institution-icp">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">ICP</span><div>
 <p class="nf-eyebrow" id="institution-icp">Regulated institutions</p>
 <h2>Built for EU and US buyers who cannot afford undocumented Copilot decisions</h2>
 <p class="nf-section-lead">Financial services · insurance · healthcare · professional services · public sector — same evaluate → TLE → export spine.</p>
 </div></div>
 <div class="nf-personas">{cards}</div>
 </section>"""


def eu_us_regulatory_block() -> str:
    """EU + US regulatory orientation — honest scope, not certifier claims."""
    return """
 <section class="nf-section-block" aria-labelledby="regulatory-orientation">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">§</span><div>
 <p class="nf-eyebrow" id="regulatory-orientation">Regulatory orientation</p>
 <h2>Board-grade trust signals buyers inspect before pilot sign-off</h2>
 <p class="nf-section-lead">Orientation only — not legal advice. Noetfield produces governance artifacts; we are not a certifier or regulator.</p>
 </div></div>
 <div class="nf-trust" role="region" aria-label="EU and US regulatory anchors">
 <div class="nf-trust__item"><strong>EU AI Act Art. 12</strong><span>Automatic logging orientation · tamper-evident decision records</span></div>
 <div class="nf-trust__item"><strong>ISO 42001</strong><span>AI management system evidence mapping</span></div>
 <div class="nf-trust__item"><strong>NIST AI RMF</strong><span>Govern · Map · Measure · Manage crosswalk</span></div>
 <div class="nf-trust__item"><strong>DORA / NIS2</strong><span>Incident evidence · audit trail exports</span></div>
 <div class="nf-trust__item"><strong>Microsoft Purview</strong><span>Metadata-only evidence index · complement CCS</span></div>
 <div class="nf-trust__item"><strong>Fail-closed export</strong><span>Board PDF + procurement ZIP · verify integrity</span></div>
 </div>
 <aside class="nf-callout"><p><strong>Honest scope:</strong> TLE v1 receipts and export bundles are available today. Ed25519 / Merkle transparency log is <strong>Planned</strong>. We do not claim ISO, SOC, or eIDAS certification.</p></aside>
 </section>"""


def pilot_page_body() -> str:
    """Full Copilot Governance Pack pilot landing — lead GTM wedge."""
    deliverables = [
        ("Governance evaluate", "Pre-execution allow / deny / review with Request ID lineage on every decision."),
        ("Evidence index", "Metadata-only Purview, Entra ID, Audit, SharePoint connectors — read-only; complements Microsoft DLP."),
        ("TLE v1", "Signed go/no-go with confidence score and sequential approval chain."),
        ("Board pack", "JSON, HTML, and PDF export for board, risk, or legal governance meetings."),
        ("Procurement pack", "One-click ZIP — JSON + PDF + README + audit slice for diligence reviewers."),
        ("Audit export", "Tenant-scoped audit bundle orientation via governance API."),
    ]
    del_rows = "".join(
        f"<tr><td><strong>{d}</strong></td><td>{desc}</td></tr>" for d, desc in deliverables
    )
    return hero(
        "Board-grade trust · EU + US regulated institutions",
        "Copilot Governance Pack · $2k–10k",
        "90 days to a board PDF your risk committee can use",
        (
            "Fixed-fee pilot for Microsoft 365 Copilot rollouts: evaluate operational intent, index metadata-only M365 evidence, "
            "produce signed <strong>Trust Ledger Entries</strong> with <strong>tamper-evident export integrity</strong>, and export board-ready diligence artifacts. "
            "<strong>Success signal:</strong> one approved TLE and board PDF used in a real governance meeting."
        ),
        [("$2k–10k · 90 days", True), ("Board PDF success signal", True), ("Tamper-evident TLE", False)],
        [(PILOT_INTAKE, "Apply for pilot", True), ("/copilot/demo/", "5-minute demo", False), ("/start/", "Start sandbox", False)],
        HERO_MARQUEE,
        panel("Success signals", [
            "M365 metadata evidence connected or uploaded",
            "At least one approved TLE with confidence score",
            "Board pack PDF used in governance meeting",
            "Optional: procurement ZIP shared with diligence",
        ]),
    ) + digital_trust_lane_block() + copilot_governance_gaps_section() + f"""
 <section class="nf-section-block" aria-labelledby="pilot-deliverables">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="pilot-deliverables">In scope</p>
 <h2>Pilot deliverables — Copilot governance evidence layer</h2>
 <p class="nf-section-lead">Same evaluate → TLE → export spine as sandbox — production tenant, API keys, and board-grade exports per SOW.</p>
 </div></div>
 <div class="nf-table-wrap"><table class="nf-table nf-table--compact"><thead><tr><th>Deliverable</th><th>Description</th></tr></thead><tbody>{del_rows}</tbody></table></div>
 </section>
 <section class="nf-section-block" aria-labelledby="pilot-pricing">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="pilot-pricing">Pricing bands</p>
 <h2>Fixed-fee pilot — no SKU creep</h2>
 </div></div>
 <div class="nf-pack-grid nf-pack-grid--4">
 <article class="nf-pack-card"><p class="nf-pack-card__tag">QuickScan</p><p class="nf-pack-card__price">$2,000</p><p>Evaluate orientation · sample TLE · export walkthrough · 4-week scope.</p></article>
 <article class="nf-pack-card nf-pack-card--program"><p class="nf-pack-card__tag">Readiness Pilot · recommended</p><p class="nf-pack-card__price">$5k–10k</p><p>Production tenant · live TLE records · board PDF in governance meeting · procurement ZIP · 90 days.</p><a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for pilot</a></article>
 <article class="nf-pack-card"><p class="nf-pack-card__tag">After pilot</p><p class="nf-pack-card__price">Trust Brief</p><p>Six-week governance diagnostic ($10k) before enterprise scale — optional land SKU.</p><a class="btn btn-secondary" href="/trust-brief/">Trust Brief</a></article>
 </div>
 </section>
 <section class="nf-section-block" aria-labelledby="pilot-timeline">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">03</span><div>
 <p class="nf-eyebrow" id="pilot-timeline">Timeline</p>
 <h2>Typical 4–6 week pilot cadence</h2>
 </div></div>
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 1</p><h3>Kickoff + evidence</h3><p>Intake · RID assigned · M365 metadata connectors or evidence upload · policy baseline.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 2–3</p><h3>Evaluate + TLE</h3><p>Live evaluate on Copilot go/no-go scenarios · first approved TLE with confidence score.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 4–5</p><h3>Board export</h3><p>Board PDF draft · procurement ZIP · export integrity verification walkthrough.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 6</p><h3>Governance meeting</h3><p>Board PDF in real risk, legal, or board session — pilot success signal.</p></article>
 </div>
 </section>
 """ + pilot_success_criteria_block() + milestone_pricing_ladder() + revenue_path_strip() + assurance_levels_block() + regulated_buyer_triggers_block() + eu_us_regulatory_block() + honest_moat_grid() + role_testimonials_strip() + """
 <section class="nf-section-block" aria-labelledby="pilot-out">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">04</span><div>
 <p class="nf-eyebrow" id="pilot-out">Out of scope</p>
 <h2>What the pilot does not include</h2>
 </div></div>
 <ul class="nf-hero-panel-list" style="max-width:640px">
 <li>Payment initiation, custody, settlement, or money transmission</li>
 <li>Production Azure AD secrets management (customer-owned vault)</li>
 <li>ISO / SOC / eIDAS certification claims from Noetfield</li>
 <li>Full mailbox or content surveillance — metadata-only M365 indices</li>
 </ul>
 </section>
 """ + institution_icp_strip() + agentic_autonomous_section() + pilot_apply_form() + scope_block() + proof_grid([
        ("/copilot/demo/", "▶", "5-minute demo", "Evaluate → confidence score → export path"),
        ("/trust-ledger/sample-report/", "TLE", "TLE v1 samples", "Go · conditional · rejected YAML"),
        ("/copilot/procurement/", "ZIP", "Procurement pack", "Buyer diligence bundle"),
        ("/trust-ledger/verify/", "✓", "Verify export", "Fail-closed integrity walkthrough"),
    ]) + mega_cta("Ready for a board-grade Copilot pilot?", "Include your Request ID · non-confidential intake · operations@noetfield.com")


def fit_qualification_section() -> str:
    return """
 <section class="nf-section-block" aria-labelledby="fit-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">?</span><div>
 <p class="nf-eyebrow" id="fit-title">Fit</p>
 <h2>Built for regulated Copilot buyers</h2>
 </div></div>
""" + fit_qualification_body() + """
 </section>"""


def closing_competitive_line() -> str:
    return f'<p class="nf-closing-line">{COPY["closing_competitive"]}</p>'


def packaging_tiers_grid(compact: bool = False) -> str:
    """Access paths + contract programs — not a fourth contract SKU."""
    cls = "nf-pack-grid nf-pack-grid--4" if compact else "nf-pack-grid nf-pack-grid--4"
    return f"""
 <div class="{cls}" role="list" aria-label="Access paths and contract programs">
 <article class="nf-pack-card nf-pack-card--free" role="listitem">
 <p class="nf-pack-card__tag">Developer access · free</p>
 <p class="nf-pack-card__price">$0</p>
 <p>Self-serve sandbox — evaluate API, workspace, mock M365 connectors. {COPY["sandbox_limits"]}.</p>
 <ul><li>Sandbox mode</li><li>Instant workspace</li><li>Sample TLE export</li></ul>
 <a class="btn btn-secondary" href="/start/">Start sandbox</a>
 </article>
 <article class="nf-pack-card nf-pack-card--program" role="listitem">
 <p class="nf-pack-card__tag">Lead program · apply online</p>
 <p class="nf-pack-card__price">$2k–10k</p>
 <p>Copilot Governance Pack — production tenant, board PDF in governance meeting, procurement ZIP.</p>
 <ul><li>90-day program</li><li>Production mode</li><li>Board PDF success signal</li></ul>
 <a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for pilot</a>
 </article>
 <article class="nf-pack-card" role="listitem">
 <p class="nf-pack-card__tag">Contract SKU</p>
 <p class="nf-pack-card__price">$10,000</p>
 <p>Trust Brief — six-week governance diagnostic before Copilot or automation scale.</p>
 <ul><li>Policy map</li><li>Risk exposure</li><li>Board-ready summary</li></ul>
 <a class="btn btn-secondary" href="/trust-brief/">Trust Brief</a>
 </article>
 <article class="nf-pack-card" role="listitem">
 <p class="nf-pack-card__tag">Contract SKU · custom</p>
 <p class="nf-pack-card__price">Enterprise</p>
 <p>Bank Pilot shadow simulation — read-only governance evaluate for FRFI and regulated institutions.</p>
 <ul><li>Shadow mode</li><li>No custody rails</li><li>Audit lineage export</li></ul>
 <a class="btn btn-secondary" href="/bank-pilot/">Bank Pilot</a>
 </article>
 </div>
 <p class="nf-section-lead">Three contract SKUs only — free sandbox is product access, not a retail SKU. Upgrade path: sandbox → Copilot Governance Pack → Trust Brief or enterprise SOW.</p>"""


def agentic_autonomous_section() -> str:
    return """
 <section class="nf-section-block nf-section--elevated" aria-labelledby="automation-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">A</span><div>
 <p class="nf-eyebrow" id="automation-title">Automated governance</p>
 <h2>Policy-bound workflows — not manual checklists alone</h2>
 <p class="nf-section-lead">Your team sets policy. Noetfield runs investigate → triage → draft → approve on metadata-only M365 evidence — same evaluate semantics as <code>POST /evaluate</code>. High-risk Copilot go/no-go stays with named human approvers.</p>
 </div></div>
 <div class="nf-agentic-grid">
 <article class="nf-agentic-step"><strong>Investigate</strong><p>Surfaces Purview label gaps, Entra CA posture, and audit index coverage before rollout sign-off.</p></article>
 <article class="nf-agentic-step"><strong>Triage</strong><p>Confidence score and policy rules route allow, review, or deny — recorded on every decision.</p></article>
 <article class="nf-agentic-step"><strong>Draft TLE</strong><p>Prepares Trust Ledger Entry YAML, approval chain, and evidence index for human sign-off.</p></article>
 <article class="nf-agentic-step"><strong>Act on low-risk</strong><p>Pre-approved policy paths auto-record sandbox evaluates; production requires Governance Pack keys and approver chain.</p></article>
 </div>
 </section>"""


def sandbox_signup_form(next_path: str = "/cognitive-dashboard/?sandbox=1") -> str:
    return f"""
 <form id="nfSandboxForm" class="nf-sandbox-form" data-next="{next_path}" aria-labelledby="sandbox-form-title">
 <h3 id="sandbox-form-title">Start your developer sandbox</h3>
 <p class="nf-section-lead">No credit card · no sales call · {COPY["sandbox_limits"]}</p>
 <label>Work email<input type="email" name="email" required autocomplete="email" placeholder="you@company.com" /></label>
 <label>Organization (optional)<input type="text" name="org" autocomplete="organization" placeholder="Your team or company" /></label>
 <button type="submit" class="btn btn-primary">Create sandbox &amp; open console</button>
 </form>
 <div id="nfSandboxStatus" class="nf-callout" hidden aria-live="polite"></div>
 <script src="/assets/noetfield-sandbox.js?v={WWW_VER}" defer></script>"""


def ciso_strip_inner() -> str:
    cards = [
        ("Metadata-only M365", "Purview · Entra · audit indices — evidence index on every TLE, no mailbox custody.", "available", SCOPE_LABELS["available"]),
        ("Fail-closed export", "Board PDF and procurement ZIP fail verification when tampered — by design.", "available", SCOPE_LABELS["available"]),
        ("EU + US regulatory orientation", "EU AI Act Art. 12 · NIST AI RMF · ISO 42001 mapping — orientation only, not certifier claims.", "orientation", SCOPE_LABELS["orientation"]),
        ("Ed25519 transparency log", "Cryptographic receipt chain — planned product capability.", "roadmap", SCOPE_LABELS["roadmap"]),
        ("SOC 2 Type II", "Independent audit planned — not yet completed.", "roadmap", SCOPE_LABELS["roadmap"]),
        ("No custody rails", "No payment execution, MSB, asset custody, or money-transmission claims.", "na", SCOPE_LABELS["na"]),
    ]
    items = "".join(
        f'<article class="nf-ciso-card"><h3>{h}</h3><p>{p}</p>'
        f'<span class="nf-signal-badge {SCOPE_BADGES[k]}">{label}</span></article>'
        for h, p, k, label in cards
    )
    return f"""
 <div class="nf-ciso-strip nf-block-inner" id="ciso-h">
 <div class="nf-ciso-strip-head">
 <p class="nf-eyebrow">Procurement diligence</p>
 <h3>What legal and security reviewers need to see</h3>
 <p>Honest Available · Orientation · Planned · Out of scope — what legal, security, and procurement reviewers inspect before pilot sign-off.</p>
 </div>
 <div class="nf-ciso-grid">{items}</div>
 </div>"""


def ciso_strip() -> str:
    cards = [
        ("Metadata-only M365", "Purview · Entra · audit indices — evidence index on every TLE, no mailbox custody.", "available", SCOPE_LABELS["available"]),
        ("Fail-closed export", "Board PDF and procurement ZIP fail verification when tampered — by design.", "available", SCOPE_LABELS["available"]),
        ("EU + US regulatory orientation", "EU AI Act Art. 12 · NIST AI RMF · ISO 42001 mapping — orientation only, not certifier claims.", "orientation", SCOPE_LABELS["orientation"]),
        ("Ed25519 transparency log", "Cryptographic receipt chain — planned product capability.", "roadmap", SCOPE_LABELS["roadmap"]),
        ("SOC 2 Type II", "Independent audit planned — not yet completed.", "roadmap", SCOPE_LABELS["roadmap"]),
        ("No custody rails", "No payment execution, MSB, asset custody, or money-transmission claims.", "na", SCOPE_LABELS["na"]),
    ]
    items = "".join(
        f'<article class="nf-ciso-card"><h3>{h}</h3><p>{p}</p>'
        f'<span class="nf-signal-badge {SCOPE_BADGES[k]}">{label}</span></article>'
        for h, p, k, label in cards
    )
    return f"""
 <section class="nf-ciso-strip" aria-labelledby="ciso-h">
 <div class="nf-ciso-strip-head">
 <p class="nf-eyebrow" id="ciso-h">Procurement diligence</p>
 <h2>What legal and security reviewers need to see</h2>
 <p>Honest Available · Orientation · Planned · Out of scope — what legal, security, and procurement reviewers inspect before pilot sign-off.</p>
 </div>
 <div class="nf-ciso-grid">{items}</div>
 </section>"""


def write(rel: str, title: str, desc: str, canonical: str, body: str, body_class: str = "nf-www nf-site-v14") -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        HEAD.format(title=title, desc=desc, canonical=canonical, www_ver=WWW_VER, body_class=body_class, font_link=FONT_LINK) + body + FOOT,
        encoding="utf-8",
    )
    print("wrote", rel)


def homepage() -> str:
    """Four-act homepage — Pilot · Prove · Package · Trust (≤8 top-level sections, U5 v17)."""
    act_pilot = f"""
 <section class="nf-section-block nf-act-try" aria-labelledby="act-try">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="act-try">Pilot</p>
 <h2 class="nf-sr-only">Copilot Governance Pack — board-grade Copilot governance</h2>
 </div></div>
""" + hero(
        "Board-grade trust · EU + US regulated institutions",
        "AI Governance &amp; Evidence · Microsoft 365 Copilot",
        COPY["hero_h1"],
        COPY["hero_lead"],
        [("Copilot Governance Pack · $2k–10k", True), ("Tamper-evident TLE", True), ("Board-grade trust", False)],
        [(PILOT_INTAKE, "Apply for pilot ($2k–10k)", True), ("/copilot/demo/", "5-minute demo", False), ("/start/", "Start free sandbox", False)],
        HERO_MARQUEE + ["Microsoft Purview"],
        live_proof_panel(),
        h1_class="nf-hero-h1--wide",
    ).replace(
        '<p class="nf-lead">',
        f'<p class="nf-first-receipt-promise">{COPY["first_receipt_promise"]}</p>\n <p class="nf-lead">',
        1,
    ).replace(
        '</header>',
        hero_regulatory_chips() + "\n </header>",
        1,
    ) + stat_bar() + pilot_hero_wedge() + social_proof_industry_strip() + buyer_journey_strip() + revenue_path_ladder_inner() + homepage_depth_links() + "\n </section>"

    act_prove = f"""
 <section class="nf-section-block nf-act-prove" aria-labelledby="act-prove">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="act-prove">Prove</p>
 <h2>The moment Copilot becomes auditable</h2>
 <p class="nf-section-lead">{COPY["demo_sentence"]} · {COPY["m365_position"]}</p>
 </div></div>
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">01</p><h3>Evaluate</h3><p>Pre-execution evaluate — operational intent before production scope opens.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">02</p><h3>Decide</h3><p>Confidence score and named approvers — defensible go/no-go.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">03</p><h3>Record</h3><p>Signed Trust Ledger Entry · TLE v1 with M365 metadata evidence index.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">04</p><h3>Export</h3><p>Board PDF and procurement ZIP — <strong>export_integrity</strong> fails closed on tamper.</p></article>
 </div>
 {proof_grid([
        ("/copilot/demo/", "▶", "5-minute demo", "Evaluate → confidence score → Purview · Entra · SharePoint index"),
        ("/trust-ledger/sample-report/", "TLE", "TLE v1 samples", "Go · conditional · rejected YAML for procurement review"),
        ("/copilot/procurement/", "ZIP", "Procurement pack", "Buyer diligence ZIP · NIST AI RMF · trust center crosswalk"),
        ("/trust-ledger/verify/", "✓", "Verify export", "Fail-closed export integrity walkthrough"),
    ])}
 {governance_output_suite_inner()}
 <p class="nf-section-lead" style="margin-top:20px"><a href="/copilot/">What buyers ask</a> · extended FAQ · stack complement · category map on the Copilot hub.</p>
 </section>"""

    act_package = f"""
 <section class="nf-section-block nf-act-package" aria-labelledby="act-package">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">03</span><div>
 <p class="nf-eyebrow" id="act-package">Package</p>
 <h2>Published tiers — pilot to contract</h2>
 <p class="nf-section-lead">Lead with the <strong>Copilot Governance Pack ($2k–10k · 90 days · board PDF)</strong>, try free in developer sandbox, or buy a locked contract SKU — same evaluate → TLE → export spine.</p>
 </div></div>
 {buyer_delivery_outcomes_inner()}
 {packaging_tiers_grid(compact=True)}
 {offerings_three_skus()}
 <p class="nf-section-lead"><a href="/pricing/">See all tiers</a> · Sandbox + production modes · three contract SKUs only.</p>
 </section>"""

    act_trust = f"""
 <section class="nf-section-block nf-act-trust" aria-labelledby="act-trust">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">04</span><div>
 <p class="nf-eyebrow" id="act-trust">Trust</p>
 <h2>Procurement diligence — honest scope</h2>
 <p class="nf-section-lead">For you / not for you · trust center · export verification.</p>
 </div></div>
 {fit_qualification_body()}
 {assurance_levels_inner()}
 {honest_moat_inner()}
 {procurement_rail()}
 {ciso_strip_inner()}
 {scope_block_inner()}
 {closing_competitive_line()}
 </section>
""" + mega_cta() + sticky_mobile_cta()

    return act_pilot + act_prove + act_package + act_trust


def category_map_block() -> str:
    """Buyer category zones — no third-party vendor names."""
    return category_zones_public()


def section_block(num: str, eyebrow: str, h2: str, body: str, lead: str = "", section_id: str = "") -> str:
    sid = section_id or f"s{num.replace('↗', 'x')}"
    lead_html = f'<p class="nf-section-lead">{lead}</p>' if lead else ""
    return f"""
 <section class="nf-section-block nf-section--elevated" aria-labelledby="{sid}">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">{num}</span><div>
 <p class="nf-eyebrow" id="{sid}">{eyebrow}</p>
 <h2>{h2}</h2>
 {lead_html}
 </div></div>
 {body}
 </section>"""


def outcome_cards(cards: list[tuple[str, str, str, bool]]) -> str:
    items = []
    for tag, h3, p, gold in cards:
        cls = "nf-outcome-card nf-outcome-card--approved" if gold else "nf-outcome-card"
        items.append(f'<article class="{cls}"><p class="nf-outcome-label">{tag}</p><h3>{h3}</h3><p>{p}</p></article>')
    return f'<div class="nf-outcome-grid">{"".join(items)}</div>'


def proof_grid(links: list[tuple[str, str, str, str]]) -> str:
    items = []
    for href, icon, h3, p in links:
        items.append(
            f'<a class="nf-proof-card" href="{href}"><span class="nf-proof-icon">{icon}</span>'
            f"<div><h3>{h3}</h3><p>{p}</p></div></a>"
        )
    return f'<div class="nf-proof-grid">{"".join(items)}</div>'


def offerings_three_skus() -> str:
    return f"""
 <div class="nf-offerings-v5">
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Copilot Governance Pack · LEAD</p><p class="price">$2k–10k · 90 days</p><p>Live TLE records, board PDF in governance meeting, procurement ZIP on every go/no-go.</p><a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for pilot</a></article>
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Trust Brief</p><p class="price">$10,000 · 6 weeks</p><p>Governance audit, AI policy mapping, and risk exposure analysis — diagnostic land SKU before enterprise scale.</p><a class="btn btn-secondary" href="/trust-brief/">Trust Brief</a></article>
 <article class="nf-offer-card"><p class="meta">Bank Pilot</p><p class="price">Custom</p><p>Read-only shadow governance simulation — policy evaluate without execution authority or custody rails.</p><a class="btn btn-secondary" href="/bank-pilot/">Bank Pilot</a></article>
 </div>"""


def category_zones_public() -> str:
    return """
 <div class="nf-zone-grid" aria-label="Where Noetfield fits for buyers">
 <div class="nf-zone"><strong>Company compliance automation</strong><span>SOC · ISO · trust center</span></div>
 <div class="nf-zone"><strong>AI estate governance</strong><span>Registry · policy · enforce</span></div>
 <div class="nf-zone"><strong>Decision evidence</strong><span>Signed receipts · audit export</span></div>
 <div class="nf-zone"><strong>MSP tenant readiness</strong><span>Phase 1 · Purview · Copilot enable</span></div>
 <div class="nf-zone nf-zone--gold"><strong>Copilot execution receipts</strong><span>Noetfield · evaluate → TLE → export</span></div>
 </div>
 <p class="nf-category-map__note">Noetfield receipts <strong>operational go/no-go decisions</strong> with signed TLE export after tenant readiness. Metadata-only M365 · Evaluate · Record · Export.</p>"""


def investor_category_map_8() -> str:
    """Investor zone grid — buyer zones only, no vendor names."""
    return category_zones_public()


def stack_complement_block() -> str:
    return """
 <div class="nf-stack-ladder" role="region" aria-label="Microsoft stack complement">
 <div class="nf-stack-tier"><p class="nf-stack-tier__label">Microsoft Copilot Control System</p><p>Security &amp; governance (Purview) · management · measurement (Copilot Analytics). <a href="https://learn.microsoft.com/en-us/copilot/microsoft-365/copilot-control-system/overview" rel="noopener noreferrer">Learn overview ↗</a></p></div>
 <div class="nf-stack-tier"><p class="nf-stack-tier__label">Partner Phase 1 · tenant readiness</p><p>Labels · DLP · readiness assessment · Copilot enable — MSP or internal IT leads.</p></div>
 <div class="nf-stack-tier nf-stack-tier--gold"><p class="nf-stack-tier__label">Noetfield Phase 2 · execution receipts</p><p>Evaluate operational intent → sign TLE v1 → board PDF · procurement ZIP. Evidence index: <code>purview · entra · audit</code>.</p></div>
 </div>"""


def workspace_mock(label: str = "Workspace · evaluate") -> str:
    return f"""
 <aside class="nf-workspace-mock" aria-label="Governance workspace preview">
 <p class="nf-workspace-mock__title">{label}</p>
 <div class="nf-workspace-mock__row"><span>Intent</span><code>Copilot rollout · prod</code></div>
 <div class="nf-workspace-mock__row"><span>Decision</span><code class="nf-workspace-mock__ok">allow · 0.82</code></div>
 <div class="nf-workspace-mock__row"><span>TLE</span><code>TLE-015DCFB8B953</code></div>
 <div class="nf-workspace-mock__row"><span>Export</span><code>board.pdf · pack.zip</code></div>
 <p class="nf-workspace-mock__foot"><a href="/workspace/">Open workspace</a> · <a href="/copilot/demo/">5-minute demo</a></p>
 </aside>"""


def faq_block(items: list[tuple[str, str]]) -> str:
    parts = []
    for q, a in items:
        parts.append(f'<details class="nf-faq-item"><summary>{q}</summary><p>{a}</p></details>')
    return f'<div class="nf-faq">{"".join(parts)}</div>'


def homepage_extended_sections() -> str:
    s07 = """
 <section class="nf-section-block" aria-labelledby="s07">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">07</span><div>
 <p class="nf-eyebrow" id="s07">Pain moment</p>
 <h2>The moment Copilot becomes auditable</h2>
 <p class="nf-section-lead">Copilot is enabled. Purview shows labels and DLP. Then the board, auditor, or GC AIA reviewer asks: <strong>who approved this deployment</strong>, under which policy, with what evidence — and can you prove the record was not altered?</p>
 </div></div>
 <div class="nf-stat-bar" role="region" aria-label="Governance gap">
 <div class="nf-stat-bar-item"><strong>Logs</strong><span>Activity trails — not board receipts</span></div>
 <div class="nf-stat-bar-item"><strong>Inventory</strong><span>Registers — not go/no-go decisions</span></div>
 <div class="nf-stat-bar-item"><strong>TLE</strong><span>Signed decision + fail-closed export</span></div>
 <div class="nf-stat-bar-item"><strong>&lt;5 min</strong><span>Self-serve demo + YAML samples</span></div>
 </div>
 </section>"""
    s08 = f"""
 <section class="nf-section-block nf-section--elevated" aria-labelledby="s08">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">08</span><div>
 <p class="nf-eyebrow" id="s08">What you get</p>
 <h2>Execution receipts for Copilot operational decisions</h2>
 <p class="nf-section-lead">Evaluate every Copilot go/no-go, record a signed Trust Ledger Entry, and export board PDF plus procurement ZIP — metadata-only M365 evidence on every decision.</p>
 </div></div>
 {category_zones_public()}
 </section>"""
    s09 = f"""
 <section class="nf-section-block" aria-labelledby="s09">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">09</span><div>
 <p class="nf-eyebrow" id="s09">Stack complement</p>
 <h2>Phase 2 after Microsoft CCS and partner readiness</h2>
 <p class="nf-section-lead">We produce the signed governance record when your team decides Copilot may execute in production — {COPY["m365_position"]}</p>
 </div></div>
 {stack_complement_block()}
 </section>"""
    faq_items = [
        ("What does Noetfield receipt?", "Copilot execution go/no-go with signed TLE export, confidence score, and M365 metadata evidence index — Evaluate · Decide · Record · Export before production scope opens."),
        ("How does Noetfield fit with Microsoft Purview and Copilot Control System?", "Metadata-only connectors index Purview · Entra · audit on every TLE. Noetfield records operational go/no-go decisions and exports board PDF + procurement ZIP after tenant readiness."),
        ("How does TLE support audit and procurement?", "TLE v1 bundles decision, confidence score, evidence index, and <strong>export_integrity: fail closed on tamper</strong> — board PDF and procurement ZIP ready for institutional diligence."),
        ("Are you SOC 2 or ISO certified?", "We do not claim SOC 2 or ISO certification today. See <a href=\"/trust/\">Trust &amp; security</a> for our Available · Planned · Out of scope posture. We produce governance artifacts, not company certification."),
        ("What is the entry price?", "Copilot Governance Pack $2k–10k · 90 days (lead wedge · board PDF success signal). Trust Brief $10,000 · 6 weeks (diagnostic land SKU). Bank Pilot custom — three contract SKUs only."),
        ("Can MSPs resell this?", "Yes — Phase 2 attach after your Phase 1 Purview readiness practice. See <a href=\"/msp/\">MSP lane</a> for Readiness → Record handoff."),
    ]
    s10 = f"""
 <section class="nf-section-block" aria-labelledby="s10">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">10</span><div>
 <p class="nf-eyebrow" id="s10">FAQ</p>
 <h2>What buyers ask</h2>
 </div></div>
 {faq_block(faq_items)}
 </section>"""
    return s07 + s08 + s09 + s10


def federal_official_links() -> str:
    return """
 <div class="nf-official-bar" role="navigation" aria-label="Official GC policy references">
 <a href="https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592" rel="noopener noreferrer">TBS · Directive on ADM ↗</a>
 <a href="https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/algorithmic-impact-assessment.html" rel="noopener noreferrer">Canada.ca · AIA ↗</a>
 <a href="https://www.canada.ca/en/government/system/digital-government/policies-standards/microsoft-copilot-for-work-policy-implementation-notice.html" rel="noopener noreferrer">Copilot for Work PIN ↗</a>
 <a href="https://www.nist.gov/itl/ai-risk-management-framework" rel="noopener noreferrer">NIST AI RMF ↗</a>
 </div>"""


def federal_aia_preview_table() -> str:
    return """
 <div class="nf-table-wrap"><table class="nf-table nf-table--compact"><caption class="sr-only">AIA to TLE field preview</caption><thead><tr><th>AIA theme</th><th>TLE v1 field</th><th>Noetfield role</th></tr></thead><tbody>
 <tr><td>Risk level / mitigation</td><td><code>confidence_score</code> · decision</td><td>Orientation crosswalk — supplementary evidence</td></tr>
 <tr><td>Human oversight</td><td><code>approver_chain</code></td><td>Named approvers on allow/review</td></tr>
 <tr><td>Transparency record</td><td><code>tle_id</code> · <code>rid</code></td><td>Signed export for AIA package</td></tr>
 <tr><td>Monitoring / refresh</td><td>export bundle timestamp</td><td>TLE refresh on policy change</td></tr>
 <tr><td>Copilot PIN alignment</td><td><code>evidence_index</code></td><td>purview · entra · audit metadata</td></tr>
 </tbody></table></div>
 <p class="nf-section-lead">Full mapping: <a href="/docs/federal/AIA_TLE_MAPPING_v1.md">AIA ↔ TLE mapping v1</a>. Not a federal certifier or AIA approver.</p>"""


def msp_phase_diagram() -> str:
    return """
 <div class="nf-phase-ladder" role="region" aria-label="MSP two-tier model">
 <div class="nf-phase-step"><p class="nf-phase-step__num">Phase 1</p><h3>MSP + Microsoft stack</h3><p>Readiness · Purview · labels · DLP · tenant baselines · Copilot enable.</p></div>
 <div class="nf-phase-arrow" aria-hidden="true">→</div>
 <div class="nf-phase-step nf-phase-step--gold"><p class="nf-phase-step__num">Phase 2</p><h3>Noetfield</h3><p>Evaluate intent · TLE v1 · board PDF · procurement ZIP per tenant.</p></div>
 </div>
 <p class="nf-section-lead"><strong>Phase 1 readiness → Phase 2 signed TLE receipts.</strong> Partner success: LOI + one live tenant on Governance Pack. Handoff: <a href="/docs/msp/READINESS_TO_RECORD_MAPPING_v1.md">Readiness → Record mapping</a>.</p>"""


def trust_center_body() -> str:
    cert_rows = [
        ("TLE v1 + workspace", "available"),
        ("Export integrity fail-closed", "available"),
        ("M365 metadata-only processing", "available"),
        ("Board PDF + procurement ZIP", "available"),
        ("SOC 2 Type II", "roadmap"),
        ("ISO 27001 / 42001 certification", "na"),
        ("Ed25519 / Merkle transparency log", "roadmap"),
    ]
    cert_html = "".join(
        f'<div class="nf-trust-signal"><span class="nf-trust-signal-label">{l}</span>'
        f'<span class="nf-signal-badge {SCOPE_BADGES[k]}">{SCOPE_LABELS[k]}</span></div>'
        for l, k in cert_rows
    )
    return hero(
        "Trust &amp; security · Canada",
        "Procurement diligence · honest scope",
        "Trust center for AI Governance &amp; Evidence",
        "Metadata-only Microsoft 365 processing. Export bundles <strong>fail closed on tamper</strong>. No custody, payment rails, or certifier claims — Available · Planned · Out of scope only.",
        [("Metadata-only M365", True), ("Fail-closed export", False)],
        [("/copilot/procurement/", "Procurement pack", True), ("/trust-ledger/verify/", "Verify export integrity", False)],
        ["Retention · subprocessors · scope"],
        receipt("RID-2026-0602-TRUST", "Diligence path — <a href=\"/status/\">status</a> · <a href=\"/trust-ledger/sample-report/\">TLE samples</a>"),
    ) + procurement_rail() + ciso_strip() + f"""
 <section class="nf-section-block" aria-labelledby="trust-01">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="trust-01">Data handling</p>
 <h2>Metadata-only M365 connectors</h2>
 <p class="nf-section-lead">Purview · Entra ID · audit log indices — no mailbox content custody. See <a href="/privacy/">Privacy</a> and <a href="/docs/api/CANADA_TRUST.md">Canada trust notes</a>.</p>
 </div></div>
 </section>
 <section class="nf-section-block" aria-labelledby="trust-02">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="trust-02">Export integrity</p>
 <h2>Fail closed on tamper</h2>
 <p class="nf-section-lead">Board PDF and procurement ZIP include integrity checks. Walkthrough: <a href="/trust-ledger/verify/">offline verify guide</a>.</p>
 </div></div>
 </section>
 <section class="nf-section-block" aria-labelledby="trust-03">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">03</span><div>
 <p class="nf-eyebrow" id="trust-03">Honest certification posture</p>
 <h2>Available · Planned · Out of scope</h2>
 </div></div>
 <div class="nf-trust-signals-grid">{cert_html}</div>
 </section>
 {proof_grid([
        ("/copilot/demo/", "▶", "5-minute demo", "Live evaluate → TLE path"),
        ("/trust-ledger/sample-report/", "TLE", "YAML samples", "Go · conditional · rejected"),
        ("/copilot/procurement/", "ZIP", "Procurement pack", "Buyer diligence bundle"),
        ("/status/", "●", "Status", "Public surface availability"),
 ])}""" + mega_cta()


def verify_page_body() -> str:
    return hero(
        "Export verify · TLE v1",
        "Offline integrity walkthrough",
        "Verify export integrity — fail closed on tamper",
        "Procurement and engineering can replay integrity checks on board PDF and procurement ZIP bundles without trusting a dashboard narrative.",
        [("Orientation guide", True), ("Not legal advice", False)],
        [("/trust-ledger/sample-report/", "Download TLE YAML", True), ("/trust/", "Trust center", False)],
        [],
        receipt("RID-2026-0602-VERIFY", "Sample <code>export_integrity: PASS</code>"),
    ) + """
 <section class="nf-section-block" aria-labelledby="verify-01">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="verify-01">Walkthrough</p>
 <h2>Four steps — under five minutes</h2>
 </div></div>
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">01</p><h3>Export</h3><p>Generate board PDF + procurement ZIP from workspace or pilot host.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">02</p><h3>Manifest</h3><p>JSON sidecar lists <code>tle_id</code>, hashes, and <code>export_integrity</code> fields.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">03</p><h3>Verify PASS</h3><p>Integrity check returns PASS on unmodified bundle.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">04</p><h3>Tamper FAIL</h3><p>Alter any file — export verification <strong>fail closed</strong> (expected).</p></article>
 </div>
 </section>
 <aside class="nf-callout"><p><strong>Current capability:</strong> Offline verify covers export integrity available today. Cryptographic transparency-log verification (Ed25519 / Merkle) is a <strong>planned capability</strong> — not available yet.</p></aside>
""" + mega_cta(MEGA_CTA_TITLE, "Procurement diligence · pilot export walkthrough")


def hub_page(kicker, eyebrow, h1, lead, badges, actions, tags, side, extra: str, cta: str | None = None) -> str:
    if cta is None:
        cta = mega_cta()
    return hero(kicker, eyebrow, h1, lead, badges, actions, tags, side) + scope_block() + extra + cta


def legal_prose(kind: str) -> str:
    blocks = {
        "privacy": """
 <div class="nf-prose">
 <section><h2>Overview</h2><p>Noetfield processes operational and intake metadata to deliver governance evaluation, Trust Ledger records, and export bundles. We do not take custody of Microsoft 365 mailbox content.</p></section>
 <section><h2>What we collect</h2><p>Trust Brief and sandbox intake: contact details, organization name, and non-confidential scope notes you provide. M365 connectors use metadata-only indices (Purview labels, Entra ID configuration, audit log references).</p></section>
 <section><h2>Your Request ID</h2><p>We assign a Request ID (RID) to thread intake, evaluate, and export on your engagement. You may copy it from the site footer.</p></section>
 <section><h2>Contact</h2><p>Privacy questions: <a href="mailto:operations@noetfield.com">operations@noetfield.com</a></p></section>
 </div>""",
        "terms": """
 <div class="nf-prose">
 <section><h2>Use of public surfaces</h2><p>Noetfield public websites, sandbox, and documentation are provided for evaluation and diligence. Orientation materials are not legal advice.</p></section>
 <section><h2>No custody or payment execution</h2><p>Noetfield is a governance evaluation layer — not a bank, MSB, certifier, or payment processor.</p></section>
 <section><h2>Sandbox and production</h2><p>Free sandbox uses mock connectors and sample limits. Production evaluate, workspace, and export require a Copilot Governance Pack or Trust Brief engagement.</p></section>
 <section><h2>Contact</h2><p>Terms questions: <a href="mailto:operations@noetfield.com">operations@noetfield.com</a></p></section>
 </div>""",
        "status": """
 <div class="nf-prose">
 <section><h2>Public website</h2><p>Marketing pages, sandbox signup, pricing, and buyer documentation are available.</p></section>
 <section><h2>Workspace and evaluate API</h2><p>Sandbox evaluate and workspace are available for self-serve trial. Production API keys and tenant-scoped evaluate are provisioned per Copilot Governance Pack or Trust Brief SOW.</p></section>
 <section><h2>Engagement support</h2><p>For status on your organization&rsquo;s engagement, contact <a href="mailto:operations@noetfield.com">operations@noetfield.com</a> with your Request ID.</p></section>
 </div>""",
    }
    return blocks[kind]


def copilot_link_cards(*extra_cards: str) -> str:
    cards = [
        ('/copilot/', "Overview", "Copilot Governance Pack", "Full offering overview."),
        ('/trust-ledger/sample-report/', "Samples", "TLE v1 YAML", "Go · conditional · rejected."),
    ]
    card_html = "".join(
        f'<a class="nf-card nf-card--link" href="{href}"><p class="nf-card__tag">{tag}</p>'
        f"<h3>{title}</h3><p>{desc}</p></a>"
        for href, tag, title, desc in cards
    )
    card_html += "".join(extra_cards)
    return f"""
 <section class="nf-section nf-section--lift"><div class="nf-cards">
{card_html}
 </div></section>"""


def procurement_diligence_body() -> str:
    return """
 <section class="nf-section">
 <h2>Framework alignment (orientation only)</h2>
 <p>Citations use primary sources from the Governance Sources Book — not legal advice.</p>
 <table class="nf-table" style="width:100%;border-collapse:collapse;font-size:.9rem">
 <thead>
 <tr><th style="text-align:left;padding:.5rem">Framework</th><th style="text-align:left;padding:.5rem">Noetfield artifact</th></tr>
 </thead>
 <tbody>
 <tr><td style="padding:.5rem">NIST AI RMF Govern / Manage</td><td style="padding:.5rem">TLE approval chain + board pack decision record</td></tr>
 <tr><td style="padding:.5rem">ISO/IEC 42001-style evidence</td><td style="padding:.5rem">Evidence index (Purview, Entra, Audit metadata)</td></tr>
 <tr><td style="padding:.5rem">Microsoft Purview / M365</td><td style="padding:.5rem">Connector ingest → evidence IDs in TLE</td></tr>
 </tbody>
 </table>
 <p class="text-sm" style="margin-top:1rem">
 Framework citations cover NIST AI RMF, ISO/IEC 42001-style evidence, EU AI Act orientation, and Microsoft Purview metadata indices — orientation only, not legal advice.
 See <a href="/trust/">Trust center</a> for cert posture and scope badges.
 </p>
 <h3 style="margin-top:1.25rem">Governance control checkpoints</h3>
 <p>
 Noetfield provides an evaluate-then-enforce loop for Copilot governance:
 <strong>Evaluate</strong> operational intent before production use;
 <strong>Enforce</strong> fail-closed export when board PDF or procurement ZIP bundles are tampered.
 </p>
 <p style="margin-top:1rem">
 Production API surface:
 <a href="/docs/api/">Governance API reference</a>
 (evaluate, trust ledger, audit export) — orientation only.
 </p>
 </section>

 <section class="nf-section">
 <h2>Diligence attachments</h2>
 <p>For legal, risk, and procurement reviewers under NDA:</p>
 <ul>
 <li><a href="/docs/copilot/PROCUREMENT_ONE_PAGER.md">Copilot procurement one-pager</a> — buyer summary (positioning, deliverables, scope)</li>
 <li><a href="/docs/diligence/rpaa-positioning-onepager.md">RPAA-safe positioning one-pager</a> — governance vendor layer; no payment or custody claims</li>
 <li><a href="/docs/diligence/EVIDENCE_INTAKE_CONTRACT_v1.md">Evidence Intake Contract v1</a></li>
 <li><a href="/docs/diligence/CONNECTORS_CONTROLS_v1.md">Connectors Controls v1</a></li>
 </ul>
 </section>

 <section class="nf-section">
 <h2>Deliverables</h2>
 <ul>
 <li>Trust Ledger Entry (TLE v1) with <strong>confidence score</strong> and sequential approval chain</li>
 <li>Evidence index — metadata only (Purview, Entra ID, Audit, SharePoint)</li>
 <li>Governance evaluate + audit export tenant bundle</li>
 </ul>
 </section>"""


START_H1 = (
    '<span class="nf-hero-flow">'
    '<span class="nf-hero-flow__step">Sign up</span>'
    '<span class="nf-hero-flow__sep" aria-hidden="true">'
    '<svg viewBox="0 0 16 16" fill="none"><path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    '</span>'
    '<span class="nf-hero-flow__step">Sandbox</span>'
    '<span class="nf-hero-flow__sep" aria-hidden="true">'
    '<svg viewBox="0 0 16 16" fill="none"><path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    '</span>'
    '<span class="nf-hero-flow__step">Try in minutes</span>'
    '</span>'
)


def start_page_body() -> str:
    return hero(
        "Self-serve sandbox · EU + US institutions",
        "Self-serve · no sales call",
        START_H1,
        "Create a free developer sandbox, open the Governance Console, and run evaluate → tamper-evident TLE → export with mock M365 connectors — "
        "then upgrade to the <strong>Copilot Governance Pack ($2k–10k)</strong> for production tenant and board PDF.",
        [("14-day trial", True), ("50 evaluate calls", False), ("Sandbox mode", False)],
        [(PILOT_INTAKE, "Apply for pilot", True), ("#trial-os", "Start sandbox", False), ("/copilot/demo/", "5-minute demo", False)],
        HERO_MARQUEE,
        workspace_mock("Sandbox · evaluate"),
    ) + self_serve_rail() + f"""
 <section class="nf-section-block" id="trial-os" aria-labelledby="start-trial">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="start-trial">Trial OS</p>
 <h2>Full self-serve flow — no calendar required</h2>
 <p class="nf-section-lead">Sandbox mode · mock M365 · evaluate API · sample export — {COPY["sandbox_limits"]}.</p>
 </div></div>
 {trial_os_wizard()}
 {production_upgrade_callout()}
 </section>
 {fit_qualification_section()}
 {agentic_autonomous_section()}
""" + packaging_tiers_grid(compact=True) + revenue_path_strip() + mega_cta("Upgrade to Copilot Governance Pack", "Production keys · real M365 metadata · board PDF in governance meeting", (PILOT_INTAKE, "Apply for pilot ($2k–10k)"), ("/pricing/", "Published tiers"))


def pricing_page_body() -> str:
    return hero(
        "Published tiers · EU + US institutions",
        "Access paths + contract programs",
        "Packaged offering — pilot, sandbox, and contract SKUs",
        "Transparent packaging for regulated buyers: <strong>Copilot Governance Pack ($2k–10k · board PDF)</strong> as lead wedge, "
        "<strong>free developer sandbox</strong>, and <strong>three locked contract SKUs</strong> — no catalog creep.",
        [("Pilot · $2k–10k", True), ("Sandbox free", False), ("3 contract SKUs", False)],
        [(PILOT_INTAKE, "Apply for pilot ($2k–10k)", True), ("/start/", "Start free sandbox", False)],
        HERO_MARQUEE,
        receipt("RID-2026-0602-PRICE", "Sandbox limits · <a href=\"/docs/api/\">API reference</a>"),
    ) + """
 <section class="nf-section-block" aria-labelledby="price-modes">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="price-modes">Environment modes</p>
 <h2>Sandbox + production — same API spine</h2>
 </div></div>
 <div class="nf-mode-toggle" role="group" aria-label="Environment mode">
 <span class="is-active">Sandbox</span><span>Production</span>
 </div>
 <div class="nf-table-wrap" style="margin-top:20px"><table class="nf-table nf-tier-table"><thead><tr><th>Capability</th><th>Sandbox (free)</th><th>Production (Governance Pack)</th></tr></thead><tbody>
 <tr><td>Evaluate API</td><td>50 calls / 14 days</td><td>Per SOW · tenant-scoped keys</td></tr>
 <tr><td>M365 connectors</td><td>Mock OAuth</td><td>Metadata-only Purview · Entra · audit</td></tr>
 <tr><td>TLE export</td><td>Sample YAML + orientation PDF</td><td>Board PDF + procurement ZIP</td></tr>
 <tr><td>Policy automation</td><td>Investigate · triage · draft (sandbox)</td><td>Full chain + named approvers</td></tr>
 <tr><td>Sales call required</td><td>No</td><td>Program intake · SOW</td></tr>
 </tbody></table></div>
 </section>
 """ + contrast_table_section() + milestone_pricing_ladder() + revenue_path_strip() + section_block("02", "Tiers", "Access paths and contract programs", packaging_tiers_grid(compact=True), "Free sandbox is developer access — not a fourth contract SKU.") + mega_cta()


def ai_automation_body() -> str:
    """Lane B operator reference — sub-page of Copilot SKU, not a fourth contract."""
    return hub_page(
        "Governance-first · Operator reference",
        "Lane B · not a new SKU",
        "Make your AI automation defensible",
        "Regulated SMBs want AI automation; <strong>Noetfield sells the governance and evidence layer before automation runs</strong> — "
        "evaluate intent, RID-threaded decisions, signed Trust Ledger Entries, and board-ready export. "
        "Operator reference under the Copilot Governance Pack — not a catalog of bots.",
        [("Scope (locked)", True), ("Three offerings only", False)],
        [(PILOT_INTAKE, "Apply for pilot", True), (TRUST_BRIEF_INTAKE, "Request Trust Brief", False)],
        ["Evaluate · Record · Export"],
        panel(
            "Governance artifacts",
            [
                "Pre-execution evaluate",
                "Signed TLE v1",
                "Board PDF + procurement ZIP",
                "Metadata-only M365 index",
            ],
        ),
        f"""
 <section class="nf-section-block" aria-labelledby="aa-01">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="aa-01">Commercial lock</p>
 <h2>Three contract SKUs only</h2>
 <p class="nf-section-lead">Trust Brief · Copilot Governance Pack · Bank Pilot. This page orients automation buyers to the Copilot Pack — it is not a separate product line.</p>
 </div></div>
 <div class="nf-offerings-v5">
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Copilot Governance Pack · LEAD</p><p class="price">$2k–10k pilot</p><p>Receipt Copilot and workflow go/no-go decisions with signed tamper-evident TLE export — not a bot catalog.</p><a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for pilot</a></article>
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Trust Brief</p><p class="price">$10,000</p><p>Governance diagnostic before automation or Copilot scale — policy map and risk exposure for executive sign-off.</p><a class="btn btn-secondary" href="/trust-brief/">Trust Brief</a></article>
 <article class="nf-offer-card"><p class="meta">Bank Pilot</p><p class="price">Custom</p><p>Shadow simulation — read-only.</p><a class="btn btn-secondary" href="/bank-pilot/">Bank Pilot</a></article>
 </div>
 </section>""",
    )


def main() -> None:
    write("index.html", "Noetfield — Copilot Governance &amp; Trust Ledger Evidence",
          COPY["meta_home"],
          "/", homepage())

    write("start/index.html", "Noetfield — Start Free Sandbox",
          "Developer sandbox: sign up, try Governance API and workspace without a sales call. 14-day trial, 50 evaluate calls.",
          "/start/", start_page_body())

    write("pricing/index.html", "Noetfield — Pricing &amp; Packaging",
          "Published tiers: free developer sandbox, Copilot Governance Pack, Trust Brief and Bank Pilot contract SKUs.",
          "/pricing/", pricing_page_body())

    write("trust/index.html", "Noetfield — Trust &amp; Security",
          "Trust center: metadata-only M365, export integrity, honest certification posture.",
          "/trust/", trust_center_body(),
          body_class="nf-www nf-site-v14 nf-trust-diligence")

    write("trust-ledger/verify/index.html", "Noetfield — Verify Export Integrity",
          "Offline walkthrough: export integrity verification, fail closed on tamper.",
          "/trust-ledger/verify/", verify_page_body())

    # Trust Brief
    write("trust-brief/index.html", "Noetfield — Trust Brief ($10,000)",
          "Six-week Trust Brief: governance audit, AI policy mapping, risk exposure analysis. $10,000.",
          "/trust-brief/",
          hub_page("Trust Brief · $10,000 fixed", "Six-week governance diagnostic · land SKU",
                   "Governance diagnostic before enterprise scale",
                   "Fixed-scope Trust Brief: governance audit, AI policy mapping, and risk exposure analysis — executive summary for board and procurement. "
                   "<strong>Most regulated buyers start with the Copilot Governance Pack ($2k–10k)</strong>; Trust Brief is the diagnostic land SKU when you need policy mapping before scale.",
                   [("$10,000 fixed", True), ("6 weeks", False), ("Board-ready output", False)],
                   [("/trust-brief/intake/", "Request Trust Brief", True), (PILOT_INTAKE, "Apply for pilot first", False), ("/copilot/demo/", "5-minute demo", False)],
                   ["NIST AI RMF", "Executive summary", "AI policy map"],
                   panel("Deliverables", ["Governance audit report", "AI policy mapping", "Risk exposure analysis", "Executive summary for board"]),
                   """
 <section class="nf-section nf-section--lift"><div class="nf-section__head"><span class="nf-section__num">01</span><div>
 <p class="nf-section__label">Land SKU</p><h2>Trust Brief after pilot — or when diagnostic comes first</h2>
 <p class="nf-section__lead">Lead wedge: Copilot Governance Pack with live TLE and board PDF. Trust Brief fits when you need a six-week policy map before Copilot scale.</p>
 </div></div>
 <div class="nf-cards">
 <article class="nf-card nf-card--gold"><p class="nf-card__tag">Lead wedge</p><h3>Copilot pilot · $2k–10k</h3><p>Live TLE records · board PDF in governance meeting · 90 days.</p><a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for pilot</a></article>
 <article class="nf-card"><p class="nf-card__tag">Fixed scope</p><h3>$10,000 · 6 weeks</h3><p>No SKU creep — governance diagnostic only.</p></article>
 <article class="nf-card"><p class="nf-card__tag">Output</p><h3>Board-ready summary</h3><p>Policy gaps, risk exposure, recommended rollout scope.</p></article>
 </div></section>""".format(PILOT_INTAKE=PILOT_INTAKE)))

    # Copilot hub
    write("copilot/index.html", "Noetfield — Copilot Governance Pack",
          "AI Governance & Evidence layer for Microsoft 365 Copilot — signed TLE v1 and board-ready export.",
          "/copilot/",
          hub_page("Copilot Governance Pack · EU + US institutions", "Microsoft 365 Copilot · board-grade governance",
                   "The audit trail your Copilot deployment will be asked for later",
                   "Noetfield governs Copilot execution for regulated EU and US institutions — evaluate operational intent, index M365 metadata evidence, and produce signed Trust Ledger Entries your board, auditor, and procurement can defend. "
                   + COPY["m365_position"],
                   [("Copilot Governance Pack · $2k–10k", True), ("TLE v1 signed records", False)],
                   [(PILOT_INTAKE, "Apply for pilot", True), ("/copilot/demo/", "5-minute demo", False), ("/copilot/procurement/", "Procurement pack", False)],
                   ["Evaluate · Decide · Record · Export"],
                   hero_artifacts(receipt("RID-2026-0602-COPILOT"), workspace_mock("Workspace · evaluate")),
                   """
 <section class="nf-section-block" aria-labelledby="copilot-ccs">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="copilot-ccs">Stack complement</p><h2>Phase 2 after Copilot Control System and partner readiness</h2>
 <p class="nf-section-lead">Microsoft secures and measures Copilot. Partners standardize tenants. Noetfield receipts the operational go/no-go when Copilot touches production scope.</p>
 </div></div>
""" + stack_complement_block() + """
 </section>
 <section class="nf-section-block" aria-labelledby="copilot-prs">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="copilot-prs">Problem · Risk · Solution</p><h2>Copilot spreads before legal signs off</h2>
 </div></div>
 <div class="nf-personas">
 <article class="nf-persona"><p class="nf-persona-role">Problem</p><h3>Undocumented decisions</h3><p>Copilot adoption outpaces policy and risk review.</p></article>
 <article class="nf-persona"><p class="nf-persona-role">Risk</p><h3>Audit exposure</h3><p>Oversharing and unlogged go/no-go create regulatory risk.</p></article>
 <article class="nf-persona"><p class="nf-persona-role">Solution</p><h3>Signed TLE v1</h3><p>Confidence score + procurement-grade export your board and auditor can defend.</p></article>
 </div></section>"""))

    pages = [
        ("copilot/demo/index.html", "Noetfield — 5-Minute Copilot Governance Demo", "Live demo: confidence score, Purview, Entra, SharePoint evidence index.", "/copilot/demo/",
         "5-minute demo", "Live proof · Copilot governance",
         "See confidence score, M365 evidence index, and TLE export in five minutes",
         "Walk through evaluate → receipt → export with Purview, Entra ID, and SharePoint metadata. Demo script (locked narrative) — confidence score on every decision. "
         + COPY["m365_position"],
         [("Live demo script", True), ("Confidence score", False)],
         [("/workspace/", "Open workspace", True), ("/copilot/procurement/", "Procurement pack", False)],
         workspace_mock("Live workspace path")),
        ("copilot/procurement/index.html", "Noetfield — Copilot Procurement Pack", "Buyer diligence ZIP, NIST AI RMF citations, procurement export.", "/copilot/procurement/",
         "Procurement pack", "Buyer diligence · ZIP export",
         "Procurement-grade export for Copilot governance diligence",
         "Framework citations, vendor scope boundaries, and sample TLE artifacts — the buyer pack institutional buyers request before pilot sign-off. See <a href=\"/trust/\">Trust center</a> for honest cert posture.",
         [("NIST AI RMF", True), ("ZIP export", False), ("Trust center", False)],
         [(PILOT_INTAKE, "Apply for pilot", True), ("/trust/", "Trust &amp; security", False)],
         receipt("RID-2026-0602-PROC", "Orientation sample — request pack via intake.")),
        ("copilot/sme/index.html", "Noetfield — SME Governance Pack", "SME Copilot governance pack for CISO, GRC, and procurement.", "/copilot/sme/",
         "SME Governance Pack", "Mid-market · Copilot governance",
         "Governance pack sized for SME Copilot rollouts",
         "Same TLE v1 lifecycle as enterprise — confidence score, approval chain, and export scoped for teams that need signed receipts at pilot scale.",
         [("90-day Governance Pack", True), ("TLE v1", False)],
         [(PILOT_INTAKE, "Apply for pilot", True), ("/copilot/demo/", "5-minute demo", False)],
         panel("SME buyer path", ["Direct pilot intake · $2k–10k", "Purview metadata connectors", "Board PDF + procurement ZIP", "Workspace for TLE drafts"])),
    ]
    write("copilot/pilot/index.html", "Copilot Governance Pack — 90-day pilot | Noetfield",
          "90-day Copilot governance pilot for EU and US regulated institutions — $2k–10k, board PDF, procurement ZIP.",
          "/copilot/pilot/", pilot_page_body())
    for rel, title, desc, canon, kick, eye, h1, lead, badges, actions, side in pages:
        if "procurement" in rel:
            extra = procurement_diligence_body() + copilot_link_cards(
                '<a class="nf-card nf-card--link" href="/copilot/demo/"><p class="nf-card__tag">Demo</p><h3>5-minute demo script</h3><p>Procurement walkthrough.</p></a>',
                '<a class="nf-card nf-card--link" href="/workspace/"><p class="nf-card__tag">Workspace</p><h3>Trust Ledger Workspace</h3><p>Evaluate and export.</p></a>',
            )
        else:
            extra = copilot_link_cards()
        write(rel, title, desc, canon,
              hub_page(kick, eye, h1, lead, badges, actions, [], side, extra))

    write("enterprise/index.html", "Noetfield Enterprise — Governance for Regulated Organizations",
          "For banks, regulated enterprises, and institutional buyers. Three offerings from $10,000.",
          "/enterprise/",
          hub_page("Enterprise · Banks · Regulated institutions", "Institutional buyers",
                   "Governance evaluation for institutions that cannot afford policy failure",
                   "For CCO, CRO, and technology leaders: pre-execution policy evaluate, signed Trust Ledger evidence, and audit lineage your board and regulators can inspect — governance layer only, no custody or payment rails.",
                   [("From $10,000", True), ("Read-only Bank Pilot", False), ("No custody", False)],
                   [(PILOT_INTAKE, "Apply for pilot", True), (TRUST_BRIEF_INTAKE, "Request Trust Brief", False), ("/console/", "Governance Console", False)],
                   [],
                   panel("What we do not do", ["No transaction execution or custody", "No movement of financial value", "Governance evaluation layer only", "Policy-aligned allow or deny + compliance log"]),
                   """
 <section class="nf-section-block" aria-labelledby="ent-skus">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="ent-skus">Institutional SKUs</p><h2>Trust Brief → Copilot Pack → Bank Pilot</h2>
 </div></div>
""" + offerings_three_skus() + """
 </section>"""))

    write("federal/index.html", "Federal Governance Pack — GC Copilot &amp; ADM | Noetfield",
          "Government of Canada: Copilot governance evidence for ADM, AIA, and Copilot PIN. Unclassified scope.",
          "/federal/",
          hub_page("Federal lane · Government of Canada", "Unclassified information only",
                   "Copilot governance evidence for ADM and AIA reviewers",
                   "Before GC institutions scale Microsoft 365 Copilot, Noetfield produces the governance decision record deputy ministers and GRC teams expect — evaluate → receipt → export.",
                   [("Legacy ADS · June 24, 2026", True), ("AIA · ADM · Copilot PIN", False)],
                   [("/trust-brief/intake/?interest=federal", "Request Federal Brief", True), ("/copilot/demo/?federal=1", "5-minute demo", False)],
                   ["ADM", "AIA", "Copilot PIN", "GC AI Register"],
                   panel("Governance execution loop", ["Evaluate — intent before production use", "Decide — policy + approval chain", "Record — TLE v1 + AIA crosswalk", "Export — board PDF · procurement ZIP"]),
                   """
""" + federal_official_links() + """
 <div class="nf-trust" role="region" aria-label="Federal policy anchors">
 <div class="nf-trust__item"><strong>ADM</strong><span>Directive on Automated Decision-Making</span></div>
 <div class="nf-trust__item"><strong>AIA</strong><span>Algorithmic Impact Assessment</span></div>
 <div class="nf-trust__item"><strong>Copilot PIN</strong><span>Copilot for Work · unclassified</span></div>
 <div class="nf-trust__item"><strong>GC AI Register</strong><span>Inventory + governance depth</span></div>
 </div>
 <aside class="nf-callout"><p><strong>Scope:</strong> Unclassified information only. Noetfield produces governance artifacts for federal buyers — <strong>not a federal certifier</strong>.</p></aside>
 <section class="nf-section-block" aria-labelledby="fed-aia">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="fed-aia">AIA crosswalk preview</p><h2>TLE as supplementary AIA evidence</h2>
 </div></div>
""" + federal_aia_preview_table() + """
 </section>
 <section class="nf-section-block" aria-labelledby="fed-proof">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="fed-proof">Proof</p><h2>Federal lane documents</h2>
 </div></div>
""" + proof_grid([
        ("/docs/federal/FEDERAL_GOVERNANCE_PACK_v1.md", "DOC", "Federal Governance Pack", "Lane SSOT"),
        ("/docs/federal/AIA_TLE_MAPPING_v1.md", "AIA", "AIA ↔ TLE mapping", "Risk crosswalk"),
        ("/docs/federal/GC_COPILOT_PIN_CHECKLIST_v1.md", "PIN", "Copilot PIN checklist", "GC M365 compliance"),
        ("/trust-ledger/sample-report/", "TLE", "TLE samples", "Confidence + approval chain"),
 ]) + """
 </section>""",
          mega_cta("Request Federal Governance Brief", "Trust Brief intake · Schedule I/II departments · operations@noetfield.com", ("/trust-brief/intake/?interest=federal", "Request Federal Brief"))))

    write("msp/index.html", "MSP Partner Program — Readiness to Record | Noetfield",
          "Microsoft 365 MSP: Phase 1 Purview readiness · Phase 2 TLE governance receipts.",
          "/msp/",
          hub_page("MSP partner lane", "Readiness → Record · multi-tenant",
                   "Readiness → Record · Phase 2 TLE attach",
                   "Phase 1 stays in your Purview and tenant-readiness practice. Phase 2 attaches when customers need signed TLE records for Copilot enablement.",
                   [("Phase 1 · Phase 2 RACI", True), ("Partner LOI + 1 tenant", True)],
                   [("/gate/partners/intake/", "MSP partner intake", True), ("/copilot/demo/", "5-minute demo", False)],
                   ["Purview", "Copilot attach", "TLE receipts"],
                   panel("Two-tier model", ["Phase 1 — readiness + Purview (MSP leads)", "Phase 2 — evaluate + TLE (Noetfield)", "Import readiness gaps → pilot scope", "Governance Pack $2k–10k attach"]),
                   """
""" + msp_phase_diagram() + """
 <aside class="nf-callout"><p><strong>Phase 2 attach:</strong> Metadata-only TLE receipts per tenant — after Purview readiness and Copilot enablement in Phase 1.</p></aside>
 <section class="nf-section-block" aria-labelledby="msp-raci">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="msp-raci">RACI</p><h2>Phase 1 vs Phase 2 delivery</h2>
 </div></div>
 <div class="nf-table-wrap"><table class="nf-table"><thead><tr><th>Activity</th><th>MSP Phase 1</th><th>Noetfield Phase 2</th></tr></thead><tbody>
 <tr><td>Copilot readiness assessment</td><td>Lead</td><td>Import gaps → scope</td></tr>
 <tr><td>Purview labels · DLP</td><td>Configure</td><td>Metadata index only</td></tr>
 <tr><td>Go/no-go record</td><td>Facilitate sign-off</td><td>Sign TLE · board PDF · ZIP</td></tr>
 </tbody></table></div>
 </section>
 <section class="nf-section-block" aria-labelledby="msp-proof">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="msp-proof">Proof</p><h2>Partner documents</h2>
 </div></div>
""" + proof_grid([
        ("/docs/msp/MSP_GOVERNANCE_PACK_v1.md", "MSP", "MSP Governance Pack", "Lane SSOT"),
        ("/docs/msp/PHASE1_PHASE2_RACI_v1.md", "RACI", "Phase 1 / 2 RACI", "Delivery boundaries"),
        ("/docs/msp/READINESS_TO_RECORD_MAPPING_v1.md", "MAP", "Readiness → Record", "Assessment import"),
        ("/copilot/demo/", "▶", "5-minute demo", "Phase 2 proof"),
 ]) + """
 </section>""",
          mega_cta("MSP partner intake", "Partner enablement · first tenant pilot · co-marketing path", ("/gate/partners/intake/", "MSP partner intake"))))

    write("bank-pilot/index.html", "Noetfield — Bank Pilot (Shadow Governance)",
          "Read-only Bank Pilot: policy evaluation in shadow mode for OSFI E-23 readiness.",
          "/bank-pilot/",
          hub_page("Bank Pilot · Shadow mode", "FRFI · read-only simulation",
                   "Governance simulation for FRFI buyers",
                   "Evaluate operational intent against policy <strong>before</strong> any partner or bank execution layer acts. Read-only — no payment rails or custody.",
                   [("Read-only only", True), ("OSFI E-23 orientation", False), ("No custody", False)],
                   [("/gate/intake/?vector=bank-pilot&interest=bank-pilot", "Discuss Bank Pilot", True), ("/console/", "Governance Console", False)],
                   [],
                   panel("Shadow mode", ["Policy evaluate in shadow", "Compliance log export", "No transaction authority", "Partner execution stays in your environment"]),
                   """
 <section class="nf-section nf-section--lift"><div class="nf-cards">
 <article class="nf-card nf-card--gold"><p class="nf-card__tag">Scope</p><h3>Governance layer only</h3><p>Not a bank core system or payment rail.</p></article>
 <article class="nf-card"><p class="nf-card__tag">Output</p><h3>Audit lineage</h3><p>RID-keyed records for board and OSFI conversations.</p></article>
 </div></section>""",
          mega_cta("Discuss Bank Pilot", "Non-confidential intake for FRFI shadow governance", ("/gate/intake/?vector=bank-pilot&interest=bank-pilot", "Discuss Bank Pilot"), None)))

    write("partners/index.html", "Noetfield — Partner Governance Infrastructure",
          "Partner governance programs for banks, credit unions, and licensed execution partners.",
          "/partners/",
          hub_page("Partner programs · Canada", "Licensed execution partners",
                   "AI governance and risk intelligence for partners",
                   "Programs for banks, credit unions, and supervised firms: evaluate operational intent, record Trust Ledger evidence, return allow or deny. "
                   "<strong>Ecosystem apply:</strong> connectors, facilitators, co-partners, and MSP/SI partners — see <a href=\"/work-with-us/\">Work with Noetfield</a>.",
                   [("Governance evaluate", True), ("Trust Ledger export", False)],
                   [(WORK_WITH_US_INTAKE, "Apply to work with us", True), ("/msp/", "MSP lane", False)],
                   [],
                   panel("What partners get", ["Governance evaluate — shadow then enforce", "Trust Ledger — RID-keyed audit export", "Decision webhooks — SIEM / GRC hooks", "HTTP contracts: Governance API"]),
                   f"""
 <section class="nf-section"><div class="nf-cards">
 <a class="nf-card nf-card--link nf-card--gold" href="/work-with-us/"><p class="nf-card__tag">Apply</p><h3>Work with Noetfield</h3><p>Connector · facilitator · co-partner · partner lanes.</p></a>
 <a class="nf-card nf-card--link" href="/docs/api/"><p class="nf-card__tag">API</p><h3>Governance API</h3><p>OpenAPI + evaluate routes.</p></a>
 <a class="nf-card nf-card--link" href="/msp/"><p class="nf-card__tag">MSP</p><h3>MSP partners</h3><p>Readiness → Record.</p></a>
 </div></section>"""))

    write("work-with-us/index.html", "Work with Noetfield — Connectors, Facilitators & Partners",
          "Apply to work with Noetfield as a connector, facilitator, co-partner, or MSP/SI partner on Copilot Governance Pack programs.",
          "/work-with-us/", work_with_us_page_body())

    # FAQ
    write("faq/index.html", "Noetfield — FAQ",
          "Frequently asked questions about Noetfield AI Governance & Evidence for Microsoft 365 Copilot.",
          "/faq/",
          hero("FAQ", "Quick answers", "Frequently asked questions",
               "Use the assistant (bottom-right) or read below.",
               [], [(PILOT_INTAKE, "Apply for pilot", True), (TRUST_BRIEF_INTAKE, "Request Trust Brief", False)], [],
               panel("Start here", ["Copilot Governance Pack · $2k–10k", "5-minute demo", "Procurement pack", "Trust Brief · $10k land SKU"])) + """
 <div class="nf-prose">
 <section><h2>What is Noetfield?</h2><p>AI Governance &amp; Evidence for Microsoft 365 Copilot — board-grade, tamper-evident decision records. Evaluate operational intent before execution, with signed Trust Ledger Entries and fail-closed export. No custody or payment execution.</p></section>
 <section><h2>What do you offer?</h2><p>Lead wedge: Copilot Governance Pack ($2k–10k · 90 days · board PDF). Land SKU: Trust Brief ($10k · 6 weeks). Custom: Bank Pilot shadow simulation. Three contract SKUs only.</p></section>
 <section><h2>What does Noetfield add to Microsoft Purview?</h2><p>Signed Copilot governance receipts — metadata-only evidence index plus board PDF and procurement ZIP on every go/no-go decision.</p></section>
 <section><h2>Are you a certifier?</h2><p>No. We produce governance records and export bundles — honest Available · Planned · Out of scope posture, not ISO/SOC certification claims.</p></section>
 </div>""" + mega_cta())

    # Simple pages
    for rel, title, desc, canon, h1, lead in [
        ("status/index.html", "Noetfield — Status", "Noetfield platform status.", "/status/", "Platform status", "Public surfaces and workspace availability."),
        ("privacy/index.html", "Noetfield — Privacy", "Privacy policy.", "/privacy/", "Privacy", "How Noetfield handles intake and operational metadata."),
        ("terms/index.html", "Noetfield — Terms", "Terms of use.", "/terms/", "Terms", "Terms governing use of Noetfield public surfaces."),
    ]:
        write(rel, title, desc, canon,
              hero("", "", h1, lead, [], [("/contact/", "Contact", False)], [], receipt("RID-STATUS", "Operational metadata only.")) +
              legal_prose({"privacy": "privacy", "terms": "terms", "status": "status"}[rel.split("/")[0]]) + mega_cta())

    write("contact/index.html", "Noetfield — Contact", "Contact Noetfield operations.", "/contact/",
          hero("", "Contact", "Operations intake",
               "All contract offerings route through Copilot Governance Pack intake, Trust Brief, or operations@noetfield.com.",
               [], [(PILOT_INTAKE, "Apply for pilot", True), ("mailto:operations@noetfield.com", "operations@noetfield.com", False)], [],
               panel("Routing", ["Copilot Governance Pack · $2k–10k", "Trust Brief · land SKU", "operations@noetfield.com", "Non-confidential intake only"])) + mega_cta())

    write("trust-ledger/index.html", "Noetfield — Trust Ledger", "Trust Ledger workspace and TLE v1 lifecycle.", "/trust-ledger/",
          hub_page("Trust Ledger", "TLE v1 lifecycle",
                   "Signed governance records for Copilot decisions",
                   "Trust Ledger Entries document evaluate → decide → record → export with tamper-evident integrity.",
                   [("TLE v1", True), ("Workspace UI", False)],
                   [("/workspace/", "Open workspace", True), ("/trust-ledger/sample-report/", "TLE samples", False)],
                   [],
                   receipt("RID-2026-0602-TL"),
                   """
 <section class="nf-section"><div class="nf-proof">
 <a class="nf-proof__item" href="/trust-ledger/sample-report/"><span class="nf-proof__icon">YAML</span><div><h3>Sample reports</h3><p>Go · conditional · rejected</p></div></a>
 <a class="nf-proof__item" href="/workspace/"><span class="nf-proof__icon">UI</span><div><h3>Workspace</h3><p>Create TLE draft</p></div></a>
 </div></section>"""))

    write("trust-ledger/sample-report/index.html", "Noetfield — TLE v1 Sample Report", "Sample Trust Ledger Entry YAML reports.", "/trust-ledger/sample-report/",
          hub_page("TLE v1 samples", "Orientation artifacts",
                   "Sample Trust Ledger Entry reports",
                   "Go, conditional, and rejected YAML samples — canonical schema orientation for procurement and engineering.",
                   [("YAML download", True), ("Not live records", False)],
                   [("/workspace/", "Workspace", True), ("/copilot/demo/", "5-minute demo", False)],
                   [],
                   receipt("RID-2026-0602-SAMPLE", "Orientation sample — not a live record."),
                   ""))

    write("investors/index.html", "Noetfield — Investor success model",
          "AI Governance & Evidence for Copilot — shipped product, land-expand-channel success model, honest milestone path for investors.",
          "/investors/",
          hero(
              "Investor brief · Canada",
              "Success model · product shipped · proof is the step function",
              "We produce the audit trail your Copilot deployment will be asked for later",
              "Noetfield is the <strong>governance execution layer</strong> for M365 Copilot: evaluate intent, sign Trust Ledger Entries, export board-ready diligence. "
              "<strong>Product is demo-ready today</strong> — TLE v1, workspace, evaluate API, board PDF, procurement ZIP. "
              "The step function investors underwrite is <strong>one contracted org</strong> using a board PDF in a real governance meeting.",
              [("Demo-ready product", True), ("Board PDF pilots open", True), ("No custody · no MSB", False)],
              [("/copilot/demo/", "5-minute demo", True), ("mailto:operations@noetfield.com?subject=Investor%20brief", "Investor inquiry", False)],
              ["Land · Expand · Channel", "Governance Pack ≥ CAD 2K", "Metadata-only M365"],
              receipt("RID-2026-0602-INV", "Live product path — <a href=\"/copilot/demo/\">demo</a> · <a href=\"/trust-ledger/sample-report/\">TLE samples</a>"),
          )
          + investor_stat_bar()
          + """
 <section class="nf-section-block nf-section--elevated" aria-labelledby="inv-cat">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="inv-cat">Product wedge</p>
 <h2>Signed receipts for Copilot execution decisions</h2>
 <p class="nf-section-lead">Evaluate operational intent, sign TLE v1, export board PDF and procurement ZIP — metadata-only M365 evidence. Partners attach after Purview readiness in Phase 1.</p>
 </div></div>
""" + investor_category_map_8() + """
 </section>

 <section class="nf-section-block" aria-labelledby="inv-02">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="inv-02">Investment thesis</p>
 <h2>Copilot rollouts need tamper-evident execution receipts</h2>
 <p class="nf-section-lead">Boards and procurement ask for defensible go/no-go records when Copilot touches production data. Noetfield delivers pre-execution evaluate, signed TLE records, and board PDF export.</p>
 </div></div>
 <div class="nf-stat-bar" role="region" aria-label="Market timing">
 <div class="nf-stat-bar-item"><strong>M365</strong><span>Copilot already in buyer stack</span></div>
 <div class="nf-stat-bar-item"><strong>Jun 2026</strong><span>GC legacy ADS / ADM clock</span></div>
 <div class="nf-stat-bar-item"><strong>MSP</strong><span>Phase 2 attach after readiness</span></div>
 <div class="nf-stat-bar-item"><strong>Board</strong><span>PDF unlocks budget conversation</span></div>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-03">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">03</span><div>
 <p class="nf-eyebrow" id="inv-03">Success model</p>
 <h2>Land → Expand → Channel on three locked SKUs</h2>
 <p class="nf-section-lead">Services-led revenue now, same TLE spine across enterprise, federal, MSP, and bank lanes — no SKU creep, no platform fiction.</p>
 </div></div>
 <div class="nf-offerings-v5">
 <article class="nf-offer-card nf-offer-card--featured">
 <p class="meta">Land · Copilot Governance Pack</p>
 <p class="price">$2k–10k · 90 days</p>
 <p>Lead wedge: live TLE records, confidence score, board PDF in governance meeting — fixed-fee institutional entry before scale.</p>
 <a class="btn btn-primary" href="/copilot/pilot/">Apply for pilot</a>
 </article>
 <article class="nf-offer-card nf-offer-card--featured">
 <p class="meta">Expand · Trust Brief</p>
 <p class="price">$10,000 · 6 weeks</p>
 <p>Six-week governance diagnostic — policy map, risk exposure, executive summary when diagnostic precedes Copilot scale.</p>
 <a class="btn btn-primary" href="/trust-brief/">Trust Brief</a>
 </article>
 <article class="nf-offer-card">
 <p class="meta">Channel · Federal · MSP · Bank</p>
 <p class="price">Partner margin</p>
 <p>Same product spine — federal ADM attach, MSP Phase 2 after Purview readiness, bank shadow simulation for FRFI diligence.</p>
 <a class="btn btn-secondary" href="/federal/">Federal lane</a>
 </article>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-04">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">04</span><div>
 <p class="nf-eyebrow" id="inv-04">Honest milestone stack</p>
 <h2>Shipped today · what capital accelerates next</h2>
 <p class="nf-section-lead">No fake traction. Product converts in a 5-minute demo — economic proof is a contracted pilot and referenceable board PDF.</p>
 </div></div>
 <div class="nf-trust-signals-grid">
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Governance evaluate + TLE v1 + workspace</span><span class="nf-signal-badge nf-signal-badge--available">Available</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Board PDF + procurement ZIP export</span><span class="nf-signal-badge nf-signal-badge--available">Available</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">M365 metadata evidence index</span><span class="nf-signal-badge nf-signal-badge--available">Available</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">First org: TLE in production + board PDF in meeting</span><span class="nf-signal-badge nf-signal-badge--orientation">Target</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Governance Pack LOI / deposit ≥ CAD 2K</span><span class="nf-signal-badge nf-signal-badge--orientation">Target</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Governance Monitor MRR · tenant refresh</span><span class="nf-signal-badge nf-signal-badge--roadmap">Planned</span></div>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-05">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">05</span><div>
 <p class="nf-eyebrow" id="inv-05">90-day path to reference</p>
 <h2>Copilot Governance Pack — week-by-week proof</h2>
 <p class="nf-section-lead">Commercial path from first demo to contracted Governance Pack. Capital maps to running this playbook in parallel across 3–5 pilot conversations.</p>
 </div></div>
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 0–2</p><h3>Demo + CIO contact</h3><p>5-minute demo live · qualified CIO engagement · confidence score visible.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 3–6</p><h3>Pilot SOW + evidence</h3><p>M365 metadata connected · first TLE v1 approved in workspace.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 7–10</p><h3>Board PDF in meeting</h3><p>Referenceable governance artifact — partner success signal for expand.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 11–12</p><h3>LOI / deposit ≥ CAD 2K</h3><p>Contracted Governance Pack deposit · expand seats or MSP attach conversation.</p></article>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-06">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">06</span><div>
 <p class="nf-eyebrow" id="inv-06">Use of capital</p>
 <h2>Bottleneck is distribution and buyer proof — not product invention</h2>
 </div></div>
 <div class="nf-outcome-grid">
 <article class="nf-outcome-card nf-outcome-card--approved"><p class="nf-outcome-label">Acquire</p><h3>Governance Pack pipeline</h3><p>Targeted outreach to CISO and GRC leaders at Copilot rollouts — Trust Brief land wedge in Canada.</p></article>
 <article class="nf-outcome-card nf-outcome-card--approved"><p class="nf-outcome-label">Prove</p><h3>First referenceable board PDF</h3><p>One org exports TLE + board pack used in governance — unlocks procurement and case study.</p></article>
 <article class="nf-outcome-card"><p class="nf-outcome-label">Expand</p><h3>MSP + federal attach</h3><p>Phase 2 TLE receipts after partner readiness · GC ADM clock for federal Trust Brief attach.</p></article>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-07">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">07</span><div>
 <p class="nf-eyebrow" id="inv-07">Defensibility</p>
 <h2>Receipt spine + M365 metadata evidence</h2>
 </div></div>
 <div class="nf-outcome-grid">
 <article class="nf-outcome-card nf-outcome-card--approved"><p class="nf-outcome-label">Moat</p><h3>TLE v1 + fail-closed export</h3><p>Signed decision records with tamper-evident integrity — the artifact auditors ask for after Copilot is live.</p></article>
 <article class="nf-outcome-card"><p class="nf-outcome-label">Integration</p><h3>Metadata-only M365</h3><p>Purview · Entra · audit evidence index on every TLE.</p></article>
 <article class="nf-outcome-card"><p class="nf-outcome-label">Discipline</p><h3>Three SKUs · no scope creep</h3><p>Trust Brief · Copilot Pack · Bank Pilot — services cash now, platform expand later.</p></article>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-proof">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">↗</span><div>
 <p class="nf-eyebrow" id="inv-proof">Inspect the product</p>
 <h2>Due diligence in five minutes — not a deck</h2>
 </div></div>
 <div class="nf-proof-grid">
 <a class="nf-proof-card" href="/copilot/demo/"><span class="nf-proof-icon">▶</span><div><h3>5-minute demo</h3><p>Evaluate → TLE → confidence score → export</p></div></a>
 <a class="nf-proof-card" href="/trust-ledger/sample-report/"><span class="nf-proof-icon">TLE</span><div><h3>TLE v1 samples</h3><p>Go · conditional · rejected YAML</p></div></a>
 <a class="nf-proof-card" href="/copilot/procurement/"><span class="nf-proof-icon">ZIP</span><div><h3>Procurement pack</h3><p>Buyer diligence · NIST AI RMF</p></div></a>
 <a class="nf-proof-card" href="/docs/api/"><span class="nf-proof-icon">API</span><div><h3>Governance API</h3><p>Evaluate · ledger · audit export</p></div></a>
 </div>
 </section>

 <aside class="nf-callout"><p><strong>Investor honesty:</strong> We do not claim ISO/SOC certification, custody, payment rails, or MSB execution. We do not inflate ARR or logo count. Product is shipped and demoable today — capital accelerates <strong>first contracted Governance Pack</strong> and <strong>referenceable board PDF</strong> on the three locked SKUs.</p></aside>
"""
          + mega_cta(
              "Investor or Governance Pack conversation",
              "Live demo · commercial SSOT · 90-day milestone plan — operations@noetfield.com",
              ("mailto:operations@noetfield.com?subject=Investor%20brief", "Email operations"),
              ("/copilot/demo/", "Run 5-minute demo"),
          ))

    # Console
    write("console/index.html", "Noetfield — Governance Console",
          "Governance Evaluation Interface — submit intent, view decision and compliance log.",
          "/console/",
          hub_page(
              "Governance Console",
              "Evaluate · Decide · Record · Export",
              "Governance Evaluation Interface",
              "Submit operational intent, receive an allow or deny decision, and review the compliance log — start in <a href=\"/start/\">free sandbox</a> or open your Governance Pack tenant.",
              [("Sandbox · free", True), ("RID-threaded", False)],
              [("/copilot/demo/", "5-minute demo", True), (PILOT_INTAKE, "Apply for pilot", False)],
              [],
              panel("What you get", ["Submit Intent — evaluate API or console", "Decision + RID — threaded request identity", "Compliance log — immutable ledger entries", "Export — audit bundle for diligence"]),
              """
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">01</p><h3>Submit</h3><p>Describe proposed operational action.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">02</p><h3>Decide</h3><p>Allow or deny with confidence score.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">03</p><h3>Record</h3><p>RID ties intake, evaluate, audit export.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">04</p><h3>Review</h3><p>Compliance log for diligence evidence.</p></article>
 </div>
 <aside class="nf-callout"><p><strong>Enterprise access:</strong> Pilot SSO and identity provider integration configured per engagement.</p></aside>""",
          ) + """
 <script>
 (function () {
   var host = window.location.hostname;
   var target = "https://platform.noetfield.com/cognitive-dashboard/";
   if (host === "localhost" || host === "127.0.0.1") target = "/cognitive-dashboard/";
   else if (host.indexOf("platform.") === 0) target = window.location.protocol + "//" + host + "/cognitive-dashboard/";
   var a = document.querySelector(".nf-hero-cinematic .nf-cta-actions .btn-secondary");
   if (a) a.href = target;
   if (/[?&]go=1/.test(location.search)) location.replace(target);
 })();
 </script>""")

    # API docs
    write("docs/api/index.html", "Noetfield — Governance API",
          "Institutional governance API: evaluate AI-driven intent, compliance log, audit export.",
          "/docs/api/",
          hero(
              "Governance API · Canada",
              "Technical reference · pilot contracts",
              "Policy evaluate, compliance log, and audit export",
              "HTTP contracts for governance evaluation, RID lineage, and Trust Ledger export. "
              "<strong>Start in sandbox</strong> without a sales call — production keys via Copilot Governance Pack.",
              [("OpenAPI", True), ("Sandbox + production", False)],
              [(PILOT_INTAKE, "Apply for pilot", True), ("/start/", "Start free sandbox", False)],
              [],
              receipt("RID-2026-0602-API", "Evaluate → ledger → export routes available in sandbox and production."),
          ) + scope_block() + f"""
 <section class="nf-section nf-section--lift" aria-labelledby="api-sandbox">
 <div class="nf-section__head"><span class="nf-section__num">00</span><div>
 <p class="nf-section__label" id="api-sandbox">Developer sandbox</p><h2>Try without a sales call</h2>
 <p class="nf-section__lead">{COPY["sandbox_limits"]} · mock M365 · same evaluate semantics as production.</p>
 </div></div>
 <p><a class="btn btn-primary" href="{PILOT_INTAKE}">Apply for pilot</a> · <a class="btn btn-secondary" href="/start/">Start sandbox</a> · <a href="/pricing/">Published tiers</a></p>
 </section>
""" + """
 <section class="nf-section nf-section--lift" aria-labelledby="api-v1">
 <div class="nf-section__head"><span class="nf-section__num">01</span><div>
 <p class="nf-section__label" id="api-v1">Pilot surface</p><h2>Governance API v1</h2>
 </div></div>
 <div class="nf-table-wrap"><table class="nf-table"><thead><tr><th>Method</th><th>Route</th><th>Role</th></tr></thead><tbody>
 <tr><td><code>POST</code></td><td><code>/api/v1/governance/evaluate</code></td><td>Allow, restrict, or block before external execution</td></tr>
 <tr><td><code>GET</code></td><td><code>/api/v1/governance/ledger</code></td><td>Compliance log read</td></tr>
 <tr><td><code>GET</code></td><td><code>/api/v1/governance/audit-export</code></td><td>Procurement / audit slice by RID</td></tr>
 <tr><td><code>GET</code></td><td><code>/api/v1/governance/vendor-evidence</code></td><td>Vendor due diligence metadata</td></tr>
 <tr><td><code>POST</code></td><td><code>/api/v1/governance/partner-signals</code></td><td>Read-only operational signals (pilots)</td></tr>
 <tr><td><code>GET</code></td><td><code>/api/v1/governance/scenario-presets/{name}</code></td><td>Shadow demo payloads</td></tr>
 </tbody></table></div>
 <p class="nf-section-lead">Decision semantics (orientation): <code>allow</code> ≈ HTTP 201 · <code>review</code> ≈ 202 · <code>deny</code> ≈ 403 — mapped in evaluate response, not agent proxy.</p>
 </section>
 <section class="nf-section" aria-labelledby="api-intake">
 <div class="nf-section__head"><span class="nf-section__num">02</span><div>
 <p class="nf-section__label" id="api-intake">Public intake</p><h2>Intake and status routes</h2>
 </div></div>
 <div class="nf-prose"><ul>
 <li><code>POST /api/intake</code> — governance brief and partner intakes (RID on every submission)</li>
 <li><code>POST /api/public/chat</code> — site assistant (rate-limited)</li>
 <li><code>GET /api/status</code> — platform summary · <a href="/status/">status page</a></li>
 </ul></div>
 </section>
 <section class="nf-section" aria-labelledby="api-artifacts">
 <div class="nf-section__head"><span class="nf-section__num">03</span><div>
 <p class="nf-section__label" id="api-artifacts">Artifacts</p><h2>Schema and SDK</h2>
 </div></div>
 <div class="nf-proof">
 <a class="nf-proof__item" href="./openapi.json"><span class="nf-proof__icon">JSON</span><div><h3>openapi.json</h3><p>Machine-readable schema</p></div></a>
 <a class="nf-proof__item" href="/console/"><span class="nf-proof__icon">UI</span><div><h3>Governance Console</h3><p>Evaluate interface</p></div></a>
 <a class="nf-proof__item" href="/trust-ledger/"><span class="nf-proof__icon">TLE</span><div><h3>Trust Ledger</h3><p>TLE v1 lifecycle</p></div></a>
 </div>
 </section>""" + mega_cta("Production API keys", "Copilot Governance Pack or Trust Brief — tenant-scoped keys after intake", ("/copilot/pilot/", "Apply for Governance Pack"), ("/status/", "Status")))

    # Gate intake
    gate_body = hero(
        "Engagement intake · Canada",
        "Unified gateway",
        "Request governance engagement",
        "All intake vectors — Trust Brief, Copilot, Bank Pilot, and partner programs — route through a single operational inbox: <strong><a href=\"mailto:operations@noetfield.com\">operations@noetfield.com</a></strong>. Include your footer <strong>Request ID</strong> (<code>RID-…</code>) when you have one.",
        [("Non-confidential", True), ("RID-threaded", False)],
        [("mailto:operations@noetfield.com", "operations@noetfield.com", True), ("/trust-brief/intake/", "Trust Brief intake", False)],
        [],
        receipt("RID-2026-0602-GATE", "Same RID ties intake, evaluate, export."),
    ) + scope_block() + f"""
 <section class="nf-section" aria-labelledby="gate-paths">
 <div class="nf-section__head"><span class="nf-section__num">01</span><div>
 <p class="nf-section__label" id="gate-paths">Choose your path</p><h2>Engagement vectors</h2>
 </div></div>
 <div class="nf-dir-grid">
 <article class="nf-dir-card featured"><p class="meta">Copilot Governance Pack</p><p>$2k–10k · 90 days · board PDF in governance meeting.</p><a class="btn btn-primary" id="giCopilot" href="{PILOT_INTAKE}">Apply for pilot</a></article>
 <article class="nf-dir-card featured"><p class="meta">Trust Brief</p><p>Six-week governance diagnostic — from $10,000.</p><a class="btn btn-secondary" id="giTrustBrief" href="/trust-brief/intake/?vector=trust-brief">Trust Brief intake</a></article>
 <article class="nf-dir-card featured"><p class="meta">Bank Pilot</p><p>Shadow governance evaluation for institutional buyers — read-only simulation only.</p><a class="btn btn-secondary" id="giBankPilot" href="/trust-brief/intake/?vector=bank-pilot&amp;interest=bank-pilot">Bank Pilot intake</a><a class="btn btn-secondary" href="/bank-pilot/">Bank Pilot overview</a></article>
 <article class="nf-dir-card featured"><p class="meta">Work with Noetfield</p><p>Connector · facilitator · co-partner · MSP/SI partner — ecosystem apply.</p><a class="btn btn-primary" id="giWorkWithUs" href="{WORK_WITH_US_INTAKE}">Apply to work with us</a><a class="btn btn-secondary" href="/work-with-us/">Program overview</a></article>
 <article class="nf-dir-card"><p class="meta">Partner programs</p><p>Control layer for banks, credit unions, and licensed partners.</p><a class="btn btn-secondary" href="/partners/">Partners hub</a><a class="btn btn-secondary" id="giPartner" href="/trust-brief/intake/?vector=partner-gateway">Licensed partner intake</a></article>
 <article class="nf-dir-card"><p class="meta">Licensed MSB / PSP</p><p>Control layer before payment APIs — execution stays with you.</p><a class="btn btn-secondary" id="giPartnerMsb" href="/trust-brief/intake/?vector=partner-msb&amp;interest=partner-msb">MSB partner intake</a></article>
 <article class="nf-dir-card"><p class="meta">Licensed exchange / VASP</p><p>Shadow evaluate + read-only signals; partner executes.</p><a class="btn btn-secondary" id="giPartnerExchange" href="/trust-brief/intake/?vector=partner-exchange&amp;interest=partner-exchange">Exchange partner intake</a></article>
 </div>
 </section>""" + mega_cta("Email operations directly", "Include your Request ID if you have one", ("mailto:operations@noetfield.com", "operations@noetfield.com"), (PILOT_INTAKE, "Apply for pilot"))
    write("gate/intake/index.html", "Noetfield — Engagement Intake Gateway",
          "Unified engagement intake for Trust Brief, Copilot, and Bank Pilot.",
          "/gate/intake/",
          gate_body + """
 <script src="/assets/noetfield-intake-email.js" defer></script>
 <script>
 (function () {
   var sp = new URLSearchParams(location.search);
   var vector = sp.get("vector") || sp.get("interest") || "";
   if (vector && sp.get("auto") === "1") {
     sp.set("vector", vector);
     location.replace("/trust-brief/intake/?" + sp.toString());
     return;
   }
   var mail = document.querySelector('a[href^="mailto:operations@noetfield.com"]');
   if (mail && window.noetfieldIntakeMailto) {
     mail.href = window.noetfieldIntakeMailto(
       "Noetfield — Gate intake",
       "Engagement intake via /gate/intake/\\n",
       vector || "gate-intake"
     );
   }
   ["giTrustBrief", "giCopilot", "giBankPilot", "giPartner", "giPartnerMsb", "giPartnerExchange"].forEach(function (id) {
     var el = document.getElementById(id);
     if (!el || !vector) return;
     try {
       var u = new URL(el.href, location.origin);
       u.searchParams.set("vector", vector);
       el.href = u.pathname + "?" + u.searchParams.toString();
     } catch (e) {}
   });
 })();
 </script>""")

    write(
        "ai-automation/index.html",
        "Noetfield — Governance for SMB AI Adoption",
        "Governance-first operating reference for SMB AI adoption — evaluate, RID, TLE, audit-ready export before automation runs.",
        "/ai-automation/",
        ai_automation_body(),
    )

    # Batch-update remaining shell pages CSS only
    old_css = [
        "noetfield-components.css",
        "noetfield-enterprise.css",
        "noetfield-institutional.css",
        "noetfield-sales.css",
    ]
    for path in ROOT.rglob("*.html"):
        if "services/governance" in str(path) or "docs/collateral" in str(path):
            continue
        text = path.read_text(encoding="utf-8")
        if 'id="nfHeader"' not in text:
            continue
        if "noetfield-www.css" in text:
            continue
        # skip already written
        rel = str(path.relative_to(ROOT))
        if rel in {"index.html"} or rel.startswith(("copilot/", "trust-brief/", "enterprise/", "federal/", "msp/", "bank-pilot/", "partners/", "faq/", "contact/", "status/", "privacy/", "terms/", "trust-ledger/", "investors/")):
            continue
        new = text
        for o in old_css:
            new = re.sub(rf'\s*<link rel="stylesheet" href="/assets/{re.escape(o)}[^"]*" />\n?', "", new)
        if "noetfield-www.css" not in new:
            new = new.replace(
                '<link rel="stylesheet" href="/assets/noetfield-shell.css" />',
                '<link rel="stylesheet" href="/assets/noetfield-shell.css" />\n <link rel="stylesheet" href="/assets/noetfield-www.css?v=' + WWW_VER + '" />',
            )
        new = re.sub(r'<body class="[^"]*">', '<body class="nf-www nf-site-v14">', new, count=1)
        new = re.sub(r"<body>", '<body class="nf-www nf-site-v14">', new, count=1)
        new = re.sub(r'noetfield-shell\.js[^"]*', f"noetfield-shell.js?v={WWW_VER}", new)
        new = re.sub(r'noetfield-www\.css\?v=[^"]*', f"noetfield-www.css?v={WWW_VER}", new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print("patched css", rel)


def sync_all_shell_pages() -> None:
    """Ensure every public shell page uses Inter + www v20 assets."""
    ibm = "IBM+Plex"
    for path in ROOT.rglob("*.html"):
        if "services/governance" in str(path) or "docs/collateral" in str(path):
            continue
        text = path.read_text(encoding="utf-8")
        if 'id="nfHeader"' not in text:
            continue
        new = text
        if ibm in new:
            new = re.sub(
                r' <link rel="preconnect" href="https://fonts\.googleapis\.com" />\n'
                r' <link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin />\n'
                r' <link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=[^"]+" />\n?',
                FONT_LINK + "\n",
                new,
            )
        if "fonts.googleapis.com" not in new and "noetfield-tokens.css" in new:
            new = new.replace(
                '<link rel="stylesheet" href="/assets/noetfield-tokens.css" />',
                FONT_LINK + '\n <link rel="stylesheet" href="/assets/noetfield-tokens.css" />',
            )
        new = re.sub(r"noetfield-www\.css\?v=[^\"']+", f"noetfield-www.css?v={WWW_VER}", new)
        new = re.sub(r"noetfield-print\.css\?v=[^\"']+", f"noetfield-print.css?v={WWW_VER}", new)
        new = re.sub(r"noetfield-shell\.js\?v=[^\"']+", f"noetfield-shell.js?v={WWW_VER}", new)
        new = re.sub(r"noetfield-sandbox\.js\?v=[^\"']+", f"noetfield-sandbox.js?v={WWW_VER}", new)
        new = re.sub(r"noetfield-live-proof\.js\?v=[^\"']+", f"noetfield-live-proof.js?v={WWW_VER}", new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print("synced assets", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
    sync_all_shell_pages()
