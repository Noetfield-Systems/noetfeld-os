#!/usr/bin/env python3
"""Generate batch 010 documentation standards, RFC governance, execution kernel registry."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-010"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-dual-layer-documentation-standard-v1.md",
        "document_key": "noetfield-dual-layer-documentation-standard-v1",
        "title": "Noetfield Dual-Layer Documentation Standard v1.0",
        "domain": "noetfield_documentation_standard",
        "version_label": "dual-layer-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-rfc-standard-v1-github-ci.md",
        "document_key": "noetfield-rfc-standard-v1-github-ci",
        "title": "Noetfield RFC Standard v1.0 (GitHub-Ready + CI-Enforced)",
        "domain": "noetfield_rfc_governance",
        "version_label": "rfc-standard-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-langgraph-rfc-execution-integration-v1.md",
        "document_key": "noetfield-langgraph-rfc-execution-integration-v1",
        "title": "Noetfield LangGraph Execution Kernel Integration v1.0",
        "domain": "noetfield_langgraph_integration",
        "version_label": "langgraph-integration-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-execution-kernel-full-stack-blueprint-v1.md",
        "document_key": "noetfield-execution-kernel-full-stack-blueprint-v1",
        "title": "Noetfield Execution Kernel — Full Stack Blueprint v1.0",
        "domain": "noetfield_execution_kernel_architecture",
        "version_label": "kernel-blueprint-v1.0",
        "classification": "superseded_implementation_reference",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-stack-blueprint-v1-refined-final",
    },
    {
        "file": "noetfield-stack-blueprint-v1-refined-final.md",
        "document_key": "noetfield-stack-blueprint-v1-refined-final",
        "title": "Noetfield Stack Blueprint v1 — Refined Final Architecture",
        "domain": "noetfield_execution_kernel_architecture",
        "version_label": "stack-refined-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [
            "noetfield-data-stack-kafka-qdrant-alternative",
            "noetfield-execution-kernel-full-stack-blueprint-v1",
        ],
        "superseded_by": None,
    },
    {
        "file": "noetfield-data-stack-kafka-qdrant-alternative.md",
        "document_key": "noetfield-data-stack-kafka-qdrant-alternative",
        "title": "Noetfield Data Stack — Kafka/Qdrant Multi-DB Alternative",
        "domain": "noetfield_execution_kernel_architecture",
        "version_label": "multi-db-stack-draft",
        "classification": "superseded_architecture_draft",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-stack-blueprint-v1-refined-final",
    },
    {
        "file": "noetfield-architecture-verdict-postgres-first-fa.md",
        "document_key": "noetfield-architecture-verdict-postgres-first-fa",
        "title": "Architecture Verdict — Postgres-First Stack (Persian)",
        "domain": "noetfield_execution_kernel_architecture",
        "version_label": "verdict-fa-v1",
        "classification": "reference_methodology",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-enterprise-framing-sor-vs-computation-fa.md",
        "document_key": "noetfield-enterprise-framing-sor-vs-computation-fa",
        "title": "Enterprise Framing — SoR vs System of Computation (Persian)",
        "domain": "noetfield_execution_kernel_architecture",
        "version_label": "sor-framing-fa-v1",
        "classification": "reference_methodology",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-5-year-vision-enterprise-ai-os.md",
        "document_key": "noetfield-5-year-vision-enterprise-ai-os",
        "title": "5-Year Vision — Noetfield as Enterprise AI Operating System",
        "domain": "noetfield_execution_roadmap",
        "version_label": "5yr-vision-narrative-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-5-year-vision-roadmap-table.md",
        "document_key": "noetfield-5-year-vision-roadmap-table",
        "title": "5-Year Vision — Full Stack Roadmap Table",
        "domain": "noetfield_execution_roadmap",
        "version_label": "5yr-vision-table-v1",
        "classification": "active_operational_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-5-year-master-plan-compressed.md",
        "document_key": "noetfield-5-year-master-plan-compressed",
        "title": "5-Year Master Plan — Ultra-Compressed",
        "domain": "noetfield_execution_roadmap",
        "version_label": "5yr-master-plan-v1",
        "classification": "active_executive_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-conversation-kernel-maturity-report.md",
        "document_key": "noetfield-conversation-kernel-maturity-report",
        "title": "Conversation Performance Report — Kernel Maturity Assessment",
        "domain": "noetfield_execution_kernel_architecture",
        "version_label": "maturity-report-v1",
        "classification": "reference_only",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
]

BODIES = {
    "noetfield-dual-layer-documentation-standard-v1.md": """# Noetfield Dual-Layer Documentation Standard v1.0

Document key: `noetfield-dual-layer-documentation-standard-v1`

