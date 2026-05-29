#!/usr/bin/env python3
"""Generate batch 017: v3 AI orchestration product, SME visibility pilot, prohibited capital-execution drafts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-017"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-master-blueprint-capital-intelligence-execution-v1.md",
        "document_key": "noetfield-master-blueprint-capital-intelligence-execution-v1",
        "title": "Master Blueprint v1.0 — Capital Intelligence & Execution Infrastructure",
        "domain": "noetfield_capital_execution_lineage",
        "version_label": "capital-exec-v1",
        "classification": "prohibited_positioning_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitution-gcip-v4",
    },
    {
        "file": "noetfield-master-blueprint-sme-visibility-readonly-v1.md",
        "document_key": "noetfield-master-blueprint-sme-visibility-readonly-v1",
        "title": "Master Blueprint 2026 — SME Cross-Rail Visibility (Read-Only Pilot)",
        "domain": "noetfield_sme_visibility_pilot",
        "version_label": "visibility-pilot-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-master-blueprint-capital-execution-samara-v1.md",
        "document_key": "noetfield-master-blueprint-capital-execution-samara-v1",
        "title": "Master Blueprint 2026 — Capital Execution & RWA (Samara Alignment)",
        "domain": "noetfield_capital_execution_lineage",
        "version_label": "samara-capital-v1",
        "classification": "prohibited_positioning_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitution-gcip-v4",
    },
    {
        "file": "noetfield-unified-master-control-plane-v9.md",
        "document_key": "noetfield-unified-master-control-plane-v9",
        "title": "Unified Master Document v9 — AI Capital Execution Control Plane",
        "domain": "noetfield_capital_execution_lineage",
        "version_label": "control-plane-v9",
        "classification": "prohibited_positioning_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-constitution-gcip-v4",
    },
    {
        "file": "noetfield-lightweight-conversation-replacement-engine-v3.md",
        "document_key": "noetfield-lightweight-conversation-replacement-engine-v3",
        "title": "Lightweight Conversation Replacement Engine v3.0",
        "domain": "operator_prompt_tooling",
        "version_label": "lcre-v3",
        "classification": "active_operator_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-creation-governance-stack-separation-fa.md",
        "document_key": "noetfield-creation-governance-stack-separation-fa",
        "title": "Creation Stack vs Governance Stack Separation (Persian)",
        "domain": "noetfield_capital_execution_lineage",
        "version_label": "creation-gov-fa-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-moat-defensibility-map.md",
        "document_key": "noetfield-v3-moat-defensibility-map",
        "title": "Noetfield v3 — Moat Defensibility Map (Investor-Grade)",
        "domain": "noetfield_v3_ai_orchestration_product",
        "version_label": "moat-v3",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-mvp-production-spec-final.md",
        "document_key": "noetfield-v3-mvp-production-spec-final",
        "title": "Noetfield v3 MVP — Final Clean Production Spec",
        "domain": "noetfield_v3_ai_orchestration_product",
        "version_label": "mvp-spec-final",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-investor-memo-capital-v3.md",
        "document_key": "noetfield-v3-investor-memo-capital-v3",
        "title": "Investment Memorandum v3.0 — Deterministic Multi-Model Execution",
        "domain": "noetfield_v3_investor_gtm",
        "version_label": "capital-memo-v3",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-build-evolution-report.md",
        "document_key": "noetfield-v3-build-evolution-report",
        "title": "Build Session — Performance & Evolution Report (v1→v3 MVP)",
        "domain": "noetfield_v3_ai_orchestration_product",
        "version_label": "build-report-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-investor-one-pager-rbc-v3.md",
        "document_key": "noetfield-v3-investor-one-pager-rbc-v3",
        "title": "Noetfield v3 — Investor One-Pager (RBC / Post Oak Style)",
        "domain": "noetfield_v3_investor_gtm",
        "version_label": "one-pager-rbc-v3",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-landing-page-spec.md",
        "document_key": "noetfield-v3-landing-page-spec",
        "title": "Noetfield v3 — Conversion-Ready Landing Page Spec",
        "domain": "noetfield_v3_product_ux",
        "version_label": "landing-v3",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-pitch-deck-13-slide.md",
        "document_key": "noetfield-v3-pitch-deck-13-slide",
        "title": "Noetfield v3 — 13-Slide Investor Pitch Deck",
        "domain": "noetfield_v3_investor_gtm",
        "version_label": "deck-13-v3",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-architecture-spec-fa.md",
        "document_key": "noetfield-v3-architecture-spec-fa",
        "title": "Noetfield v3 Architecture — Persian MVP Spec",
        "domain": "noetfield_v3_ai_orchestration_product",
        "version_label": "arch-fa-v3",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-live-streaming-dashboard-spec.md",
        "document_key": "noetfield-v3-live-streaming-dashboard-spec",
        "title": "Noetfield v3 — Live Streaming Execution Dashboard Spec",
        "domain": "noetfield_v3_product_ux",
        "version_label": "live-dashboard-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-dag-animation-layer-spec.md",
        "document_key": "noetfield-v3-dag-animation-layer-spec",
        "title": "Noetfield v3 — Live DAG Animation Layer Spec",
        "domain": "noetfield_v3_product_ux",
        "version_label": "dag-ui-v1",
        "classification": "product_roadmap_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-governance-visualization-layer-spec.md",
        "document_key": "noetfield-v3-governance-visualization-layer-spec",
        "title": "Noetfield v3 — Governance Visualization Layer Spec",
        "domain": "noetfield_v3_product_ux",
        "version_label": "gov-viz-v1",
        "classification": "product_roadmap_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-execution-replay-system-spec.md",
        "document_key": "noetfield-v3-execution-replay-system-spec",
        "title": "Noetfield v3 — Execution Replay System Spec",
        "domain": "noetfield_v3_product_ux",
        "version_label": "replay-v1",
        "classification": "product_roadmap_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v3-multi-agent-contribution-timeline-spec.md",
        "document_key": "noetfield-v3-multi-agent-contribution-timeline-spec",
        "title": "Noetfield v3 — Multi-Agent Contribution Timeline Spec",
        "domain": "noetfield_v3_product_ux",
        "version_label": "agent-timeline-v1",
        "classification": "product_roadmap_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
]

BODIES: dict[str, str] = {
    "noetfield-master-blueprint-capital-intelligence-execution-v1.md": """# Master Blueprint v1.0 — Capital Intelligence & Execution

