#!/usr/bin/env python3
"""Regenerate Noetfield GTM www pages — v6 ground-up rebuild."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WWW_VER = "20"

FONT_LINK = (
    ' <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    ' <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    ' <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400..700;1,14..32,400..700&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap" />'
)

SCOPE_LABELS = {
    "shipped": "Available",
    "orientation": "Orientation",
    "roadmap": "Planned",
    "na": "Out of scope",
}

# Commercial narrative — SSOT: docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md · docs/GTM_COPYBOOK.md
COPY = {
    "meta_home": "Govern Copilot execution for regulated buyers — blocked changes, receipted decisions, fail-closed export. Metadata-only M365.",
    "hero_h1": "The audit trail your Copilot deployment will be asked for later",
    "hero_lead": (
        "Noetfield is the <strong>AI Governance &amp; Evidence</strong> layer for Microsoft 365 Copilot — "
        "invalid changes <strong>blocked</strong>, allowed decisions <strong>receipted</strong>, export "
        "<strong>fail closed</strong> on tamper. Metadata-only M365 — complement Purview and Copilot Control System, not replace."
    ),
    "demo_sentence": "Show the record your auditor would accept before Copilot touches production data.",
    "mega_sub": (
        "Non-confidential intake · include your Request ID · Trust Brief ($10k), Copilot pilot ($2k–10k), "
        "federal or MSP lane · operations@noetfield.com"
    ),
    "scope_lead": "Honest scope for procurement — what you can demo, export, and defend today.",
    "footer_note": (
        "AI Governance &amp; Evidence for Microsoft 365 Copilot. Govern execution before production scope opens — "
        "signed TLE v1, board PDF, procurement ZIP. Invalid changes blocked · allowed decisions receipted · export fails closed on tamper."
    ),
    "sandbox_limits": "14-day sandbox · 50 evaluate calls · mock M365 connectors · no sales call",
    "first_receipt_promise": (
        "Run one evaluate · get one signed receipt · <strong>before your next Copilot standup</strong> "
        "(~5 minutes in sandbox)."
    ),
    "closing_competitive": (
        "Your peers roll out Copilot with slides. You roll out with <strong>signed receipts</strong>."
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
 <article class="nf-trial-os__env-tile is-locked"><strong>Production</strong><p>Real metadata index · board PDF · design partner keys.</p><span class="nf-trial-os__lock">🔒 <a href="/copilot/pilot/">Apply to design partner</a></span></article>
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
 <a class="btn btn-secondary" href="/trust-ledger/sample-report/">Download sample export orientation</a>
 </div>
 </div>
 </div>
 <script src="/assets/noetfield-sandbox.js?v={WWW_VER}" defer></script>"""


