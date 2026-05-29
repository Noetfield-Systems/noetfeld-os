#!/usr/bin/env python3
"""Generate batch 014 Constitution v4, L2 MECR, L3 EGS v3.2, L4 SoT, system graph."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-014"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-constitution-gcip-v4.md",
        "document_key": "noetfield-constitution-gcip-v4",
        "title": "Noetfield Constitution v4.0 (GCIP — Canada-Safe)",
        "domain": "noetfield_constitution_l0",
        "version_label": "gcip-v4.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-unified-system-graph-v1.md",
        "document_key": "noetfield-unified-system-graph-v1",
        "title": "Unified System Graph v1.0 (L0–L4 + Dataflow)",
        "domain": "noetfield_unified_system_graph",
        "version_label": "system-graph-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-mecr-governance-kernel-l2-v1.md",
        "document_key": "noetfield-mecr-governance-kernel-l2-v1",
        "title": "L2 MECR Governance Kernel v1.0",
        "domain": "noetfield_mecr_l2",
        "version_label": "mecr-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-l3-egs-runtime-v3-2.md",
        "document_key": "noetfield-l3-egs-runtime-v3-2",
        "title": "L3 EGS Runtime v3.2 (Enforcement Layer)",
        "domain": "noetfield_l3_egs_runtime",
        "version_label": "egs-v3.2",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["noetfield-l3-execution-engine-egs-v2"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-sot-registry-l4-v3-2.md",
        "document_key": "noetfield-sot-registry-l4-v3-2",
        "title": "L4 SoT Registry v3.2 (Reference-Only Index)",
        "domain": "noetfield_sot_registry_l4",
        "version_label": "sot-l4-v3.2",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-unified-tri-layer-architecture-v2.md",
        "document_key": "noetfield-unified-tri-layer-architecture-v2",
        "title": "Unified Tri-Layer Architecture v2.0 (SoT + Bank + Chain-Lock)",
        "domain": "noetfield_bank_governance_integration",
        "version_label": "tri-layer-v2.0",
        "classification": "active_architecture_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-rpaa-legal-opinion-letter-v1-1.md",
        "document_key": "noetfield-rpaa-legal-opinion-letter-v1-1",
        "title": "RPAA Legal Opinion Letter v1.1 (Bulletproof Draft)",
        "domain": "noetfield_legal_regulatory_positioning",
        "version_label": "rpaa-opinion-v1.1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["noetfield-rpaa-legal-opinion-letter-v1"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-rbc-td-procurement-diligence-pack-v1.md",
        "document_key": "noetfield-rbc-td-procurement-diligence-pack-v1",
        "title": "RBC/TD Procurement Due Diligence Pack v1.0",
        "domain": "noetfield_bank_procurement",
        "version_label": "procurement-pack-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["noetfield-bank-procurement-one-pager-rbc-td-v1"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-constitutional-annex-unified-final-duplicate.md",
        "document_key": "noetfield-constitutional-annex-unified-final-duplicate",
        "title": "Constitutional Annex Unified Final (Duplicate)",
        "domain": "noetfield_product_kernel_l1",
        "version_label": "annex-unified-dup",
        "classification": "duplicate",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitutional-annex-product-kernel-v4-en",
    },
]

BODIES = {
    "noetfield-constitution-gcip-v4.md": """# Noetfield Constitution v4.0 (GCIP)

Document key: `noetfield-constitution-gcip-v4`

**Active L0 Constitution SOT.** Supersedes conceptual v3.2 references (v1.x–v3.1 retired).

Pre-execution governance coordination protocol: deterministic, non-custodial, non-executing, non-instructional, Canada-safe.

## Immutable axioms (A1–A11)

Governance–execution separation; non-custody; execution boundary; regulatory isolation (MSB/PSP/OSFI);
determinism; neutrality; coordination principle; honest positioning; Canada regulatory supremacy;
non-actionable outputs; user-approval mandate.

## CDA

Governance-only, non-actionable. MUST NOT contain payee, amount, currency, routing, execution parameters.

## Stack position

L0 truth → L1 structure (Annex v4) → L2 MECR → L3 EGS → L4 SoT reference index.
""",
    "noetfield-unified-system-graph-v1.md": """# Unified System Graph v1.0

Document key: `noetfield-unified-system-graph-v1`

End-to-end architecture: control flow, data flow, enforcement, SoT anchoring aligned to GCIP v4.

## Flow

Intent → L1 normalize → L2 MECR → Decision → L3 EGS → APPROVED → external licensed execution.

## Failure modes

C0–C3 escalation; boundary failure (custody/payment) → L3 BLOCK; orphan state → INVALID DROP.

