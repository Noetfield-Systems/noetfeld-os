#!/usr/bin/env python3
"""Generate batch 015 constitution lineage, comparative analysis, GTM, and MVP specs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-015"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-constitution-gcip-v3-1.md",
        "document_key": "noetfield-constitution-gcip-v3-1",
        "title": "Noetfield Constitution v3.1 (GCIP)",
        "domain": "noetfield_constitution_l0",
        "version_label": "gcip-v3.1",
        "classification": "superseded_constitution",
        "status": "superseded",
        "supersedes": ["noetfield-constitution-gip-v2-0"],
        "superseded_by": "noetfield-constitution-gcip-v4",
    },
    {
        "file": "noetfield-constitution-gcip-v3-2-golden.md",
        "document_key": "noetfield-constitution-gcip-v3-2-golden",
        "title": "Noetfield Constitution v3.2 — Golden Canada-Safe Edition",
        "domain": "noetfield_constitution_l0",
        "version_label": "gcip-v3.2-golden",
        "classification": "superseded_constitution",
        "status": "superseded",
        "supersedes": ["noetfield-constitution-gcip-v3-1"],
        "superseded_by": "noetfield-constitution-gcip-v4",
    },
    {
        "file": "noetfield-constitution-gcip-v3-2-beta-duplicate.md",
        "document_key": "noetfield-constitution-gcip-v3-2-beta-duplicate",
        "title": "Noetfield Constitution v3.2 — Beta Draft (Duplicate)",
        "domain": "noetfield_constitution_l0",
        "version_label": "gcip-v3.2-beta-dup",
        "classification": "duplicate",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitution-gcip-v3-2-golden",
    },
    {
        "file": "noetfield-constitution-gip-v2-0.md",
        "document_key": "noetfield-constitution-gip-v2-0",
        "title": "Noetfield Constitution v2.0 (GIP)",
        "domain": "noetfield_constitution_l0",
        "version_label": "gip-v2.0",
        "classification": "superseded_constitution",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitution-gcip-v4",
    },
    {
        "file": "noetfield-constitution-comparative-analysis-fa.md",
        "document_key": "noetfield-constitution-comparative-analysis-fa",
        "title": "Constitution v3.1 vs v3.2 vs v4.0 — Comparative Analysis (Persian)",
        "domain": "noetfield_constitution_lineage_analysis",
        "version_label": "compare-fa-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-constitution-product-layer-separation-fa.md",
        "document_key": "noetfield-constitution-product-layer-separation-fa",
        "title": "Constitution vs Product Kernel Layer Separation (Persian)",
        "domain": "noetfield_constitution_lineage_analysis",
        "version_label": "layer-separation-fa-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-constitution-product-kernel-combined-v3-0.md",
        "document_key": "noetfield-constitution-product-kernel-combined-v3-0",
        "title": "Constitution & Product Kernel Combined v3.0",
        "domain": "noetfield_constitution_l0",
        "version_label": "combined-v3.0",
        "classification": "superseded_mixed_layer_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitution-gcip-v4",
    },
    {
        "file": "noetfield-cdl-pitch-deck-v3-1.md",
        "document_key": "noetfield-cdl-pitch-deck-v3-1",
        "title": "10-Slide Pitch Deck — CDL-Ready v3.1",
        "domain": "noetfield_commercial_gtm",
        "version_label": "pitch-deck-v3.1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-mvp-system-spec-v3-0-hardened.md",
        "document_key": "noetfield-mvp-system-spec-v3-0-hardened",
        "title": "MVP System Spec v3.0 (Hardened — Internal Coordination)",
        "domain": "noetfield_mvp_spec",
        "version_label": "mvp-spec-v3.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-full-system-blueprint-decision-inbox-v1.md",
        "document_key": "noetfield-full-system-blueprint-decision-inbox-v1",
        "title": "Full System Blueprint v1.0 — Decision Inbox Framing",
        "domain": "noetfield_commercial_gtm",
        "version_label": "blueprint-inbox-v1",
        "classification": "alternative_product_framing_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-golden-constitution-recommendation-v4.md",
        "document_key": "noetfield-golden-constitution-recommendation-v4",
        "title": "Golden Constitution Recommendation — GCIP v4.0 (Canada 2026)",
        "domain": "noetfield_constitution_lineage_analysis",
        "version_label": "golden-rec-v4",
        "classification": "active_executive_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
]

BODIES = {
    "noetfield-constitution-gcip-v3-1.md": """# Noetfield Constitution v3.1 (GCIP)