def sticky_mobile_cta() -> str:
    return """
 <div class="nf-sticky-mobile-cta" aria-label="Quick start">
 <a class="btn btn-primary" href="/start/">Start free sandbox</a>
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
        ("Pre-execution evaluate", "shipped"),
        ("TLE v1 + workspace UI", "shipped"),
        ("Board PDF · procurement ZIP", "shipped"),
        ("M365 metadata connectors", "shipped"),
        ("Framework citations", "orientation"),
        ("Payment rails / MSB execution", "na"),
    ]
    badges = {
        "shipped": "nf-signal-badge--shipped",
        "orientation": "nf-signal-badge--orientation",
        "roadmap": "nf-signal-badge--roadmap",
        "na": "nf-signal-badge--na",
    }
    labels = SCOPE_LABELS
    return "".join(
        f'<div class="nf-trust-signal"><span class="nf-trust-signal-label">{l}</span>'
        f'<span class="nf-signal-badge {badges[k]}">{labels[k]}</span></div>'
        for l, k in items
    )


def scope_block() -> str:
    return f"""
 <section class="nf-trust-signals" aria-labelledby="scope-title">
 <h2 id="scope-title">Available now — capability scope</h2>
 <p class="nf-trust-signals-lead">{COPY["scope_lead"]}</p>
 <div class="nf-trust-signals-grid">{scope_rows_html()}</div>
 </section>"""


def stat_bar() -> str:
    return outcome_stat_bar()


def outcome_stat_bar() -> str:
    return """
 <div class="nf-stat-bar nf-stat-bar--outcome" role="region" aria-label="Outcome metrics">
 <div class="nf-stat-bar-item"><strong>6 wk → 5 min</strong><span>Trust Brief diagnostic vs live evaluate demo</span></div>
 <div class="nf-stat-bar-item"><strong>1 RID</strong><span>Intake → evaluate → export on one thread</span></div>
 <div class="nf-stat-bar-item"><strong>4 exports</strong><span>TLE · board PDF · procurement ZIP · audit</span></div>
 <div class="nf-stat-bar-item"><strong>3 SKUs</strong><span>Contract programs · no catalog creep</span></div>
 </div>"""


def investor_stat_bar() -> str:
    return """
 <div class="nf-stat-bar" role="region" aria-label="Investor metrics">
 <div class="nf-stat-bar-item"><strong>Live</strong><span>Evaluate · TLE · export available</span></div>
 <div class="nf-stat-bar-item"><strong>$10k</strong><span>Trust Brief land wedge</span></div>
 <div class="nf-stat-bar-item"><strong>90d</strong><span>Design partner path</span></div>
 <div class="nf-stat-bar-item"><strong>3</strong><span>Locked SKUs only</span></div>
 </div>"""


def mega_cta(title: str = "Request Governance Brief", sub: str | None = None, primary: tuple[str, str] = ("/trust-brief/intake/", "Request Governance Brief"), secondary: tuple[str, str] | None = ("/copilot/pilot/", "Become a design partner")) -> str:
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
    return """
 <nav class="nf-self-serve-rail" aria-label="Self-serve product access">
 <p class="nf-self-serve-rail__label">Try without a sales call</p>
 <a href="/start/">Developer sandbox</a>
 <a href="/pricing/">Published tiers</a>
 <a href="/docs/api/">Governance API</a>
 <a href="/copilot/demo/">5-minute demo</a>
 <a class="btn btn-primary" href="/start/">Start free sandbox</a>
 </nav>"""


def three_traps_section() -> str:
    return """
 <section class="nf-section-block nf-section--elevated" aria-labelledby="traps-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">!</span><div>
 <p class="nf-eyebrow" id="traps-title">Why governance fails today</p>
 <h2>Three traps before Copilot touches production data</h2>
 <p class="nf-section-lead">Most rollouts stall on policy decks and spreadsheets — not on Microsoft readiness alone.</p>
 </div></div>
 <div class="nf-traps-grid">
 <article class="nf-trap-card"><p class="nf-trap-card__label">Purview-only trap</p><h3>You labeled data. Nobody receipted the go/no-go.</h3><p>Purview readiness is necessary — it is not a signed Copilot execution record your board can defend.</p></article>
 <article class="nf-trap-card"><p class="nf-trap-card__label">Spreadsheet trap</p><h3>Policy lives in SharePoint. Evidence lives in someone&rsquo;s inbox.</h3><p>When audit asks who approved Copilot for production, the thread is gone.</p></article>
 <article class="nf-trap-card"><p class="nf-trap-card__label">Retrofit trap</p><h3>You discover the gap in the audit — not before rollout.</h3><p>Regulators and boards ask <em>after</em> Copilot already touched production data.</p></article>
 </div>
 </section>"""


def buyer_journey_strip() -> str:
    return """
 <nav class="nf-journey-strip" aria-label="Buyer journey — Try Prove Package Trust">
 <a class="nf-journey-step" href="/start/"><span class="nf-journey-step__num">01 · Try</span><strong>Start free sandbox</strong><span>~5 min · first receipt · mock M365</span></a>
 <a class="nf-journey-step" href="/copilot/demo/"><span class="nf-journey-step__num">02 · Prove</span><strong>5-minute demo</strong><span>Evaluate → confidence score → export</span></a>
 <a class="nf-journey-step" href="/pricing/"><span class="nf-journey-step__num">03 · Package</span><strong>Published tiers</strong><span>Sandbox · design partner · 3 SKUs</span></a>
 <a class="nf-journey-step" href="/trust/"><span class="nf-journey-step__num">04 · Trust</span><strong>Trust center</strong><span>Procurement pack · verify export</span></a>
 </nav>"""


def governance_output_suite() -> str:
    return """
 <section class="nf-section-block" aria-labelledby="export-suite-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">↗</span><div>
 <p class="nf-eyebrow" id="export-suite-title">Governance Output Suite</p>
 <h2>One evaluate · four exports</h2>
 <p class="nf-section-lead">Buyers file artifacts — not API access alone. Same spine from sandbox to production tenant.</p>
 </div></div>
 <div class="nf-export-suite" role="list">
 <article class="nf-export-suite__item" role="listitem"><span class="nf-export-suite__icon">TLE</span><h3>TLE v1 YAML</h3><p>Signed decision · confidence score · approval chain · evidence index.</p></article>
 <article class="nf-export-suite__item" role="listitem"><span class="nf-export-suite__icon">PDF</span><h3>Board PDF</h3><p>Executive-ready digest for governance and budget conversations.</p></article>
 <article class="nf-export-suite__item" role="listitem"><span class="nf-export-suite__icon">ZIP</span><h3>Procurement ZIP</h3><p>Buyer diligence bundle · fail-closed integrity on tamper.</p></article>
 <article class="nf-export-suite__item is-roadmap" role="listitem"><span class="nf-export-suite__icon">API</span><h3>Audit export <span class="nf-signal-badge nf-signal-badge--roadmap">Planned</span></h3><p>Tenant audit bundle · SIEM / GRC webhooks — planned capability, orientation only.</p></article>
 </div>
 </section>"""


def contrast_table_section() -> str:
    return """
 <section class="nf-section-block" aria-labelledby="contrast-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">⇄</span><div>
 <p class="nf-eyebrow" id="contrast-title">Why Noetfield</p>
 <h2>What you tried vs what breaks vs what Noetfield delivers</h2>
 <p class="nf-section-lead">Self-sort in one table — built for CISO, GRC, and procurement reviewers.</p>
 </div></div>
 <div class="nf-contrast-table-wrap">
 <table class="nf-contrast-table">
 <thead><tr><th>Approach</th><th>What breaks</th><th>Noetfield</th></tr></thead>
 <tbody>
 <tr><td>Purview + policy deck only</td><td>No signed execution receipt per go/no-go</td><td>TLE v1 + confidence score on every decision</td></tr>
 <tr><td>Spreadsheet + email approvals</td><td>No tamper-evident export for diligence</td><td>Board PDF + procurement ZIP · fail closed on tamper</td></tr>
 <tr><td>Enterprise GRC platform rollout</td><td>Slow · expensive · not Copilot-native</td><td>Metadata-only M365 · evaluate in minutes</td></tr>
 <tr><td>Consultant PDF once</td><td>Static · ages before next rollout wave</td><td>Live evaluate + export cadence per tenant</td></tr>
 </tbody>
 </table>
 </div>
 </section>"""


def fit_qualification_body() -> str:
    return """
 <div class="nf-fit-grid">
 <article class="nf-fit-card nf-fit-card--yes"><h3>This is for you if</h3><ul>
 <li>You are rolling out or scaling <strong>Microsoft 365 Copilot</strong> under legal or procurement scrutiny</li>
 <li>You need <strong>metadata-only</strong> M365 evidence — no mailbox custody</li>
 <li>You want <strong>honest scope</strong> — Available · Planned · Out of scope badges, not certifier claims</li>
 <li>You need a receipt your <strong>board and auditor</strong> can inspect before production scope opens</li>
 </ul></article>
 <article class="nf-fit-card nf-fit-card--no"><h3>This is not for you if</h3><ul>
 <li>You need payment rails, custody, MSB execution, or transaction processing</li>
 <li>You want full mailbox/content surveillance — we index metadata only</li>
 <li>You need ISO/SOC <strong>certification</strong> from us — we produce governance artifacts, not company certification</li>
 <li>You want a generic AI chatbot catalog — three contract SKUs only</li>
 </ul></article>
 </div>"""


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
 <a class="btn btn-primary" href="/start/">Start sandbox</a>
 </article>
 <article class="nf-pack-card nf-pack-card--program" role="listitem">
 <p class="nf-pack-card__tag">Named program · apply online</p>
 <p class="nf-pack-card__price">$2k–10k</p>
 <p>Copilot Governance Pack design partner — production tenant, board PDF in governance meeting, procurement ZIP.</p>
 <ul><li>90-day program</li><li>Production mode</li><li>API keys per engagement</li></ul>
 <a class="btn btn-primary" href="/copilot/pilot/">Apply to design partner</a>
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
 <p class="nf-section-lead">Three contract SKUs only — free sandbox is product access, not a retail SKU. Upgrade path: sandbox → design partner → Trust Brief or enterprise SOW.</p>"""