## Objects

Intent → Decision (L2) → ExecutionState (L3) → external outcome only.
""",
    "noetfield-mecr-governance-kernel-l2-v1.md": """# L2 MECR Governance Kernel v1.0

Document key: `noetfield-mecr-governance-kernel-l2-v1`

Deterministic decision layer: APPROVE | REJECT | REWRITE_REQUIRED | OUTSIDE_SYSTEM.

Pipeline: normalization → L0 axiom → boundary → regulatory class → C0–C3 → SoT binding → decision core.

Does NOT generate content or trigger execution. Orphan artifacts without SoT binding → REJECT.
""",
    "noetfield-l3-egs-runtime-v3-2.md": """# L3 EGS Runtime v3.2

Document key: `noetfield-l3-egs-runtime-v3-2`

**Active L3 enforcement SOT.** Supersedes EGS v2.0. Aligned to Constitution GCIP v4 + MECR.

DCER: validates MECR decisions against L0, boundary, contradiction sync, regulatory gate.
Modules: boundary_enforcement, constitution_validator, contradiction_sync, regulatory_gate.

States: APPROVED | BLOCKED | REWRITE_REQUIRED | INVALID. No decision mutation; no execution generation.
""",
    "noetfield-sot-registry-l4-v3-2.md": """# L4 SoT Registry v3.2

Document key: `noetfield-sot-registry-l4-v3-2`

Strict reference-only directory (SSoT index). Root: NF-L0-01 → Constitution GCIP v4.

Nodes index architecture, governance model, economic model, CDA schema, EGS/MECR references.
No logic, no decisions, no output generation. DCRI — deterministic constitutional reference index.
""",
    "noetfield-unified-tri-layer-architecture-v2.md": """# Unified Tri-Layer Architecture v2.0

Document key: `noetfield-unified-tri-layer-architecture-v2`

Triad: L4 SoT (what exists) + Bank GHP/NIG (what leaves safely) + NF-CHAIN-LOCK (integrity).

Failure: structural drift → MECR reject; GHP contamination → EGS C3; hash mismatch → hard stop.

Complements `noetfield-bank-integration-pack-v2` and Constitution v4.
""",
    "noetfield-rpaa-legal-opinion-letter-v1-1.md": """# RPAA Legal Opinion Letter v1.1

Document key: `noetfield-rpaa-legal-opinion-letter-v1-1`

**Active legal SOT.** Supersedes v1.0. Subordinate to Constitution GCIP v4.0 + Annex v4.0.

Non-PSP, non-MSB, non-custodial positioning contingent on non-execution and non-actionable CDA/PHO.
""",
    "noetfield-rbc-td-procurement-diligence-pack-v1.md": """# RBC/TD Procurement Due Diligence Pack v1.0

Document key: `noetfield-rbc-td-procurement-diligence-pack-v1`

Full vendor assessment: executive summary, annex architecture, bank-view diagram, CDA boundaries,
regulatory table, commercial model, deployment contexts. Supersedes one-pager as procurement SOT.
""",
    "noetfield-constitutional-annex-unified-final-duplicate.md": """# Constitutional Annex Unified — Duplicate

Document key: `noetfield-constitutional-annex-unified-final-duplicate`

Duplicate of Product Kernel v4.0 annex. Active: `noetfield-constitutional-annex-product-kernel-v4-en`.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_constitution_l0",
        "active_document_key": "noetfield-constitution-gcip-v4",
        "active_version": "gcip-v4.0",
        "decision": "active_source_of_truth",
        "rationale": "L0 GCIP Constitution v4.0 with A1–A11 axioms; supersedes all prior constitution version references.",
        "confidence": 0.96,
    },
    {
        "domain": "noetfield_unified_system_graph",
        "active_document_key": "noetfield-unified-system-graph-v1",
        "active_version": "system-graph-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "Canonical L0–L4 control/data flow, branching, and failure-mode graph.",
        "confidence": 0.92,
    },
    {
        "domain": "noetfield_mecr_l2",
        "active_document_key": "noetfield-mecr-governance-kernel-l2-v1",
        "active_version": "mecr-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "L2 deterministic governance decision engine with C0–C3 and SoT binding validation.",
        "confidence": 0.93,
    },
    {
        "domain": "noetfield_sot_registry_l4",
        "active_document_key": "noetfield-sot-registry-l4-v3-2",
        "active_version": "sot-l4-v3.2",
        "decision": "active_source_of_truth",
        "rationale": "L4 reference-only index rooted at NF-L0-01; no runtime logic.",
        "confidence": 0.92,
    },
    {
        "domain": "noetfield_l3_egs_runtime",
        "active_document_key": "noetfield-l3-egs-runtime-v3-2",
        "active_version": "egs-v3.2",
        "decision": "active_source_of_truth",
        "rationale": "L3 constitutional enforcement runtime; supersedes EGS v2.0.",
        "confidence": 0.91,
    },
    {
        "domain": "noetfield_legal_regulatory_positioning",
        "active_document_key": "noetfield-rpaa-legal-opinion-letter-v1-1",
        "active_version": "rpaa-opinion-v1.1",
        "decision": "active_source_of_truth",
        "rationale": "Updated RPAA/FINTRAC/OSFI opinion aligned to Constitution v4 and Annex v4.",
        "confidence": 0.91,
    },
    {
        "domain": "noetfield_bank_procurement",
        "active_document_key": "noetfield-rbc-td-procurement-diligence-pack-v1",
        "active_version": "procurement-pack-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "Full RBC/TD vendor diligence pack with architecture annex and diagram.",
        "confidence": 0.9,
    },
]

