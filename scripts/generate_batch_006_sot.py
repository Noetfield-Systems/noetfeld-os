#!/usr/bin/env python3
"""Generate batch 006 source-of-truth uploads and registry updates."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-006"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "architecture-of-meaning-semantic-superconductivity-essay.md",
        "document_key": "architecture-of-meaning-semantic-superconductivity-essay",
        "title": "The Architecture of Meaning: Semantic Superconductivity and the Cybernetic Noosphere",
        "domain": "cognitive_publishing",
        "version_label": "full-essay-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["architecture-of-meaning-book-proposal"],
        "superseded_by": None,
        "summary": "Full treatise on context resonance, latent space conditioning, semantic superconductivity, agentic noosphere, and the sovereign architect role.",
    },
    {
        "file": "context-resonance-ultimate-guide-co-cognition.md",
        "document_key": "context-resonance-ultimate-guide-co-cognition",
        "title": "Context Resonance, Latent Intelligence, and Human–AI Co-Cognition (Ultimate Guide)",
        "domain": "context_resonance_theory",
        "version_label": "ultimate-guide-v1",
        "classification": "active_practitioner_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "summary": "Extended practitioner guide: latent space, attention as compression, CRT definition, agentic orchestration, constraint engineering.",
    },
    {
        "file": "context-resonance-ieee-research-paper-crt.md",
        "document_key": "context-resonance-ieee-research-paper-crt",
        "title": "Context Resonance and Co-Cognitive Alignment in LLMs (IEEE-Style CRT Paper)",
        "domain": "context_resonance_theory",
        "version_label": "ieee-crt-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["context-resonance-theory-paper"],
        "superseded_by": None,
        "summary": "Formal CRT framework: latent semantic geometry, attention as salience filter, entropy reduction, agentic closed-loop systems.",
    },
    {
        "file": "architecture-md-v2-event-driven-agentic-system.md",
        "document_key": "architecture-md-v2-event-driven-agentic-system",
        "title": "ARCHITECTURE.md v2.0 — Event-Driven Agentic System Blueprint (Bank-Grade)",
        "domain": "event_driven_agentic_architecture",
        "version_label": "v2.0",
        "classification": "active_implementation_reference",
        "status": "implementation_ready",
        "supersedes": [],
        "superseded_by": None,
        "summary": "Canonical event schema, six layers, HALT protocol (max 2 retries), event-sourced memory, tooling contracts.",
    },
    {
        "file": "cursor-token-efficiency-context-discipline-v1.md",
        "document_key": "cursor-token-efficiency-context-discipline-v1",
        "title": "Cursor Token Efficiency and Context Discipline — Source of Truth v1.0",
        "domain": "operator_context_discipline",
        "version_label": "v1.0",
        "classification": "active_operator_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "summary": "Surgical context injection, .cursorrules + ARCHITECTURE.md locking, micro-tasking, model tiering, loop prevention.",
    },
    {
        "file": "chat-corpora-deduplication-pipeline-methodology-fa.md",
        "document_key": "chat-corpora-deduplication-pipeline-methodology-fa",
        "title": "Chat Corpora Deduplication and Contradiction Pipeline (Persian Methodology)",
        "domain": "data_pipeline_methodology",
        "version_label": "v1",
        "classification": "reference_methodology",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "summary": "Four-stage pipeline: ingestion, semantic clustering, dedup/contradiction flagging, structured output (JSON/Notion).",
    },
    {
        "file": "sot-guidelines-vs-slf-relationship-fa.md",
        "document_key": "sot-guidelines-vs-slf-relationship-fa",
        "title": "Source of Truth Guidelines vs SLF — Epistemic Layer Relationship (Persian)",
        "domain": "sot_epistemology",
        "version_label": "v1",
        "classification": "active_epistemic_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "summary": "SoT Guidelines = epistemic DNA; SLF = architectural expansion; compression → expansion loop.",
    },
    {
        "file": "sot-engine-repo-v1.md",
        "document_key": "sot-engine-repo-v1",
        "title": "SoT Engine Repository v1.0 — Self-Learning Execution System",
        "domain": "sot_engine",
        "version_label": "repo-v1",
        "classification": "active_implementation_scaffold_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "summary": "FastAPI + Supabase + sot_miner + telegram; execution logs, rule extraction, policy injector.",
    },
    {
        "file": "sot-extraction-routine-v1.md",
        "document_key": "sot-extraction-routine-v1",
        "title": "SoT Extraction Routine v1.0 — Reality to Rule Mining Pipeline",
        "domain": "sot_engine",
        "version_label": "extraction-v1",
        "classification": "active_methodology_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "summary": "If it does not repeat, it is not a rule. Pattern detection ≥3, validation cycle, structured SoT store.",
    },
    {
        "file": "sot-engine-auto-running-architecture-v1.md",
        "document_key": "sot-engine-auto-running-architecture-v1",
        "title": "Auto-Running SoT Engine v1.0 — Closed-Loop Architecture",
        "domain": "sot_engine",
        "version_label": "auto-arch-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["sot-engine-repo-v1"],
        "superseded_by": None,
        "summary": "Execution → logs → miner → validator → registry → policy injector → next cycle.",
    },
    {
        "file": "unified-system-genealogy-map.md",
        "document_key": "unified-system-genealogy-map",
        "title": "Unified System Genealogy Map — Reality to Learning Loop",
        "domain": "system_genealogy",
        "version_label": "v1",
        "classification": "active_lineage_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "summary": "Reality → SoT DNA → SLF Core → SLF Autonomy → SLF Execution → feedback.",
    },
    {
        "file": "slf-v5-frozen-canonical-spec.md",
        "document_key": "slf-v5-frozen-canonical-spec",
        "title": "SLF v5.0 — Frozen Canonical Specification",
        "domain": "slf_framework",
        "version_label": "v5.0-frozen",
        "classification": "active_source_of_truth",
        "status": "frozen_canonical",
        "supersedes": [],
        "superseded_by": None,
        "summary": "Cognitive OS: v3 thinking, v4 autonomy, v5 execution + memory + governance; immutable meaning layer.",
    },
]

BODIES: dict[str, str] = {
    "architecture-of-meaning-semantic-superconductivity-essay.md": """# The Architecture of Meaning: Semantic Superconductivity and the Cybernetic Noosphere

