#!/usr/bin/env python3
"""Generate batch 007 SLF, SoT guidelines, PAIOS, and Noetfield org runtime registry."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-007"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "slf-v5-logic-extension-layer-execution-state-control.md",
        "document_key": "slf-v5-logic-extension-layer-execution-state-control",
        "title": "SLF v5.0 Logic Extension Layer — Execution, State, and Control",
        "domain": "slf_framework",
        "version_label": "v5.0-extension",
        "classification": "active_execution_layer_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "slf-v3-system-logic-framework-epistemic.md",
        "document_key": "slf-v3-system-logic-framework-epistemic",
        "title": "System Logic Framework SLF v3.0 — Epistemic Engineering Model",
        "domain": "slf_epistemic_core",
        "version_label": "v3.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["slf-v2-system-logic-framework", "slg-v1-system-logic-source-generation"],
        "superseded_by": None,
    },
    {
        "file": "slf-v2-system-logic-framework.md",
        "document_key": "slf-v2-system-logic-framework",
        "title": "System Logic Framework SLF v2.0 — Epistemic Build Loop",
        "domain": "slf_epistemic_core",
        "version_label": "v2.0",
        "classification": "superseded_framework_reference",
        "status": "superseded",
        "supersedes": ["slg-v1-system-logic-source-generation"],
        "superseded_by": "slf-v3-system-logic-framework-epistemic",
    },
    {
        "file": "slg-v1-system-logic-source-generation.md",
        "document_key": "slg-v1-system-logic-source-generation",
        "title": "System Logic for Source Generation SLG v1.0",
        "domain": "slf_epistemic_core",
        "version_label": "v1.0",
        "classification": "historical_predecessor",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "slf-v3-system-logic-framework-epistemic",
    },
    {
        "file": "sot-creation-guidelines-practical.md",
        "document_key": "sot-creation-guidelines-practical",
        "title": "Source of Truth Creation Guidelines — Practical System Design Rules",
        "domain": "sot_epistemology",
        "version_label": "guidelines-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "personal-ai-operating-system-team-blueprint.md",
        "document_key": "personal-ai-operating-system-team-blueprint",
        "title": "Personal AI Operating System — Full Team Blueprint v1",
        "domain": "paios_system",
        "version_label": "team-blueprint-v1",
        "classification": "active_team_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "sot-path-to-truth-methodology-fa.md",
        "document_key": "sot-path-to-truth-methodology-fa",
        "title": "Path to Source of Truth — Methodology (Persian)",
        "domain": "sot_epistemology",
        "version_label": "path-v1-fa",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "paios-source-of-truth-blueprint-v1.md",
        "document_key": "paios-source-of-truth-blueprint-v1",
        "title": "PAIOS — Personal AI Operating System Source of Truth Blueprint v1.0",
        "domain": "paios_system",
        "version_label": "sot-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["personal-ai-operating-system-team-blueprint"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-ai-organization-runtime-sot-v1.md",
        "document_key": "noetfield-ai-organization-runtime-sot-v1",
        "title": "Noetfield AI Organization Runtime — Source of Truth Blueprint v1.0 (2026)",
        "domain": "noetfield_org_vision",
        "version_label": "org-runtime-v1.0",
        "classification": "active_strategic_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-strong-core-runtime-minimal-fa.md",
        "document_key": "noetfield-strong-core-runtime-minimal-fa",
        "title": "Noetfield Strong Core Runtime — Minimal MVP (Persian)",
        "domain": "noetfield_runtime_mvp",
        "version_label": "core-runtime-v0.1",
        "classification": "active_mvp_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
]

BODIES = {
    "slf-v5-logic-extension-layer-execution-state-control.md": """# SLF v5.0 Logic Extension Layer

Document key: `slf-v5-logic-extension-layer-execution-state-control`

## Role

v5 is the physical body: execution runtime, memory/state fabric, governance/safety — not philosophical logic.

