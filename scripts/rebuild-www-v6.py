#!/usr/bin/env python3
"""Regenerate Noetfield GTM www pages — v6 ground-up rebuild."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
 <meta charset="UTF-8" />
 <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>{title}</title>
 <meta name="description" content="{desc}" />
 <meta name="robots" content="index,follow" />
 <meta name="theme-color" content="#07070b" />
 <link rel="canonical" href="https://www.noetfield.com{canonical}" />
 <link rel="icon" href="/noetfield-favicon-512.png" type="image/png" />
 <link rel="stylesheet" href="/assets/noetfield-tokens.css" />
 <link rel="stylesheet" href="/assets/noetfield-shell.css" />
 <link rel="stylesheet" href="/assets/noetfield-www.css?v=10" />
 <script src="/assets/noetfield-shell.js?v=10" defer></script>
</head>
<body class="nf-www nf-site-v5">
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
 <aside class="nf-receipt-mock" aria-label="Trust Ledger Entry receipt">
 <div class="nf-receipt-mock-header">
 <p class="nf-receipt-mock-title">Trust Ledger Entry · v1</p>
 <span class="nf-receipt-mock-status">Verified</span>
 </div>
 <dl class="nf-receipt-mock-body">
 <div class="nf-receipt-row"><dt>tle_id</dt><dd>TLE-015DCFB8B953</dd></div>
 <div class="nf-receipt-row"><dt>decision</dt><dd>allow</dd></div>
 <div class="nf-receipt-row"><dt>confidence_score</dt><dd>0.82</dd></div>
 <div class="nf-receipt-row"><dt>rid</dt><dd>{rid}</dd></div>
 <div class="nf-receipt-row"><dt>evidence_index</dt><dd>purview · entra · audit</dd></div>
 <div class="nf-receipt-row"><dt>export_integrity</dt><dd class="nf-receipt-ok">PASS · fail closed on tamper</dd></div>
 </dl>
 <p class="nf-receipt-mock-footer">{footer}</p>
 </aside>"""


def panel(label: str, items: list[str], btn: str = "") -> str:
    lis = "".join(f"<li>{i}</li>" for i in items)
    b = f'<a class="btn btn-secondary" href="{btn}">Trust Ledger Workspace</a>' if btn else ""
    return f"""
 <aside class="nf-hero-panel" aria-label="{label}">
 <p class="nf-hero-panel-label">{label}</p>
 <ul class="nf-hero-panel-list">{lis}</ul>
 {b}
 </aside>"""


