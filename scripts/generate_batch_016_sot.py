#!/usr/bin/env python3
"""Generate batch 016 investor, accelerator, bank submission, and positioning lineage docs."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-016"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-institutional-investment-memo-1pager-v1.md",
        "document_key": "noetfield-institutional-investment-memo-1pager-v1",
        "title": "Institutional Investment Memo (1-Pager) — Tier-1 Strategics",
        "domain": "noetfield_investor_positioning",
        "version_label": "investor-memo-v1",
        "classification": "superseded_gtm_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-bank-ready-institutional-document-v1",
    },
    {
        "file": "noetfield-ic-diligence-memo-blackrock-style-v1.md",
        "document_key": "noetfield-ic-diligence-memo-blackrock-style-v1",
        "title": "Internal IC Diligence Memo (BlackRock-Style)",
        "domain": "noetfield_internal_ic_assessment",
        "version_label": "ic-memo-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-bc-tech-cdl-one-pager-venture-v1.md",
        "document_key": "noetfield-bc-tech-cdl-one-pager-venture-v1",
        "title": "BC Tech / CDL One-Pager — Venture-Scale Edition",
        "domain": "noetfield_accelerator_cdl",
        "version_label": "cdl-venture-v1",
        "classification": "superseded_gtm_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-bc-tech-cdl-one-pager-locked-v1",
    },
    {
        "file": "noetfield-bc-tech-cdl-one-pager-egel-v1.md",
        "document_key": "noetfield-bc-tech-cdl-one-pager-egel-v1",
        "title": "BC Tech / CDL One-Pager — EGEL Edition",
        "domain": "noetfield_accelerator_cdl",
        "version_label": "cdl-egel-v1",
        "classification": "superseded_gtm_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-bc-tech-cdl-one-pager-locked-v1",
    },
    {
        "file": "noetfield-bc-tech-cdl-one-pager-locked-v1.md",
        "document_key": "noetfield-bc-tech-cdl-one-pager-locked-v1",
        "title": "BC Tech / CDL One-Pager — Locked (RPAA-Safe Wording)",
        "domain": "noetfield_accelerator_cdl",
        "version_label": "cdl-locked-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [
            "noetfield-bc-tech-cdl-one-pager-venture-v1",
            "noetfield-bc-tech-cdl-one-pager-egel-v1",
        ],
        "superseded_by": None,
    },
    {
        "file": "noetfield-spark-centre-one-pager-v1.md",
        "document_key": "noetfield-spark-centre-one-pager-v1",
        "title": "Spark Centre One-Pager — Ontario SME Governance OS",
        "domain": "noetfield_accelerator_spark",
        "version_label": "spark-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-operating-model-2026-trustfield-v1.md",
        "document_key": "noetfield-operating-model-2026-trustfield-v1",
        "title": "Full Operating Model 2026 — Noetfield / TrustField Split",
        "domain": "noetfield_operating_model_reference",
        "version_label": "operating-model-2026",
        "classification": "historical_operating_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": "noetfield-bank-integration-pack-v2",
    },
    {
        "file": "noetfield-rbc-finsec-submission-v1.md",
        "document_key": "noetfield-rbc-finsec-submission-v1",
        "title": "Formal RBC FinSec Submission — RPAA Perimeter (2026)",
        "domain": "noetfield_regulatory_submissions",
        "version_label": "rbc-finsec-v1",
        "classification": "historical_bank_submission",
        "status": "reference",
        "supersedes": [],
        "superseded_by": "noetfield-rpaa-legal-opinion-letter-v1-1",
    },
    {
        "file": "noetfield-bank-of-canada-rpaa-submission-v1.md",
        "document_key": "noetfield-bank-of-canada-rpaa-submission-v1",
        "title": "Bank of Canada RPAA Perimeter Clarification Request",
        "domain": "noetfield_regulatory_submissions",
        "version_label": "boc-rpaa-v1",
        "classification": "historical_bank_submission",
        "status": "reference",
        "supersedes": [],
        "superseded_by": "noetfield-rpaa-legal-opinion-letter-v1-1",
    },
    {
        "file": "noetfield-bank-ready-institutional-document-v1.md",
        "document_key": "noetfield-bank-ready-institutional-document-v1",
        "title": "Bank-Ready Institutional Document — RPAA/MSB-Safe (2026)",
        "domain": "noetfield_investor_positioning",
        "version_label": "bank-ready-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["noetfield-institutional-investment-memo-1pager-v1"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-master-blueprint-comparative-analysis-fa-v1.md",
        "document_key": "noetfield-master-blueprint-comparative-analysis-fa-v1",
        "title": "Master Blueprint Comparative Analysis (Persian) — Orchestration vs Governance",
        "domain": "noetfield_positioning_lineage_analysis",
        "version_label": "blueprint-compare-fa-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-master-blueprint-kavodax-benchmark-v1.md",
        "document_key": "noetfield-master-blueprint-kavodax-benchmark-v1",
        "title": "Master Blueprint — Kavodax/BVNK Wallet-Orchestration Benchmark",
        "domain": "noetfield_positioning_lineage_analysis",
        "version_label": "kavodax-blueprint-v1",
        "classification": "prohibited_positioning_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitution-gcip-v4",
    },
    {
        "file": "noetfield-master-blueprint-non-custodial-governance-v1.md",
        "document_key": "noetfield-master-blueprint-non-custodial-governance-v1",
        "title": "Master Blueprint — Non-Custodial Governance (Regulation-Safe)",
        "domain": "noetfield_positioning_lineage_analysis",
        "version_label": "governance-blueprint-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-operator-hardware-selection-macbook-v1.md",
        "document_key": "noetfield-operator-hardware-selection-macbook-v1",
        "title": "Operator Hardware Selection — MacBook M3/M4 Pro Blueprint",
        "domain": "operator_equipment",
        "version_label": "hardware-v1",
        "classification": "operator_reference_non_product",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-payment-orchestration-meta-gateway-v1.md",
        "document_key": "noetfield-payment-orchestration-meta-gateway-v1",
        "title": "Payment Orchestration & Meta-Gateway Blueprint (2026)",
        "domain": "noetfield_positioning_lineage_analysis",
        "version_label": "meta-gateway-v1",
        "classification": "prohibited_positioning_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitution-gcip-v4",
    },
]

BODIES: dict[str, str] = {
    "noetfield-institutional-investment-memo-1pager-v1.md": """# Institutional Investment Memo (1-Pager)

