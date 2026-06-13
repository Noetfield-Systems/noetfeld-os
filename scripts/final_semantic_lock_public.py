#!/usr/bin/env python3
"""Apply FINAL LOCK semantic replacements to public/GTM HTML layer."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_ROOTS = [
    ROOT / "gate",
    ROOT / "trust-brief",
    ROOT / "trust-ledger",
    ROOT / "copilot",
    ROOT / "contact",
    ROOT / "about",
    ROOT / "for-whom",
    ROOT / "playbook",
    ROOT / "vendor",
    ROOT / "faq",
    ROOT / "status",
    ROOT / "platform",
    ROOT / "policies",
    ROOT / "privacy",
    ROOT / "terms",
    ROOT / "cookies",
    ROOT / "accessibility",
    ROOT / "feedback",
    ROOT / "kits",
    ROOT / "assets" / "partials",
    ROOT / "index.html",
]

CARD_CHECKOUT_DISCLAIMER = """
<p class="nf-card-checkout-disclaimer" style="font-size:12px;line-height:1.6;opacity:.88;margin-top:14px;max-width:52rem;">
  <strong>Commercial software licensing only.</strong> Card checkout purchases Noetfield professional services and software access.
  No financial custody, payment routing, or money transmission is performed by Noetfield Systems Inc.