Industry-grade spec separating Vision (WHY/WHAT/OUTCOME) from Engineering (HOW/TRUTH).

## Canonical structure

Every document: A Vision Layer, B Engineering Layer, C Traceability Map, D Governance Metadata.

## Vision rules

No implementation details, schemas, DB, or APIs. Readable by non-engineers.

## Engineering rules

Fully technical, deterministic, testable. No narrative language.

## Traceability rule

If any Vision element lacks Engineering mapping → document is INVALID.

## Layer priority

Engineering overrides Vision on execution conflicts. Authoritative layer: Engineering only.
""",
    "noetfield-rfc-standard-v1-github-ci.md": """# Noetfield RFC Standard v1.0

Document key: `noetfield-rfc-standard-v1-github-ci`

Machine-verifiable governance: each RFC is a 4-file unit (`vision.md`, `engineering.md`,
`traceability.json`, `metadata.yaml`) under `rfc/RFC-NNNN-slug/`.

## CI gates

- Schema validation (`tools/validator.py`)
- Traceability completeness (`tools/trace-checker.py`)
- Replay safety (`tools/replay-simulator.py`)

## Hard rules

All vision fields mapped; no orphan engineering sections; metadata matches schema;
engineering deterministic; replay-safe or explicitly marked unsafe.

## Lifecycle

Draft → In Review → CI Passed → Approved → Active → Deprecated.
""",
    "noetfield-langgraph-rfc-execution-integration-v1.md": """# Noetfield LangGraph + RFC Integration v1.0

Document key: `noetfield-langgraph-rfc-execution-integration-v1`

Pipeline: RFC (GitHub) → CI → RFC Compiler → LangGraph DAG → Event Ledger.

## RFC output contract

Each RFC may include `execution_graph.json` with nodes: LLM_NODE, VALIDATION_NODE,
POLICY_NODE, STATE_NODE.

## Runtime binding rules

1. RFC immutable after compilation (change = new graph version)
2. Graph cannot bypass kernel — all outputs commit to ledger
3. LLM sandboxed — cannot mutate state directly
4. All edges are enforced transitions

## Replay

RFC + event log + graph → deterministic re-execution → hash compare → drift detection.
""",
    "noetfield-execution-kernel-full-stack-blueprint-v1.md": """# Noetfield Execution Kernel — Full Stack Blueprint v1.0

Document key: `noetfield-execution-kernel-full-stack-blueprint-v1`

Postgres-centered deterministic kernel: immutable events, LLM advisory-only,
policy-governed execution, full replay.

## Stack (initial draft)

PostgreSQL (truth), pgvector (semantic advisory), Timescale (extension-only optimization),
Redis (ephemeral), S3 (archive), LangGraph (runtime).

## Pipeline

Input → LLM proposal → schema gate → policy → risk (advisory) → LangGraph → PG commit → snapshot → S3.

**Superseded by** `noetfield-stack-blueprint-v1-refined-final` for canonical architecture SOT.
""",
    "noetfield-stack-blueprint-v1-refined-final.md": """# Noetfield Stack Blueprint v1 — Refined Final

Document key: `noetfield-stack-blueprint-v1-refined-final`

**Active execution-kernel architecture SOT.**

PostgreSQL is the only system of truth. All other stores are projection, optimization,
cache, or derived intelligence layers.

## Layer roles

| Layer | Role | Technology |
| Truth | immutable facts | PostgreSQL |
| Temporal opt | partitioning (extension only) | TimescaleDB in PG |
| Semantic | advisory similarity | pgvector in PG |
| Execution | state machine | LangGraph (checkpoints in PG) |
| Ephemeral | speed, locks | Redis |
| Archive | cold artifacts | S3 |

## Production rules

1. Postgres only source of truth
2. Every action emits an event
3. No probabilistic system mutates state directly
4. Replay from ledger + snapshots
5. Semantic advisory only
6. Timescale must not be a parallel logical model

## MVP minimum

PostgreSQL + Redis + S3 (Kafka/vector external DB deferred).
""",
    "noetfield-data-stack-kafka-qdrant-alternative.md": """# Noetfield Data Stack — Kafka/Qdrant Alternative

Document key: `noetfield-data-stack-kafka-qdrant-alternative`

Earlier draft proposing Kafka/Redpanda stream bus and Qdrant/Weaviate as separate semantic layer.

**Superseded:** conflicts with Postgres-first single-truth model. Retained for lineage only.
Canonical stack: `noetfield-stack-blueprint-v1-refined-final`.
""",
    "noetfield-architecture-verdict-postgres-first-fa.md": """# Architecture Verdict — Postgres-First (Persian)

Document key: `noetfield-architecture-verdict-postgres-first-fa`