Document key: `noetfield-institutional-investment-memo-1pager-v1`

Target: RBC Capital Markets, BlackRock / Aladdin ecosystem, tier-1 strategics.

**Registry status:** Superseded GTM draft. Contains high-risk phrases including
"Outputs Execution-Ready Instructions" and "Cross-Institution Routing Layer" —
incompatible with GCIP v4 A9–A11 and Bank Integration Pack v2.

Use `noetfield-bank-ready-institutional-document-v1` or CDL locked one-pager for external circulation.
""",
    "noetfield-ic-diligence-memo-blackrock-style-v1.md": """# Internal IC Diligence Memo (BlackRock-Style)

Document key: `noetfield-ic-diligence-memo-blackrock-style-v1`

Neutral IC assessment: concept coherent; category ambiguity; adoption dependency;
regulatory reclassification risk if outputs influence execution.

Verdict: NOT YET INVESTABLE (as-is) — promising concept requiring structural de-risking.

Required: wedge product, measurable governance latency, pilot, boundary vs ERP/orchestration.
""",
    "noetfield-bc-tech-cdl-one-pager-venture-v1.md": """# BC Tech / CDL One-Pager — Venture Edition

Document key: `noetfield-bc-tech-cdl-one-pager-venture-v1`

Superseded by locked RPAA-safe edition. Retained for lineage.
""",
    "noetfield-bc-tech-cdl-one-pager-egel-v1.md": """# BC Tech / CDL One-Pager — EGEL Edition

Document key: `noetfield-bc-tech-cdl-one-pager-egel-v1`

Enterprise Governance Execution Layer framing. Superseded by locked edition.
""",
    "noetfield-bc-tech-cdl-one-pager-locked-v1.md": """# BC Tech / CDL One-Pager — Locked

Document key: `noetfield-bc-tech-cdl-one-pager-locked-v1`

**Active CDL/BC Tech one-pager SOT.** Governance-native, non-custodial, non-RPAA, non-MSB.
Cascadia / Pacific Gateway wedge. Per-governance-event monetization. Advisory outputs only.

Avoid: execution OS, routing payments, instruction layer language.
""",
    "noetfield-spark-centre-one-pager-v1.md": """# Spark Centre One-Pager

Document key: `noetfield-spark-centre-one-pager-v1`

**Active Spark Centre accelerator SOT.** Stand-alone governance infrastructure for Ontario SMEs.
Non-custodial governance OS; clients execute via existing banks/MSBs. Zero RPAA/MSB triggers.