</p>
"""

PROTECT_PATTERNS = [
    r"/gate/procurement[^\"'\\s]*",
    r"#procurement\b",
    r'id=["\']procurement["\']',
    r"data-proc=",
    r"engagements@noetfield\.com",
]

REPLACEMENTS: list[tuple[str, str]] = [
    ("payment intent", ""),
    ("Payment Intent", ""),
    ("Payment intent", ""),
    ("Submit Payment Intent", ""),
    ("Invoice / PO", "Engagement artifact"),
    ("invoice / PO", "engagement artifact"),
    ("Invoice/PO", "Engagement artifact"),
    ("invoice/PO", "engagement artifact"),
    ("Open Procurement", "Open engagement intake"),
    ("Procurement lane", "Engagement intake lane"),
    ("procurement lane", "engagement intake lane"),
    ("Procurement-safe", "Institution-safe"),
    ("procurement-safe", "institution-safe"),
    ("procurement-aware", "engagement-intake-aware"),
    ("board/procurement-ready", "board-ready"),
    ("Procurement-ready", "Engagement-intake-ready"),
    ("procurement-ready", "engagement-intake-ready"),
    ("Procurement pack", "Engagement intake pack"),
    ("procurement pack", "engagement intake pack"),
    ("Procurement (Invoice/PO)", "Engagement intake (artifact)"),
    ("Procurement (Invoice / PO)", "Engagement intake (artifact)"),
    ("Procurement</", "Engagement intake</"),
    ("Procurement<", "Engagement intake<"),
    ("Procurement:", "Engagement intake:"),
    ("Procurement.", "Engagement intake."),
    ("Procurement,", "Engagement intake,"),
    ("Procurement)", "Engagement intake)"),
    ("Procurement ", "Engagement intake "),
    ("Procurement\n", "Engagement intake\n"),
    (" procurement ", " engagement intake "),
    (" procurement.", " engagement intake."),
    (" procurement,", " engagement intake,"),
    (" procurement)", " engagement intake)"),
    (" procurement:", " engagement intake:"),
    (" procurement\n", " engagement intake\n"),
    ("procurement ", "engagement intake "),
    ("procurement.", "engagement intake."),
    ("procurement,", "engagement intake,"),
    ("procurement)", "engagement intake)"),
    ("procurement:", "engagement intake:"),
    ("procurement\n", "engagement intake\n"),
    ("Keep procurement calm", "Keep engagement intake calm"),
    ("Partner intake (routing)", "Partner intake (lane assignment)"),
    ("Partner intake (Routing)", "Partner intake (lane assignment)"),
    ("lane routing", "lane assignment"),
    ("Lane routing", "Lane assignment"),
    ("Routing map", "Lane assignment map"),
    ("Routing panel", "Lane assignment panel"),
    ("Routing summary", "Governance flow summary"),
    ("Routing pack", "Governance flow pack"),
    ("Routing links", "Governance flow links"),
    ("Routing rules", "Lane assignment rules"),
    ("Routing discipline", "Lane assignment discipline"),
    ("Routing:</", "Lane assignment:</"),
    ("Routing:", "Lane assignment:"),
    ("Routing ", "Governance flow "),
    (" routing ", " governance flow "),
    ("routing,", "governance flow,"),
    ("routing.", "governance flow."),
    ("routing)", "governance flow)"),
    ("routing\n", "governance flow\n"),
    ("routing</", "governance flow</"),
    ("Partner routing", "Partner lane assignment"),
    ("portfolio routing", "portfolio programs"),
    ("Cohort routing", "Cohort programs"),
    ("Request ID routing", "Request ID traceability"),
    ("RID routing", "RID traceability"),
    ("routing token", "traceability token"),
    ("complaints routing", "complaints classification flow"),
    ("Card payment", "Commercial license (card)"),
    ("card payment", "commercial license (card)"),
    ("Open payment link", "Commercial checkout (card)"),
    ("Pay by card", "License via card"),
    ("Payment link", "Commercial checkout link"),
    ("Payment terms", "Commercial terms"),
    ("payment/PO", "engagement artifact"),
    ("payment routing", "fund movement"),
    ("money transmission", "regulated transfer activity"),
    ("routes to card payment", "routes to commercial license checkout"),
    ("card payment,", "commercial license (card),"),
    ("Pay Base", "License Base"),
    ("Pay Pro", "License Pro"),
    ("Pay Enterprise", "License Enterprise"),
    ("Pay (card)", "License (card)"),
    ("Pay QuickScan", "License QuickScan"),
    ("card payment link", "commercial checkout link"),
    ("via Gate/Procurement", "via Gate engagement intake"),
    ("Gate/Procurement", "Gate engagement intake"),
    ("wizard routing", "wizard lane assignment"),
    ("Wizard routing", "Wizard lane assignment"),
    ("directory + intake (non-confidential) + Reference ID + next-step routing", "directory + intake (non-confidential) + Reference ID + next-step governance flow"),
    ("next-step routing", "next-step governance flow"),
    ("Email map (fast routing)", "Email map (fast lane assignment)"),
    ("Contact (buyer-ready routing)", "Contact (buyer-ready lane assignment)"),
    ("procurement-compatible", "engagement-intake-compatible"),
    ("Procurement-compatible", "Engagement-intake-compatible"),
]

FORBIDDEN_SCAN = [
    "payment intent",
    "cross-border payment",
    "Payment Intent",
    "FX Calculator",
    "Submit Payment",
    "treasury routing",
    "settlement route",
    "Active Corridors",
    "payment routing",
]


def protect(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    for i, pattern in enumerate(PROTECT_PATTERNS):
        for m in re.finditer(pattern, text):
            key = f"__PROT_{i}_{len(placeholders)}__"
            placeholders[key] = m.group(0)
            text = text.replace(m.group(0), key, 1)
    return text, placeholders


def restore(text: str, placeholders: dict[str, str]) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def apply_replacements(text: str) -> str:
    text, ph = protect(text)
    for old, new in REPLACEMENTS:
        if old:
            text = text.replace(old, new)
    text = restore(text, ph)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def add_card_checkout_disclaimer(text: str) -> str:
    checkout_host = "buy." + "stripe.com"
    if checkout_host not in text:
        return text
    if "nf-card-checkout-disclaimer" in text:
        return text
    if "</body>" in text:
        return text.replace("</body>", CARD_CHECKOUT_DISCLAIMER + "\n</body>", 1)
    return text + CARD_CHECKOUT_DISCLAIMER


def iter_html_files() -> list[Path]:
    files: list[Path] = []
    for root in PUBLIC_ROOTS:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(root.rglob("*.html"))
    return sorted(set(files))


def main() -> None:
    changed = 0
    for path in iter_html_files():
        original = path.read_text(encoding="utf-8")
        updated = apply_replacements(original)
        updated = add_card_checkout_disclaimer(updated)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print("updated", path.relative_to(ROOT))
    print(f"files_changed: {changed}")


if __name__ == "__main__":
    main()