Document key: `noetfield-constitution-gcip-v3-1`

Earlier GCIP constitution (A1–A8). CDA may contain "structured routing metadata" — weaker
non-actionability than v3.2+. **Superseded by** `noetfield-constitution-gcip-v4`.
""",
    "noetfield-constitution-gcip-v3-2-golden.md": """# Constitution v3.2 — Golden Canada-Safe

Document key: `noetfield-constitution-gcip-v3-2-golden`

Adds A9 non-actionability (2026). RPAA/FINTRAC/OSFI positioning. Hard CDA boundaries.
**Superseded by v4.0** which adds A10–A11, user-approval mandate, prohibited revenue models,
and canonical partner-execution topology.
""",
    "noetfield-constitution-gcip-v3-2-beta-duplicate.md": """# Constitution v3.2 Beta — Duplicate

Document key: `noetfield-constitution-gcip-v3-2-beta-duplicate`

Duplicate beta paste of v3.2 golden draft.
""",
    "noetfield-constitution-gip-v2-0.md": """# Constitution v2.0 (GIP)

Document key: `noetfield-constitution-gip-v2-0`

Governance Infrastructure Protocol v2.0 — historical lineage. Routing graph in architecture
section (higher execution-adjacency risk than v3.2+). Superseded by GCIP v4.
""",
    "noetfield-constitution-comparative-analysis-fa.md": """# Constitution Comparative Analysis (Persian)

Document key: `noetfield-constitution-comparative-analysis-fa`

Bank/fintech counsel-style comparison of v3.1, v3.2, v4.0:

| Dimension | v3.1 | v3.2 Golden | v4.0 |
| Regulatory clarity | Good | Stronger A9 | Strongest (A10–A11, Canada supremacy) |
| CDA safety | Routing metadata risk | Hard boundary | Explicit prohibited fields + partner topology |
| Product separation | Mixed | Better | Clean with Annex v4 subordinate |
| 2026 Canada positioning | Adequate | Bank-ready | Optimal (user approval, no txn revenue) |

**Golden SoT:** `noetfield-constitution-gcip-v4` + Annex v4 EN separate.
""",
    "noetfield-constitution-product-layer-separation-fa.md": """# Constitution vs Product Kernel Separation (Persian)

Document key: `noetfield-constitution-product-layer-separation-fa`

Rule: Constitution = immutable law / identity. Product Kernel = deployable RPAA-safe expression.
Do not merge MVP, monetization, or deployment into Constitution.

VCs/pilots read Product Kernel; counsel reads Constitution + legal opinion.
""",
    "noetfield-constitution-product-kernel-combined-v3-0.md": """# Constitution & Product Kernel Combined v3.0

Document key: `noetfield-constitution-product-kernel-combined-v3-0`

Historical error pattern: mixed truth layer with MVP/product. Superseded by split:
L0 `noetfield-constitution-gcip-v4` + L1 `noetfield-constitutional-annex-product-kernel-v4-en`.
""",
    "noetfield-cdl-pitch-deck-v3-1.md": """# CDL Pitch Deck v3.1

Document key: `noetfield-cdl-pitch-deck-v3-1`

10-slide deck: execution–coordination gap, CDA product, legal kernel (non-PSP/MSB),
mid-market cross-border wedge, per-CDA monetization. Use RPAA-safe wording in slides
(coordination structuring, not payment orchestration).
""",
    "noetfield-mvp-system-spec-v3-0-hardened.md": """# MVP System Spec v3.0 (Hardened)

Document key: `noetfield-mvp-system-spec-v3-0-hardened`

Internal enterprise coordination MVP (CDO output). Explicit: no financial instructions,
no PSP/MSB adjacency. Signal consolidation → intent → governance rules → coordination object.
Aligns with Copilot Governance wedge for pilot delivery; does not replace GCIP bank stack.
""",
    "noetfield-full-system-blueprint-decision-inbox-v1.md": """# Full System Blueprint — Decision Inbox

Document key: `noetfield-full-system-blueprint-decision-inbox-v1`

