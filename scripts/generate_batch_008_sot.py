#!/usr/bin/env python3
"""Generate batch 008 Noetfield v3.1, GIE, and execution VM registry."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-008"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-gie-cursor-master-prompt-v31.md",
        "document_key": "noetfield-gie-cursor-master-prompt-v31",
        "title": "Noetfield GIE v3.1 — Cursor Master Build Prompt",
        "domain": "noetfield_gie",
        "version_label": "cursor-prompt-v31",
        "classification": "active_implementation_prompt",
        "status": "implementation_ready",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-ambient-intelligence-nervous-system-sot-v31.md",
        "document_key": "noetfield-ambient-intelligence-nervous-system-sot-v31",
        "title": "Noetfield Ambient Intelligence Nervous System — Source of Truth v3.1",
        "domain": "noetfield_product_vision",
        "version_label": "v3.1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [
            "noetfield-ambient-intelligence-sot-v30",
            "noetfield-ambient-intelligence-sot-v21",
            "noetfield-ambient-intelligence-sot-v20",
            "noetfield-ambient-lead-intelligence-sot-v11",
            "noetfield-ai-organization-runtime-sot-v1",
        ],
        "superseded_by": None,
    },
    {
        "file": "noetfield-gie-specification-supplement-v31.md",
        "document_key": "noetfield-gie-specification-supplement-v31",
        "title": "Graph Inference Engine (GIE) — Technical Specification Supplement v3.1",
        "domain": "noetfield_gie",
        "version_label": "gie-spec-v31",
        "classification": "active_source_of_truth",
        "status": "implementation_ready",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-ambient-intelligence-sot-v30.md",
        "document_key": "noetfield-ambient-intelligence-sot-v30",
        "title": "Noetfield Ambient Intelligence — Source of Truth v3.0",
        "domain": "noetfield_product_vision",
        "version_label": "v3.0",
        "classification": "superseded_product_reference",
        "status": "superseded",
        "supersedes": ["noetfield-ambient-intelligence-sot-v21"],
        "superseded_by": "noetfield-ambient-intelligence-nervous-system-sot-v31",
    },
    {
        "file": "noetfield-ambient-intelligence-sot-v21.md",
        "document_key": "noetfield-ambient-intelligence-sot-v21",
        "title": "Noetfield Ambient Intelligence Runtime — Source of Truth v2.1",
        "domain": "noetfield_product_vision",
        "version_label": "v2.1",
        "classification": "superseded_product_reference",
        "status": "superseded",
        "supersedes": ["noetfield-ambient-intelligence-sot-v20"],
        "superseded_by": "noetfield-ambient-intelligence-nervous-system-sot-v31",
    },
    {
        "file": "noetfield-ambient-intelligence-sot-v20.md",
        "document_key": "noetfield-ambient-intelligence-sot-v20",
        "title": "Noetfield Ambient Intelligence Runtime — Source of Truth v2.0",
        "domain": "noetfield_product_vision",
        "version_label": "v2.0",
        "classification": "superseded_product_reference",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-ambient-intelligence-nervous-system-sot-v31",
    },
    {
        "file": "noetfield-autonomous-ambient-inspectors-ecosystem-fa.md",
        "document_key": "noetfield-autonomous-ambient-inspectors-ecosystem-fa",
        "title": "Autonomous Ambient Intelligence — Inspectors Ecosystem (Persian)",
        "domain": "noetfield_product_vision",
        "version_label": "inspectors-ecosystem-v1",
        "classification": "active_operational_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-ambient-lead-intelligence-sot-v11.md",
        "document_key": "noetfield-ambient-lead-intelligence-sot-v11",
        "title": "Noetfield Ambient Lead Intelligence — Source of Truth v1.1",
        "domain": "noetfield_product_vision",
        "version_label": "v1.1",
        "classification": "superseded_product_reference",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-ambient-intelligence-nervous-system-sot-v31",
    },
    {
        "file": "noetfield-ai-native-lean-enterprise-blueprint-fa.md",
        "document_key": "noetfield-ai-native-lean-enterprise-blueprint-fa",
        "title": "AI-Native Lean Enterprise — Technical Blueprint (Persian)",
        "domain": "ai_native_enterprise_methodology",
        "version_label": "blueprint-v1",
        "classification": "reference_methodology",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "governed-execution-system-mvp-blueprint-v1.md",
        "document_key": "governed-execution-system-mvp-blueprint-v1",
        "title": "Governed Execution System — MVP Blueprint v1",
        "domain": "governed_execution_product",
        "version_label": "mvp-v1",
        "classification": "active_commercial_wedge_reference",
        "status": "implementation_ready",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "notion-ai-brain-hybrid-architecture-guide-fa.md",
        "document_key": "notion-ai-brain-hybrid-architecture-guide-fa",
        "title": "Notion + AI Brain Hybrid Architecture Guide (Persian)",
        "domain": "operator_tooling",
        "version_label": "guide-v1-fa",
        "classification": "reference_only",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-vm-execution-substrate-summary-fa.md",
        "document_key": "noetfield-vm-execution-substrate-summary-fa",
        "title": "NOETFIELD VM — Execution Substrate Summary (Persian)",
        "domain": "noetfield_execution_vm",
        "version_label": "vm-summary-v1-fa",
        "classification": "active_theory_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": "noetfield-execution-consensus-vm-v40-blueprint",
    },
    {
        "file": "noetfield-execution-consensus-vm-v40-blueprint.md",
        "document_key": "noetfield-execution-consensus-vm-v40-blueprint",
        "title": "NOETFIELD Execution Consensus VM v4.0 — Full System Blueprint",
        "domain": "noetfield_execution_vm",
        "version_label": "v4.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["noetfield-vm-execution-substrate-summary-fa"],
        "superseded_by": None,
    },
]

BODIES = {
    "noetfield-gie-cursor-master-prompt-v31.md": """# Noetfield GIE v3.1 — Cursor Master Build Prompt