Reference analysis (FA): Postgres-first + pgvector inside PG aligns with Stripe/Temporal-style
single source of truth. Timescale must remain extension-only, not split truth path.
""",
    "noetfield-enterprise-framing-sor-vs-computation-fa.md": """# Enterprise Framing — SoR vs Computation (Persian)

Document key: `noetfield-enterprise-framing-sor-vs-computation-fa`

Reference warning: Postgres is System of Record, not System of Computation. Avoid monolithic
truth blob at scale — keep logical layer boundaries (truth / temporal / semantic / execution / ephemeral / archive).
""",
    "noetfield-5-year-vision-enterprise-ai-os.md": """# 5-Year Vision — Enterprise AI Operating System

Document key: `noetfield-5-year-vision-enterprise-ai-os`

North star: deterministic event-sourced substrate for probabilistic AI in regulated enterprise.

## Phases

- P1 (0–1y): Kernel — ledger, reducer, replay, schema gate, basic policy
- P2 (1–2y): Governance — Policy DSL, semantic risk (advisory), arbitration routing
- P3 (2–3y): Distributed — event replication, multi-node sync, conflict resolution
- P4 (3–4y): Enterprise — API gateway, identity, audit dashboards, connectors
- P5 (4–5y): Protocol — policy marketplace, federated audit, cross-org standard

Separation of powers: Cognition (LLM) / Authority (policy) / Truth (ledger).
""",
    "noetfield-5-year-vision-roadmap-table.md": """# 5-Year Vision — Roadmap Table

Document key: `noetfield-5-year-vision-roadmap-table`

Tabular phase map: Kernel Inception → Governance → Distributed → Enterprise → Global Infrastructure.

Tracks system state, architecture focus, LLM role, governance model, infrastructure, and deliverables per phase.
""",
    "noetfield-5-year-master-plan-compressed.md": """# 5-Year Master Plan — Compressed

Document key: `noetfield-5-year-master-plan-compressed`

| Phase | Timeline | Core goal |
| P1 | 0–12mo | Truth engine — ledger, replay, schema gate |
| P2 | 12–24mo | Control — Policy DSL, arbitration, risk |
| P3 | 24–36mo | Scale — streaming, replication |
| P4 | 36–48mo | Enterprise adoption |
| P5 | 48–60mo | Industry protocol layer |

One line: LLMs are untrusted intent compilers; Noetfield is the OS that decides allowed state.
""",
    "noetfield-conversation-kernel-maturity-report.md": """# Conversation Kernel Maturity Report

Document key: `noetfield-conversation-kernel-maturity-report`

End-to-end thread assessment: shift from agent orchestration to temporal execution kernel.

## Maturity scores (reference)

Deterministic integrity 9.5, replay 9, LLM isolation 9, production readiness 7.

## Gaps noted

Policy DSL, LLM arbitration engine, OpenAPI contracts, distributed ledger consistency.

Aligns with Phase 2+ roadmap; does not override engineering SOT documents.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_documentation_standard",
        "active_document_key": "noetfield-dual-layer-documentation-standard-v1",
        "active_version": "dual-layer-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "Canonical A/B/C/D document contract for all Noetfield specs; engineering layer authoritative at runtime.",
        "confidence": 0.93,
    },
    {
        "domain": "noetfield_rfc_governance",
        "active_document_key": "noetfield-rfc-standard-v1-github-ci",
        "active_version": "rfc-standard-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "4-file RFC units with CI validation, traceability, and replay-safety gates before merge.",
        "confidence": 0.92,
    },
    {
        "domain": "noetfield_langgraph_integration",
        "active_document_key": "noetfield-langgraph-rfc-execution-integration-v1",
        "active_version": "langgraph-integration-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "Defines RFC→compiler→LangGraph→ledger pipeline and runtime binding invariants.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_execution_kernel_architecture",
        "active_document_key": "noetfield-stack-blueprint-v1-refined-final",
        "active_version": "stack-refined-v1",
        "decision": "active_source_of_truth",
        "rationale": "Postgres-only truth with pgvector/Redis/S3 as projections; supersedes Kafka/Qdrant multi-DB draft.",
        "confidence": 0.94,
    },
    {
        "domain": "noetfield_execution_roadmap",
        "active_document_key": "noetfield-5-year-vision-enterprise-ai-os",
        "active_version": "5yr-vision-narrative-v1",
        "decision": "active_source_of_truth",
        "rationale": "Five-phase enterprise AI OS roadmap from kernel to protocol layer.",
        "confidence": 0.88,
    },
]