## Three pillars

1. **Execution Runtime** — Event → Trigger → Routing → Tool Call → Execution → Log
2. **Memory + State** — Short/long-term, semantic, event log, versioned truth store
3. **Governance** — Permissions, approval gates, conflict arbitration, rollback, integrity monitoring

## Stack

v3 intelligence core → v4 autonomy → v5 execution/memory/governance → real world → feedback loop.

## Registry

Companion to `slf-v5-frozen-canonical-spec`; use for execution-layer implementation detail.
""",
    "slf-v3-system-logic-framework-epistemic.md": """# SLF v3.0 — Epistemic Engineering Model

Document key: `slf-v3-system-logic-framework-epistemic`

## Master loop

Intuition → Blueprint (hypothesis) → MVP (reality) → Observed Behavior → Source of Truth (invariants) → Refined Blueprint ↺

## Core axiom

Truth is not designed. Truth is the compressed residue of repeated interaction between model and reality.

## Laws

- Reality dominance: execution overrides design
- Compression: each iteration reduces entropy
- Separation of cognitive domains
- Invariant rule: only repeatable behavior becomes truth

## Registry

**Active SLF epistemic core SOT**; supersedes SLF v2 and SLG v1.
""",
    "slf-v2-system-logic-framework.md": """# SLF v2.0 — Epistemic Build Loop

Document key: `slf-v2-system-logic-framework`

## Content

Earlier formulation of intuition → blueprint → MVP → behavior → SoT → refined blueprint.

## Registry

Superseded by `slf-v3-system-logic-framework-epistemic`; retained for provenance.
""",
    "slg-v1-system-logic-source-generation.md": """# SLG v1.0 — System Logic for Source Generation

Document key: `slg-v1-system-logic-source-generation`

## Content

Formal pipeline from idea to stable system truth; closed learning loop with progressive abstraction.

## Registry

Historical predecessor to SLF v2/v3 epistemic frameworks.
""",
    "sot-creation-guidelines-practical.md": """# Source of Truth Creation Guidelines

Document key: `sot-creation-guidelines-practical`

## Principles

1. Start from reality, not theory — SoT emerges from execution
2. Identify repeated patterns (structural, not accidental)
3. Separate core functions — thinking, deciding, executing, coordinating
4. Strict non-overlapping role boundaries
5. Minimum stable structure; tool-independent
6. Validate through execution

## Core principle

SoT is the smallest stable rule set describing how a system behaves, independent of tools.

## Registry

**Active SoT epistemology SOT** alongside relationship and extraction docs from batch 006.
""",
    "personal-ai-operating-system-team-blueprint.md": """# Personal AI Operating System — Team Blueprint

Document key: `personal-ai-operating-system-team-blueprint`

## Architecture

Analyst → Brain → Chief of Staff → Operator with Supabase as shared memory.

## Rules

- Role separation: see / decide / coordinate / execute
- No overlap between agents
- Human approval for critical actions
- Memory is law

## Registry

Team layout reference; normative PAIOS spec is `paios-source-of-truth-blueprint-v1`.
""",
    "sot-path-to-truth-methodology-fa.md": """# Path to Source of Truth (Methodology)

Document key: `sot-path-to-truth-methodology-fa`

## Stages

Chaos → Pattern extraction → Role separation → Constraint definition → Abstraction → Stabilization

## Insight

SoT forms when you can explain the system without tools. ~70% experience, ~30% design.

## Registry

Persian methodology reference under `sot_epistemology`.
""",
    "paios-source-of-truth-blueprint-v1.md": """# PAIOS Source of Truth Blueprint v1.0

Document key: `paios-source-of-truth-blueprint-v1`

## System

Personal AI execution + intelligence runtime: Analyst, Brain, Chief of Staff, Operator, Supabase memory.

## Lifecycle