Document key: `noetfield-gie-cursor-master-prompt-v31`

## Purpose

Production-ready `graph_inference_engine.py`: LangGraph pipeline with resolve_entities,
extract_direct_relations, perform_multi_hop_inference, calculate_strength_confidence,
update_knowledge_graph, propagate_inferences, final_reflection.

## Constraints

- Claude primary, Ollama fallback; Supabase + pgvector
- Min confidence 0.55; deterministic explainable JSON output
- Functions: run_full_inference, resolve_or_create_entity, upsert_relationship, get_graph_paths

## Registry

Implementation prompt for GIE module; normative spec is `noetfield-gie-specification-supplement-v31`.
""",
    "noetfield-ambient-intelligence-nervous-system-sot-v31.md": """# Noetfield Ambient Intelligence Nervous System — SOT v3.1

Document key: `noetfield-ambient-intelligence-nervous-system-sot-v31`

## Thesis

Autonomous governed intelligence nervous system: predictive ambient sensing, collaborative
bounded autonomy, living knowledge graph, closed-loop self-improvement.

## Layers

Ambient Sensing → Cognitive Inspectors → Personal AI Org → Executive Synthesis →
Living Memory Core → Governance & Trust.

## Agents

Sina's Brain, Operator, Analyst; Executive Agent; Inspectors (Opportunity Hunter, Threat Monitor, Lead Scout MVP).

## Schema

signals, entities, entity_relationships, inspector_findings, audit_log (Supabase + pgvector).

## Registry

**Active Noetfield product vision SOT**; supersedes v1.1–v3.0 and org-runtime v1. Does not replace
WP-01 / WP-03 / orchestration layer for current Postgres governance runtime in repo.
""",
    "noetfield-gie-specification-supplement-v31.md": """# Graph Inference Engine — Specification Supplement v3.1

Document key: `noetfield-gie-specification-supplement-v31`