Document key: `noetfield-master-blueprint-capital-intelligence-execution-v1`

**PROHIBITED for Noetfield corporate identity.** Positions Noetfield as Execution OS, settlement
orchestrator, RWA lifecycle with settlement phases — conflicts with GCIP v4 governance-only L0.

Retain as negative reference only. Implementation SOT remains Copilot Governance MVP + Temporal v2 (batch 011).
""",
    "noetfield-master-blueprint-sme-visibility-readonly-v1.md": """# SME Cross-Rail Visibility Pilot (Read-Only)

Document key: `noetfield-master-blueprint-sme-visibility-readonly-v1`

**Active bank pilot wedge SOT.** Outbound CAD→FX→MSB→settlement observability; sandbox/shadow;
no routing influence, no execution control. North Star: read-only visibility without modifying rails.

Aligns with RBCx email template in source upload. Subordinate to Bank Integration Pack v2 + legal opinion v1.1.
""",
    "noetfield-master-blueprint-capital-execution-samara-v1.md": """# Capital Execution & RWA (Samara)

Document key: `noetfield-master-blueprint-capital-execution-samara-v1`

**PROHIBITED.** Capital execution infrastructure, settlement interoperability, execution-ready structures.
Not the Noetfield GCIP identity. Trust Brief as product here is governance diligence — use bank pack CDA/GHP framing instead.
""",
    "noetfield-unified-master-control-plane-v9.md": """# Unified Master Control Plane v9

Document key: `noetfield-unified-master-control-plane-v9`

**PROHIBITED.** Federated AI capital execution control plane, cross-rail routing surface,
execution authorization semantics — RPAA/PSP adjacency. Superseded by Constitution GCIP v4.
""",
    "noetfield-lightweight-conversation-replacement-engine-v3.md": """# Lightweight Conversation Replacement Engine v3.0

Document key: `noetfield-lightweight-conversation-replacement-engine-v3`

Operator prompt for chat compression / memory replacement. **Not** product or regulatory SOT.
Use under `operator_prompt_tooling` for founder workflows only.
""",
    "noetfield-creation-governance-stack-separation-fa.md": """# Creation vs Governance Stack (Persian)

Document key: `noetfield-creation-governance-stack-separation-fa`

Methodology: Creation OS (Claude/GPT/Cursor) separate from Governance OS (policy, audit, approve).
Maps to Constitution vs Product Kernel separation. Warns against orchestration/instruction packaging in governance layer.
""",
    "noetfield-v3-moat-defensibility-map.md": """# Noetfield v3 — Moat Defensibility Map

Document key: `noetfield-v3-moat-defensibility-map`