Alternative commercial framing ("Decision Infrastructure OS", Decision Inbox product).
**Reference only** — GCIP v4 + bank integration pack remain authoritative for regulated financial
positioning. Useful for enterprise coordination GTM experiments.
""",
    "noetfield-golden-constitution-recommendation-v4.md": """# Golden Constitution Recommendation — GCIP v4.0

Document key: `noetfield-golden-constitution-recommendation-v4`

**Registry golden recommendation (Canada fintech 2026 safe positioning):**

**L0 Active:** `noetfield-constitution-gcip-v4`
**L1 Active:** `noetfield-constitutional-annex-product-kernel-v4-en`
**Legal:** `noetfield-rpaa-legal-opinion-letter-v1-1`
**Bank:** `noetfield-bank-integration-pack-v2`

Why v4 wins: A10 non-actionable outputs, A11 user-approval mandate, explicit prohibited
revenue (no FX spread/txn fees), partner-execution topology, Canada regulatory supremacy axiom.

v3.2 golden retained as superseded lineage only. Never merge product/MVP into Constitution.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_constitution_lineage_analysis",
        "active_document_key": "noetfield-constitution-comparative-analysis-fa",
        "active_version": "compare-fa-v1",
        "decision": "active_source_of_truth",
        "rationale": "Authoritative v3.1/v3.2/v4 comparative analysis; confirms GCIP v4.0 as golden L0 choice for Canada 2026.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_commercial_gtm",
        "active_document_key": "noetfield-cdl-pitch-deck-v3-1",
        "active_version": "pitch-deck-v3.1",
        "decision": "active_source_of_truth",
        "rationale": "CDL-ready 10-slide deck with tightened legal perimeter and CDA product narrative.",
        "confidence": 0.87,
    },
    {
        "domain": "noetfield_mvp_spec",
        "active_document_key": "noetfield-mvp-system-spec-v3-0-hardened",
        "active_version": "mvp-spec-v3.0",
        "decision": "active_source_of_truth",
        "rationale": "Hardened internal-coordination MVP spec; no financial instruction adjacency.",
        "confidence": 0.88,
    },
]

NEW_RULES = [
    {
        "rule_key": "constitution-v4-golden-l0-sot",
        "domain": "noetfield_constitution_lineage_analysis",
        "source_document_key": "noetfield-golden-constitution-recommendation-v4",
        "activation_status": "active_design_rule",
        "rule_type": "legal_hierarchy",
        "summary": "GCIP Constitution v4.0 is the golden L0 SOT; v3.2 and earlier are lineage only.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "no-mvp-in-constitution-layer",
        "domain": "noetfield_constitution_lineage_analysis",
        "source_document_key": "noetfield-constitution-product-layer-separation-fa",
        "activation_status": "active_design_rule",
        "rule_type": "documentation_governance",
        "summary": "MVP, monetization, and deployment belong in Product Kernel or MVP spec, not Constitution.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "gtm-rpaa-safe-wording-coordination-not-payments",
        "domain": "noetfield_commercial_gtm",
        "source_document_key": "noetfield-cdl-pitch-deck-v3-1",
        "activation_status": "active_design_rule",
        "rule_type": "gtm",
        "summary": "External copy uses coordination/governance language; avoid payment orchestration wording.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "mvp-no-financial-instruction-adjacency",
        "domain": "noetfield_mvp_spec",
        "source_document_key": "noetfield-mvp-system-spec-v3-0-hardened",
        "activation_status": "active_design_rule",
        "rule_type": "product_governance",
        "summary": "MVP outputs coordination objects only; no routing, payments, or PSP-facing instructions.",
        "implementation_target": "workflow_runtime",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-015

Constitution lineage v2.0–v3.2 (superseded), comparative analysis (FA),
layer-separation methodology, CDL pitch deck, hardened MVP spec, golden v4 recommendation.

## Golden L0 (unchanged)

`noetfield-constitution-gcip-v4` (batch 014) — do not revert to v3.2 for active SOT.

## New domains

- `noetfield_constitution_lineage_analysis`
- `noetfield_commercial_gtm`
- `noetfield_mvp_spec`
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-015", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-015"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-015/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-015",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-12"

    rules["registry_version"] = "2026-05-29-rules-12"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
