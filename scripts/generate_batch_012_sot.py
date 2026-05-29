#!/usr/bin/env python3
"""Generate batch 012 bank governance, GCIP L0-L5, and document hierarchy registry."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-012"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-bank-integration-pack-v2.md",
        "document_key": "noetfield-bank-integration-pack-v2",
        "title": "Noetfield Bank Integration Pack v2.0 (Canada-Safe)",
        "domain": "noetfield_bank_governance_integration",
        "version_label": "bank-integration-v2.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["noetfield-cross-layer-integration-spec-v1"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-governance-infrastructure-positioning-v1.md",
        "document_key": "noetfield-governance-infrastructure-positioning-v1",
        "title": "Noetfield — Deterministic Governance Infrastructure (Institutional Positioning)",
        "domain": "noetfield_bank_governance_integration",
        "version_label": "institutional-positioning-v1",
        "classification": "active_commercial_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-bank-due-diligence-deck-v1.md",
        "document_key": "noetfield-bank-due-diligence-deck-v1",
        "title": "Noetfield Bank Due Diligence Deck v1.0 (RBC/OSFI Format)",
        "domain": "noetfield_bank_due_diligence",
        "version_label": "due-diligence-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-bank-grade-implementation-design-v1.md",
        "document_key": "noetfield-bank-grade-implementation-design-v1",
        "title": "Noetfield Bank-Grade Implementation Design v1.0",
        "domain": "noetfield_bank_production_architecture",
        "version_label": "bank-impl-design-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-master-document-directory-l0-l5-v1.md",
        "document_key": "noetfield-master-document-directory-l0-l5-v1",
        "title": "Noetfield Master Document Directory — L0–L5 Final Stack v1.0",
        "domain": "noetfield_gcip_document_hierarchy",
        "version_label": "master-directory-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-l3-execution-engine-egs-v2.md",
        "document_key": "noetfield-l3-execution-engine-egs-v2",
        "title": "Noetfield L3 Execution Engine (EGS v2.0) — Enforcement-Only",
        "domain": "noetfield_l3_egs_runtime",
        "version_label": "egs-v2.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-cross-layer-integration-spec-v1.md",
        "document_key": "noetfield-cross-layer-integration-spec-v1",
        "title": "Noetfield Cross-Layer Integration Spec v1.0 (L0–L4)",
        "domain": "noetfield_gcip_document_hierarchy",
        "version_label": "cross-layer-v1.0",
        "classification": "superseded_for_regulated_execution",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-bank-integration-pack-v2",
    },
    {
        "file": "noetfield-document-hierarchy-structural-stack-fa.md",
        "document_key": "noetfield-document-hierarchy-structural-stack-fa",
        "title": "Noetfield Document Hierarchy — Full Structural Stack (Persian)",
        "domain": "noetfield_gcip_document_hierarchy",
        "version_label": "hierarchy-stack-fa-v1",
        "classification": "active_operational_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-sot-vs-layers-clarification-fa.md",
        "document_key": "noetfield-sot-vs-layers-clarification-fa",
        "title": "SoT vs L0–L3 Layer Clarification (Persian)",
        "domain": "noetfield_gcip_document_hierarchy",
        "version_label": "sot-layers-fa-v1",
        "classification": "reference_methodology",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-layer-architecture-unified-map-fa.md",
        "document_key": "noetfield-layer-architecture-unified-map-fa",
        "title": "Unified Layer Architecture Map — Runtime vs Law (Persian)",
        "domain": "noetfield_gcip_document_hierarchy",
        "version_label": "unified-map-fa-v1",
        "classification": "reference_methodology",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-agent-governance-executive-bundle-duplicate.md",
        "document_key": "noetfield-agent-governance-executive-bundle-duplicate",
        "title": "Agent Catalog + Evidence Pack Executive Bundle (Duplicate)",
        "domain": "noetfield_agent_catalog",
        "version_label": "exec-bundle-dup",
        "classification": "duplicate",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-agent-catalog-bank-grade-v1",
    },
    {
        "file": "noetfield-v2-temporal-governance-duplicate-bundle.md",
        "document_key": "noetfield-v2-temporal-governance-duplicate-bundle",
        "title": "v2 Temporal Governance OS Executive Bundle (Duplicate)",
        "domain": "noetfield_temporal_governance_v2",
        "version_label": "v2-bundle-dup",
        "classification": "duplicate",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-v2-temporal-governance-os-bank-grade",
    },
]

BODIES = {
    "noetfield-bank-integration-pack-v2.md": """# Noetfield Bank Integration Pack v2.0

