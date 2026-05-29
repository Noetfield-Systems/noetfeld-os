#!/usr/bin/env python3
"""Generate batch 018: AI Company OS stack, founder positioning, corridor & MSB narratives."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-018"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-system-architecture-v2.md",
        "document_key": "noetfield-system-architecture-v2",
        "title": "System Architecture v2 — Production AI Orchestration OS",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "arch-v2",
        "classification": "target_architecture_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-ai-company-quarter-v1.md",
        "document_key": "noetfield-ai-company-quarter-v1",
        "title": "AI Company Quarter — 90-Day Operating Simulation",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "quarter-sim-v1",
        "classification": "operating_simulation_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-ai-company-day-v1.md",
        "document_key": "noetfield-ai-company-day-v1",
        "title": "AI Company Day — Full-Day Operating Simulation",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "day-sim-v1",
        "classification": "operating_simulation_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-control-plane-spec-v1.md",
        "document_key": "noetfield-control-plane-spec-v1",
        "title": "Control Plane Spec v1 — Institutional Execution Layer",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "control-plane-v1",
        "classification": "target_architecture_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-capability-registry-v1.md",
        "document_key": "noetfield-capability-registry-v1",
        "title": "Capability Registry v1 — Structured Intelligence Map",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "cap-registry-v1",
        "classification": "target_architecture_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-execution-graph-compiler-v1.md",
        "document_key": "noetfield-execution-graph-compiler-v1",
        "title": "Execution Graph Compiler v1 — DAG Runtime",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "egc-v1",
        "classification": "target_architecture_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-runtime-execution-engine-v1.md",
        "document_key": "noetfield-runtime-execution-engine-v1",
        "title": "Runtime Execution Engine v1 — Live DAG Layer",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "runtime-v1",
        "classification": "target_architecture_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-audit-ledger-v1.md",
        "document_key": "noetfield-audit-ledger-v1",
        "title": "Audit Ledger v1 — Immutable Memory & Compliance Layer",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "audit-ledger-v1",
        "classification": "target_architecture_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-orgchart-v1.md",
        "document_key": "noetfield-orgchart-v1",
        "title": "AI-First Organizational Structure — OrgChart v1",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "orgchart-v1",
        "classification": "operating_simulation_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-two-layer-positioning-system-v1.md",
        "document_key": "noetfield-two-layer-positioning-system-v1",
        "title": "Two-Layer Institutional Positioning (Public vs Private)",
        "domain": "noetfield_founder_capital_positioning",
        "version_label": "two-layer-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-two-layer-positioning-refined-v1-1.md",
        "document_key": "noetfield-two-layer-positioning-refined-v1-1",
        "title": "Two-Layer Positioning — Refined v1.1",
        "domain": "noetfield_founder_capital_positioning",
        "version_label": "two-layer-v1.1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["noetfield-two-layer-positioning-system-v1"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-two-layer-positioning-capital-markets-v1.md",
        "document_key": "noetfield-two-layer-positioning-capital-markets-v1",
        "title": "Two-Layer Positioning — Capital Markets 10/10 Edition",
        "domain": "noetfield_founder_capital_positioning",
        "version_label": "capital-markets-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-msb-partnership-narrative-fa-v1.md",
        "document_key": "noetfield-msb-partnership-narrative-fa-v1",
        "title": "MSB Partnership Narrative (Persian) — Orchestration Framing",
        "domain": "noetfield_msb_partner_narrative",
        "version_label": "msb-narr-fa-v1",
        "classification": "prohibited_positioning_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-master-blueprint-sme-visibility-readonly-v1",
    },
    {
        "file": "noetfield-ai-artifact-production-pipeline-v1.md",
        "document_key": "noetfield-ai-artifact-production-pipeline-v1",
        "title": "AI Artifact Production Pipeline — Multi-Model Stack",
        "domain": "noetfield_ai_company_os_lineage",
        "version_label": "artifact-pipeline-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-product-page-narrative-settlement-orchestration-fa-v1.md",
        "document_key": "noetfield-product-page-narrative-settlement-orchestration-fa-v1",
        "title": "Product Page Narrative — Settlement Orchestration (Persian)",
        "domain": "noetfield_commercial_gtm",
        "version_label": "product-page-orch-fa-v1",
        "classification": "prohibited_positioning_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-bc-tech-cdl-one-pager-locked-v1",
    },
    {
        "file": "noetfield-ai-governance-system-v1.md",
        "document_key": "noetfield-ai-governance-system-v1",
        "title": "AI Governance System — Propose vs Execute Separation",
        "domain": "noetfield_ai_governance_methodology",
        "version_label": "ai-gov-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-corridor-architecture-execution-realistic-fa-v1.md",
        "document_key": "noetfield-corridor-architecture-execution-realistic-fa-v1",
        "title": "CAD→INR Corridor Architecture — Execution-Realistic (Persian)",
        "domain": "noetfield_corridor_architecture_lineage",
        "version_label": "corridor-realistic-fa-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-corridor-architecture-stablecoin-mvp-v1.md",
        "document_key": "noetfield-corridor-architecture-stablecoin-mvp-v1",
        "title": "Corridor Architecture — Stablecoin MVP (Instruction Interface)",
        "domain": "noetfield_corridor_architecture_lineage",
        "version_label": "corridor-stablecoin-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-corridor-architecture-routing-intelligence-v1.md",
        "document_key": "noetfield-corridor-architecture-routing-intelligence-v1",
        "title": "Corridor Architecture — Routing Intelligence (Circle/NDAX)",
        "domain": "noetfield_corridor_architecture_lineage",
        "version_label": "corridor-routing-v1",
        "classification": "prohibited_positioning_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-corridor-architecture-stablecoin-mvp-v1",
    },
]

BODIES: dict[str, str] = {
    "noetfield-system-architecture-v2.md": """# System Architecture v2