CREATED → ANALYZED → DECIDED → QUEUED → APPROVED → EXECUTED → CLOSED

## Design law

No agent combines thinking + execution + coordination.

## Registry

**Active PAIOS product lineage SOT** — separate from Noetfield governance platform runtime.
""",
    "noetfield-ai-organization-runtime-sot-v1.md": """# Noetfield AI Organization Runtime SOT v1.0

Document key: `noetfield-ai-organization-runtime-sot-v1`

## Vision

Governed AI organization runtime — not chatbot chains. Persistent memory, bounded autonomy, event-driven, full traceability.

## Prime directives

- Single source of truth (canonical DB)
- Event-driven architecture
- Bounded autonomy with human approval gates
- Deterministic workers vs reasoning directors/executives

## Stack (vision)

Docker, n8n, LangGraph, Supabase, Mem0, pgvector, Redis, Langfuse, OPA, Telegram.

## Registry

**Active strategic reference** for org-scale vision. Does not supersede WP-01, WP-03, or `orchestration-policy-layer-source-of-truth-2026` for current Postgres governance runtime implementation.
""",
    "noetfield-strong-core-runtime-minimal-fa.md": """# Noetfield Strong Core Runtime — Minimal MVP

Document key: `noetfield-strong-core-runtime-minimal-fa`

## Goal

Six capabilities: orchestration, memory, routing, observability, governance, events.

## MVP v0.1

n8n + Supabase + Ollama + Telegram + Langfuse; three agents: Research Scout, Outreach Draft, CEO Brief.

## Critical rule

Agents communicate via events through runtime mediator — not direct agent-to-agent chaos.

## Registry