NEW_RULES = [
    {
        "rule_key": "constitution-gcip-v4-supremacy",
        "domain": "noetfield_constitution_l0",
        "source_document_key": "noetfield-constitution-gcip-v4",
        "activation_status": "active_design_rule",
        "rule_type": "legal_hierarchy",
        "summary": "GCIP Constitution v4.0 axioms override all lower layers on conflict.",
        "implementation_target": "policy_runtime",
    },
    {
        "rule_key": "mecr-deterministic-decision-only",
        "domain": "noetfield_mecr_l2",
        "source_document_key": "noetfield-mecr-governance-kernel-l2-v1",
        "activation_status": "active_design_rule",
        "rule_type": "runtime_governance",
        "summary": "L2 MECR emits governance decisions only; no content generation or execution triggers.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "mecr-contradiction-c0-c3-taxonomy",
        "domain": "noetfield_mecr_l2",
        "source_document_key": "noetfield-mecr-governance-kernel-l2-v1",
        "activation_status": "active_design_rule",
        "rule_type": "runtime_governance",
        "summary": "C3 axiom violation hard-rejects; C1 rewrite; C2 reject; C0 proceed.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "egs-l0-supremacy-lock",
        "domain": "noetfield_l3_egs_runtime",
        "source_document_key": "noetfield-l3-egs-runtime-v3-2",
        "activation_status": "active_design_rule",
        "rule_type": "runtime_governance",
        "summary": "EGS blocks immediately on L0/GCIP violation; cannot override MECR with execution.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "sot-l4-no-logic-no-output",
        "domain": "noetfield_sot_registry_l4",
        "source_document_key": "noetfield-sot-registry-l4-v3-2",
        "activation_status": "active_design_rule",
        "rule_type": "architecture",
        "summary": "L4 may only map references; forbidden to run algorithms or emit CDAs/decisions.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "user-approval-mandate-axiom-a11",
        "domain": "noetfield_constitution_l0",
        "source_document_key": "noetfield-constitution-gcip-v4",
        "activation_status": "active_design_rule",
        "rule_type": "product_governance",
        "summary": "Users must explicitly approve execution pathways; no autonomous pathway selection.",
        "implementation_target": "workflow_runtime",
    },
]

INVENTORY_SUPERSESSIONS = {
    "noetfield-rpaa-legal-opinion-letter-v1": "noetfield-rpaa-legal-opinion-letter-v1-1",
    "noetfield-bank-procurement-one-pager-rbc-td-v1": "noetfield-rbc-td-procurement-diligence-pack-v1",
    "noetfield-l3-execution-engine-egs-v2": "noetfield-l3-egs-runtime-v3-2",
}


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-014

Constitution GCIP v4.0 (L0), unified system graph, L2 MECR, L3 EGS v3.2, L4 SoT v3.2,
tri-layer architecture, RPAA opinion v1.1, RBC/TD procurement pack.

## Canonical stack (now complete L0–L4)

L0 Constitution v4 → L1 Annex v4 (batch 013) → L2 MECR → L3 EGS v3.2 → L4 SoT v3.2

## Supersedes in-registry

- RPAA opinion v1.0 → v1.1
- Procurement one-pager → full diligence pack
- EGS v2.0 → v3.2
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-014", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-014"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-014/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-014",
            }
        )

    for doc in inventory["documents"]:
        key = doc["document_key"]
        if key in INVENTORY_SUPERSESSIONS:
            doc["superseded_by"] = INVENTORY_SUPERSESSIONS[key]
            doc["status"] = "superseded"

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-11"

    rules["registry_version"] = "2026-05-29-rules-11"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