Document key: `noetfield-bank-integration-pack-v2`

**Canonical regulated-financial governance SOT.** Canada-safe (RPAA / FINTRAC / OSFI boundary-aligned).
Non-custodial, non-execution, pre-execution governance coordination only.

## Position

Enterprise → Noetfield L0–L5 + SEOP → GHP → NIG → Bank/PSP/MSB → settlement rails

## Artifacts

- **CDA** — internal governance normalization (no accounts, routing, payment, settlement fields)
- **GHP** — institution-facing handoff (governance metadata only)
- **Enforcement envelope** — governance-state metadata, NOT execution triggers

## NIG

Translation/normalization boundary only. Forbidden: execution routing, transaction trigger, settlement.

## NF-CHAIN-LOCK

`H = SHA-256(L0_state + L4_snapshot + system_version)` — mismatch → C3 HARD STOP

## Regulatory

NOT MSB/PSP/custodian/settlement operator. Execution authority exclusively external institutions.
""",
    "noetfield-governance-infrastructure-positioning-v1.md": """# Noetfield Governance Infrastructure Positioning

Document key: `noetfield-governance-infrastructure-positioning-v1`

Institutional executive summary: pre-execution coordination layer, CDA/GHP outputs,
NF-CHAIN-LOCK integrity, RPAA/FINTRAC/OSFI-safe positioning. Commercial reference aligned with bank integration pack v2.
""",
    "noetfield-bank-due-diligence-deck-v1.md": """# Noetfield Bank Due Diligence Deck v1.0

Document key: `noetfield-bank-due-diligence-deck-v1`

RBC/OSFI/institutional review format: problem statement, CDA/GHP model, NIG boundary,
EGS hard-stop rules, NF-CHAIN-LOCK, audit traceability, explicit non-execution architecture.

For enterprise diligence and sandbox submissions; complements TrustField / Copilot Governance wedge.
""",
    "noetfield-bank-grade-implementation-design-v1.md": """# Noetfield Bank-Grade Implementation Design v1.0

Document key: `noetfield-bank-grade-implementation-design-v1`

Production multi-service topology:

- Edge: API Gateway, identity, policy pre-check
- Core: L1 normalization → CDA/PHO → MECR (L2) stateless cluster
- L3 EGS: enforcement + append-only audit (no financial logic persistence)
- L4: SoT graph (reference/trace only — Neo4j-style index, no decision logic)

Sequence: intake → auth → L1 → CDA → MECR → EGS → L4 trace → external handoff.

Failure modes: L2 mismatch → REWRITE; SoT orphan → REJECT; boundary violation → HARD BLOCK.
""",
    "noetfield-master-document-directory-l0-l5-v1.md": """# Noetfield Master Document Directory — L0–L5

Document key: `noetfield-master-document-directory-l0-l5-v1`

Canonical document stack map:

| Layer | Role | Primary artifact |
| L0 | Constitution v3.2 | Identity, boundaries, axioms |
| L1 | Product Kernel v4.0 | CDA, PHO, corridors, intent structure |
| L2 | MECR Governance Kernel | APPROVE/REJECT/REWRITE/FLAG |
| L3 | EGS Runtime | Enforce L2 only; external trigger |
| L4 | SoT Registry | Reference index — no decisions |
| L5 | NF-CHAIN-LOCK | Integrity binding |

L4 answers "where defined" not "what to do". Pipeline: L0→L1→L2→L3 with L4 observability.
""",
    "noetfield-l3-execution-engine-egs-v2.md": """# Noetfield L3 Execution Engine (EGS v2.0)

Document key: `noetfield-l3-execution-engine-egs-v2`

Enforcement-only runtime. **Subordinate to** `noetfield-bank-integration-pack-v2` on all execution boundaries.

## Rules

- R1: L2 supremacy — cannot override REJECT
- R3: Execute forward only if APPROVE + SAFE + INSIDE + valid SoT binding
- R4–R5: No internal financial logic; external banks/PSP/MSB execute EFT/FX/settlement

