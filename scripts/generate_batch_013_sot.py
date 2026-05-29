#!/usr/bin/env python3
"""Generate batch 013 legal, product kernel v4, and bank procurement registry."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-013"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-rpaa-legal-opinion-letter-v1.md",
        "document_key": "noetfield-rpaa-legal-opinion-letter-v1",
        "title": "RPAA Legal Opinion Letter v1.0 (Bulletproof Draft)",
        "domain": "noetfield_legal_regulatory_positioning",
        "version_label": "rpaa-opinion-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["noetfield-legal-counsel-memorandum-rpaa-draft"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-legal-counsel-memorandum-rpaa-draft.md",
        "document_key": "noetfield-legal-counsel-memorandum-rpaa-draft",
        "title": "Legal Counsel Memorandum — RPAA/FINTRAC/OSFI (Draft)",
        "domain": "noetfield_legal_regulatory_positioning",
        "version_label": "counsel-memo-draft-v1",
        "classification": "superseded_legal_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-rpaa-legal-opinion-letter-v1",
    },
    {
        "file": "noetfield-constitutional-annex-product-kernel-v4-en.md",
        "document_key": "noetfield-constitutional-annex-product-kernel-v4-en",
        "title": "Constitutional Annex — Product Kernel v4.0 (English)",
        "domain": "noetfield_product_kernel_l1",
        "version_label": "product-kernel-v4.0-en",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [
            "noetfield-product-kernel-schedule-v4-duplicate",
        ],
        "superseded_by": None,
    },
    {
        "file": "noetfield-constitutional-annex-product-kernel-v4-fa.md",
        "document_key": "noetfield-constitutional-annex-product-kernel-v4-fa",
        "title": "Constitutional Annex — Product Kernel v4.0 (Persian)",
        "domain": "noetfield_product_kernel_l1",
        "version_label": "product-kernel-v4.0-fa",
        "classification": "active_operational_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-product-kernel-schedule-v4-duplicate.md",
        "document_key": "noetfield-product-kernel-schedule-v4-duplicate",
        "title": "Constitution Schedule v4.0 Product Kernel (Duplicate)",
        "domain": "noetfield_product_kernel_l1",
        "version_label": "schedule-v4-dup",
        "classification": "duplicate",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitutional-annex-product-kernel-v4-en",
    },
    {
        "file": "noetfield-product-kernel-v4-design-assessment.md",
        "document_key": "noetfield-product-kernel-v4-design-assessment",
        "title": "Product Kernel v4.0 — Design Strength Assessment",
        "domain": "noetfield_product_kernel_l1",
        "version_label": "v4-assessment-v1",
        "classification": "reference_only",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-bank-procurement-one-pager-rbc-td-v1.md",
        "document_key": "noetfield-bank-procurement-one-pager-rbc-td-v1",
        "title": "Bank Procurement One-Pager (RBC/TD Format)",
        "domain": "noetfield_bank_procurement",
        "version_label": "procurement-one-pager-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-bank-implementation-unified-canonical-v2.md",
        "document_key": "noetfield-bank-implementation-unified-canonical-v2",
        "title": "Bank-Grade Implementation System v2.0 (Unified Canonical)",
        "domain": "noetfield_bank_governance_integration",
        "version_label": "unified-impl-v2.0",
        "classification": "active_unified_reference",
        "status": "reference",
        "supersedes": ["noetfield-bank-implementation-layer-mapping-v1"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-bank-implementation-layer-mapping-v1.md",
        "document_key": "noetfield-bank-implementation-layer-mapping-v1",
        "title": "Bank Implementation Layer Mapping v1.0",
        "domain": "noetfield_bank_governance_integration",
        "version_label": "layer-mapping-v1",
        "classification": "superseded_implementation_reference",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-bank-implementation-unified-canonical-v2",
    },
    {
        "file": "noetfield-nf-chain-lock-manifest-layer-spec-v1.md",
        "document_key": "noetfield-nf-chain-lock-manifest-layer-spec-v1",
        "title": "NF-CHAIN-LOCK Manifest Layer — Compile-Time Integrity Spec",
        "domain": "noetfield_bank_governance_integration",
        "version_label": "nf-chain-lock-manifest-v1",
        "classification": "active_compliance_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
]

BODIES = {
    "noetfield-rpaa-legal-opinion-letter-v1.md": """# RPAA Legal Opinion Letter v1.0

Document key: `noetfield-rpaa-legal-opinion-letter-v1`

**Active legal/regulatory positioning SOT.** Subordinate to Constitution v3.2 Golden + Product Kernel v4.0.

## Conclusion (draft counsel position)

Noetfield is NOT a PSP (RPAA), NOT an MSB (FINTRAC/PCMLTFA), NOT custodial/settlement under OSFI —
when operated as governance-only pre-execution coordination.