Partner-agnostic; no TrustField dependency in external narrative.
""",
    "noetfield-operating-model-2026-trustfield-v1.md": """# Operating Model 2026 — Noetfield / TrustField

Document key: `noetfield-operating-model-2026-trustfield-v1`

Historical RACI: Noetfield governance vs TrustField execution. Reference for two-entity flows.

**Superseded for bank diligence by:** `noetfield-bank-integration-pack-v2` + GCIP v4 stack.
""",
    "noetfield-rbc-finsec-submission-v1.md": """# RBC FinSec Submission

Document key: `noetfield-rbc-finsec-submission-v1`

Counsel-grade RPAA trigger analysis; non-initiation, non-transmission, non-custody.
Historical submission reference — align live diligence with legal opinion v1.1 and bank pack v2.
""",
    "noetfield-bank-of-canada-rpaa-submission-v1.md": """# Bank of Canada RPAA Submission

Document key: `noetfield-bank-of-canada-rpaa-submission-v1`

Perimeter clarification request: Noetfield outside retail payment activities.
Historical reference — authoritative legal position: `noetfield-rpaa-legal-opinion-letter-v1-1`.
""",
    "noetfield-bank-ready-institutional-document-v1.md": """# Bank-Ready Institutional Document (2026)

Document key: `noetfield-bank-ready-institutional-document-v1`

**Active investor / institutional narrative SOT.** Non-custodial governance + intelligence;
no instruction transmission; TrustField or licensed partners execute; RPAA/MSB non-applicability.
""",
    "noetfield-master-blueprint-comparative-analysis-fa-v1.md": """# Master Blueprint Comparative Analysis (Persian)

Document key: `noetfield-master-blueprint-comparative-analysis-fa-v1`

Compares orchestration-PSP blueprint (payment initiation, routing) vs governance-only blueprint.

**Strategic alignment (2026):** GCIP v4 + non-custodial governance path is canonical.
Orchestration/wallet/Kavodax-class models are prohibited positioning drafts for Noetfield identity.
""",
    "noetfield-master-blueprint-kavodax-benchmark-v1.md": """# Master Blueprint — Kavodax Benchmark

Document key: `noetfield-master-blueprint-kavodax-benchmark-v1`

**PROHIBITED POSITIONING DRAFT.** Implies wallet UX, settlement orchestration, instruction layer,
internal ledger with transaction states — conflicts with Constitution GCIP v4 and A9–A11.

Retained only as negative reference for bank conversations.
""",
    "noetfield-master-blueprint-non-custodial-governance-v1.md": """# Master Blueprint — Non-Custodial Governance

Document key: `noetfield-master-blueprint-non-custodial-governance-v1`

Aligns with GCIP v4: governance-only, client approves execution with licensed partner.
Methodology reference; subordinate to `noetfield-constitution-gcip-v4`.
""",
    "noetfield-operator-hardware-selection-macbook-v1.md": """# Operator Hardware Selection

Document key: `noetfield-operator-hardware-selection-macbook-v1`

Founder operator equipment only (M4 Pro 32GB recommended). **Not** Noetfield product SOT.
""",
    "noetfield-payment-orchestration-meta-gateway-v1.md": """# Payment Orchestration Meta-Gateway Blueprint

Document key: `noetfield-payment-orchestration-meta-gateway-v1`

**PROHIBITED POSITIONING DRAFT.** Meta-gateway / Stripe-Adyen routing — PSP-adjacent.
Superseded by GCIP v4 governance coordination layer identity.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_investor_positioning",
        "active_document_key": "noetfield-bank-ready-institutional-document-v1",
        "active_version": "bank-ready-v1",
        "decision": "active_source_of_truth",
        "rationale": "Counsel-grade institutional narrative without execution-ready instruction language.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_internal_ic_assessment",
        "active_document_key": "noetfield-ic-diligence-memo-blackrock-style-v1",
        "active_version": "ic-memo-v1",
        "decision": "active_source_of_truth",
        "rationale": "Neutral IC diligence framing and de-risking checklist for fundraising readiness.",
        "confidence": 0.88,
    },
    {
        "domain": "noetfield_accelerator_cdl",
        "active_document_key": "noetfield-bc-tech-cdl-one-pager-locked-v1",
        "active_version": "cdl-locked-v1",
        "decision": "active_source_of_truth",
        "rationale": "RPAA-safe CDL/BC Tech one-pager; supersedes venture and EGEL draft variants.",
        "confidence": 0.91,
    },
    {
        "domain": "noetfield_accelerator_spark",
        "active_document_key": "noetfield-spark-centre-one-pager-v1",
        "active_version": "spark-v1",
        "decision": "active_source_of_truth",
        "rationale": "Locked Spark Centre accelerator narrative for Ontario SME governance wedge.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_positioning_lineage_analysis",
        "active_document_key": "noetfield-master-blueprint-comparative-analysis-fa-v1",
        "active_version": "blueprint-compare-fa-v1",
        "decision": "active_source_of_truth",
        "rationale": "Authoritative orchestration vs governance blueprint comparison for 2026 Canada strategy.",
        "confidence": 0.92,
    },
    {
        "domain": "noetfield_regulatory_submissions",
        "active_document_key": "noetfield-rbc-finsec-submission-v1",
        "active_version": "submissions-index-v1",
        "decision": "reference_index",
        "rationale": "Historical RBC/BoC submission corpus; live legal SOT remains RPAA opinion v1.1.",
        "confidence": 0.85,
    },
    {
        "domain": "noetfield_operating_model_reference",
        "active_document_key": "noetfield-operating-model-2026-trustfield-v1",
        "active_version": "operating-model-2026",
        "decision": "historical_reference",
        "rationale": "TrustField RACI operating model; bank pack v2 supersedes for external diligence.",
        "confidence": 0.8,
    },
]

