#!/usr/bin/env python3
"""Generate batch 019: corporate definitions V2.x, corridor routing drafts, gov funding narratives."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-019"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-cross-border-architecture-routing-refined-v1.md",
        "document_key": "noetfield-cross-border-architecture-routing-refined-v1",
        "title": "Cross-Border Architecture — Routing & Orchestration (Refined)",
        "domain": "noetfield_corridor_architecture_lineage",
        "version_label": "corridor-routing-refined-v1",
        "classification": "prohibited_positioning_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-corporate-definition-governance-v2-1",
    },
    {
        "file": "noetfield-corporate-definition-clean-no-msb-fa-v1.md",
        "document_key": "noetfield-corporate-definition-clean-no-msb-fa-v1",
        "title": "Corporate Definition — Clean No-MSB (Persian)",
        "domain": "noetfield_corporate_api_definition",
        "version_label": "def-clean-fa-v1",
        "classification": "superseded_gtm_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-corporate-definition-governance-v2-1",
    },
    {
        "file": "noetfield-corporate-definition-strict-instruction-fa-v1.md",
        "document_key": "noetfield-corporate-definition-strict-instruction-fa-v1",
        "title": "Corporate Definition — Strict Instruction Layer (Persian)",
        "domain": "noetfield_corporate_api_definition",
        "version_label": "def-strict-fa-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-corporate-definition-governance-v2-1.md",
        "document_key": "noetfield-corporate-definition-governance-v2-1",
        "title": "Corporate Definition — Governance Infrastructure v2.1 (Canonical)",
        "domain": "noetfield_corporate_api_definition",
        "version_label": "gov-v2.1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [
            "noetfield-corporate-definition-governance-v2",
            "noetfield-corporate-definition-clean-no-msb-fa-v1",
        ],
        "superseded_by": None,
    },
    {
        "file": "noetfield-corporate-definition-governance-v2.md",
        "document_key": "noetfield-corporate-definition-governance-v2",
        "title": "Corporate Definition — Workflow Coordination v2",
        "domain": "noetfield_corporate_api_definition",
        "version_label": "gov-v2",
        "classification": "superseded_gtm_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-corporate-definition-governance-v2-1",
    },
    {
        "file": "noetfield-psp-rpaa-lane-analysis-fa-v1.md",
        "document_key": "noetfield-psp-rpaa-lane-analysis-fa-v1",
        "title": "PSP / RPAA Lane Analysis — Execution-Adjacent (Persian)",
        "domain": "noetfield_corporate_api_definition",
        "version_label": "psp-lane-fa-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-innovate-bc-investment-narrative-v6-1.md",
        "document_key": "noetfield-innovate-bc-investment-narrative-v6-1",
        "title": "Innovate BC Investment Narrative & Strategic Brief v6.1",
        "domain": "noetfield_government_funding_bc",
        "version_label": "innovate-bc-v6.1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-enterprise-bank-pilot-brief-v6-1.md",
        "document_key": "noetfield-enterprise-bank-pilot-brief-v6-1",
        "title": "Enterprise Bank Pilot Brief — Pre-Execution Coordination v6.1",
        "domain": "noetfield_bank_enterprise_pilot",
        "version_label": "bank-pilot-v6.1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-nrc-irap-technical-prospectus-v6-1.md",
        "document_key": "noetfield-nrc-irap-technical-prospectus-v6-1",
        "title": "NRC-IRAP Technical Validation & R&D Prospectus v6.1",
        "domain": "noetfield_government_funding_irap",
        "version_label": "irap-v6.1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-oci-investment-narrative-v6-1.md",
        "document_key": "noetfield-oci-investment-narrative-v6-1",
        "title": "OCI Investment Narrative & Strategic Brief v6.1",
        "domain": "noetfield_government_funding_ontario",
        "version_label": "oci-v6.1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
]

BODIES: dict[str, str] = {
    "noetfield-cross-border-architecture-routing-refined-v1.md": """# Cross-Border Architecture — Routing Refined

Document key: `noetfield-cross-border-architecture-routing-refined-v1`

**PROHIBITED.** "Routing engine", "selects how money moves", NDAX vs Circle route comparison.
Superseded by `noetfield-corporate-definition-governance-v2-1` + GCIP v4 for identity.
""",
    "noetfield-corporate-definition-clean-no-msb-fa-v1.md": """# Corporate Definition — Clean (Persian)

Document key: `noetfield-corporate-definition-clean-no-msb-fa-v1`

Still includes routing/orchestration framing. Superseded by governance v2.1 (data/policy layer only).
""",
    "noetfield-corporate-definition-strict-instruction-fa-v1.md": """# Corporate Definition — Strict Instruction (Persian)

Document key: `noetfield-corporate-definition-strict-instruction-fa-v1`

Instruction layer without custody; still mentions routing decision — use v2.1 for external copy.
""",
    "noetfield-corporate-definition-governance-v2-1.md": """# Corporate Definition — Governance Infrastructure v2.1

Document key: `noetfield-corporate-definition-governance-v2-1`

**Canonical corporate API/governance definition (non-payment).**

Pre-execution data, policy, and system coordination only. No payment execution, settlement,
custody, or fund movement. Subordinate to Constitution GCIP v4 for legal supremacy.

Use for: partner onboarding, IRAP/OCI/BC narratives, bank pilot framing (with bank brief v6.1).
""",
    "noetfield-corporate-definition-governance-v2.md": """# Corporate Definition — v2

Document key: `noetfield-corporate-definition-governance-v2`

Workflow coordination v2. Superseded by v2.1 governance infrastructure wording.
""",
    "noetfield-psp-rpaa-lane-analysis-fa-v1.md": """# PSP / RPAA Lane Analysis (Persian)