Active MVP reference for org kernel; aligns with Phase 3 event bus posture in repo.
""",
}

NEW_SOT = [
    {
        "domain": "slf_epistemic_core",
        "active_document_key": "slf-v3-system-logic-framework-epistemic",
        "active_version": "v3.0",
        "decision": "active_source_of_truth",
        "rationale": "SLF v3 formalizes the epistemic loop and invariant compression engine. v2 and SLG v1 are historical predecessors.",
        "confidence": 0.92,
    },
    {
        "domain": "sot_epistemology",
        "active_document_key": "sot-creation-guidelines-practical",
        "active_version": "guidelines-v1",
        "decision": "active_source_of_truth",
        "rationale": "Practical SoT creation guidelines define how truth is mined from execution. Complements auto-running engine and SLF relationship docs.",
        "confidence": 0.9,
    },
    {
        "domain": "paios_system",
        "active_document_key": "paios-source-of-truth-blueprint-v1",
        "active_version": "sot-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "PAIOS blueprint is the normative four-agent personal OS spec with governance and memory contracts.",
        "confidence": 0.88,
    },
    {
        "domain": "noetfield_org_vision",
        "active_document_key": "noetfield-ai-organization-runtime-sot-v1",
        "active_version": "org-runtime-v1.0",
        "decision": "active_strategic_reference",
        "rationale": "2026 org-runtime vision informs scale path but does not replace current Noetfield WP and orchestration implementation SOT.",
        "confidence": 0.86,
    },
    {
        "domain": "noetfield_runtime_mvp",
        "active_document_key": "noetfield-strong-core-runtime-minimal-fa",
        "active_version": "core-runtime-v0.1",
        "decision": "active_mvp_reference",
        "rationale": "Minimal six-capability runtime kernel and v0.1 agent set for phased deployment.",
        "confidence": 0.84,
    },
]

NEW_RULES = [
    {
        "rule_key": "slf-reality-dominance-law",
        "domain": "slf_epistemic_core",
        "source_document_key": "slf-v3-system-logic-framework-epistemic",
        "activation_status": "active_design_rule",
        "rule_type": "epistemic_governance",
        "summary": "Execution overrides design assumptions; blueprint invalid if behavior contradicts it.",
        "implementation_target": "governance_policy_runtime",
    },
    {
        "rule_key": "slf-invariant-only-repeatable-behavior",
        "domain": "slf_epistemic_core",
        "source_document_key": "slf-v3-system-logic-framework-epistemic",
        "activation_status": "active_design_rule",
        "rule_type": "source_of_truth",
        "summary": "Only patterns surviving multiple execution cycles under variation become truth.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "sot-tool-independent-minimal-rules",
        "domain": "sot_epistemology",
        "source_document_key": "sot-creation-guidelines-practical",
        "activation_status": "active_design_rule",
        "rule_type": "epistemic_governance",
        "summary": "SoT must survive tool changes; describes roles, flow, and rules—not APIs or schemas.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "paios-no-agent-role-overlap",
        "domain": "paios_system",
        "source_document_key": "paios-source-of-truth-blueprint-v1",
        "activation_status": "reference_only",
        "rule_type": "agent_coordination",
        "summary": "Analyst, Brain, Chief of Staff, and Operator must not combine thinking, deciding, coordinating, and executing.",
        "implementation_target": None,
    },
    {
        "rule_key": "paios-operator-execution-only",
        "domain": "paios_system",
        "source_document_key": "paios-source-of-truth-blueprint-v1",
        "activation_status": "reference_only",
        "rule_type": "agent_boundary",
        "summary": "Operator executes approved tasks only; no reasoning or prioritization.",
        "implementation_target": None,
    },
    {
        "rule_key": "noetfield-bounded-autonomy",
        "domain": "noetfield_org_vision",
        "source_document_key": "noetfield-ai-organization-runtime-sot-v1",
        "activation_status": "active_design_rule",
        "rule_type": "governance",
        "summary": "Agents may observe, classify, infer, recommend, and draft; high-risk execution requires human approval.",
        "implementation_target": "governance_runtime",
    },
    {
        "rule_key": "noetfield-runtime-event-mediation",
        "domain": "noetfield_org_vision",
        "source_document_key": "noetfield-strong-core-runtime-minimal-fa",
        "activation_status": "active_design_rule",
        "rule_type": "event_runtime",
        "summary": "Agents must not communicate directly; routing goes through runtime events and mediator.",
        "implementation_target": "event_bus",
    },
    {
        "rule_key": "slf-v5-autonomy-requires-governance-pair",
        "domain": "slf_framework",
        "source_document_key": "slf-v5-logic-extension-layer-execution-state-control",
        "activation_status": "reference_only",
        "rule_type": "governance",
        "summary": "Autonomy without governance is chaos; governance without autonomy is stagnation.",
        "implementation_target": None,
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(
            BODIES[doc["file"]].strip() + "\n", encoding="utf-8"
        )

    readme = """# Uploaded Source Document Batch 2026-05-007

SLF v2/v3/SLG epistemic lineage, SLF v5 execution extension layer, SoT creation
guidelines, PAIOS personal OS, and Noetfield organization runtime vision.

## Active decisions

- SLF epistemic: `slf-v3-system-logic-framework-epistemic`
- SLF frozen body: `slf-v5-frozen-canonical-spec` (batch 006) + extension layer reference
- SoT epistemology: `sot-creation-guidelines-practical`
- PAIOS: `paios-source-of-truth-blueprint-v1`
- Noetfield vision: `noetfield-ai-organization-runtime-sot-v1` (strategic only)
- Noetfield MVP kernel: `noetfield-strong-core-runtime-minimal-fa`

Noetfield WP-01 / WP-03 / orchestration implementation SOT unchanged.
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {
            "batch_id": "2026-05-007",
            "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-007",
        }
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-007/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-007",
            }
        )

    for document in inventory["documents"]:
        if document["document_key"] == "sot-guidelines-vs-slf-relationship-fa":
            document["classification"] = "active_epistemic_supporting_reference"

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-4"

    rules["registry_version"] = "2026-05-29-rules-4"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