## Pipeline

Entity resolution → direct relations → multi-hop inference → strength/confidence →
graph update → propagation → reflection.

## Tables

entities, entity_relationships (strength, confidence, evidence_sources, temporal_metadata).

## Prompts

System GIE prompt, direct relation extraction, multi-hop inference, strength calculator.

## Integration

Lead Scout → GIE before outreach; Executive queries graph; full audit logging.

## Registry

**Active GIE technical SOT** for knowledge graph reasoning module.
""",
    "noetfield-ambient-intelligence-sot-v30.md": """# Noetfield SOT v3.0

Document key: `noetfield-ambient-intelligence-sot-v30`

Predictive ambient autonomy, dynamic knowledge graph, multi-agent collaboration. Superseded by v3.1.
""",
    "noetfield-ambient-intelligence-sot-v21.md": """# Noetfield SOT v2.1

Document key: `noetfield-ambient-intelligence-sot-v21`

Ambient autonomy, three inspectors, executive layer, Supabase schema v2.1. Superseded by v3.1.
""",
    "noetfield-ambient-intelligence-sot-v20.md": """# Noetfield SOT v2.0

Document key: `noetfield-ambient-intelligence-sot-v20`

Governed market intelligence runtime, Lead Scout MVP priority. Superseded by v3.1.
""",
    "noetfield-autonomous-ambient-inspectors-ecosystem-fa.md": """# Autonomous Ambient Inspectors Ecosystem

Document key: `noetfield-autonomous-ambient-inspectors-ecosystem-fa`

## Content

Crawler layer + three inspectors (Opportunity Hunter, Threat Monitor, Lead Scout);
Executive Agent; REPORT / SUGGEST / ACT modes; human approval for spend/commitments.

## Registry

Operational reference aligned with v3.1 Lead Scout MVP focus.
""",
    "noetfield-ambient-lead-intelligence-sot-v11.md": """# Noetfield Ambient Lead Intelligence SOT v1.1

Document key: `noetfield-ambient-lead-intelligence-sot-v11`

Signal taxonomy, weighted scoring, governance framework, VC white paper v1.1. Superseded by v3.1.
""",
    "noetfield-ai-native-lean-enterprise-blueprint-fa.md": """# AI-Native Lean Enterprise Blueprint

Document key: `noetfield-ai-native-lean-enterprise-blueprint-fa`

Five layers: Command Center, Brain, n8n runtime, Supabase memory, multi-agent layer.
Free-max stack reference. Separate methodology from Noetfield product SOT.
""",
    "governed-execution-system-mvp-blueprint-v1.md": """# Governed Execution System — MVP Blueprint

Document key: `governed-execution-system-mvp-blueprint-v1`

## Product

AI-powered approval & decision system: INPUT → CLASSIFY → POLICY → RISK → ROUTE → DECISION → LOG.

## Stack

FastAPI, Postgres, simple UI, LLM assistive only (not deciding).

## Registry

**Active commercial wedge reference** aligned with repo Phase 3 Copilot Governance runtime.
""",
    "notion-ai-brain-hybrid-architecture-guide-fa.md": """# Notion + AI Brain Hybrid Guide

Document key: `notion-ai-brain-hybrid-architecture-guide-fa`

Notion = human control plane UI only; decision and policy execution in backend.
Reference only — not platform SOT.
""",
    "noetfield-vm-execution-substrate-summary-fa.md": """# NOETFIELD VM — Execution Substrate Summary

Document key: `noetfield-vm-execution-substrate-summary-fa`

Execution as unit of truth; deterministic core; deferred side effects; consensus ordering.
Superseded by v4.0 blueprint for normative VM spec.
""",
    "noetfield-execution-consensus-vm-v40-blueprint.md": """# NOETFIELD Execution Consensus VM v4.0

Document key: `noetfield-execution-consensus-vm-v40-blueprint`

## Model