Document key: `noetfield-psp-rpaa-lane-analysis-fa-v1`

Execution-adjacent not execution-bearing; Plaid/ZeroHash infra lane. No payment initiation,
processing, settlement orchestration, or fund handling by Noetfield.
""",
    "noetfield-innovate-bc-investment-narrative-v6-1.md": """# Innovate BC Narrative v6.1

Document key: `noetfield-innovate-bc-investment-narrative-v6-1`

Vancouver/BC commercialization: execution-adjacent coordination, non-custodial, deterministic
governance engine. Funding stack: Innovate BC, Mitacs, PacifiCan, NRC-IRAP. Aligns with CDL locked one-pager.
""",
    "noetfield-enterprise-bank-pilot-brief-v6-1.md": """# Enterprise Bank Pilot Brief v6.1

Document key: `noetfield-enterprise-bank-pilot-brief-v6-1`

12-week pilot: read/validate-only overlay, non-custodial middleware, shadow run, KPIs for STP prep
and audit lineage. Complements SME visibility read-only pilot (batch 017).
""",
    "noetfield-nrc-irap-technical-prospectus-v6-1.md": """# NRC-IRAP Technical Prospectus v6.1

Document key: `noetfield-nrc-irap-technical-prospectus-v6-1`

R&D focus: deterministic governance engine, cryptographic audit lineage, cross-institutional
signaling. Technical uncertainty framing for ITA — not payment product positioning.
""",
    "noetfield-oci-investment-narrative-v6-1.md": """# OCI Investment Narrative v6.1

Document key: `noetfield-oci-investment-narrative-v6-1`

Ontario variant of v6.1 governance coordination narrative. IPON, Mitacs, OCI co-investment stack.
Same regulatory guardrails as Innovate BC doc.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_corporate_api_definition",
        "active_document_key": "noetfield-corporate-definition-governance-v2-1",
        "active_version": "gov-v2.1",
        "decision": "active_source_of_truth",
        "rationale": "Canonical non-payment corporate definition for partners, grants, and banks; subordinate to GCIP v4 L0.",
        "confidence": 0.93,
    },
    {
        "domain": "noetfield_government_funding_bc",
        "active_document_key": "noetfield-innovate-bc-investment-narrative-v6-1",
        "active_version": "innovate-bc-v6.1",
        "decision": "active_source_of_truth",
        "rationale": "Innovate BC / PacifiCan / Vancouver ecosystem investment narrative.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_government_funding_ontario",
        "active_document_key": "noetfield-oci-investment-narrative-v6-1",
        "active_version": "oci-v6.1",
        "decision": "active_source_of_truth",
        "rationale": "OCI / Ontario commercialization and IPON funding stack narrative.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_government_funding_irap",
        "active_document_key": "noetfield-nrc-irap-technical-prospectus-v6-1",
        "active_version": "irap-v6.1",
        "decision": "active_source_of_truth",
        "rationale": "NRC-IRAP technical validation and R&D prospectus for ITA engagement.",
        "confidence": 0.91,
    },
    {
        "domain": "noetfield_bank_enterprise_pilot",
        "active_document_key": "noetfield-enterprise-bank-pilot-brief-v6-1",
        "active_version": "bank-pilot-v6.1",
        "decision": "active_source_of_truth",
        "rationale": "12-week bank innovation/risk committee pilot brief; read-validate overlay model.",
        "confidence": 0.92,
    },
]

NEW_RULES = [
    {
        "rule_key": "corporate-definition-v2-1-external-default",
        "domain": "noetfield_corporate_api_definition",
        "source_document_key": "noetfield-corporate-definition-governance-v2-1",
        "activation_status": "active_design_rule",
        "rule_type": "gtm",
        "summary": "Use governance v2.1 for partner/grant copy; subordinate to Constitution GCIP v4.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "prohibit-corridor-routing-refined-architecture",
        "domain": "noetfield_corridor_architecture_lineage",
        "source_document_key": "noetfield-cross-border-architecture-routing-refined-v1",
        "activation_status": "active_design_rule",
        "rule_type": "legal_positioning",
        "summary": "Do not use routing-engine or selects-how-money-moves corridor architecture externally.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "government-narratives-execution-adjacent-only",
        "domain": "noetfield_government_funding_bc",
        "source_document_key": "noetfield-innovate-bc-investment-narrative-v6-1",
        "activation_status": "active_design_rule",
        "rule_type": "gtm",
        "summary": "BC/Ontario/IRAP narratives must state no payment initiation, routing, or execution authority.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "bank-pilot-brief-v6-1-enterprise-default",
        "domain": "noetfield_bank_enterprise_pilot",
        "source_document_key": "noetfield-enterprise-bank-pilot-brief-v6-1",
        "activation_status": "active_design_rule",
        "rule_type": "bank_pilot",
        "summary": "Tier-1 bank committee pilots use v6.1 enterprise brief; SME wedge uses visibility read-only pilot.",
        "implementation_target": "bank_integration",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-019

Corporate definition v2.1 (canonical non-payment), prohibited corridor routing draft,
PSP/RPAA lane analysis, and government funding narratives (Innovate BC, OCI, IRAP, bank pilot).

## Hierarchy

1. **L0:** `noetfield-constitution-gcip-v4`
2. **Corporate copy:** `noetfield-corporate-definition-governance-v2-1`
3. **Bank SME wedge:** `noetfield-master-blueprint-sme-visibility-readonly-v1`
4. **Bank enterprise pilot:** `noetfield-enterprise-bank-pilot-brief-v6-1`

## Prohibited

- `noetfield-cross-border-architecture-routing-refined-v1`
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-019", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-019"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-019/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-019",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-16"

    rules["registry_version"] = "2026-05-29-rules-16"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