Investor moat stack: deterministic execution core, governance gate, audit ledger, workflow memory,
domain templates. **Product track:** AI orchestration engine — distinct from GCIP bank L0.
""",
    "noetfield-v3-mvp-production-spec-final.md": """# Noetfield v3 MVP — Final Production Spec

Document key: `noetfield-v3-mvp-production-spec-final`

**Active v3 product SOT.** Linear pipeline: Intent → Orchestrator → rule router → sequential execution
→ single governance PASS/FAIL → append-only ledger. Explicitly excludes DAG compiler, scoring router,
microservices for MVP ship. Buildable in 48h; FastAPI single service.
""",
    "noetfield-v3-investor-memo-capital-v3.md": """# Investment Memo v3 — Deterministic Multi-Model Execution

Document key: `noetfield-v3-investor-memo-capital-v3`

Institutional memo: GTU pricing, switching-cost economics, inline governance gates, forensic audit ledger.
**Scope:** AI orchestration product for regulated content/workflows — not payment execution.
""",
    "noetfield-v3-build-evolution-report.md": """# Build Evolution Report (v1→v3)

Document key: `noetfield-v3-build-evolution-report`

Documents simplification from over-engineered OS (DAG, scoring, microservices) to minimal deterministic
MVP (complexity 9/10 → 3/10). Strategic positioning: workflow engine, not enterprise control plane.
""",
    "noetfield-v3-investor-one-pager-rbc-v3.md": """# Investor One-Pager — RBC / Post Oak Style

Document key: `noetfield-v3-investor-one-pager-rbc-v3`

Concise capital memo for v3 orchestration product. Problem: non-deterministic AI in regulated environments.
Solution: governed multi-model execution with traceability.
""",
    "noetfield-v3-landing-page-spec.md": """# Landing Page Spec v3

Document key: `noetfield-v3-landing-page-spec`

SaaS homepage copy: deterministic multi-model engine, governance gate, audit ledger, use cases
(MSB memos, IC docs, research pipelines). Product GTM for v3 track.
""",
    "noetfield-v3-pitch-deck-13-slide.md": """# 13-Slide Pitch Deck v3

Document key: `noetfield-v3-pitch-deck-13-slide`

Investor deck outline for v3 orchestration layer. ASCII architecture diagram included in source.
""",
    "noetfield-v3-architecture-spec-fa.md": """# Architecture Spec (Persian) — v3 MVP

Document key: `noetfield-v3-architecture-spec-fa`

Five layers: Intent, Orchestrator, DAG-lite sequential execution, Governance Gate, Audit Ledger.
Rule-based router (structure→GPT, research→Perplexity, etc.). Aligns with mvp-production-spec-final.
""",
    "noetfield-v3-live-streaming-dashboard-spec.md": """# Live Streaming Dashboard Spec

Document key: `noetfield-v3-live-streaming-dashboard-spec`

WebSocket event stream UI: INTENT → TASKS → EXECUTION → GOVERNANCE → OUTPUT.
Phase-2 product surface; not required for MVP ship per production-spec-final.
""",
    "noetfield-v3-dag-animation-layer-spec.md": """# DAG Animation Layer Spec

Document key: `noetfield-v3-dag-animation-layer-spec`

D3.js live graph visualization — roadmap tier. MVP spec deliberately omits full DAG engine.
""",
    "noetfield-v3-governance-visualization-layer-spec.md": """# Governance Visualization Layer Spec

Document key: `noetfield-v3-governance-visualization-layer-spec`

Per-node PASS/FAIL/RISK coloring on execution graph — roadmap tier post-MVP.
""",
    "noetfield-v3-execution-replay-system-spec.md": """# Execution Replay System Spec

Document key: `noetfield-v3-execution-replay-system-spec`

Timeline replay of ledger events — observability roadmap; aligns with Copilot audit narrative.
""",
    "noetfield-v3-multi-agent-contribution-timeline-spec.md": """# Multi-Agent Contribution Timeline Spec

Document key: `noetfield-v3-multi-agent-contribution-timeline-spec`