Document key: `architecture-of-meaning-semantic-superconductivity-essay`

## Thesis

Transition from prompt engineering to **context architecture**. High-density constraints induce **entropy collapse** and **latent space conditioning**, producing context resonance across tools.

## Law of Semantic Superconductivity

When constraint density crosses a critical threshold, the model phase-transitions from probabilistic text generation to **deterministic execution** (virtual CPU).

## Agentic Noosphere

Event-driven multi-agent stack: Human Intent → Event Router → Orchestrator + Validation → State Machine Runtime. HALT on `RETRY_LIMIT_REACHED_EVENT`.

## Sovereign Architect

Human role shifts from implementer to curator of meaning via `.cursorrules` and `ARCHITECTURE.md`.

## Registry

Active knowledge-product SOT; supersedes `architecture-of-meaning-book-proposal`.
""",
    "context-resonance-ultimate-guide-co-cognition.md": """# Context Resonance — Ultimate Guide to Co-Cognition

Document key: `context-resonance-ultimate-guide-co-cognition`

## Cognitive Resonance Theory (CRT)

Resonance occurs when human intent structure, model latent structure, and contextual constraints align into a stable inference attractor.

## Core mechanisms

- Semantic positioning in latent space
- Attention as cognitive compression under constraint pressure
- Emergence as constraint completion over learned system priors
- Agentic stack: planner, executor, memory, critic

## Registry

Practitioner companion to formal IEEE CRT paper and batch 004 theory paper.
""",
    "context-resonance-ieee-research-paper-crt.md": """# Context Resonance Theory — IEEE-Style Research Framework

Document key: `context-resonance-ieee-research-paper-crt`

## Abstract

CRT models emergent alignment between structured prompts and LLM latent-space convergence. Intelligence is a function of **constraint architecture**, not static model capability.

## Formalization

Resonance when f(C) → A such that ∇H(A) ↓ (entropy reduction in activated region).

## Agentic closed loop

S_{t+1} = E(S_t, I, feedback) — co-cognitive system, not single-pass generation.

## Registry

**Active CRT source of truth**; supersedes `context-resonance-theory-paper` from batch 004.
""",
    "architecture-md-v2-event-driven-agentic-system.md": """# ARCHITECTURE.md v2.0 — Event-Driven Agentic System

Document key: `architecture-md-v2-event-driven-agentic-system`

## System law