Distributed deterministic execution VM: command-first, consensus ordering, derived state,
deferred side effects, append-only event store, replication.

## Layers

Consensus → Scheduler → Execution Kernel → Transaction → Policy → Risk → Decision →
Domain State → Side Effect Queue → Event Store.

## Registry

**Active execution VM lineage SOT** — infrastructure substrate separate from ambient intelligence product docs.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_product_vision",
        "active_document_key": "noetfield-ambient-intelligence-nervous-system-sot-v31",
        "active_version": "v3.1",
        "decision": "active_source_of_truth",
        "rationale": "v3.1 is the definitive ambient intelligence nervous system specification with living knowledge graph, inspectors, and governance layers. Supersedes v1.1 through v3.0 and batch-007 org-runtime draft.",
        "confidence": 0.94,
    },
    {
        "domain": "noetfield_gie",
        "active_document_key": "noetfield-gie-specification-supplement-v31",
        "active_version": "gie-spec-v31",
        "decision": "active_source_of_truth",
        "rationale": "GIE supplement defines graph inference pipeline, schema, prompts, and integration points for the living knowledge graph.",
        "confidence": 0.91,
    },
    {
        "domain": "governed_execution_product",
        "active_document_key": "governed-execution-system-mvp-blueprint-v1",
        "active_version": "mvp-v1",
        "decision": "active_commercial_wedge_reference",
        "rationale": "Deterministic approval workflow MVP aligns with Copilot Governance and Phase 3 policy runtime as first sellable wedge.",
        "confidence": 0.88,
    },
    {
        "domain": "noetfield_execution_vm",
        "active_document_key": "noetfield-execution-consensus-vm-v40-blueprint",
        "active_version": "v4.0",
        "decision": "active_source_of_truth",
        "rationale": "Execution Consensus VM v4.0 is the implementation-grade blueprint for deterministic distributed execution substrate.",
        "confidence": 0.87,
    },
    {
        "domain": "ai_native_enterprise_methodology",
        "active_document_key": "noetfield-ai-native-lean-enterprise-blueprint-fa",
        "active_version": "blueprint-v1",
        "decision": "reference_methodology",
        "rationale": "Free-max lean enterprise stack is operational methodology, not Noetfield product SOT.",
        "confidence": 0.75,
    },
    {
        "domain": "operator_tooling",
        "active_document_key": "notion-ai-brain-hybrid-architecture-guide-fa",
        "active_version": "guide-v1-fa",
        "decision": "reference_only",
        "rationale": "Notion as control plane UI only; backend remains source of execution truth.",
        "confidence": 0.7,
    },
]