Logs immutable audit per action. Does NOT evaluate intent or mutate CDA/PHO.
""",
    "noetfield-cross-layer-integration-spec-v1.md": """# Cross-Layer Integration Spec v1.0 (Superseded for Regulated Execution)

Document key: `noetfield-cross-layer-integration-spec-v1`

Early L0–L4 flow spec. **Superseded for regulated financial execution semantics by**
`noetfield-bank-integration-pack-v2` (which prohibits Noetfield-side payment/settlement initiation).

Retained for lineage. Generic state-machine and trace rules remain reference-only where
they do not imply Noetfield execution authority.
""",
    "noetfield-document-hierarchy-structural-stack-fa.md": """# Document Hierarchy Structural Stack (Persian)

Document key: `noetfield-document-hierarchy-structural-stack-fa`

FA map: Constitution → Annex → Regulatory interpretation → Product/integration layer.
Output tracks: investor, legal (RPAA/OSFI/FINTRAC), product PRD, engineering API contracts.
""",
    "noetfield-sot-vs-layers-clarification-fa.md": """# SoT vs Layers Clarification (Persian)

Document key: `noetfield-sot-vs-layers-clarification-fa`

L4 SoT = reference map only (pointer, no decisions). L0 law, L1 behavior, L2 judge, L3 enforcer.
SoT sits outside decision pipeline as audit backbone index.
""",
    "noetfield-layer-architecture-unified-map-fa.md": """# Unified Layer Architecture Map (Persian)

Document key: `noetfield-layer-architecture-unified-map-fa`

Clarifies EGS/MECR/SoT as operational subsystems inside product layer, not replacements for Constitution/Annex.
MECR/EGS = validation/enforcement pipeline; Governance Kernel = decision; SoT = index only.
""",
    "noetfield-agent-governance-executive-bundle-duplicate.md": """# Agent Governance Executive Bundle — Duplicate

Document key: `noetfield-agent-governance-executive-bundle-duplicate`

Duplicate of batch 011 agent catalog, Evidence Pack schema, Gatekeeper UI, and 6-week sprint.
See `noetfield-agent-catalog-bank-grade-v1` and related batch 011 documents.
""",
    "noetfield-v2-temporal-governance-duplicate-bundle.md": """# v2 Temporal Governance Duplicate Bundle

Document key: `noetfield-v2-temporal-governance-duplicate-bundle`

Duplicate executive content. Superseded by `noetfield-v2-temporal-governance-os-bank-grade`.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_bank_governance_integration",
        "active_document_key": "noetfield-bank-integration-pack-v2",
        "active_version": "bank-integration-v2.0",
        "decision": "active_source_of_truth",
        "rationale": "Canonical Canada-safe CDA/GHP/NIG/SEOP model; non-custodial pre-execution governance only; supersedes conflicting L3 execution semantics.",
        "confidence": 0.95,
    },
    {
        "domain": "noetfield_bank_due_diligence",
        "active_document_key": "noetfield-bank-due-diligence-deck-v1",
        "active_version": "due-diligence-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "Institutional diligence deck for OSFI/RBC-style review of non-execution governance boundary.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_bank_production_architecture",
        "active_document_key": "noetfield-bank-grade-implementation-design-v1",
        "active_version": "bank-impl-design-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "Deployable multi-service topology: gateway, MECR cluster, EGS enforcement, SoT graph audit layer.",
        "confidence": 0.91,
    },
    {
        "domain": "noetfield_gcip_document_hierarchy",
        "active_document_key": "noetfield-master-document-directory-l0-l5-v1",
        "active_version": "master-directory-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "Master index of L0 Constitution through L5 NF-CHAIN-LOCK and layer responsibilities.",
        "confidence": 0.92,
    },
    {
        "domain": "noetfield_l3_egs_runtime",
        "active_document_key": "noetfield-l3-execution-engine-egs-v2",
        "active_version": "egs-v2.0",
        "decision": "active_source_of_truth",
        "rationale": "L3 enforcement-only runtime; external execution trigger; subordinate to bank integration pack v2 boundaries.",
        "confidence": 0.89,
    },
]