**No action occurs without an event. No state changes without traceability.**

## Paradigm

Event → Plan → Execute → Transition → Persist

## Canonical event schema

`event_id`, `event_type`, `timestamp`, `source`, `context_id`, `payload`, `state_before`, `state_after`, `retry_count`

## HALT protocol

Max retry per task: **2**. On `RETRY_LIMIT_REACHED_EVENT`: stop autonomous execution, emit diagnostics, return to human layer.

## Memory

Event-sourced only. No memory write without `STATE_VALIDATION_EVENT`.

## Registry

**Active bank-grade event architecture reference** aligned with Noetfield Phase 3 runtime posture.
""",
    "cursor-token-efficiency-context-discipline-v1.md": """# Cursor Token Efficiency and Context Discipline v1.0

Document key: `cursor-token-efficiency-context-discipline-v1`

## System law

**Precision of context > power of model**

## Rules

1. Selection hierarchy: selected block → single file → small group → codebase (last resort)
2. Persistent `.cursorrules` + `ARCHITECTURE.md` as architecture lock
3. Micro-tasking — no large multi-file transforms in one request
4. Two consecutive failures → STOP (HALT alignment)
5. Fast tokens only for irreversible design decisions

## Registry

Active operator reference; complements `cursor-ide-shortcuts-m5-pro-2026`.
""",
    "chat-corpora-deduplication-pipeline-methodology-fa.md": """# Chat Corpora Deduplication Pipeline (Methodology)

Document key: `chat-corpora-deduplication-pipeline-methodology-fa`

## Pipeline stages

1. Ingestion and parsing to unified Markdown/JSON
2. Semantic clustering via embeddings
3. Dedup merge and `[CONTRADICTION_FLAG]` reasoning pass
4. Structured output to relational DB, Notion, or Obsidian

## Tools referenced

AnythingLLM, Open WebUI, Flowise, Fabric CLI, custom Python + Pydantic structured outputs.

## Registry

Methodology reference for future chat-archive ingestion; not Noetfield runtime SOT.
""",
    "sot-guidelines-vs-slf-relationship-fa.md": """# SoT Guidelines vs SLF — Layer Relationship

Document key: `sot-guidelines-vs-slf-relationship-fa`

## Layers

| Layer | Role |
|-------|------|
| SoT Guidelines | Epistemic DNA — what is true about systems |
| SLF | Engineering expansion — how to build with that truth |

## Insight

SoT = compression of experience to law; SLF = expansion of law into executable architecture.

## Registry

Epistemic reference linking SoT mining doctrine to SLF v5 canonical spec.
""",
    "sot-engine-repo-v1.md": """# SoT Engine Repository v1.0

Document key: `sot-engine-repo-v1`

## Stack

FastAPI (`app/`), `sot_miner/` (pattern detection, extractor, validator, scheduler), Supabase (`execution_logs`, `sot_rules`), Telegram integration.

## Core loop

Log execution → detect frequency ≥3 → extract rules → validate → policy inject.

## Registry

Implementation scaffold; superseded as normative architecture by `sot-engine-auto-running-architecture-v1`.
""",
    "sot-extraction-routine-v1.md": """# SoT Extraction Routine v1.0

Document key: `sot-extraction-routine-v1`

## Principles

- SoT is **mined from reality**, not written from theory
- Required log schema: agent, task, input, output, status, failure reason
- Pattern → rule when frequency ≥3 and stability holds
- Validation: apply rule, re-run, measure stability

## Rule types

Structural, behavioral, failure, efficiency.

## Registry

Active methodology reference under `sot_engine` domain.
""",
    "sot-engine-auto-running-architecture-v1.md": """# Auto-Running SoT Engine v1.0

Document key: `sot-engine-auto-running-architecture-v1`

## Closed loop

Execution → Logging (Supabase) → SoT Miner (24h) → Validator → Registry → Policy Injector → Next Execution

## Critical rules

1. No log = no truth
2. No repetition = no rule
3. No validation = no SoT
4. No injection = no learning

## Registry

**Active SoT engine architecture SOT** for self-modifying behavioral systems lineage.
""",
    "unified-system-genealogy-map.md": """# Unified System Genealogy Map

Document key: `unified-system-genealogy-map`

## Chain

REALITY → SOURCE OF TRUTH (DNA) → SLF CORE (v3) → SLF AUTONOMY (v4) → SLF EXECUTION (v5) → OBSERVED REALITY ↺