Per-agent contribution weights in ledger schema — roadmap tier beyond MVP single-gate governance.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_v3_ai_orchestration_product",
        "active_document_key": "noetfield-v3-mvp-production-spec-final",
        "active_version": "mvp-spec-final",
        "decision": "active_source_of_truth",
        "rationale": "Canonical build spec for Noetfield v3 deterministic multi-model workflow MVP (separate from GCIP L0).",
        "confidence": 0.93,
    },
    {
        "domain": "noetfield_v3_investor_gtm",
        "active_document_key": "noetfield-v3-investor-one-pager-rbc-v3",
        "active_version": "one-pager-rbc-v3",
        "decision": "active_source_of_truth",
        "rationale": "Primary investor one-pager for v3 AI orchestration product track.",
        "confidence": 0.88,
    },
    {
        "domain": "noetfield_v3_product_ux",
        "active_document_key": "noetfield-v3-landing-page-spec",
        "active_version": "landing-v3",
        "decision": "active_source_of_truth",
        "rationale": "Default product marketing surface for v3; streaming/DAG specs are roadmap references.",
        "confidence": 0.86,
    },
    {
        "domain": "noetfield_sme_visibility_pilot",
        "active_document_key": "noetfield-master-blueprint-sme-visibility-readonly-v1",
        "active_version": "visibility-pilot-v1",
        "decision": "active_source_of_truth",
        "rationale": "Bank-safe read-only SME cross-border visibility pilot wedge for RBCx/FinSec/Circle.",
        "confidence": 0.91,
    },
    {
        "domain": "noetfield_capital_execution_lineage",
        "active_document_key": "noetfield-creation-governance-stack-separation-fa",
        "active_version": "creation-gov-fa-v1",
        "decision": "active_methodology_reference",
        "rationale": "Explains why capital-execution and control-plane drafts are rejected in favor of governance-only GCIP.",
        "confidence": 0.9,
    },
]

NEW_RULES = [
    {
        "rule_key": "v3-product-track-separate-from-gcip-l0",
        "domain": "noetfield_v3_ai_orchestration_product",
        "source_document_key": "noetfield-v3-mvp-production-spec-final",
        "activation_status": "active_design_rule",
        "rule_type": "architecture_governance",
        "summary": "Noetfield v3 AI orchestration MVP is a distinct product track; GCIP v4 remains constitutional L0 for bank/regulatory identity.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "prohibit-capital-execution-control-plane-identity",
        "domain": "noetfield_capital_execution_lineage",
        "source_document_key": "noetfield-unified-master-control-plane-v9",
        "activation_status": "active_design_rule",
        "rule_type": "legal_positioning",
        "summary": "No federated capital execution control plane, RWA settlement OS, or Samara-style execution positioning as Noetfield identity.",
        "implementation_target": "gtm_policy",
    },
    {
        "rule_key": "bank-pilot-readonly-no-routing-influence",
        "domain": "noetfield_sme_visibility_pilot",
        "source_document_key": "noetfield-master-blueprint-sme-visibility-readonly-v1",
        "activation_status": "active_design_rule",
        "rule_type": "bank_pilot",
        "summary": "RBC/Circle pilot scope is read-only observability; no routing, execution control, or production dependency.",
        "implementation_target": "bank_integration",
    },
    {
        "rule_key": "v3-mvp-ship-linear-before-dag-ui",
        "domain": "noetfield_v3_ai_orchestration_product",
        "source_document_key": "noetfield-v3-mvp-production-spec-final",
        "activation_status": "active_design_rule",
        "rule_type": "product_governance",
        "summary": "Ship sequential MVP per production spec before DAG animation, replay, or multi-agent timeline features.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "conversation-engine-not-product-sot",
        "domain": "operator_prompt_tooling",
        "source_document_key": "noetfield-lightweight-conversation-replacement-engine-v3",
        "activation_status": "reference_only",
        "rule_type": "documentation_governance",
        "summary": "Chat compression prompts are operator tooling, not Noetfield product or regulatory SOT.",
        "implementation_target": "source_of_truth_registry",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-017

Two tracks ingested:

## A — GCIP / Bank (unchanged L0)

- **L0:** `noetfield-constitution-gcip-v4`
- **Pilot wedge:** `noetfield-master-blueprint-sme-visibility-readonly-v1` (read-only)
- **Prohibited:** capital execution v1, Samara capital blueprint, control plane v9

## B — Noetfield v3 AI Orchestration Product (build track)

- **Product SOT:** `noetfield-v3-mvp-production-spec-final`
- **Investor:** `noetfield-v3-investor-one-pager-rbc-v3`
- **UX:** `noetfield-v3-landing-page-spec`
- **Roadmap (not MVP):** DAG UI, replay, governance viz, agent timeline

## C — Operator tooling

- `noetfield-lightweight-conversation-replacement-engine-v3` (not product SOT)
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-017", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-017"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-017/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-017",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-14"

    rules["registry_version"] = "2026-05-29-rules-14"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