## Determinative conditions

- Non-execution: no payment triggers, instructions, or execution-ready messages
- Non-actionability: CDA/PHO informational and structural only
- No funds proximity: no hold, route, or intermediate funds
- Partner execution independence: banks/PSP/MSB execute exclusively

## CDA legal class

Non-actionable governance representation — not a substitute payment message.

## Conditions precedent

Opinion invalid if execution-triggering, instruction-derivable PHO, or funds touch system boundary.
""",
    "noetfield-legal-counsel-memorandum-rpaa-draft.md": """# Legal Counsel Memorandum — RPAA Draft

Document key: `noetfield-legal-counsel-memorandum-rpaa-draft`

Earlier counsel draft with RPAA/FINTRAC/OSFI tables and CDA risk review.
**Superseded by** `noetfield-rpaa-legal-opinion-letter-v1` for active legal SOT.
""",
    "noetfield-constitutional-annex-product-kernel-v4-en.md": """# Constitutional Annex — Product Kernel v4.0

Document key: `noetfield-constitutional-annex-product-kernel-v4-en`

**Active L1 Product Kernel SOT.** Strictly subordinate to Constitution v3.2 (supremacy clause).

## Principles

P1 User-approved pathways | P2 Partner-executed only | P3 CDA + PHO governance-only |
P4 Zero instruction transmission | P5 Zero custody | P6 Corridor modularity (config only)

## Topology

USER → Noetfield (CDA + PHO) → Licensed Partner → execution/settlement

## Modules

Corridor (config), Partner integration (read-only Noetfield / write-only partner),
Trust Brief (not a receipt), SLA intelligence (ranking only, no execution influence).

## Safety S1–S5

No execution API calls; PHO without accounts/amounts/routing; user authority required.

## Economic model

Allowed: SaaS, governance API, per-CDA. Prohibited: FX spread, transaction commission, settlement-linked revenue.
""",
    "noetfield-constitutional-annex-product-kernel-v4-fa.md": """# Constitutional Annex — Product Kernel v4.0 (Persian)

Document key: `noetfield-constitutional-annex-product-kernel-v4-fa`

Persian operational reference for Product Kernel v4.0. Mirrors English annex;
subordinate to Constitution v3.2. Active operational reference for FA workflows.
""",
    "noetfield-product-kernel-schedule-v4-duplicate.md": """# Product Kernel Schedule v4.0 — Duplicate

Document key: `noetfield-product-kernel-schedule-v4-duplicate`

Duplicate of Constitutional Annex Product Kernel v4.0. Superseded by English annex SOT.
""",
    "noetfield-product-kernel-v4-design-assessment.md": """# Product Kernel v4.0 Design Assessment

Document key: `noetfield-product-kernel-v4-design-assessment`

Reference: strengths — user-approved execution, partner executes, no custody,
governance/execution separation, corridor modularity, SLA non-executional, economic separation.
""",
    "noetfield-bank-procurement-one-pager-rbc-td-v1.md": """# Bank Procurement One-Pager (RBC/TD)

Document key: `noetfield-bank-procurement-one-pager-rbc-td-v1`

Vendor assessment format: pre-execution governance layer, CDA definition and prohibitions,
regulatory positioning (non-PSP/non-MSB), safeguards, commercial model (per-CDA),
strategic fit for banks, risk classification summary.
""",
    "noetfield-bank-implementation-unified-canonical-v2.md": """# Bank Implementation Unified Canonical v2.0

Document key: `noetfield-bank-implementation-unified-canonical-v2`

Unified L0–L5 stack + GHP/NIG/bank flow. Complements `noetfield-bank-integration-pack-v2`.
Consolidates layer mapping v1 into single canonical reference for bank-grade presentations.

Stack: L0 Constitution → L1 Kernel → L2 MECR → L3 EGS → L4 SoT → L5 NF-CHAIN-LOCK → external FIs.
""",
    "noetfield-bank-implementation-layer-mapping-v1.md": """# Bank Implementation Layer Mapping v1.0

Document key: `noetfield-bank-implementation-layer-mapping-v1`

Early GHP/NIG/bank integration mapping. Superseded by unified canonical v2.0.
Authority remains `noetfield-bank-integration-pack-v2` for regulated boundaries.
""",
    "noetfield-nf-chain-lock-manifest-layer-spec-v1.md": """# NF-CHAIN-LOCK Manifest Layer Spec v1

Document key: `noetfield-nf-chain-lock-manifest-layer-spec-v1`