def agentic_autonomous_section() -> str:
    return """
 <section class="nf-section-block nf-section--elevated" aria-labelledby="agentic-title">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">A</span><div>
 <p class="nf-eyebrow" id="agentic-title">Agentic governance</p>
 <h2>Fully agentic workflows — not AI assist alone</h2>
 <p class="nf-section-lead">Governance agents execute investigate → triage → draft → act on policy-bounded paths. High-risk Copilot go/no-go stays with named human approvers; low-risk allows auto-record to signed TLE when policy permits.</p>
 </div></div>
 <div class="nf-agentic-grid">
 <article class="nf-agentic-step"><strong>Investigate</strong><p>Agent pulls M365 metadata gaps — Purview labels, Entra CA, audit indices — before rollout sign-off.</p></article>
 <article class="nf-agentic-step"><strong>Triage</strong><p>Confidence score and policy rules route allow, review, or deny — same semantics as <code>POST /evaluate</code>.</p></article>
 <article class="nf-agentic-step"><strong>Draft TLE</strong><p>Agent prepares Trust Ledger Entry YAML, approval chain, and evidence index for human sign-off.</p></article>
 <article class="nf-agentic-step"><strong>Act on low-risk</strong><p>Pre-approved policy paths auto-record sandbox evaluates; production requires design partner keys and approver chain.</p></article>
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


def ciso_strip() -> str:
    cards = [
        ("Metadata-only M365", "Purview · Entra · audit indices — evidence index on every TLE, no mailbox custody.", "shipped", SCOPE_LABELS["shipped"]),
        ("Fail-closed export", "Board PDF and procurement ZIP fail verification when tampered — by design.", "shipped", SCOPE_LABELS["shipped"]),
        ("Canada trust posture", "Data handling and GC buyer notes for regulated procurement.", "orientation", SCOPE_LABELS["orientation"]),
        ("SOC 2 Type II", "Independent audit planned — not yet completed.", "roadmap", SCOPE_LABELS["roadmap"]),
        ("SSO / SAML", "Enterprise IdP for console access — planned product capability.", "roadmap", SCOPE_LABELS["roadmap"]),
        ("No custody rails", "No payment execution, MSB, asset custody, or money-transmission claims.", "na", SCOPE_LABELS["na"]),
    ]
    badges = {
        "shipped": "nf-signal-badge--shipped",
        "orientation": "nf-signal-badge--orientation",
        "roadmap": "nf-signal-badge--roadmap",
        "na": "nf-signal-badge--na",
    }
    items = "".join(
        f'<article class="nf-ciso-card"><h3>{h}</h3><p>{p}</p>'
        f'<span class="nf-signal-badge {badges[k]}">{label}</span></article>'
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
    """UI-03 four-act homepage — Try · Prove · Package · Trust (+ Wave 1 conversion blocks)."""
    act_try = f"""
 <section class="nf-section-block nf-act-try" aria-labelledby="act-try">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="act-try">Try</p>
 <h2 class="nf-sr-only">Try evaluate — governance playground</h2>
 </div></div>