Document key: `noetfield-system-architecture-v2`

10-layer AI orchestration OS: Intent API, COO orchestrator, capability registry, DAG compiler,
runtime engine, agent microservices, validation, governance kernel, execution layer, audit ledger.

**Target-state reference only.** MVP ship authority: `noetfield-v3-mvp-production-spec-final` (linear).
Aligns with Temporal Governance v2 / Copilot stack for production path.
""",
    "noetfield-ai-company-quarter-v1.md": """# AI Company Quarter v1

Document key: `noetfield-ai-company-quarter-v1`

90-day operating simulation (strategic month → execution → governance audit → optimization).
Narrative operating model, not regulatory SOT.
""",
    "noetfield-ai-company-day-v1.md": """# AI Company Day v1

Document key: `noetfield-ai-company-day-v1`

Full-day simulation: founder intent → orchestrator stand-up → agent parallel work → kernel gates.
Useful for demos; not bank perimeter definition.
""",
    "noetfield-control-plane-spec-v1.md": """# Control Plane Spec v1

Document key: `noetfield-control-plane-spec-v1`

State machine: INITIATED → INTENT_PARSED → ROUTED → GOVERNANCE_CHECKED → EXECUTED → ARCHIVED.
Hard invariants: no execution without kernel approval, full replay, no model autonomy.

Index document for AI Company OS component stack in this batch.
""",
    "noetfield-capability-registry-v1.md": """# Capability Registry v1

Document key: `noetfield-capability-registry-v1`

Quantitative model scoring and routing modes (single, pipeline, parallel). Superseded for MVP
by rule-based router in v3 production spec.
""",
    "noetfield-execution-graph-compiler-v1.md": """# Execution Graph Compiler v1

Document key: `noetfield-execution-graph-compiler-v1`

DAG construction with kernel gate injection. Roadmap tier; v3 MVP explicitly omits DAG compiler.
""",
    "noetfield-runtime-execution-engine-v1.md": """# Runtime Execution Engine v1

Document key: `noetfield-runtime-execution-engine-v1`

Live DAG execution with governance pre-checks, parallel branches, fallback models.
Maps to batch 011 Temporal kernel for enterprise path.
""",
    "noetfield-audit-ledger-v1.md": """# Audit Ledger v1

Document key: `noetfield-audit-ledger-v1`