NEW_RULES = [
    {
        "rule_key": "gie-min-confidence-threshold-055",
        "domain": "noetfield_gie",
        "source_document_key": "noetfield-gie-specification-supplement-v31",
        "activation_status": "active_design_rule",
        "rule_type": "graph_inference",
        "summary": "Graph inferences below 0.55 confidence must not commit to the knowledge graph without review.",
        "implementation_target": "graph_runtime",
    },
    {
        "rule_key": "gie-full-audit-reasoning-chain",
        "domain": "noetfield_gie",
        "source_document_key": "noetfield-gie-specification-supplement-v31",
        "activation_status": "active_design_rule",
        "rule_type": "audit_governance",
        "summary": "All GIE inferences log complete reasoning chains to the audit ledger.",
        "implementation_target": "audit_ledger_runtime",
    },
    {
        "rule_key": "noetfield-bounded-autonomy-human-approval",
        "domain": "noetfield_product_vision",
        "source_document_key": "noetfield-ambient-intelligence-nervous-system-sot-v31",
        "activation_status": "active_design_rule",
        "rule_type": "governance",
        "summary": "High-risk external actions require human approval; inspectors default to report/suggest modes.",
        "implementation_target": "governance_runtime",
    },
    {
        "rule_key": "noetfield-living-knowledge-graph-central",
        "domain": "noetfield_product_vision",
        "source_document_key": "noetfield-ambient-intelligence-nervous-system-sot-v31",
        "activation_status": "active_design_rule",
        "rule_type": "graph_runtime",
        "summary": "Entity relationships and graph updates are the central memory substrate for ambient intelligence.",
        "implementation_target": "graph_runtime",
    },
    {
        "rule_key": "governed-execution-deterministic-pipeline",
        "domain": "governed_execution_product",
        "source_document_key": "governed-execution-system-mvp-blueprint-v1",
        "activation_status": "active_design_rule",
        "rule_type": "workflow_governance",
        "summary": "Every request follows classify → policy → risk → route → decision → audit with no exceptions.",
        "implementation_target": "governance_policy_runtime",
    },
    {
        "rule_key": "governed-execution-llm-assistive-only",
        "domain": "governed_execution_product",
        "source_document_key": "governed-execution-system-mvp-blueprint-v1",
        "activation_status": "active_design_rule",
        "rule_type": "ai_governance",
        "summary": "LLM provides risk interpretation only; policy engine and router make final decisions.",
        "implementation_target": "policy_engine",
    },
    {
        "rule_key": "execution-vm-command-first",
        "domain": "noetfield_execution_vm",
        "source_document_key": "noetfield-execution-consensus-vm-v40-blueprint",
        "activation_status": "reference_only",
        "rule_type": "execution_substrate",
        "summary": "Only commands enter execution; consensus orders globally; side effects are deferred.",
        "implementation_target": None,
    },
    {
        "rule_key": "execution-vm-append-only-event-truth",
        "domain": "noetfield_execution_vm",
        "source_document_key": "noetfield-execution-consensus-vm-v40-blueprint",
        "activation_status": "reference_only",
        "rule_type": "audit_governance",
        "summary": "State is derived from append-only event store; all execution must be replayable.",
        "implementation_target": None,
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-008

Noetfield Ambient Intelligence v3.1 (definitive product SOT), GIE specification,
version lineage v1.1–v3.0, governed execution MVP, execution consensus VM v4.0.

## Active

- Product vision: `noetfield-ambient-intelligence-nervous-system-sot-v31`
- GIE: `noetfield-gie-specification-supplement-v31`
- GIE build prompt: `noetfield-gie-cursor-master-prompt-v31`
- Commercial wedge: `governed-execution-system-mvp-blueprint-v1`
- Execution VM: `noetfield-execution-consensus-vm-v40-blueprint`

Platform implementation SOT (WP-01, WP-03, orchestration, Phase 3 runtime) unchanged.
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-008", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-008"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-008/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-008",
            }
        )

    supersede_keys = {
        "noetfield-ai-organization-runtime-sot-v1",
        "noetfield-ambient-intelligence-sot-v30",
        "noetfield-ambient-intelligence-sot-v21",
        "noetfield-ambient-intelligence-sot-v20",
        "noetfield-ambient-lead-intelligence-sot-v11",
        "noetfield-vm-execution-substrate-summary-fa",
    }
    for document in inventory["documents"]:
        if document["document_key"] in supersede_keys:
            document["superseded_by"] = document.get("superseded_by") or (
                "noetfield-execution-consensus-vm-v40-blueprint"
                if "vm-" in document["document_key"]
                else "noetfield-ambient-intelligence-nervous-system-sot-v31"
            )
            if document["document_key"] != "noetfield-ai-organization-runtime-sot-v1":
                document["classification"] = "superseded_product_reference"
            else:
                document["classification"] = "superseded_strategic_reference"

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)

    if not any(d["domain"] == "noetfield_org_vision" for d in sot["decisions"]):
        pass
    else:
        sot["decisions"] = [
            d
            for d in sot["decisions"]
            if d["domain"] != "noetfield_org_vision"
        ]

    sot["registry_version"] = "2026-05-29-sot-5"
    rules["registry_version"] = "2026-05-29-rules-5"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