""" + hero(
        "Governance execution · Canada",
        "AI Governance &amp; Evidence · Microsoft 365 Copilot",
        COPY["hero_h1"],
        COPY["hero_lead"],
        [("First receipt · ~5 min", True), ("Trust Ledger · TLE v1", True), ("No custody · no payment rails", False)],
        [("/start/", "Start free sandbox", True), ("/copilot/demo/", "5-minute demo", False), ("/trust-brief/intake/", "Request Governance Brief", False)],
        ["NIST AI RMF", "ISO-style evidence", "Microsoft Purview", "RPAA-safe vendor"],
        live_proof_panel(),
        h1_class="nf-hero-h1--wide",
    ).replace(
        '<p class="nf-lead">',
        f'<p class="nf-first-receipt-promise">{COPY["first_receipt_promise"]}</p>\n <p class="nf-lead">',
        1,
    ) + stat_bar() + buyer_journey_strip() + three_traps_section() + self_serve_rail() + "\n </section>"

    act_prove = f"""
 <section class="nf-section-block nf-act-prove" aria-labelledby="act-prove">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="act-prove">Prove</p>
 <h2>The moment Copilot becomes auditable</h2>
 <p class="nf-section-lead">{COPY["demo_sentence"]} · Execution receipts for Copilot operational decisions — complement the <strong>Copilot Control System</strong>, not replace Purview.</p>
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
 {governance_output_suite()}
 <p class="nf-section-lead" style="margin-top:20px"><a href="/copilot/">What buyers ask</a> · extended FAQ · stack complement · category map on the Copilot hub.</p>
 </section>"""

    act_package = f"""
 <section class="nf-section-block nf-act-package" aria-labelledby="act-package">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">03</span><div>
 <p class="nf-eyebrow" id="act-package">Package</p>
 <h2>Published tiers — sandbox to contract</h2>
 <p class="nf-section-lead">Start free in developer sandbox, apply to the design partner program, or buy a locked contract SKU — same evaluate → TLE → export spine.</p>
 </div></div>
 {contrast_table_section()}
 {packaging_tiers_grid(compact=True)}
 <p class="nf-section-lead"><a href="/pricing/">See all tiers</a> · Sandbox + production modes · three contract SKUs only.</p>
 </section>
 {agentic_autonomous_section()}
 <section class="nf-section-block" aria-labelledby="act-offerings">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">—</span><div>
 <p class="nf-eyebrow" id="act-offerings">Contract programs</p>
 <h2>Three SKUs — locked scope</h2>
 </div></div>
 {offerings_three_skus()}
 </section>"""

    act_trust = f"""
 <section class="nf-section-block nf-act-trust" aria-labelledby="act-trust">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">04</span><div>
 <p class="nf-eyebrow" id="act-trust">Trust</p>
 <h2>Procurement diligence — honest scope</h2>
 <p class="nf-section-lead">For you / not for you · trust center · export verification.</p>
 </div></div>
 {fit_qualification_body()}
 {procurement_rail()}
 {ciso_strip()}
 {scope_block()}
 {closing_competitive_line()}
 </section>