def hero(kicker: str, eyebrow: str, h1: str, lead: str, badges: list[tuple[str, bool]], actions: list[tuple[str, str, bool]], tags: list[str], side: str) -> str:
    badge_html = "".join(
        f'<span class="nf-badge-pill{" nf-badge-pill--gold" if gold else ""}">{t}</span>' for t, gold in badges
    )
    act_html = "".join(
        f'<a class="btn btn-{"primary" if pri else "secondary"}" href="{href}">{label}</a>' for href, label, pri in actions
    )
    tag_html = "".join(f"<li>{t}</li>" for t in tags)
    kick = f'<p class="nf-hero-kicker"><span class="nf-hero-kicker-dot" aria-hidden="true"></span> {kicker}</p>' if kicker else ""
    eye = f'<p class="nf-eyebrow">{eyebrow}</p>' if eyebrow else ""
    return f"""
 <header class="nf-hero-cinematic">
 <div>
 {kick}
 {eye}
 <h1>{h1}</h1>
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
    labels = {"shipped": "Shipped", "orientation": "Orientation", "roadmap": "Roadmap", "na": "Out of scope"}
    return "".join(
        f'<div class="nf-trust-signal"><span class="nf-trust-signal-label">{l}</span>'
        f'<span class="nf-signal-badge {badges[k]}">{labels[k]}</span></div>'
        for l, k in items
    )


def scope_block() -> str:
    return f"""
 <section class="nf-trust-signals" aria-labelledby="scope-title">
 <h2 id="scope-title">Shipped today — honest scope</h2>
 <p class="nf-trust-signals-lead">No certifier claims. No custody. What you can demo and export now.</p>
 <div class="nf-trust-signals-grid">{scope_rows_html()}</div>
 </section>"""


def stat_bar() -> str:
    return """
 <div class="nf-stat-bar" role="region" aria-label="Key metrics">
 <div class="nf-stat-bar-item"><strong>4</strong><span>Evaluate · Decide · Record · Export</span></div>
 <div class="nf-stat-bar-item"><strong>$10k</strong><span>Trust Brief entry</span></div>
 <div class="nf-stat-bar-item"><strong>90d</strong><span>Design partner program</span></div>
 <div class="nf-stat-bar-item"><strong>3</strong><span>Institutional SKUs only</span></div>
 </div>"""


def investor_stat_bar() -> str:
    return """
 <div class="nf-stat-bar" role="region" aria-label="Investor metrics">
 <div class="nf-stat-bar-item"><strong>Shipped</strong><span>Evaluate · TLE · export live</span></div>
 <div class="nf-stat-bar-item"><strong>$10k</strong><span>Trust Brief land wedge</span></div>
 <div class="nf-stat-bar-item"><strong>90d</strong><span>Design partner path</span></div>
 <div class="nf-stat-bar-item"><strong>3</strong><span>Locked SKUs only</span></div>
 </div>"""


def mega_cta(title: str = "Request Governance Brief", sub: str = "Non-confidential intake · Trust Brief, Copilot pilot, or federal / MSP lane.", primary: tuple[str, str] = ("/trust-brief/intake/", "Request Governance Brief"), secondary: tuple[str, str] | None = ("/copilot/pilot/", "Become a design partner")) -> str:
    sec = f'<a class="btn btn-secondary" href="{secondary[0]}">{secondary[1]}</a>' if secondary else ""
    return f"""
 <section class="nf-cta-mega" aria-labelledby="cta-h">
 <h2 id="cta-h">{title}</h2>
 <p>{sub}</p>
 <div class="nf-cta-actions">
 <a class="btn btn-primary" href="{primary[0]}">{primary[1]}</a>
 {sec}
 </div>
 </section>"""


def write(rel: str, title: str, desc: str, canonical: str, body: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEAD.format(title=title, desc=desc, canonical=canonical) + body + FOOT, encoding="utf-8")
    print("wrote", rel)


def homepage() -> str:
    h = hero(
        "Governance execution · Canada",
        "AI Governance &amp; Evidence · Microsoft 365 Copilot",
        "The audit trail your Copilot deployment will be asked for later",
        "Invalid changes <strong>blocked</strong>. Allowed decisions <strong>receipted</strong>. Export bundles that <strong>fail closed</strong> on tamper. Metadata-only M365 — complement Purview, not replace it.",
        [("Trust Ledger · TLE v1", True), ("No custody · no payment rails", False)],
        [("/copilot/pilot/", "Become a design partner", True), ("/copilot/demo/", "5-minute demo", False), ("/copilot/procurement/", "Procurement pack", False)],
        ["NIST AI RMF", "ISO-style evidence", "Microsoft Purview", "RPAA-safe vendor"],
        receipt(),
    )
    s01 = """
 <section class="nf-section-block" aria-labelledby="s01">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="s01">Governance execution</p>
 <h2>We govern Copilot execution — not another chatbot</h2>
 <p class="nf-section-lead">Show the record your auditor would accept before Copilot touches production data.</p>
 </div></div>
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">01</p><h3>Evaluate</h3><p>Operational intent against policy — allow, deny, or review.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">02</p><h3>Decide</h3><p>Approval chain with confidence score and named approvers.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">03</p><h3>Record</h3><p>Signed Trust Ledger Entry + M365 evidence index.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">04</p><h3>Export</h3><p>Board PDF and procurement ZIP — tamper fails closed.</p></article>
 </div>
 </section>"""
    s02 = """
 <section class="nf-section-block" aria-labelledby="s02">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="s02">Honest scope</p>
 <h2>Shipped today — what is real vs roadmap</h2>
 <p class="nf-section-lead">No certifier claims. No custody. What you can demo and export now.</p>
 </div></div>
 <div class="nf-trust-signals-grid">{scope_rows_html()}</div>
 </section>"""
    s03 = """
 <section class="nf-section-block" aria-labelledby="s03">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">03</span><div>
 <p class="nf-eyebrow" id="s03">Buyers</p>
 <h2>Built for CISO, GRC, and procurement</h2>
 </div></div>
 <div class="nf-personas">
 <article class="nf-persona"><p class="nf-persona-role">CISO · Head of AI</p><h3>Security leadership</h3><p>Copilot rollout with defensible go/no-go.</p></article>
 <article class="nf-persona"><p class="nf-persona-role">GRC · Compliance</p><h3>Risk officers</h3><p>Signed TLE records and tamper-evident export.</p></article>
 <article class="nf-persona"><p class="nf-persona-role">Procurement · Legal</p><h3>Institutional diligence</h3><p>Procurement ZIP, framework citations, board PDF.</p></article>
 </div>
 </section>"""
    s04 = """
 <section class="nf-section-block" aria-labelledby="s04">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">04</span><div>
 <p class="nf-eyebrow" id="s04">Specialized lanes</p>
 <h2>Federal GC · MSP partners</h2>
 </div></div>
 <div class="nf-proof-grid">
 <a class="nf-proof-card" href="/federal/"><span class="nf-proof-icon">GC</span><div><h3>Federal · ADM · AIA · Copilot PIN</h3><p>GC governance evidence — June 24, 2026 legacy ADS deadline.</p></div></a>
 <a class="nf-proof-card" href="/msp/"><span class="nf-proof-icon">MSP</span><div><h3>MSP · Readiness → Record</h3><p>Phase 1 Purview · Phase 2 TLE receipts after readiness.</p></div></a>
 </div>
 </section>"""
    s05 = """
 <section class="nf-section-block" aria-labelledby="s05">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">05</span><div>
 <p class="nf-eyebrow" id="s05">Proof</p>
 <h2>Evidence your stakeholders can inspect</h2>
 </div></div>
 <div class="nf-proof-grid">
 <a class="nf-proof-card" href="/copilot/demo/"><span class="nf-proof-icon">▶</span><div><h3>5-minute demo</h3><p>Confidence score · Purview · Entra · SharePoint</p></div></a>
 <a class="nf-proof-card" href="/trust-ledger/sample-report/"><span class="nf-proof-icon">TLE</span><div><h3>TLE v1 samples</h3><p>Go · conditional · rejected YAML</p></div></a>
 <a class="nf-proof-card" href="/copilot/procurement/"><span class="nf-proof-icon">ZIP</span><div><h3>Procurement pack</h3><p>Buyer diligence ZIP · NIST AI RMF</p></div></a>
 <a class="nf-proof-card" href="/enterprise/"><span class="nf-proof-icon">ENT</span><div><h3>Enterprise</h3><p>Banks · regulated institutions · Bank Pilot</p></div></a>
 </div>
 </section>"""
    s06 = """
 <section class="nf-section-block" aria-labelledby="s06">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">06</span><div>
 <p class="nf-eyebrow" id="s06">Offerings</p>
 <h2>Three SKUs — locked scope</h2>
 </div></div>
 <div class="nf-offerings-v5">
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Trust Brief</p><p class="price">$10,000 · 6 weeks</p><p>Governance audit, AI policy mapping, risk exposure analysis, executive summary.</p><a class="btn btn-primary" href="/trust-brief/">Trust Brief</a></article>
 <article class="nf-offer-card nf-offer-card--featured"><p class="meta">Copilot Governance Pack</p><p class="price">$2k–10k pilot</p><p>Live TLE records, board PDF, procurement export — 90-day design partner.</p><a class="btn btn-primary" href="/copilot/">Copilot Pack</a></article>
 <article class="nf-offer-card"><p class="meta">Bank Pilot</p><p class="price">Custom</p><p>Shadow governance simulation — read-only, no execution authority.</p><a class="btn btn-secondary" href="/bank-pilot/">Bank Pilot</a></article>
 </div>
 </section>"""
    return h + stat_bar() + s01 + s02 + s03 + s04 + s05 + s06 + mega_cta()


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


def hub_page(kicker, eyebrow, h1, lead, badges, actions, tags, side, extra: str, cta: str | None = None) -> str:
    if cta is None:
        cta = mega_cta()
    return hero(kicker, eyebrow, h1, lead, badges, actions, tags, side) + scope_block() + extra + cta


def main() -> None:
    write("index.html", "Noetfield — Copilot Governance &amp; Trust Ledger Evidence",
          "Governance execution for Microsoft 365 Copilot — invalid changes blocked, allowed decisions receipted, tamper fails on export.",
          "/", homepage())

    # Trust Brief
    write("trust-brief/index.html", "Noetfield — Trust Brief ($10,000)",
          "Six-week Trust Brief: governance audit, AI policy mapping, risk exposure analysis. $10,000.",
          "/trust-brief/",
          hub_page("Trust Brief · $10,000 fixed", "Six-week governance diagnostic",
                   "Know your AI governance exposure before the board asks",
                   "Fixed-scope assessment: governance audit, AI policy mapping, and risk exposure analysis for executive decision-making.",
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
                   "Evaluate operational intent, index M365 metadata evidence, and produce signed Trust Ledger Entries your board and procurement can defend.",
                   [("TLE v1 signed records", True), ("Purview · Entra · SharePoint", False)],
                   [("/copilot/demo/", "5-minute demo", True), ("/copilot/pilot/", "Design-partner pilot", False), ("/copilot/procurement/", "Procurement pack", False)],
                   ["Evaluate · Decide · Record · Export"],
                   panel("Governance execution loop", ["Evaluate intent before Copilot execution", "Decide with policy chain and confidence score", "Record TLE v1 with metadata-only evidence", "Export board PDF and procurement ZIP"], "/workspace/"),
                   """
 <section class="nf-section"><div class="nf-section__head"><span class="nf-section__num">01</span><div>
 <p class="nf-section__label">Problem · Risk · Solution</p><h2>Copilot spreads before legal signs off</h2>
 </div></div>
 <div class="nf-cards">
 <article class="nf-card"><p class="nf-card__tag">Problem</p><h3>Undocumented decisions</h3><p>Copilot adoption outpaces policy and risk review.</p></article>
 <article class="nf-card"><p class="nf-card__tag">Risk</p><h3>Audit exposure</h3><p>Oversharing and unlogged go/no-go create regulatory risk.</p></article>
 <article class="nf-card nf-card--gold"><p class="nf-card__tag">Solution</p><h3>Signed TLE v1</h3><p>Confidence score + procurement-grade export — not another chatbot.</p></article>
 </div></section>"""))

    pages = [
        ("copilot/demo/index.html", "Noetfield — 5-Minute Copilot Governance Demo", "Live demo: confidence score, Purview, Entra, SharePoint evidence index.", "/copilot/demo/",
         "5-minute demo", "Live proof · Copilot governance",
         "See confidence score, M365 evidence index, and TLE export in five minutes",
         "Walk through evaluate → receipt → export with Purview, Entra ID, and SharePoint metadata. Demo script (locked narrative) — confidence score on every decision.",
         [("Live demo script", True), ("Confidence score", False)],
         [("/workspace/", "Open workspace", True), ("/copilot/procurement/", "Procurement pack", False)],
         receipt("RID-2026-0602-DEMO", "Demo narrative — locked script in repo.")),
        ("copilot/procurement/index.html", "Noetfield — Copilot Procurement Pack", "Buyer diligence ZIP, NIST AI RMF citations, procurement export.", "/copilot/procurement/",
         "Procurement pack", "Buyer diligence · ZIP export",
         "Procurement-grade export for Copilot governance diligence",
         "Framework citations, vendor scope boundaries, and sample TLE artifacts — the buyer pack institutional buyers request before pilot sign-off. Procurement pack (ZIP) via intake.",
         [("NIST AI RMF", True), ("ZIP export", False)],
         [("/trust-brief/intake/", "Request Governance Brief", True), ("/copilot/demo/", "5-minute demo", False)],
         receipt("RID-2026-0602-PROC", "Orientation sample — request pack via intake.")),
        ("copilot/sme/index.html", "Noetfield — SME Governance Pack", "SME Copilot governance pack for CISO, GRC, and procurement.", "/copilot/sme/",
         "SME Governance Pack", "Mid-market · Copilot governance",
         "Governance pack sized for SME Copilot rollouts",
         "Same TLE v1 lifecycle as enterprise — confidence score, approval chain, and export scoped for teams that need receipts without a six-figure GRC platform.",
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
        write(rel, title, desc, canon,
              hub_page(kick, eye, h1, lead, badges, actions, [], side, """
 <section class="nf-section nf-section--lift"><div class="nf-cards">
 <a class="nf-card nf-card--link" href="/copilot/"><p class="nf-card__tag">Hub</p><h3>Copilot Governance Pack</h3><p>Full offering overview.</p></a>
 <a class="nf-card nf-card--link" href="/trust-ledger/sample-report/"><p class="nf-card__tag">Samples</p><h3>TLE v1 YAML</h3><p>Go · conditional · rejected.</p></a>
 </div></section>"""))

    write("enterprise/index.html", "Noetfield Enterprise — Governance for Regulated Organizations",
          "For banks, regulated enterprises, and institutional buyers. Three offerings from $10,000.",
          "/enterprise/",
          hub_page("Enterprise · Banks · Regulated institutions", "Institutional buyers",
                   "Governance evaluation for institutions that cannot afford policy failure",
                   "For CCO, CRO, and technology leaders: AI policy enforcement, risk intelligence at the decision layer, and audit lineage your board can defend.",
                   [("From $10,000", True), ("Read-only Bank Pilot", False), ("No custody", False)],
                   [("/trust-brief/intake/?source=enterprise", "Request Governance Brief", True), ("/console/", "Governance Console", False)],
                   [],
                   panel("What we do not do", ["No transaction execution or custody", "No movement of financial value", "Governance evaluation layer only", "Policy-aligned allow or deny + compliance log"]),
                   """
 <section class="nf-section"><div class="nf-section__head"><span class="nf-section__num">01</span><div>
 <p class="nf-section__label">Institutional SKUs</p><h2>Trust Brief → Copilot Pack → Bank Pilot</h2>
 </div></div>
 <div class="nf-skus">
 <article class="nf-sku nf-sku--feat"><p class="nf-sku__name">Trust Brief</p><p class="nf-sku__price">$10,000</p><p>Diagnostic before production Copilot.</p><a class="btn btn-primary" href="/trust-brief/">Trust Brief</a></article>
 <article class="nf-sku nf-sku--feat"><p class="nf-sku__name">Copilot Pack</p><p class="nf-sku__price">$2k–10k</p><p>Live TLE + board export.</p><a class="btn btn-primary" href="/copilot/">Copilot</a></article>
 <article class="nf-sku"><p class="nf-sku__name">Bank Pilot</p><p class="nf-sku__price">Custom</p><p>Shadow simulation — read-only.</p><a class="btn btn-secondary" href="/bank-pilot/">Bank Pilot</a></article>
 </div></section>"""))

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
 <div class="nf-trust" role="region" aria-label="Federal policy anchors">
 <div class="nf-trust__item"><strong>ADM</strong><span>Directive on Automated Decision-Making</span></div>
 <div class="nf-trust__item"><strong>AIA</strong><span>Algorithmic Impact Assessment</span></div>
 <div class="nf-trust__item"><strong>Copilot PIN</strong><span>Copilot for Work · unclassified</span></div>
 <div class="nf-trust__item"><strong>GC AI Register</strong><span>Inventory + governance depth</span></div>
 </div>
 <aside class="nf-callout"><p><strong>Scope:</strong> Unclassified information only. Noetfield complements Purview and departmental AIA workflows — not a federal certifier.</p></aside>
 <section class="nf-section nf-section--lift"><div class="nf-proof">
 <a class="nf-proof__item" href="/docs/federal/FEDERAL_GOVERNANCE_PACK_v1.md"><span class="nf-proof__icon">DOC</span><div><h3>Federal Governance Pack</h3><p>Lane SSOT</p></div></a>
 <a class="nf-proof__item" href="/docs/federal/AIA_TLE_MAPPING_v1.md"><span class="nf-proof__icon">AIA</span><div><h3>AIA ↔ TLE mapping</h3><p>Risk crosswalk</p></div></a>
 <a class="nf-proof__item" href="/docs/federal/GC_COPILOT_PIN_CHECKLIST_v1.md"><span class="nf-proof__icon">PIN</span><div><h3>Copilot PIN checklist</h3><p>GC M365 compliance</p></div></a>
 <a class="nf-proof__item" href="/trust-ledger/sample-report/"><span class="nf-proof__icon">TLE</span><div><h3>TLE samples</h3><p>Confidence + approval chain</p></div></a>
 </div></section>""",
          mega_cta("Request Federal Governance Brief", "Trust Brief intake · Schedule I/II departments · operations@noetfield.com", ("/trust-brief/intake/?interest=federal", "Request Federal Brief"))))

    write("msp/index.html", "MSP Partner Program — Readiness to Record | Noetfield",
          "Microsoft 365 MSP: Phase 1 Purview readiness · Phase 2 TLE governance receipts.",
          "/msp/",
          hub_page("MSP partner lane", "Readiness → Record · multi-tenant",
                   "Turn Copilot readiness into governance MRR",
                   "Phase 1 stays in your Purview practice. Phase 2 attaches when customers need signed TLE records for Copilot enablement.",
                   [("Phase 1 · Phase 2 RACI", True), ("GDAP multi-tenant", False)],
                   [("/gate/partners/intake/", "MSP partner intake", True), ("/copilot/demo/", "5-minute demo", False)],
                   ["Purview", "Copilot attach", "TLE receipts"],
                   panel("Two-tier model", ["Phase 1 — readiness + Purview (MSP leads)", "Phase 2 — evaluate + TLE (Noetfield)", "Import readiness gaps → pilot scope", "Governance Pack $2k–10k attach"]),
                   """
 <aside class="nf-callout"><p><strong>Complement, not compete:</strong> Noetfield does not replace Lighthouse, CIPP, or Purview policy management. We attach after readiness.</p></aside>
 <section class="nf-section"><div class="nf-table-wrap"><table class="nf-table"><thead><tr><th>Activity</th><th>MSP Phase 1</th><th>Noetfield Phase 2</th></tr></thead><tbody>
 <tr><td>Copilot readiness assessment</td><td>Lead</td><td>Import gaps → scope</td></tr>
 <tr><td>Purview labels · DLP</td><td>Configure</td><td>Metadata index only</td></tr>
 <tr><td>Go/no-go record</td><td>Facilitate sign-off</td><td>Sign TLE · board PDF · ZIP</td></tr>
 </tbody></table></div></section>
 <section class="nf-section nf-section--lift"><div class="nf-proof">
 <a class="nf-proof__item" href="/docs/msp/MSP_GOVERNANCE_PACK_v1.md"><span class="nf-proof__icon">MSP</span><div><h3>MSP Governance Pack</h3><p>Lane SSOT</p></div></a>
 <a class="nf-proof__item" href="/docs/msp/PHASE1_PHASE2_RACI_v1.md"><span class="nf-proof__icon">RACI</span><div><h3>Phase 1 / 2 RACI</h3><p>Delivery boundaries</p></div></a>
 <a class="nf-proof__item" href="/docs/msp/READINESS_TO_RECORD_MAPPING_v1.md"><span class="nf-proof__icon">MAP</span><div><h3>Readiness → Record</h3><p>Assessment import</p></div></a>
 <a class="nf-proof__item" href="/copilot/demo/"><span class="nf-proof__icon">▶</span><div><h3>5-minute demo</h3><p>Phase 2 proof</p></div></a>
 </div></section>""",
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
          "Frequently asked questions about Noetfield governance execution infrastructure.",
          "/faq/",
          hero("FAQ", "Quick answers", "Frequently asked questions",
               "Use the assistant (bottom-right) or read below.",
               [], [("/trust-brief/intake/", "Request Governance Brief", True)], [],
               panel("Start here", ["Trust Brief · $10k", "5-minute demo", "Procurement pack", "Request Governance Brief"])) + """
 <div class="nf-prose">
 <section><h2>What is Noetfield?</h2><p>Governance execution infrastructure — evaluate AI operational intent before execution, with compliance log and allow/deny. No custody or payment execution.</p></section>
 <section><h2>What do you offer?</h2><p>Three SKUs: Trust Brief ($10k), Copilot Governance Pack ($2k–10k pilot), Bank Pilot (custom shadow simulation).</p></section>
 <section><h2>Do you replace Microsoft Purview?</h2><p>No. We complement Purview — metadata-only evidence index and Copilot governance receipts.</p></section>
 <section><h2>Are you a certifier?</h2><p>No. We produce governance records and export bundles — not ISO/SOC certification claims.</p></section>
 </div>""" + mega_cta())

    # Simple pages
    for rel, title, desc, canon, h1, lead in [
        ("status/index.html", "Noetfield — Status", "Noetfield platform status.", "/status/", "Platform status", "Public surfaces and workspace availability."),
        ("privacy/index.html", "Noetfield — Privacy", "Privacy policy.", "/privacy/", "Privacy", "How Noetfield handles intake and operational metadata."),
        ("terms/index.html", "Noetfield — Terms", "Terms of use.", "/terms/", "Terms", "Terms governing use of Noetfield public surfaces."),
    ]:
        write(rel, title, desc, canon,
              hero("", "", h1, lead, [], [("/contact/", "Contact", False)], [], receipt("RID-STATUS", "Operational metadata only.")) +
              '<div class="nf-prose"><section><p>Full legal text maintained in repo. Contact operations@noetfield.com for questions.</p></section></div>' + mega_cta())

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
              "<strong>Product on disk is pilot-ready</strong> — TLE v1, workspace, evaluate API, board PDF, procurement ZIP. "
              "The step function investors underwrite is <strong>one contracted org</strong> using a board PDF in a real governance meeting.",
              [("Pilot-ready product", True), ("Three SKUs only", False), ("No custody · no MSB", False)],
              [("/copilot/demo/", "5-minute demo", True), ("mailto:operations@noetfield.com?subject=Investor%20brief", "Investor inquiry", False)],
              ["Land · Expand · Channel", "W3: deposit ≥ CAD 2K", "Metadata-only M365"],
              receipt("RID-2026-0602-INV", "Live product path — <a href=\"/copilot/demo/\">demo</a> · <a href=\"/trust-ledger/sample-report/\">TLE samples</a>"),
          )
          + investor_stat_bar()
          + """
 <section class="nf-section-block" aria-labelledby="inv-01">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">01</span><div>
 <p class="nf-eyebrow" id="inv-01">Investment thesis</p>
 <h2>Copilot scale created a receipt gap GRC platforms do not fill</h2>
 <p class="nf-section-lead">Enterprises inventory AI and secure data — almost nobody receipts <strong>Copilot execution decisions</strong> with tamper-evident export. Noetfield owns the wedge: pre-execution evaluate, signed TLE records, board PDF — complement Purview, not replace it.</p>
 </div></div>
 <div class="nf-stat-bar" role="region" aria-label="Market timing">
 <div class="nf-stat-bar-item"><strong>M365</strong><span>Copilot already in buyer stack</span></div>
 <div class="nf-stat-bar-item"><strong>Jun 2026</strong><span>GC legacy ADS / ADM clock</span></div>
 <div class="nf-stat-bar-item"><strong>MSP</strong><span>Phase 2 attach after readiness</span></div>
 <div class="nf-stat-bar-item"><strong>Board</strong><span>PDF unlocks budget conversation</span></div>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-02">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">02</span><div>
 <p class="nf-eyebrow" id="inv-02">Success model</p>
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

 <section class="nf-section-block" aria-labelledby="inv-03">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">03</span><div>
 <p class="nf-eyebrow" id="inv-03">Honest milestone stack</p>
 <h2>Shipped today vs what capital accelerates</h2>
 <p class="nf-section-lead">No fake traction. Product converts in a 5-minute demo — economic proof is a contracted pilot and referenceable board PDF.</p>
 </div></div>
 <div class="nf-trust-signals-grid">
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Governance evaluate + TLE v1 + workspace</span><span class="nf-signal-badge nf-signal-badge--shipped">Shipped</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Board PDF + procurement ZIP export</span><span class="nf-signal-badge nf-signal-badge--shipped">Shipped</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">M365 metadata evidence index</span><span class="nf-signal-badge nf-signal-badge--shipped">Shipped</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">First org: TLE in production + board PDF in meeting</span><span class="nf-signal-badge nf-signal-badge--orientation">Target</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Design partner LOI / deposit ≥ CAD 2K (W3)</span><span class="nf-signal-badge nf-signal-badge--orientation">Target</span></div>
 <div class="nf-trust-signal"><span class="nf-trust-signal-label">Governance Monitor MRR · tenant refresh</span><span class="nf-signal-badge nf-signal-badge--roadmap">Roadmap</span></div>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-04">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">04</span><div>
 <p class="nf-eyebrow" id="inv-04">90-day path to reference</p>
 <h2>Design partner program — week-by-week proof</h2>
 <p class="nf-section-lead">Locked commercial path from first demo to W3 economic signal. Capital maps to running this playbook in parallel across 3–5 design-partner conversations.</p>
 </div></div>
 <div class="nf-loop">
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 0–2</p><h3>Demo + CIO contact</h3><p>5-minute demo live · pipeline stage 1–2 · confidence score visible.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 3–6</p><h3>Pilot SOW + evidence</h3><p>M365 metadata connected · first TLE v1 approved in workspace.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 7–10</p><h3>Board PDF in meeting</h3><p>Referenceable governance artifact — partner success signal for expand.</p></article>
 <article class="nf-loop-step"><p class="nf-loop-step-num">Wk 11–12</p><h3>LOI / deposit ≥ CAD 2K</h3><p>W3 PASS bar · expand seats or MSP attach conversation.</p></article>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-05">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">05</span><div>
 <p class="nf-eyebrow" id="inv-05">Use of capital</p>
 <h2>Bottleneck is distribution and buyer proof — not product invention</h2>
 </div></div>
 <div class="nf-outcome-grid">
 <article class="nf-outcome-card nf-outcome-card--approved"><p class="nf-outcome-label">Acquire</p><h3>Design-partner pipeline</h3><p>Founder-led + agentic outreach to CISO/GRC at Copilot rollouts — Vancouver Trust Brief wedge first.</p></article>
 <article class="nf-outcome-card nf-outcome-card--approved"><p class="nf-outcome-label">Prove</p><h3>First referenceable board PDF</h3><p>One org exports TLE + board pack used in governance — unlocks procurement and case study.</p></article>
 <article class="nf-outcome-card"><p class="nf-outcome-label">Expand</p><h3>MSP + federal attach</h3><p>Phase 2 TLE receipts after partner readiness · GC ADM clock for federal Trust Brief attach.</p></article>
 </div>
 </section>

 <section class="nf-section-block" aria-labelledby="inv-06">
 <div class="nf-section-block-head"><span class="nf-section-num" aria-hidden="true">06</span><div>
 <p class="nf-eyebrow" id="inv-06">Defensibility</p>
 <h2>Receipt spine + M365 metadata — not another GRC catalog</h2>
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

 <aside class="nf-callout"><p><strong>Investor honesty:</strong> We do not claim ISO/SOC certification, custody, payment rails, or MSB execution. We do not inflate ARR or logo count. Product is shipped and demoable today — capital accelerates <strong>first contracted design partner</strong> and <strong>referenceable board PDF</strong>, not another product line.</p></aside>
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
              "Submit operational intent, receive an allow or deny decision, and review the compliance log on your authorized pilot host.",
              [("Pilot host", True), ("RID-threaded", False)],
              [("#", "Open Governance Console", True), ("/cognitive-dashboard/", "Cognitive dashboard", False)],
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
   var target = "https://platform.noetfield.com/console";
   if (host === "localhost" || host === "127.0.0.1") target = "http://127.0.0.1:8001/console";
   else if (host.indexOf("platform.") === 0) target = window.location.protocol + "//" + host + "/console";
   var a = document.querySelector(".nf-cta-actions .btn-primary");
   a.href = target;
   a.textContent = "Open Governance Console";
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
              "HTTP contracts for governance evaluation, RID lineage, and Trust Ledger export. Product narrative lives on GTM hubs — this page is for engineering and engagement intake.",
              [("OpenAPI", True), ("Pilot auth", False)],
              [("/trust-brief/intake/?interest=api-pilot&source=api-docs", "Request pilot access", True), ("/status/", "Status", False)],
              [],
              receipt("RID-2026-0602-API", "Evaluate → ledger → export routes shipped."),
          ) + scope_block() + """
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
 </section>""" + mega_cta("Pilot access", "Keys issued per engagement after Trust Brief or partner briefing", ("/trust-brief/intake/?interest=api-pilot&source=api-docs", "Request Governance Brief"), ("/status/", "Status")))

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
                '<link rel="stylesheet" href="/assets/noetfield-shell.css" />\n <link rel="stylesheet" href="/assets/noetfield-www.css?v=10" />',
            )
        new = re.sub(r'<body class="[^"]*">', '<body class="nf-www">', new, count=1)
        new = re.sub(r"<body>", "<body class=\"nf-www\">", new, count=1)
        new = re.sub(r'noetfield-shell\.js[^"]*', "noetfield-shell.js?v=10", new)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print("patched css", rel)


if __name__ == "__main__":
    main()