Compile-time integrity: SOT_MANIFEST snapshot, H = SHA256(manifest), embedded in MECR/EGS.
Runtime: hash mismatch → C3 HARD STOP. Dual-manifest drift reconciliation noted as future upgrade.
Aligns with bank integration pack NF-CHAIN-LOCK formula.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_legal_regulatory_positioning",
        "active_document_key": "noetfield-rpaa-legal-opinion-letter-v1",
        "active_version": "rpaa-opinion-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "Primary RPAA/FINTRAC/OSFI legal positioning; contingent on non-execution and non-actionable CDA/PHO.",
        "confidence": 0.91,
    },
    {
        "domain": "noetfield_product_kernel_l1",
        "active_document_key": "noetfield-constitutional-annex-product-kernel-v4-en",
        "active_version": "product-kernel-v4.0-en",
        "decision": "active_source_of_truth",
        "rationale": "L1 behavior layer subordinate to Constitution v3.2; CDA/PHO, corridors, Canada-safe product rules.",
        "confidence": 0.93,
    },
    {
        "domain": "noetfield_bank_procurement",
        "active_document_key": "noetfield-bank-procurement-one-pager-rbc-td-v1",
        "active_version": "procurement-one-pager-v1",
        "decision": "active_source_of_truth",
        "rationale": "RBC/TD vendor assessment one-pager for institutional procurement and diligence.",
        "confidence": 0.9,
    },
]

NEW_RULES = [
    {
        "rule_key": "constitution-v32-supremacy-over-annex",
        "domain": "noetfield_product_kernel_l1",
        "source_document_key": "noetfield-constitutional-annex-product-kernel-v4-en",
        "activation_status": "active_design_rule",
        "rule_type": "legal_hierarchy",
        "summary": "Constitution v3.2 prevails absolutely over Product Kernel v4.0 annex on any conflict.",
        "implementation_target": "policy_runtime",
    },
    {
        "rule_key": "pho-zero-instruction-construction",
        "domain": "noetfield_product_kernel_l1",
        "source_document_key": "noetfield-constitutional-annex-product-kernel-v4-en",
        "activation_status": "active_design_rule",
        "rule_type": "data_contract",
        "summary": "PHO must not contain account numbers, amounts, routing, or settlement instructions.",
        "implementation_target": "schema_validator",
    },
    {
        "rule_key": "cda-non-actionable-governance-only",
        "domain": "noetfield_legal_regulatory_positioning",
        "source_document_key": "noetfield-rpaa-legal-opinion-letter-v1",
        "activation_status": "active_design_rule",
        "rule_type": "regulatory_boundary",
        "summary": "CDA must remain non-reconstructable into payment instructions to preserve non-PSP status.",
        "implementation_target": "schema_validator",
    },
    {
        "rule_key": "no-transaction-based-revenue-model",
        "domain": "noetfield_product_kernel_l1",
        "source_document_key": "noetfield-constitutional-annex-product-kernel-v4-en",
        "activation_status": "active_design_rule",
        "rule_type": "commercial_governance",
        "summary": "Prohibited revenue: FX spread, transaction commission, settlement-linked fees.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "user-explicit-pathway-approval-required",
        "domain": "noetfield_product_kernel_l1",
        "source_document_key": "noetfield-constitutional-annex-product-kernel-v4-en",
        "activation_status": "active_design_rule",
        "rule_type": "product_governance",
        "summary": "Execution pathways require explicit user selection and confirmation; no auto-select.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "legal-position-contingent-on-non-execution",
        "domain": "noetfield_legal_regulatory_positioning",
        "source_document_key": "noetfield-rpaa-legal-opinion-letter-v1",
        "activation_status": "active_design_rule",
        "rule_type": "regulatory_boundary",
        "summary": "Non-PSP/non-MSB opinion void if system introduces execution triggers or funds proximity.",
        "implementation_target": "policy_runtime",
    },
    {
        "rule_key": "nf-chain-lock-compile-time-manifest",
        "domain": "noetfield_bank_governance_integration",
        "source_document_key": "noetfield-nf-chain-lock-manifest-layer-spec-v1",
        "activation_status": "active_design_rule",
        "rule_type": "integrity",
        "summary": "SOT manifest hash at compile-time; runtime drift vs manifest triggers C3 HARD STOP.",
        "implementation_target": "workflow_runtime",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-013

RPAA legal opinion, Product Kernel v4.0 annex (EN/FA), bank procurement one-pager,
unified bank implementation v2, and NF-CHAIN-LOCK manifest spec.

## Active SOT

- Legal/regulatory: RPAA Legal Opinion Letter v1.0
- L1 Product Kernel: Constitutional Annex v4.0 (English)
- Bank procurement: RBC/TD one-pager

## Hierarchy

Constitution v3.2 (referenced, not in this batch) > Annex v4.0 > Bank Integration Pack v2 (batch 012)

## Superseded

- Counsel memorandum draft → opinion letter
- Schedule v4 duplicate → annex EN
- Layer mapping v1 → unified canonical v2
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-013", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-013"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-013/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-013",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-10"

    rules["registry_version"] = "2026-05-29-rules-10"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