""" + mega_cta() + sticky_mobile_cta()

    return act_try + act_prove + act_package + act_trust


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
    return """
 <div class="nf-offerings-v5">
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Trust Brief</p><p class="price">$10,000 · 6 weeks</p><p>Governance audit, AI policy mapping, and risk exposure analysis — board-ready executive summary before Copilot scale.</p><a class="btn btn-primary" href="/trust-brief/">Trust Brief</a></article>
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Copilot Governance Pack</p><p class="price">$2k–10k · 90 days</p><p>Enterprise AI compliance layer for M365 Copilot — live TLE records, board PDF, and procurement ZIP on every go/no-go.</p><a class="btn btn-primary" href="/copilot/">Copilot Pack</a></article>
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
 <p class="nf-category-map__note">Noetfield complements Microsoft Copilot Control System and partner readiness work — we receipt <strong>operational go/no-go decisions</strong> with signed TLE export. Metadata-only M365 · Evaluate · Record · Export.</p>"""


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
 <p class="nf-section-lead">We produce the signed governance record when your team decides Copilot may execute in production — complement Purview and the Copilot Control System, not replace them.</p>
 </div></div>
 {stack_complement_block()}
 </section>"""
    faq_items = [
        ("What does Noetfield receipt?", "Copilot execution go/no-go with signed TLE export, confidence score, and M365 metadata evidence index — Evaluate · Decide · Record · Export before production scope opens."),
        ("How does Noetfield fit with Purview and Copilot Control System?", "We complement Microsoft readiness and control tooling — not replace. Metadata-only connectors index Purview · Entra · audit on every TLE; Phase 2 records operational decisions after tenant readiness."),
        ("How does TLE support audit and procurement?", "TLE v1 bundles decision, confidence score, evidence index, and <strong>export_integrity: fail closed on tamper</strong> — board PDF and procurement ZIP ready for institutional diligence."),
        ("Are you SOC 2 or ISO certified?", "We do not claim SOC 2 or ISO certification today. See <a href=\"/trust/\">Trust &amp; security</a> for our Available · Planned · Out of scope posture. We produce governance artifacts, not company certification."),
        ("What is the entry price?", "Trust Brief $10,000 · 6 weeks. Copilot Governance Pack $2k–10k · 90-day design partner. Bank Pilot custom — three contract SKUs only."),
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
        ("TLE v1 + workspace", "shipped"),
        ("Export integrity fail-closed", "shipped"),
        ("M365 metadata-only processing", "shipped"),
        ("Board PDF + procurement ZIP", "shipped"),
        ("SOC 2 Type II", "roadmap"),
        ("ISO 27001 / 42001 certification", "na"),
        ("Ed25519 / Merkle transparency log", "roadmap"),
    ]
    badges = {"shipped": "nf-signal-badge--shipped", "roadmap": "nf-signal-badge--roadmap", "na": "nf-signal-badge--na"}
    labels = SCOPE_LABELS
    cert_html = "".join(
        f'<div class="nf-trust-signal"><span class="nf-trust-signal-label">{l}</span>'
        f'<span class="nf-signal-badge {badges[k]}">{labels[k]}</span></div>'
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
""" + mega_cta("Request Governance Brief", "Procurement diligence · pilot export walkthrough")


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
 <section><h2>Sandbox and production</h2><p>Free sandbox uses mock connectors and sample limits. Production evaluate, workspace, and export require a design partner or Trust Brief engagement.</p></section>
 <section><h2>Contact</h2><p>Terms questions: <a href="mailto:operations@noetfield.com">operations@noetfield.com</a></p></section>
 </div>""",
        "status": """
 <div class="nf-prose">
 <section><h2>Public website</h2><p>Marketing pages, sandbox signup, pricing, and buyer documentation are available.</p></section>
 <section><h2>Workspace and evaluate API</h2><p>Sandbox evaluate and workspace are available for self-serve trial. Production API keys and tenant-scoped evaluate are provisioned per design partner or Trust Brief SOW.</p></section>
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
        "Developer sandbox · Canada",
        "Self-serve · no sales call",
        START_H1,
        "Create a free developer sandbox, open the Governance Console, and run evaluate → TLE → export with mock M365 connectors — "
        "<strong>before</strong> a Trust Brief or design partner conversation.",
        [("14-day trial", True), ("50 evaluate calls", False), ("Sandbox mode", False)],
        [("#trial-os", "Start sandbox", True), ("/copilot/demo/", "5-minute demo", False)],
        ["POST /evaluate", "Mock OAuth", "TLE samples"],
        workspace_mock("Sandbox · evaluate"),
    ) + self_serve_rail() + f"""
 <section class="nf-section-block" id="trial-os" aria-labelledby="start-trial">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="start-trial">Trial OS</p>
 <h2>Full self-serve flow — no calendar required</h2>
 <p class="nf-section-lead">Sandbox mode · mock M365 · evaluate API · sample export — {COPY["sandbox_limits"]}.</p>
 </div></div>
 {trial_os_wizard()}
 <aside class="nf-callout"><p><strong>Sandbox vs production:</strong> Sandbox uses mock connectors and local evaluate limits. Production mode unlocks via <a href="/copilot/pilot/">design partner program</a> or Trust Brief engagement.</p></aside>
 </section>
 {fit_qualification_section()}
 {agentic_autonomous_section()}
""" + packaging_tiers_grid(compact=True) + mega_cta("Upgrade to design partner", "Production keys · real M365 metadata · board PDF in governance meeting", ("/copilot/pilot/", "Apply to design partner"), ("/pricing/", "Compare tiers"))


def pricing_page_body() -> str:
    return hero(
        "Published tiers · Canada",
        "Access paths + contract programs",
        "Packaged offering — sandbox, program, and contract SKUs",
        "Transparent packaging like enterprise governance buyers expect: <strong>free developer sandbox</strong>, "
        "<strong>named design partner program</strong>, and <strong>three locked contract SKUs</strong> — no catalog creep.",
        [("Sandbox free", True), ("14-day trial", False), ("3 contract SKUs", False)],
        [("/start/", "Start free sandbox", True), ("/trust-brief/intake/", "Request Governance Brief", False)],
        ["Sandbox", "Production", "Enterprise"],
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
 <div class="nf-table-wrap" style="margin-top:20px"><table class="nf-table nf-tier-table"><thead><tr><th>Capability</th><th>Sandbox (free)</th><th>Production (design partner)</th></tr></thead><tbody>
 <tr><td>Evaluate API</td><td>50 calls / 14 days</td><td>Per SOW · tenant-scoped keys</td></tr>
 <tr><td>M365 connectors</td><td>Mock OAuth</td><td>Metadata-only Purview · Entra · audit</td></tr>
 <tr><td>TLE export</td><td>Sample YAML + orientation PDF</td><td>Board PDF + procurement ZIP</td></tr>
 <tr><td>Agentic workflows</td><td>Investigate · triage · draft (sandbox)</td><td>Full chain + named approvers</td></tr>
 <tr><td>Sales call required</td><td>No</td><td>Program intake · SOW</td></tr>
 </tbody></table></div>
 </section>
""" + contrast_table_section() + section_block("02", "Tiers", "Access paths and contract programs", packaging_tiers_grid(compact=True), "Free sandbox is developer access — not a fourth contract SKU.") + mega_cta()


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
        [("/trust-brief/intake/", "Request Governance Brief", True), ("/copilot/", "Copilot Governance Pack", False)],
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
        """
 <section class="nf-section-block" aria-labelledby="aa-01">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="aa-01">Commercial lock</p>
 <h2>Three contract SKUs only</h2>
 <p class="nf-section-lead">Trust Brief · Copilot Governance Pack · Bank Pilot. This page orients automation buyers to the Copilot Pack — it is not a separate product line.</p>
 </div></div>
 <div class="nf-offerings-v5">
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Trust Brief</p><p class="price">$10,000</p><p>Governance diagnostic before automation or Copilot scale — policy map and risk exposure for executive sign-off.</p><a class="btn btn-primary" href="/trust-brief/">Trust Brief</a></article>
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Copilot Governance Pack</p><p class="price">$2k–10k pilot</p><p>Receipt Copilot and workflow go/no-go decisions with signed TLE export — not a bot catalog.</p><a class="btn btn-primary" href="/copilot/">Copilot Pack</a></article>
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
          "Published tiers: free developer sandbox, design partner program, Trust Brief and Bank Pilot contract SKUs.",
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
          hub_page("Trust Brief · $10,000 fixed", "Six-week governance diagnostic",
                   "Know your AI governance exposure before the board asks",
                   "Fixed-scope Trust Brief: governance audit, AI policy mapping, and risk exposure analysis — executive summary your board and procurement can act on before Copilot pilot sign-off.",
                   [("$10,000 fixed", True), ("6 weeks", False), ("Board-ready output", False)],
                   [("/trust-brief/intake/", "Request Governance Brief", True), ("/copilot/demo/", "5-minute demo", False)],
                   ["NIST AI RMF", "Executive summary", "AI policy map"],
                   panel("Deliverables", ["Governance audit report", "AI policy mapping", "Risk exposure analysis", "Executive summary for board"]),
                   """
 <section class="nf-section nf-section--lift"><div class="nf-section__head"><span class="nf-section__num">01</span><div>
 <p class="nf-section__label">Entry SKU</p><h2>Trust Brief before Copilot pilot</h2>
 <p class="nf-section__lead">Most buyers start here — then attach Copilot Governance Pack when production rollout needs receipts.</p>
 </div></div>
 <div class="nf-cards">
 <article class="nf-card nf-card--gold"><p class="nf-card__tag">Fixed scope</p><h3>$10,000 · 6 weeks</h3><p>No SKU creep — governance diagnostic only.</p></article>
 <article class="nf-card"><p class="nf-card__tag">Output</p><h3>Board-ready summary</h3><p>Policy gaps, risk exposure, recommended pilot scope.</p></article>
 <article class="nf-card"><p class="nf-card__tag">Next step</p><h3>Copilot Governance Pack</h3><p>$2k–10k pilot with live TLE records.</p></article>
 </div></section>"""))

    # Copilot hub
    write("copilot/index.html", "Noetfield — Copilot Governance Pack",
          "AI Governance & Evidence layer for Microsoft 365 Copilot — signed TLE v1 and board-ready export.",
          "/copilot/",
          hub_page("Copilot Governance Pack", "Microsoft 365 Copilot · governance execution",
                   "The audit trail your Copilot deployment will be asked for later",
                   "Noetfield governs Copilot execution — evaluate operational intent, index M365 metadata evidence, and produce signed Trust Ledger Entries your board, auditor, and procurement can defend. Complement Purview and Copilot Control System, not replace.",
                   [("TLE v1 signed records", True), ("Purview · Entra · SharePoint", False)],
                   [("/copilot/demo/", "5-minute demo", True), ("/copilot/pilot/", "Design-partner pilot", False), ("/copilot/procurement/", "Procurement pack", False)],
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
         "Walk through evaluate → receipt → export with Purview, Entra ID, and SharePoint metadata. Demo script (locked narrative) — confidence score on every decision. Complement Copilot Control System — not replace.",
         [("Live demo script", True), ("Confidence score", False)],
         [("/workspace/", "Open workspace", True), ("/copilot/procurement/", "Procurement pack", False)],
         workspace_mock("Live workspace path")),
        ("copilot/procurement/index.html", "Noetfield — Copilot Procurement Pack", "Buyer diligence ZIP, NIST AI RMF citations, procurement export.", "/copilot/procurement/",
         "Procurement pack", "Buyer diligence · ZIP export",
         "Procurement-grade export for Copilot governance diligence",
         "Framework citations, vendor scope boundaries, and sample TLE artifacts — the buyer pack institutional buyers request before pilot sign-off. See <a href=\"/trust/\">Trust center</a> for honest cert posture.",
         [("NIST AI RMF", True), ("ZIP export", False), ("Trust center", False)],
         [("/trust-brief/intake/", "Request Governance Brief", True), ("/trust/", "Trust &amp; security", False)],
         receipt("RID-2026-0602-PROC", "Orientation sample — request pack via intake.")),
        ("copilot/sme/index.html", "Noetfield — SME Governance Pack", "SME Copilot governance pack for CISO, GRC, and procurement.", "/copilot/sme/",
         "SME Governance Pack", "Mid-market · Copilot governance",
         "Governance pack sized for SME Copilot rollouts",
         "Same TLE v1 lifecycle as enterprise — confidence score, approval chain, and export scoped for teams that need signed receipts at pilot scale.",
         [("90-day design partner", True), ("TLE v1", False)],
         [("/copilot/pilot/", "Become a design partner", True), ("/copilot/demo/", "5-minute demo", False)],
         panel("SME buyer path", ["Trust Brief or direct pilot intake", "Purview metadata connectors", "Board PDF + procurement ZIP", "Workspace for TLE drafts"])),
        ("copilot/pilot/index.html", "Copilot Pilot — Design Partner | Noetfield", "90-day Copilot governance pilot, board PDF, procurement ZIP.", "/copilot/pilot/",
         "Design partner program", "Copilot Governance Pack · Pilot",
         "Design-partner Go/No-Go path",
         "Run the documented pilot: evaluate intent, index evidence, produce a signed TLE, and export a board pack for procurement.",
         [("90-day program", True), ("Pilot $2k–10k", False)],
         [("/trust-brief/intake/?interest=pilot", "Become a design partner", True), ("/copilot/demo/", "5-minute demo", False)],
         panel("Success signals", ["One referenceable org · board PDF in real meeting", "Approved TLE with confidence score", "M365 metadata evidence connected", "Procurement ZIP delivered"])),
    ]
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
                   [("/trust-brief/intake/?source=enterprise", "Request Governance Brief", True), ("/console/", "Governance Console", False)],
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
 <aside class="nf-callout"><p><strong>Scope:</strong> Unclassified information only. Noetfield complements Purview and departmental AIA workflows — <strong>not a federal certifier</strong>.</p></aside>
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
                   "Programs for banks, credit unions, and supervised firms: evaluate operational intent, record Trust Ledger evidence, return allow or deny.",
                   [("Governance evaluate", True), ("Trust Ledger export", False)],
                   [("/gate/partners/intake/", "Partner intake", True), ("/msp/", "MSP lane", False)],
                   [],
                   panel("What partners get", ["Governance evaluate — shadow then enforce", "Trust Ledger — RID-keyed audit export", "Decision webhooks — SIEM / GRC hooks", "HTTP contracts: Governance API"]),
                   """
 <section class="nf-section"><div class="nf-cards">
 <a class="nf-card nf-card--link" href="/docs/api/"><p class="nf-card__tag">API</p><h3>Governance API</h3><p>OpenAPI + evaluate routes.</p></a>
 <a class="nf-card nf-card--link" href="/msp/"><p class="nf-card__tag">MSP</p><h3>MSP partners</h3><p>Readiness → Record.</p></a>
 </div></section>"""))

    # FAQ
    write("faq/index.html", "Noetfield — FAQ",
          "Frequently asked questions about Noetfield AI Governance & Evidence for Microsoft 365 Copilot.",
          "/faq/",
          hero("FAQ", "Quick answers", "Frequently asked questions",
               "Use the assistant (bottom-right) or read below.",
               [], [("/trust-brief/intake/", "Request Governance Brief", True)], [],
               panel("Start here", ["Trust Brief · $10k", "5-minute demo", "Procurement pack", "Request Governance Brief"])) + """
 <div class="nf-prose">
 <section><h2>What is Noetfield?</h2><p>AI Governance &amp; Evidence for Microsoft 365 Copilot — evaluate operational intent before execution, with signed Trust Ledger records and fail-closed export. No custody or payment execution.</p></section>
 <section><h2>What do you offer?</h2><p>Three contract SKUs only: Trust Brief ($10k · 6 weeks), Copilot Governance Pack ($2k–10k · 90-day design partner), Bank Pilot (custom shadow simulation).</p></section>
 <section><h2>Do you replace Microsoft Purview?</h2><p>No. We complement Purview and Copilot Control System — metadata-only evidence index and signed Copilot governance receipts.</p></section>
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
               "All contract offerings route through governance brief intake or operations@noetfield.com.",
               [], [("/trust-brief/intake/", "Request Governance Brief", True), ("mailto:operations@noetfield.com", "operations@noetfield.com", False)], [],
               panel("Routing", ["Trust Brief · Copilot pilot · Federal · MSP", "operations@noetfield.com", "Non-confidential intake only"])) + mega_cta())

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
              [("Demo-ready product", True), ("Accepting design partners", True), ("No custody · no MSB", False)],
              [("/copilot/demo/", "5-minute demo", True), ("mailto:operations@noetfield.com?subject=Investor%20brief", "Investor inquiry", False)],
              ["Land · Expand · Channel", "Design partner ≥ CAD 2K", "Metadata-only M365"],
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
 <p class="nf-section-lead">Boards and procurement ask for defensible go/no-go records when Copilot touches production data. Noetfield delivers pre-execution evaluate, signed TLE records, and board PDF export — complementing Purview readiness.</p>
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
 <p class="meta">Land · Trust Brief</p>
 <p class="price">$10,000 · 6 weeks</p>
 <p>Fixed-scope governance diagnostic — policy map, risk exposure, executive summary. Opens CIO conversation with board-ready output.</p>
 <a class="btn btn-primary" href="/trust-brief/">Trust Brief</a>
 </article>
 <article class="nf-offer-card nf-offer-card--featured">
 <p class="meta">Expand · Copilot Governance Pack</p>
 <p class="price">$2k–10k · 90 days</p>
 <p>Design partner: live TLE records, confidence score, board PDF in governance meeting — then expand seats and export cadence.</p>
 <a class="btn btn-primary" href="/copilot/pilot/">Design partner</a>
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
 <h2>Available now vs what capital accelerates</h2>
 <p class="nf-section-lead">No fake traction. Product converts in a 5-minute demo — economic proof is a contracted pilot and referenceable board PDF.</p>
 </div></div>
 <div class="nf-trust-signals-grid">
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Governance evaluate + TLE v1 + workspace</span><span class="nf-signal-badge nf-signal-badge--shipped">Available</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Board PDF + procurement ZIP export</span><span class="nf-signal-badge nf-signal-badge--shipped">Available</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">M365 metadata evidence index</span><span class="nf-signal-badge nf-signal-badge--shipped">Available</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">First org: TLE in production + board PDF in meeting</span><span class="nf-signal-badge nf-signal-badge--orientation">Target</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Design partner LOI / deposit ≥ CAD 2K</span><span class="nf-signal-badge nf-signal-badge--orientation">Target</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Governance Monitor MRR · tenant refresh</span><span class="nf-signal-badge nf-signal-badge--roadmap">Roadmap</span></div>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-05">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">05</span><div>
 <p class="nf-eyebrow" id="inv-05">90-day path to reference</p>
 <h2>Design partner program — week-by-week proof</h2>
 <p class="nf-section-lead">Commercial path from first demo to contracted design partner. Capital maps to running this playbook in parallel across 3–5 design-partner conversations.</p>
 </div></div>
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 0–2</p><h3>Demo + CIO contact</h3><p>5-minute demo live · qualified CIO engagement · confidence score visible.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 3–6</p><h3>Pilot SOW + evidence</h3><p>M365 metadata connected · first TLE v1 approved in workspace.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 7–10</p><h3>Board PDF in meeting</h3><p>Referenceable governance artifact — partner success signal for expand.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 11–12</p><h3>LOI / deposit ≥ CAD 2K</h3><p>Contracted design partner deposit · expand seats or MSP attach conversation.</p></article>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-06">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">06</span><div>
 <p class="nf-eyebrow" id="inv-06">Use of capital</p>
 <h2>Bottleneck is distribution and buyer proof — not product invention</h2>
 </div></div>
 <div class="nf-outcome-grid">
 <article class="nf-outcome-card nf-outcome-card--approved"><p class="nf-outcome-label">Acquire</p><h3>Design-partner pipeline</h3><p>Targeted outreach to CISO and GRC leaders at Copilot rollouts — Trust Brief land wedge in Canada.</p></article>
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
 <article class="nf-outcome-card"><p class="nf-outcome-label">Integration</p><h3>Metadata-only M365</h3><p>Purview · Entra · audit evidence index — complement Microsoft stack.</p></article>
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

 <aside class="nf-callout"><p><strong>Investor honesty:</strong> We do not claim ISO/SOC certification, custody, payment rails, or MSB execution. We do not inflate ARR or logo count. Product is shipped and demoable today — capital accelerates <strong>first contracted design partner</strong> and <strong>referenceable board PDF</strong> on the three locked SKUs.</p></aside>