Immutable event stream, replay modes, forensic traceability. Aligns with Copilot Trust Ledger /
Evidence Pack schema (batch 011).
""",
    "noetfield-orgchart-v1.md": """# OrgChart v1 — AI-First Company

Document key: `noetfield-orgchart-v1`

Models as directors, agents as teams, orchestrator as COO, governance kernel as board.
Operating metaphor for internal docs and investor storytelling on AI ops — not MSB-facing copy.
""",
    "noetfield-two-layer-positioning-system-v1.md": """# Two-Layer Positioning System v1

Document key: `noetfield-two-layer-positioning-system-v1`

Public LinkedIn (safe) vs private investor (SPV/deal-heavy). Superseded by refined v1.1.
""",
    "noetfield-two-layer-positioning-refined-v1-1.md": """# Two-Layer Positioning — Refined v1.1

Document key: `noetfield-two-layer-positioning-refined-v1-1`

**Active methodology** for founder capital identity separation. Never merge public/private layers.
""",
    "noetfield-two-layer-positioning-capital-markets-v1.md": """# Two-Layer Positioning — Capital Markets Edition

Document key: `noetfield-two-layer-positioning-capital-markets-v1`

Institutional-grade headlines and About text for private capital conversations (Post Oak / FO / PE).
Distinct from Noetfield GCIP corporate GTM.
""",
    "noetfield-msb-partnership-narrative-fa-v1.md": """# MSB Partnership Narrative (Persian)

Document key: `noetfield-msb-partnership-narrative-fa-v1`

**PROHIBITED.** Frames Noetfield as settlement orchestration / routing / quote engine sending
execution to MSB. Use `noetfield-master-blueprint-sme-visibility-readonly-v1` for MSB-facing narrative.
""",
    "noetfield-ai-artifact-production-pipeline-v1.md": """# AI Artifact Production Pipeline

Document key: `noetfield-ai-artifact-production-pipeline-v1`

Signal → design → draft → QA → packaging → versioning across multi-model stack.
Internal ops methodology for document generation.
""",
    "noetfield-product-page-narrative-settlement-orchestration-fa-v1.md": """# Product Page — Settlement Orchestration (Persian)

Document key: `noetfield-product-page-narrative-settlement-orchestration-fa-v1`

**PROHIBITED.** "Settlement Orchestration Layer", routing intelligence, quote engine — RPAA optics.
Website GTM: governance coordination per CDL locked one-pager / v3 landing spec.
""",
    "noetfield-ai-governance-system-v1.md": """# AI Governance System v1

Document key: `noetfield-ai-governance-system-v1`

Propose vs execute separation, policy/reasoning/validation/execution layers, HITL, multi-model consensus.
Aligns with GCIP v4 and Copilot Governance MVP.
""",
    "noetfield-corridor-architecture-execution-realistic-fa-v1.md": """# Corridor Architecture — Execution-Realistic (Persian)

Document key: `noetfield-corridor-architecture-execution-realistic-fa-v1`

CAD→FX→Circle→India liquidity/payout; policy-aware = schema formatting only.
Instruction interface framing (improved). Still corridor-product exploration, not L0 identity.
""",
    "noetfield-corridor-architecture-stablecoin-mvp-v1.md": """# Corridor Architecture — Stablecoin MVP

Document key: `noetfield-corridor-architecture-stablecoin-mvp-v1`

Non-custodial instruction interface; externalized execution; status aggregation only.
Preferred corridor doc over routing-intelligence variant.
""",
    "noetfield-corridor-architecture-routing-intelligence-v1.md": """# Corridor Architecture — Routing Intelligence

Document key: `noetfield-corridor-architecture-routing-intelligence-v1`