## Insight

Intelligence is evolved through recursive compression of reality into structure.

## Registry

Active lineage map connecting SoT, SLF, and execution feedback loops.
""",
    "slf-v5-frozen-canonical-spec.md": """# SLF v5.0 — Frozen Canonical Specification

Document key: `slf-v5-frozen-canonical-spec`

## Stack (locked)

- **v3** — Intelligence core (truth formation)
- **v4** — Autonomy (self-correction)
- **v5** — Execution runtime + memory/state + governance

## Invariants

Autonomy without governance = chaos. Without state, truth cannot exist — only interpretation.

## Freeze rule

Immutable meaning; extensible only via v6+ layers, not core semantic changes.

## Registry

**Active SLF framework SOT** — separate lineage from Noetfield WP packages.
""",
}

NEW_SOT = [
    {
        "domain": "context_resonance_theory",
        "active_document_key": "context-resonance-ieee-research-paper-crt",
        "active_version": "ieee-crt-v1",
        "decision": "active_source_of_truth",
        "rationale": "IEEE-style CRT paper is the formal active theory SOT. Earlier theory paper and ultimate guide remain supporting references.",
        "confidence": 0.91,
    },
    {
        "domain": "cognitive_publishing",
        "active_document_key": "architecture-of-meaning-semantic-superconductivity-essay",
        "active_version": "full-essay-v1",
        "decision": "active_source_of_truth",
        "rationale": "Full Architecture of Meaning essay supersedes the book proposal as the authoritative knowledge-product manuscript.",
        "confidence": 0.9,
    },
    {
        "domain": "event_driven_agentic_architecture",
        "active_document_key": "architecture-md-v2-event-driven-agentic-system",
        "active_version": "v2.0",
        "decision": "active_implementation_reference",
        "rationale": "Bank-grade event-driven blueprint aligns with Noetfield Phase 3 event bus, HALT, and audit posture without replacing WP-01 graph SOT.",
        "confidence": 0.89,
    },
    {
        "domain": "operator_context_discipline",
        "active_document_key": "cursor-token-efficiency-context-discipline-v1",
        "active_version": "v1.0",
        "decision": "active_operator_reference",
        "rationale": "Defines surgical context, architecture locking, and token governance for Cursor workflows.",
        "confidence": 0.87,
    },
    {
        "domain": "sot_engine",
        "active_document_key": "sot-engine-auto-running-architecture-v1",
        "active_version": "auto-arch-v1",
        "decision": "active_source_of_truth",
        "rationale": "Auto-running closed-loop SoT engine is the normative architecture over the repo scaffold alone.",
        "confidence": 0.88,
    },
    {
        "domain": "sot_epistemology",
        "active_document_key": "sot-guidelines-vs-slf-relationship-fa",
        "active_version": "v1",
        "decision": "active_epistemic_reference",
        "rationale": "Clarifies SoT as epistemic DNA versus SLF as engineering expansion.",
        "confidence": 0.85,
    },
    {
        "domain": "slf_framework",
        "active_document_key": "slf-v5-frozen-canonical-spec",
        "active_version": "v5.0-frozen",
        "decision": "active_source_of_truth",
        "rationale": "SLF v5 frozen spec is the canonical cognitive OS stack definition for the SLF product lineage.",
        "confidence": 0.92,
    },
    {
        "domain": "system_genealogy",
        "active_document_key": "unified-system-genealogy-map",
        "active_version": "v1",
        "decision": "active_lineage_reference",
        "rationale": "Maps Reality → SoT → SLF → Execution → feedback for cross-document comparison.",
        "confidence": 0.86,
    },
    {
        "domain": "data_pipeline_methodology",
        "active_document_key": "chat-corpora-deduplication-pipeline-methodology-fa",
        "active_version": "v1",
        "decision": "reference_methodology",
        "rationale": "Chat archive deduplication pipeline is operational methodology, not platform runtime SOT.",
        "confidence": 0.8,
    },
]

NEW_RULES = [
    {
        "rule_key": "no-action-without-canonical-event",
        "domain": "event_driven_agentic_architecture",
        "source_document_key": "architecture-md-v2-event-driven-agentic-system",
        "activation_status": "active_design_rule",
        "rule_type": "event_runtime",
        "summary": "Every meaningful system action must be represented as a canonical event with trace_id.",
        "implementation_target": "event_bus",
    },
    {
        "rule_key": "halt-protocol-max-two-retries",
        "domain": "event_driven_agentic_architecture",
        "source_document_key": "architecture-md-v2-event-driven-agentic-system",
        "activation_status": "active_design_rule",
        "rule_type": "failure_governance",
        "summary": "On two consecutive execution failures, emit RETRY_LIMIT_REACHED_EVENT and return control to human layer.",
        "implementation_target": "governance_runtime",
    },
    {
        "rule_key": "memory-write-requires-state-validation-event",
        "domain": "event_driven_agentic_architecture",
        "source_document_key": "architecture-md-v2-event-driven-agentic-system",
        "activation_status": "active_design_rule",
        "rule_type": "memory_governance",
        "summary": "Persistent memory writes are forbidden without STATE_VALIDATION_EVENT.",
        "implementation_target": "ledger_runtime",
    },
    {
        "rule_key": "precision-of-context-over-model-power",
        "domain": "operator_context_discipline",
        "source_document_key": "cursor-token-efficiency-context-discipline-v1",
        "activation_status": "active_design_rule",
        "rule_type": "operator_discipline",
        "summary": "Surgical context scope takes precedence over model scale for output quality and cost.",
        "implementation_target": "developer_bootstrap",
    },
    {
        "rule_key": "semantic-superconductivity-constraint-density",
        "domain": "context_resonance_theory",
        "source_document_key": "architecture-of-meaning-semantic-superconductivity-essay",
        "activation_status": "active_design_rule",
        "rule_type": "cognitive_architecture",
        "summary": "High constraint density in context reduces entropy and moves inference toward deterministic execution paths.",
        "implementation_target": "governance_policy_runtime",
    },
    {
        "rule_key": "sot-mined-from-repetition-not-theory",
        "domain": "sot_engine",
        "source_document_key": "sot-extraction-routine-v1",
        "activation_status": "active_design_rule",
        "rule_type": "epistemic_governance",
        "summary": "Rules enter SoT only after repeated observed behavior (≥3) and validation, not from one-off theory.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "sot-no-log-no-truth",
        "domain": "sot_engine",
        "source_document_key": "sot-engine-auto-running-architecture-v1",
        "activation_status": "active_design_rule",
        "rule_type": "audit_governance",
        "summary": "Execution without structured logging cannot produce source-of-truth candidates.",
        "implementation_target": "audit_ledger_runtime",
    },
    {
        "rule_key": "slf-autonomy-requires-governance",
        "domain": "slf_framework",
        "source_document_key": "slf-v5-frozen-canonical-spec",
        "activation_status": "reference_only",
        "rule_type": "governance",
        "summary": "Autonomy layer must be paired with governance gates, rollback, and integrity monitoring.",
        "implementation_target": None,
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        body = BODIES[doc["file"]]
        (BATCH_DIR / doc["file"]).write_text(body.strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-006

Architecture of Meaning (full essay), Context Resonance Theory formalization,
ARCHITECTURE.md v2.0 event-driven blueprint, Cursor context discipline, SoT/SLF
genealogy, SoT Engine closed-loop architecture, and SLF v5 frozen canonical spec.

## Active decisions (high level)

- CRT: `context-resonance-ieee-research-paper-crt`
- Architecture of Meaning: `architecture-of-meaning-semantic-superconductivity-essay`
- Event-driven blueprint: `architecture-md-v2-event-driven-agentic-system`
- SoT engine: `sot-engine-auto-running-architecture-v1`
- SLF: `slf-v5-frozen-canonical-spec`

Noetfield WP-01 / WP-03 / orchestration SOT unchanged.
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-006", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-006"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-006/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-006",
            }
        )

    for document in inventory["documents"]:
        if document["document_key"] == "context-resonance-theory-paper":
            document["classification"] = "superseded_theory_reference"
            document["superseded_by"] = "context-resonance-ieee-research-paper-crt"
        if document["document_key"] == "architecture-of-meaning-book-proposal":
            document["classification"] = "superseded_knowledge_product_reference"
            document["superseded_by"] = "architecture-of-meaning-semantic-superconductivity-essay"
        if document["document_key"] == "sot-engine-repo-v1":
            document["superseded_by"] = "sot-engine-auto-running-architecture-v1"

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-3"

    rules["registry_version"] = "2026-05-29-rules-3"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