"""
          + mega_cta(
              "Investor or design-partner conversation",
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
              "Submit operational intent, receive an allow or deny decision, and review the compliance log — start in <a href=\"/start/\">free sandbox</a> or open your design partner host.",
              [("Sandbox · free", True), ("RID-threaded", False)],
              [("/start/", "Start free sandbox", True), ("/cognitive-dashboard/", "Open console", False)],
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
              "<strong>Start in sandbox</strong> without a sales call — production keys via design partner program.",
              [("OpenAPI", True), ("Sandbox + production", False)],
              [("/start/", "Start free sandbox", True), ("/trust-brief/intake/?interest=api-pilot&source=api-docs", "Request production keys", False)],
              [],
              receipt("RID-2026-0602-API", "Evaluate → ledger → export routes available in sandbox and production."),
          ) + scope_block() + """
 <section class="nf-section nf-section--lift" aria-labelledby="api-sandbox">
 <div class="nf-section__head"><span class="nf-section__num">00</span><div>
 <p class="nf-section__label" id="api-sandbox">Developer sandbox</p><h2>Try without a sales call</h2>
 <p class="nf-section__lead">""" + COPY["sandbox_limits"] + """ · mock M365 · same evaluate semantics as production.</p>
 </div></div>
 <p><a class="btn btn-primary" href="/start/">Start free sandbox</a> · <a href="/pricing/">Compare tiers</a></p>
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
 </section>""" + mega_cta("Production API keys", "Design partner program or Trust Brief — tenant-scoped keys after intake", ("/copilot/pilot/", "Apply to design partner"), ("/status/", "Status")))

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
    ) + scope_block() + """
 <section class="nf-section" aria-labelledby="gate-paths">
 <div class="nf-section__head"><span class="nf-section__num">01</span><div>
 <p class="nf-section__label" id="gate-paths">Choose your path</p><h2>Engagement vectors</h2>
 </div></div>
 <div class="nf-dir-grid">
 <article class="nf-dir-card featured"><p class="meta">Trust Brief</p><p>Six-week governance diagnostic — from $10,000.</p><a class="btn btn-primary" id="giTrustBrief" href="/trust-brief/intake/?vector=trust-brief">Trust Brief intake</a></article>
 <article class="nf-dir-card featured"><p class="meta">Copilot Governance Pack</p><p>Microsoft 365 Copilot policy alignment and compliance layer.</p><a class="btn btn-primary" id="giCopilot" href="/trust-brief/intake/?vector=copilot-governance&amp;interest=copilot">Copilot intake</a></article>
 <article class="nf-dir-card featured"><p class="meta">Bank Pilot</p><p>Shadow governance evaluation for institutional buyers — read-only simulation only.</p><a class="btn btn-secondary" id="giBankPilot" href="/trust-brief/intake/?vector=bank-pilot&amp;interest=bank-pilot">Bank Pilot intake</a><a class="btn btn-secondary" href="/bank-pilot/">Bank Pilot overview</a></article>
 <article class="nf-dir-card"><p class="meta">Partner programs</p><p>Control layer for banks, credit unions, and licensed partners.</p><a class="btn btn-secondary" href="/partners/">Partners hub</a><a class="btn btn-secondary" id="giPartner" href="/trust-brief/intake/?vector=partner-gateway">Partner intake</a></article>
 <article class="nf-dir-card"><p class="meta">Licensed MSB / PSP</p><p>Control layer before payment APIs — execution stays with you.</p><a class="btn btn-secondary" id="giPartnerMsb" href="/trust-brief/intake/?vector=partner-msb&amp;interest=partner-msb">MSB partner intake</a></article>
 <article class="nf-dir-card"><p class="meta">Licensed exchange / VASP</p><p>Shadow evaluate + read-only signals; partner executes.</p><a class="btn btn-secondary" id="giPartnerExchange" href="/trust-brief/intake/?vector=partner-exchange&amp;interest=partner-exchange">Exchange partner intake</a></article>
 </div>
 </section>""" + mega_cta("Email operations directly", "Include your Request ID if you have one", ("mailto:operations@noetfield.com", "operations@noetfield.com"), ("/trust-brief/intake/", "Request Governance Brief"))
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