**PROHIBITED.** "Routing intelligence", Circle vs NDAX route comparison, orchestrates how systems move money.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_ai_company_os_lineage",
        "active_document_key": "noetfield-control-plane-spec-v1",
        "active_version": "control-plane-v1",
        "decision": "reference_index",
        "rationale": "Index for full AI Company OS target stack; MVP build remains v3 linear production spec.",
        "confidence": 0.88,
    },
    {
        "domain": "noetfield_founder_capital_positioning",
        "active_document_key": "noetfield-two-layer-positioning-refined-v1-1",
        "active_version": "two-layer-v1.1",
        "decision": "active_source_of_truth",
        "rationale": "Public vs private capital identity separation for founder LinkedIn and investor meetings.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_msb_partner_narrative",
        "active_document_key": "noetfield-master-blueprint-sme-visibility-readonly-v1",
        "active_version": "visibility-pilot-v1",
        "decision": "active_source_of_truth",
        "rationale": "MSB orchestration narrative superseded; read-only visibility pilot is bank-safe MSB story.",
        "confidence": 0.92,
    },
    {
        "domain": "noetfield_ai_governance_methodology",
        "active_document_key": "noetfield-ai-governance-system-v1",
        "active_version": "ai-gov-v1",
        "decision": "active_methodology_reference",
        "rationale": "Propose/execute separation aligns with GCIP v4 and Copilot governance product.",
        "confidence": 0.89,
    },
    {
        "domain": "noetfield_corridor_architecture_lineage",
        "active_document_key": "noetfield-corridor-architecture-stablecoin-mvp-v1",
        "active_version": "corridor-stablecoin-v1",
        "decision": "active_methodology_reference",
        "rationale": "Safest CAD→INR corridor framing as instruction interface; routing variant prohibited.",
        "confidence": 0.87,
    },
]

NEW_RULES = [
    {
        "rule_key": "ai-company-os-target-not-mvp-default",
        "domain": "noetfield_ai_company_os_lineage",
        "source_document_key": "noetfield-system-architecture-v2",
        "activation_status": "active_design_rule",
        "rule_type": "architecture_governance",
        "summary": "Architecture v2 / control plane stack is target reference; ship v3 linear MVP first.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "prohibit-msb-orchestration-routing-narrative",
        "domain": "noetfield_msb_partner_narrative",
        "source_document_key": "noetfield-msb-partnership-narrative-fa-v1",
        "activation_status": "active_design_rule",
        "rule_type": "gtm",
        "summary": "Do not use settlement orchestration or routing-engine framing in MSB partner materials.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "prohibit-settlement-orchestration-product-copy",
        "domain": "noetfield_commercial_gtm",
        "source_document_key": "noetfield-product-page-narrative-settlement-orchestration-fa-v1",
        "activation_status": "active_design_rule",
        "rule_type": "legal_positioning",
        "summary": "Product/website copy must not claim settlement orchestration or payment routing.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "two-layer-never-merge-public-private",
        "domain": "noetfield_founder_capital_positioning",
        "source_document_key": "noetfield-two-layer-positioning-refined-v1-1",
        "activation_status": "active_design_rule",
        "rule_type": "documentation_governance",
        "summary": "LinkedIn/public layer must not include SPV, placement, or deal execution language.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "corridor-no-routing-decision-authority",
        "domain": "noetfield_corridor_architecture_lineage",
        "source_document_key": "noetfield-corridor-architecture-stablecoin-mvp-v1",
        "activation_status": "active_design_rule",
        "rule_type": "legal_positioning",
        "summary": "Corridor docs: instruction formatting and status aggregation only; no routing intelligence claims.",
        "implementation_target": "gtm_policy",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-018

AI Company OS stack (v2 target architecture), founder two-layer positioning, AI governance
methodology, corridor CAD→INR lineage, and prohibited MSB/product orchestration narratives.

## Three-track reminder

| Track | Build / GTM authority |
|-------|------------------------|
| GCIP L0 | `noetfield-constitution-gcip-v4` |
| Bank pilot | `noetfield-master-blueprint-sme-visibility-readonly-v1` |
| v3 MVP ship | `noetfield-v3-mvp-production-spec-final` |
| AI OS target | Control plane + arch v2 components (this batch) |

## Prohibited in this batch

- MSB partnership narrative (orchestration)
- Product page settlement orchestration (Persian)
- Corridor routing intelligence (Circle/NDAX comparison)
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-018", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-018"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-018/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-018",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-15"

    rules["registry_version"] = "2026-05-29-rules-15"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
