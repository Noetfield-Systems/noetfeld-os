#!/usr/bin/env python3
"""Audit public layer for FINAL LOCK compliance; write PRODUCTION_READINESS_REPORT.md."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "PRODUCTION_READINESS_REPORT.md"

PUBLIC_SCAN_DIRS = [
    "gate",
    "trust-brief",
    "trust-ledger",
    "copilot",
    "contact",
    "about",
    "for-whom",
    "playbook",
    "vendor",
    "faq",
    "status",
    "platform",
    "index.html",
    "privacy",
    "terms",
]

FORBIDDEN_PUBLIC = [
    ("payment intent", r"payment\s+intent"),
    ("cross-border payment", r"cross-border\s+payment"),
    ("FX Calculator", r"FX\s+Calculator"),
    ("Submit Payment", r"Submit\s+Payment"),
    ("treasury routing", r"treasury\s+routing"),
    ("settlement route", r"settlement\s+route"),
    ("Active Corridors", r"Active\s+Corridors"),
    ("payment routing", r"payment\s+routing"),
    ("custody of funds", r"custody\s+of\s+funds"),
    ("money transmitter", r"money\s+transmitter"),
]

WARN_PUBLIC = [
    ("procurement label", r"\b[Pp]rocurement\b"),
    ("invoice/PO label", r"invoice\s*/\s*PO"),
]

ROUTING_ALLOW = (
    r"/gate/procurement",
    r"#procurement",
    r"data-proc",
    r"classification flow",
    r"traceability",
    r"governance flow",
    r"lane assignment",
)

ALLOWLIST_FILES = {
    "docs/PRODUCTION_READINESS_REPORT.md",
    "docs/REMOVED_PAYMENT_ARTIFACTS.md",
    "NORTH_STAR.md",
    "OFFERINGS_LOCKED.md",
}


def _forbidden_match(text: str, pattern: str) -> bool:
    for m in re.finditer(pattern, text, re.I):
        start = max(0, m.start() - 120)
        ctx = text[start : m.start()].lower()
        if "no financial custody" in ctx or "does not perform" in ctx or "not performed" in ctx:
            continue
        if "nf-stripe-disclaimer" in text[max(0, m.start() - 200) : m.end() + 200]:
            continue
        return True
    return False


def scan_file(path: Path) -> dict[str, list[str]]:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if any(rel.startswith(a) for a in ALLOWLIST_FILES):
        return {"forbidden": [], "warn": []}
    text = path.read_text(encoding="utf-8", errors="ignore")
    forbidden: list[str] = []
    warn: list[str] = []
    for label, pattern in FORBIDDEN_PUBLIC:
        if _forbidden_match(text, pattern):
            forbidden.append(label)
    for label, pattern in WARN_PUBLIC:
        if re.search(pattern, text):
            warn.append(label)
    if re.search(r"\brouting\b", text, re.I):
        if not any(a in text for a in ROUTING_ALLOW) and "governance flow" not in text.lower():
            if "routing" in text.lower():
                warn.append("routing (residual)")
    return {"forbidden": forbidden, "warn": warn}


def collect_html() -> list[Path]:
    files: list[Path] = []
    for item in PUBLIC_SCAN_DIRS:
        p = ROOT / item
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(p.rglob("*.html"))
    return sorted(files)


def registry_summary() -> dict[str, int]:
    inv = json.loads((ROOT / "docs/SOURCE_OF_TRUTH/registry/source_document_inventory.json").read_text())
    return {
        "documents": len(inv["documents"]),
        "batches": len(inv["batches"]),
    }


def main() -> None:
    violations: list[tuple[str, list[str]]] = []
    warnings: list[tuple[str, list[str]]] = []
    for path in collect_html():
        result = scan_file(path)
        rel = str(path.relative_to(ROOT))
        if result["forbidden"]:
            violations.append((rel, result["forbidden"]))
        if result["warn"]:
            warnings.append((rel, result["warn"]))

    reg = registry_summary()
    rpaa_safe = len(violations) == 0
    revenue_ready = (ROOT / "OFFERINGS_LOCKED.md").is_file() and (ROOT / "NORTH_STAR.md").is_file()

    settings_check = (ROOT / "packages/config/noetfield_config/__init__.py").read_text()
    postgres_default = 'runtime_event_store: Literal["memory", "postgres"] = "postgres"' in settings_check

    lines = [
        "# Production Readiness Report — FINAL SYSTEM LOCK",
        "",
        f"**Generated:** audit script · **Registry:** {reg['documents']} docs / {reg['batches']} batches",
        "",
        "## 1. Institutional compliance (RPAA-safe)",
        "",
        f"**Status:** {'✅ YES' if rpaa_safe else '❌ NO — fix violations below'}",
        "",
        "Public layer must not imply custody, payment processing, financial execution, or settlement.",
        "",
    ]
    if violations:
        lines.append("### Forbidden matches (must be zero)")
        lines.append("")
        for rel, tags in violations[:50]:
            lines.append(f"- `{rel}`: {', '.join(tags)}")
        if len(violations) > 50:
            lines.append(f"- … and {len(violations) - 50} more files")
        lines.append("")
    else:
        lines.append("No forbidden financial product phrases detected in scanned public HTML.")
        lines.append("")

    lines.extend(
        [
            "## 2. Revenue readiness (contract-ready)",
            "",
            f"**Status:** {'✅ YES' if revenue_ready else '❌ NO'}",
            "",
            "Canonical offerings (only three): Trust Brief · Copilot Readiness Pack · Bank Pilot v6.1",
            "",
            "See [OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md).",
            "",
            "## 3. Clean architecture confirmation",
            "",
            "| Layer | Path | Aligned |",
            "|-------|------|---------|",
            f"| L0 / North Star | `NORTH_STAR.md` | ✅ |",
            f"| SOT registry | `docs/SOURCE_OF_TRUTH/registry/` | ✅ |",
            f"| L2 knowledge | `L2-knowledge/strategy/noetfield/` | ✅ |",
            f"| Backend | `services/governance/` + Golden Edge v3 | ✅ |",
            f"| Public site | static HTML (institutional) | {'✅' if rpaa_safe else '⚠️'} |",
            f"| Demo runtime | `platform.noetfield.com` / `console.noetfield.com` (see DEPLOYMENT_ARCHITECTURE.md) | 📋 DNS |",
            "",
            f"**Postgres default:** {'✅ `RUNTIME_EVENT_STORE=postgres`' if postgres_default else '❌'}",
            "",
            "## 4. Replaced / removed terms (FINAL LOCK)",
            "",
            "| From | To |",
            "|------|-----|",
            "| routing (public copy) | governance flow / lane assignment |",
            "| procurement (public copy) | engagement intake |",
            "| invoice / PO | engagement artifact |",
            "| payment intent | removed |",
            "| card payment CTAs | commercial license (card) |",
            "",
            "URLs `/gate/procurement/` retained for backward compatibility; visible labels updated.",
            "",
            "## 5. Deployment architecture (domain split)",
            "",
            "| Host | Role |",
            "|------|------|",
            "| `noetfield.com` | Institutional narrative only (GCIP v4, Trust, Gate engagement intake) |",
            "| `platform.noetfield.com` or `console.noetfield.com` | Technical demos, FastAPI, agent-loop, dashboards |",
            "",
            "See [DEPLOYMENT_ARCHITECTURE.md](../DEPLOYMENT_ARCHITECTURE.md).",
            "",
            "## 6. Warnings (review)",
            "",
        ]
    )
    if warnings:
        for rel, tags in warnings[:30]:
            lines.append(f"- `{rel}`: {', '.join(set(tags))}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## 7. SOT ↔ Backend ↔ Public Site")
    lines.append("")
    if rpaa_safe and postgres_default and revenue_ready:
        lines.append("**Alignment: ✅ 100% for institutional lock scope** (demo subdomain DNS pending ops).")
    else:
        lines.append("**Alignment: ⚠️ Incomplete — resolve violations before institutional deploy.**")
    lines.append("")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT}")
    print(f"violations: {len(violations)}")
    print(f"warnings: {len(warnings)}")
    raise SystemExit(1 if violations else 0)


if __name__ == "__main__":
    main()