NEW_RULES = [
    {
        "rule_key": "prohibit-wallet-orchestration-positioning",
        "domain": "noetfield_positioning_lineage_analysis",
        "source_document_key": "noetfield-master-blueprint-kavodax-benchmark-v1",
        "activation_status": "active_design_rule",
        "rule_type": "legal_positioning",
        "summary": "No Kavodax-class wallet, instruction, or settlement-orchestration positioning for Noetfield.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "prohibit-meta-gateway-psp-framing",
        "domain": "noetfield_positioning_lineage_analysis",
        "source_document_key": "noetfield-payment-orchestration-meta-gateway-v1",
        "activation_status": "active_design_rule",
        "rule_type": "legal_positioning",
        "summary": "No Stripe/Adyen meta-gateway or payment-orchestration category claims.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "spark-centre-governance-only-narrative",
        "domain": "noetfield_accelerator_spark",
        "source_document_key": "noetfield-spark-centre-one-pager-v1",
        "activation_status": "active_design_rule",
        "rule_type": "gtm",
        "summary": "Spark Centre materials use governance OS framing; no TrustField execution dependency in copy.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "cdl-one-pager-locked-external-default",
        "domain": "noetfield_accelerator_cdl",
        "source_document_key": "noetfield-bc-tech-cdl-one-pager-locked-v1",
        "activation_status": "active_design_rule",
        "rule_type": "gtm",
        "summary": "BC Tech/CDL external circulation uses locked one-pager, not venture or EGEL drafts.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "investor-memo-no-execution-ready-instructions",
        "domain": "noetfield_investor_positioning",
        "source_document_key": "noetfield-bank-ready-institutional-document-v1",
        "activation_status": "active_design_rule",
        "rule_type": "legal_positioning",
        "summary": "Tier-1 investor copy must not claim execution-ready instructions or routing layers.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "hardware-docs-excluded-from-product-sot",
        "domain": "operator_equipment",
        "source_document_key": "noetfield-operator-hardware-selection-macbook-v1",
        "activation_status": "reference_only",
        "rule_type": "documentation_governance",
        "summary": "Operator laptop selection docs are not product or regulatory SOT.",
        "implementation_target": "source_of_truth_registry",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-016

Investor memos, IC diligence, BC Tech/CDL and Spark Centre one-pagers, bank submissions,
master blueprint lineage (orchestration vs governance), and prohibited positioning drafts.

## Active external GTM (by audience)

| Audience | Active document |
|----------|-----------------|
| Tier-1 / institutional | `noetfield-bank-ready-institutional-document-v1` |
| CDL / BC Tech | `noetfield-bc-tech-cdl-one-pager-locked-v1` |
| Spark Centre | `noetfield-spark-centre-one-pager-v1` |
| Pitch deck (slides) | `noetfield-cdl-pitch-deck-v3-1` (batch 015) |

## Golden L0 (unchanged)

`noetfield-constitution-gcip-v4` — Kavodax and meta-gateway blueprints are **prohibited** drafts.

## Legal authority (unchanged)

`noetfield-rpaa-legal-opinion-letter-v1-1` + `noetfield-bank-integration-pack-v2`
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-016", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-016"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-016/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-016",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-13"

    rules["registry_version"] = "2026-05-29-rules-13"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