NEW_RULES = [
    {
        "rule_key": "noetfield-never-executes-payments",
        "domain": "noetfield_bank_governance_integration",
        "source_document_key": "noetfield-bank-integration-pack-v2",
        "activation_status": "active_design_rule",
        "rule_type": "regulatory_boundary",
        "summary": "Noetfield must not move funds, initiate payments, settle, hold custody, or route transactions.",
        "implementation_target": "policy_runtime",
    },
    {
        "rule_key": "ghp-no-execution-instructions",
        "domain": "noetfield_bank_governance_integration",
        "source_document_key": "noetfield-bank-integration-pack-v2",
        "activation_status": "active_design_rule",
        "rule_type": "data_contract",
        "summary": "GHP must never contain account numbers, routing, amounts, execution triggers, or settlement logic.",
        "implementation_target": "schema_validator",
    },
    {
        "rule_key": "cda-no-payment-routing-fields",
        "domain": "noetfield_bank_governance_integration",
        "source_document_key": "noetfield-bank-integration-pack-v2",
        "activation_status": "active_design_rule",
        "rule_type": "data_contract",
        "summary": "CDA must not include payment instructions, settlement parameters, or custody semantics.",
        "implementation_target": "schema_validator",
    },
    {
        "rule_key": "nig-translation-boundary-only",
        "domain": "noetfield_bank_governance_integration",
        "source_document_key": "noetfield-bank-integration-pack-v2",
        "activation_status": "active_design_rule",
        "rule_type": "integration_boundary",
        "summary": "NIG may normalize schema and compliance metadata only; forbidden to trigger transactions or settlement.",
        "implementation_target": "integration_gateway",
    },
    {
        "rule_key": "nf-chain-lock-integrity-gate",
        "domain": "noetfield_bank_governance_integration",
        "source_document_key": "noetfield-bank-integration-pack-v2",
        "activation_status": "active_design_rule",
        "rule_type": "integrity",
        "summary": "If H_current != H_manifest then C3 HARD STOP; SHA-256 over L0+L4+version.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "l3-external-execution-authority-only",
        "domain": "noetfield_l3_egs_runtime",
        "source_document_key": "noetfield-l3-execution-engine-egs-v2",
        "activation_status": "active_design_rule",
        "rule_type": "runtime_governance",
        "summary": "L3 forwards approved decisions to external institutions only; cannot override L2 REJECT.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "sot-registry-reference-only",
        "domain": "noetfield_gcip_document_hierarchy",
        "source_document_key": "noetfield-master-document-directory-l0-l5-v1",
        "activation_status": "active_design_rule",
        "rule_type": "architecture",
        "summary": "L4 SoT indexes definitions and lineage; no decisions, policy execution, or analysis.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "bank-pack-overrides-conflicting-execution-specs",
        "domain": "noetfield_bank_governance_integration",
        "source_document_key": "noetfield-bank-integration-pack-v2",
        "activation_status": "active_design_rule",
        "rule_type": "precedence",
        "summary": "On conflict, bank integration pack v2 overrides any document implying Noetfield payment execution.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "l2-mecr-final-governance-gate",
        "domain": "noetfield_gcip_document_hierarchy",
        "source_document_key": "noetfield-master-document-directory-l0-l5-v1",
        "activation_status": "active_design_rule",
        "rule_type": "architecture",
        "summary": "Only L2 MECR may emit APPROVE/REJECT/REWRITE/FLAG; L1 structures only.",
        "implementation_target": "policy_runtime",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-012

Bank Integration Pack v2 (Canada-safe), due diligence deck, production implementation design,
L0–L5 master document directory, L3 EGS v2, and Persian layer-clarification references.

## Canonical regulated financial SOT

`noetfield-bank-integration-pack-v2` — CDA, GHP, NIG, SEOP, NF-CHAIN-LOCK; non-execution.

## Superseded / duplicate

- Cross-layer integration spec (execution semantics) → bank pack v2
- Agent/governance executive bundles → batch 011

## Coexistence

- Temporal Governance v2 (batch 011) = internal agent/event OS
- Bank Integration Pack v2 = regulated financial handoff boundary
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-012", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-012"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-012/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-012",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-9"

    rules["registry_version"] = "2026-05-29-rules-9"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