NEW_RULES = [
    {
        "rule_key": "engineering-layer-overrides-vision",
        "domain": "noetfield_documentation_standard",
        "source_document_key": "noetfield-dual-layer-documentation-standard-v1",
        "activation_status": "active_design_rule",
        "rule_type": "documentation_governance",
        "summary": "On execution conflicts, Engineering Layer overrides Vision Layer.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "vision-engineering-traceability-required",
        "domain": "noetfield_documentation_standard",
        "source_document_key": "noetfield-dual-layer-documentation-standard-v1",
        "activation_status": "active_design_rule",
        "rule_type": "documentation_governance",
        "summary": "Every vision element must map to engineering; unmapped claims invalidate the document.",
        "implementation_target": "rfc_validator",
    },
    {
        "rule_key": "rfc-ci-validation-before-merge",
        "domain": "noetfield_rfc_governance",
        "source_document_key": "noetfield-rfc-standard-v1-github-ci",
        "activation_status": "active_design_rule",
        "rule_type": "rfc_governance",
        "summary": "RFC changes under rfc/ must pass schema, traceability, and replay-safety CI gates.",
        "implementation_target": "github_workflows",
    },
    {
        "rule_key": "rfc-four-file-contract-unit",
        "domain": "noetfield_rfc_governance",
        "source_document_key": "noetfield-rfc-standard-v1-github-ci",
        "activation_status": "active_design_rule",
        "rule_type": "rfc_governance",
        "summary": "Each RFC requires vision.md, engineering.md, traceability.json, metadata.yaml.",
        "implementation_target": "rfc_validator",
    },
    {
        "rule_key": "langgraph-cannot-bypass-event-ledger",
        "domain": "noetfield_langgraph_integration",
        "source_document_key": "noetfield-langgraph-rfc-execution-integration-v1",
        "activation_status": "active_design_rule",
        "rule_type": "runtime_governance",
        "summary": "All graph node outputs must commit through the event ledger; no implicit paths.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "llm-sandboxed-proposal-only",
        "domain": "noetfield_langgraph_integration",
        "source_document_key": "noetfield-langgraph-rfc-execution-integration-v1",
        "activation_status": "active_design_rule",
        "rule_type": "runtime_governance",
        "summary": "LLM nodes generate proposals only; they cannot mutate authoritative state directly.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "postgres-single-source-of-truth",
        "domain": "noetfield_execution_kernel_architecture",
        "source_document_key": "noetfield-stack-blueprint-v1-refined-final",
        "activation_status": "active_design_rule",
        "rule_type": "data_architecture",
        "summary": "PostgreSQL is the only system of record; secondary DBs cannot hold canonical truth.",
        "implementation_target": "postgres_runtime",
    },
    {
        "rule_key": "semantic-layer-advisory-only",
        "domain": "noetfield_execution_kernel_architecture",
        "source_document_key": "noetfield-stack-blueprint-v1-refined-final",
        "activation_status": "active_design_rule",
        "rule_type": "data_architecture",
        "summary": "pgvector and risk scoring inform decisions but never define or mutate truth.",
        "implementation_target": "policy_runtime",
    },
    {
        "rule_key": "timescale-extension-not-separate-truth",
        "domain": "noetfield_execution_kernel_architecture",
        "source_document_key": "noetfield-stack-blueprint-v1-refined-final",
        "activation_status": "active_design_rule",
        "rule_type": "data_architecture",
        "summary": "TimescaleDB is a Postgres extension for partitioning only, not a parallel logical ledger.",
        "implementation_target": "postgres_runtime",
    },
    {
        "rule_key": "mvp-stack-postgres-redis-s3",
        "domain": "noetfield_execution_kernel_architecture",
        "source_document_key": "noetfield-stack-blueprint-v1-refined-final",
        "activation_status": "candidate_requires_formalization",
        "rule_type": "deployment",
        "summary": "Minimum production stack: PostgreSQL + Redis + S3; defer Kafka and external vector DB.",
        "implementation_target": "infrastructure",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-010

Documentation standards, RFC governance, LangGraph integration, execution kernel
architecture (Postgres-first refined stack), and 5-year roadmap.

## Active SOT domains

- `noetfield_documentation_standard` — dual-layer doc spec
- `noetfield_rfc_governance` — RFC + CI standard
- `noetfield_langgraph_integration` — RFC → LangGraph → ledger
- `noetfield_execution_kernel_architecture` — refined stack blueprint
- `noetfield_execution_roadmap` — 5-year enterprise AI OS vision

## Superseded

- Kafka/Qdrant multi-DB stack draft
- Full stack blueprint v1.0 (replaced by refined final)

## Reference only

- Persian architecture verdicts
- Conversation maturity report
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-010", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-010"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-010/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-010",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-7"

    rules["registry_version"] = "2026-05-29-rules-7"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
