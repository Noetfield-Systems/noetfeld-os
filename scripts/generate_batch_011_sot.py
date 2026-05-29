#!/usr/bin/env python3
"""Generate batch 011 execution kernel spec, v2 temporal governance, agent platform registry."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-011"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCS: list[dict] = [
    {
        "file": "noetfield-execution-kernel-temporal-v1-canonical.md",
        "document_key": "noetfield-execution-kernel-temporal-v1-canonical",
        "title": "Noetfield Execution Kernel v1.0 — Temporal Event-Sourced Canonical",
        "domain": "noetfield_execution_kernel_spec",
        "version_label": "temporal-kernel-v1.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-agent-catalog-bank-grade-v1.md",
        "document_key": "noetfield-agent-catalog-bank-grade-v1",
        "title": "Noetfield Agent Catalog — Bank-Grade Solo-Founder Ready",
        "domain": "noetfield_agent_catalog",
        "version_label": "agent-catalog-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-evidence-pack-json-schema-v1.md",
        "document_key": "noetfield-evidence-pack-json-schema-v1",
        "title": "Evidence Pack JSON Schema v1 — Signed Audit-Ready",
        "domain": "noetfield_evidence_pack_schema",
        "version_label": "evidence-pack-schema-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-human-gatekeeper-ui-wireframe-v1.md",
        "document_key": "noetfield-human-gatekeeper-ui-wireframe-v1",
        "title": "Human Gatekeeper UI Wireframe v1",
        "domain": "noetfield_human_gatekeeper_ui",
        "version_label": "gatekeeper-ui-v1",
        "classification": "active_operational_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-6-week-sprint-plan-solo-founder-v1.md",
        "document_key": "noetfield-6-week-sprint-plan-solo-founder-v1",
        "title": "6-Week Sprint Plan — Solo Founder Pilot Delivery",
        "domain": "noetfield_pilot_delivery_plan",
        "version_label": "sprint-6wk-v1",
        "classification": "active_operational_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v2-temporal-governance-os-bank-grade.md",
        "document_key": "noetfield-v2-temporal-governance-os-bank-grade",
        "title": "Noetfield v2.0 — Temporal Governance OS (Bank-Grade Design)",
        "domain": "noetfield_temporal_governance_v2",
        "version_label": "temporal-governance-v2.0",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["noetfield-v2-agentic-architecture-summary-duplicate"],
        "superseded_by": None,
    },
    {
        "file": "noetfield-v2-agentic-architecture-summary-duplicate.md",
        "document_key": "noetfield-v2-agentic-architecture-summary-duplicate",
        "title": "Noetfield v2.0 Agentic Architecture — Executive Summary (Duplicate)",
        "domain": "noetfield_temporal_governance_v2",
        "version_label": "agentic-summary-dup-v1",
        "classification": "duplicate",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "noetfield-v2-temporal-governance-os-bank-grade",
    },
    {
        "file": "noetfield-directory-enforced-consistency-spec-fa.md",
        "document_key": "noetfield-directory-enforced-consistency-spec-fa",
        "title": "Directory-Enforced Response Discipline & Value Basket (Persian)",
        "domain": "noetfield_operating_discipline",
        "version_label": "directory-discipline-fa-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
    {
        "file": "noetfield-governance-rollout-checklist-v1.md",
        "document_key": "noetfield-governance-rollout-checklist-v1",
        "title": "Governance Rollout & Pilot Success Checklist v1",
        "domain": "noetfield_temporal_governance_v2",
        "version_label": "rollout-checklist-v1",
        "classification": "active_compliance_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
    },
]

BODIES = {
    "noetfield-execution-kernel-temporal-v1-canonical.md": """# Noetfield Execution Kernel v1.0 — Temporal Canonical

Document key: `noetfield-execution-kernel-temporal-v1-canonical`

Canonical execution kernel: deterministic structure, probabilistic cognition, fully replayable governance.

## Core principle

All intelligence is probabilistic. All truth is event-sourced. LLMs never mutate state — only propose transitions;
kernel commits, rejects, or compensates.

## Three layers

1. LLM probabilistic layer (proposal engine)
2. Arbitration + governance (policy, validator, decision gate)
3. Event-sourced state kernel (append-only log, replay, temporal DAG)

## State model

`STATE(t) = REDUCE(EVENT_LOG[0..t])` — state is derived, not persisted as authoritative truth.

## Node types

LLM_NODE, TOOL_NODE, POLICY_NODE, SAGA_NODE, MERGE_NODE → COMMIT_EVENT

## LLM arbitration

Outputs: COMMIT | REJECT | ESCALATE_TO_FRONTIER | COMPENSATE | REQUEST_CLARIFICATION.
Policy engine is pure functions — no LLM in policy gate.

## Replay

Exact replay: cached LLM tokens, not regenerated. Semantic replay for debugging only.

## Semantic integrity

Raw events only as truth; no LLM regeneration on replay; embedding versioning required.

## MVP phases

P1: event log + graph executor | P2: policy + saga | P3: LLM arbitration + cache replay | P4: drift + audit export
""",
    "noetfield-agent-catalog-bank-grade-v1.md": """# Noetfield Agent Catalog — Bank-Grade

Document key: `noetfield-agent-catalog-bank-grade-v1`

Microservice agents with scoped permissions, auditable outputs, policy guards. Humans are the only
production-change authority.

## Agent roster

| Agent | Role | Can execute production? |
| Ingest | Normalize sources → events | No |
| Lineage | Provenance graph | Registry write only |
| Snapshot | Signed evidence snapshots | HSM sign, WORM store |
| Drift | Trajectory, slope, AUC | Alerts only |
| Risk | Risk(t), priority | Propose only |
| Decision | Ranked recommendations | Propose + Evidence Pack |
| Remediation | Playbooks (non-exec) | Flagged scripts only |
| Audit | Evidence Pack assembly | HSM sign, read-only publish |
| Orchestrator | Schedule, throttle, policy | Control plane only |
| Monitor | Health, adaptive thresholds | Propose tuning |
| Gatekeeper assistant | Triage payloads for UI | Cannot sign |
| Executor | Safe-zone automation | **Disabled by default**; multi-sig |

Every agent action emits `agent_event` with manifest_sha256 into the event store.
""",
    "noetfield-evidence-pack-json-schema-v1.md": """# Evidence Pack JSON Schema v1

Document key: `noetfield-evidence-pack-json-schema-v1`

Portable, signed, auditor-verifiable package reconstructing governance state for a scope/time window.

## Required fields

`pack_id`, `scope`, `timestamp`, `manifest_sha256`, `snapshots[]`, `events_url`, `lineage_graph`,
`drift_summary`, `decision_logs`, `signatures[]`

## Transport

`pack.json` + `data.tar.gz` + `manifest.sha256` + `manifest.sig` (detached HSM signature).

## Verification

`verify.sh` rehashes files and validates detached signature with public key.

## Signatures

Minimum: snapshot_agent, audit_agent, steward. Aligns with Copilot Governance / Trust Ledger wedge.
""",
    "noetfield-human-gatekeeper-ui-wireframe-v1.md": """# Human Gatekeeper UI Wireframe v1

Document key: `noetfield-human-gatekeeper-ui-wireframe-v1`

Single-pane triage and approval for solo founder / steward.

## Screens

1. **Triage Queue** — priority, artifact, drift sparkline, risk(t), Evidence Pack link, quick approve/defer
2. **Artifact Detail** — time slider, structural + semantic diff, drift chart, recommendations
3. **Approval Modal** — approve (HSM sign), reject, request more info → event store
4. **Replay & Export** — simulate/export window → Evidence Pack generation

Keyboard-first; mobile push for critical drift. Founder is default steward assignee.
""",
    "noetfield-6-week-sprint-plan-solo-founder-v1.md": """# 6-Week Sprint Plan — Solo Founder

Document key: `noetfield-6-week-sprint-plan-solo-founder-v1`

| Week | Focus |
| 0 | Policy matrix, HSM, event store selection |
| 1 | Orchestrator + Ingest (3 sources) |
| 2 | Lineage + Snapshot (WORM, HSM) |
| 3 | Drift Agent + dashboard |
| 4 | Risk + Decision + Evidence Pack generator |
| 5 | Gatekeeper UI + Audit Agent |
| 6 | Tuning, replay API, pilot runbook |

Pilot success: critical triage ≤4h, Evidence Pack ≤30min, FP rate ≤20%, 100% prod changes pre-signed.
""",
    "noetfield-v2-temporal-governance-os-bank-grade.md": """# Noetfield v2.0 — Temporal Governance OS (Bank-Grade)

Document key: `noetfield-v2-temporal-governance-os-bank-grade`

**Active v2 product architecture SOT** (distinct from v3.1 ambient intelligence nervous system).

Time-first: every change is an immutable event; state reconstructed via replay + snapshots.

## Logical layers

Input → Event Core → State Reconstruction → Evidence Snapshots → Drift Trajectory →
Temporal Conflict → Temporal Risk → Decision Agents → Audit/Replay → Human Gatekeeper

## Core APIs

POST /events | GET /state?time=T | GET /diff | GET /drift | POST /replay |
POST /evidence-pack | POST /agent/action-request

## Safety (non-negotiable)

No autonomous production execution. HSM-signed immutable evidence. Least-privilege agents.
Separation of duties. Fork governance with TTL. Tamper detection via rehash reconciliation.

## SLAs (pilot)

Critical drift ≥0.7 → triage ≤4h | Evidence Pack ≤30min | Replay ≤15min (≤1M events)

Aligns with `governed-execution-system-mvp-blueprint-v1` commercial wedge; extends to full Temporal OS.
""",
    "noetfield-v2-agentic-architecture-summary-duplicate.md": """# Noetfield v2.0 Agentic Architecture — Duplicate

Document key: `noetfield-v2-agentic-architecture-summary-duplicate`

Duplicate executive summary of v2 agentic Temporal Governance OS. **Superseded by**
`noetfield-v2-temporal-governance-os-bank-grade` (full design with APIs, security, roadmap).
""",
    "noetfield-directory-enforced-consistency-spec-fa.md": """# Directory-Enforced Consistency & Value Basket (Persian)

Document key: `noetfield-directory-enforced-consistency-spec-fa`

Operating discipline (FA): every prompt/command must consult the governed directory/SOT registry first so
responses are consistent, documented, citable, and enforceable.

## Requirements

- Continuous validation and risk intelligence across domains with priority ordering
- Smart classification of documents, messages, emails
- Track which documents are newer, why written, where they drifted
- Aggregate fragment values into a **value proposition basket** when system is uncertain between top options
- Operator (founder) accepts/rejects recommendations → system coherence improves
- Bank-grade PDF export of governance state for audit citation

Maps to: `docs/SOURCE_OF_TRUTH/registry/`, ingest pipeline, Evidence Pack, Human Gatekeeper triage.
""",
    "noetfield-governance-rollout-checklist-v1.md": """# Governance Rollout & Pilot Checklist v1

Document key: `noetfield-governance-rollout-checklist-v1`

Pre-production must-haves: HSM keys, Policy Engine agent rules, Evidence Pack verification guide,
legal hold metadata, multi-sig for high-risk, triage/remediation playbooks.

6-phase rollout: prep → event core → snapshots → drift/conflict → risk/decision → audit/replay.

Complements `noetfield-6-week-sprint-plan-solo-founder-v1` with compliance gates.
""",
}

NEW_SOT = [
    {
        "domain": "noetfield_execution_kernel_spec",
        "active_document_key": "noetfield-execution-kernel-temporal-v1-canonical",
        "active_version": "temporal-kernel-v1.0",
        "decision": "active_source_of_truth",
        "rationale": "Canonical temporal event-sourced kernel: derived state, LLM proposal-only, arbitration, saga, cached replay.",
        "confidence": 0.93,
    },
    {
        "domain": "noetfield_temporal_governance_v2",
        "active_document_key": "noetfield-v2-temporal-governance-os-bank-grade",
        "active_version": "temporal-governance-v2.0",
        "decision": "active_source_of_truth",
        "rationale": "Bank-grade v2 Temporal Governance OS: event core, drift, evidence packs, human gatekeeper; distinct from v3.1 ambient SOT.",
        "confidence": 0.9,
    },
    {
        "domain": "noetfield_evidence_pack_schema",
        "active_document_key": "noetfield-evidence-pack-json-schema-v1",
        "active_version": "evidence-pack-schema-v1",
        "decision": "active_source_of_truth",
        "rationale": "Signed portable Evidence Pack JSON schema for auditors; aligns with Trust Ledger / Copilot wedge.",
        "confidence": 0.92,
    },
    {
        "domain": "noetfield_agent_catalog",
        "active_document_key": "noetfield-agent-catalog-bank-grade-v1",
        "active_version": "agent-catalog-v1",
        "decision": "active_source_of_truth",
        "rationale": "Scoped agent roster with least privilege; Executor disabled by default; human-only production authority.",
        "confidence": 0.91,
    },
    {
        "domain": "noetfield_human_gatekeeper_ui",
        "active_document_key": "noetfield-human-gatekeeper-ui-wireframe-v1",
        "active_version": "gatekeeper-ui-v1",
        "decision": "active_operational_reference",
        "rationale": "Triage queue, diff viewer, HSM approval modal, replay/export flows for steward decisions.",
        "confidence": 0.86,
    },
    {
        "domain": "noetfield_pilot_delivery_plan",
        "active_document_key": "noetfield-6-week-sprint-plan-solo-founder-v1",
        "active_version": "sprint-6wk-v1",
        "decision": "active_operational_reference",
        "rationale": "Week-by-week pilot build plan for agent platform through Gatekeeper UI and hardening.",
        "confidence": 0.85,
    },
    {
        "domain": "noetfield_operating_discipline",
        "active_document_key": "noetfield-directory-enforced-consistency-spec-fa",
        "active_version": "directory-discipline-fa-v1",
        "decision": "active_source_of_truth",
        "rationale": "Directory/SOT-first responses, drift tracking, value basket for uncertain rankings, founder approval loop.",
        "confidence": 0.88,
    },
]

NEW_RULES = [
    {
        "rule_key": "state-derived-from-event-log-only",
        "domain": "noetfield_execution_kernel_spec",
        "source_document_key": "noetfield-execution-kernel-temporal-v1-canonical",
        "activation_status": "active_design_rule",
        "rule_type": "runtime_governance",
        "summary": "Authoritative state is REDUCE(events); no direct state persistence as truth.",
        "implementation_target": "postgres_runtime",
    },
    {
        "rule_key": "replay-cached-llm-outputs-only",
        "domain": "noetfield_execution_kernel_spec",
        "source_document_key": "noetfield-execution-kernel-temporal-v1-canonical",
        "activation_status": "active_design_rule",
        "rule_type": "runtime_governance",
        "summary": "Exact audit replay uses cached LLM tokens; no regeneration on replay path.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "no-autonomous-production-execution",
        "domain": "noetfield_agent_catalog",
        "source_document_key": "noetfield-agent-catalog-bank-grade-v1",
        "activation_status": "active_design_rule",
        "rule_type": "agent_governance",
        "summary": "Agents propose and package evidence; production changes require signed human approval in audit log.",
        "implementation_target": "policy_runtime",
    },
    {
        "rule_key": "executor-agent-disabled-by-default",
        "domain": "noetfield_agent_catalog",
        "source_document_key": "noetfield-agent-catalog-bank-grade-v1",
        "activation_status": "active_design_rule",
        "rule_type": "agent_governance",
        "summary": "Executor Agent locked off unless multi-sig human approval enables safe-zone automation.",
        "implementation_target": "policy_runtime",
    },
    {
        "rule_key": "evidence-pack-hsm-signed-manifest",
        "domain": "noetfield_evidence_pack_schema",
        "source_document_key": "noetfield-evidence-pack-json-schema-v1",
        "activation_status": "active_design_rule",
        "rule_type": "audit_governance",
        "summary": "Evidence Packs require manifest SHA-256 and detached HSM signatures with verify.sh path.",
        "implementation_target": "trust_ledger",
    },
    {
        "rule_key": "critical-drift-triage-sla-4h",
        "domain": "noetfield_temporal_governance_v2",
        "source_document_key": "noetfield-v2-temporal-governance-os-bank-grade",
        "activation_status": "candidate_requires_formalization",
        "rule_type": "operational_sla",
        "summary": "drift_score ≥ 0.7 or slope > 0.05/day triggers human triage within 4 hours.",
        "implementation_target": "monitoring",
    },
    {
        "rule_key": "directory-sot-consult-before-response",
        "domain": "noetfield_operating_discipline",
        "source_document_key": "noetfield-directory-enforced-consistency-spec-fa",
        "activation_status": "active_design_rule",
        "rule_type": "operating_discipline",
        "summary": "Prompts and commands must consult governed SOT registry/directory before answering or acting.",
        "implementation_target": "source_of_truth_registry",
    },
    {
        "rule_key": "value-basket-on-uncertain-ranking",
        "domain": "noetfield_operating_discipline",
        "source_document_key": "noetfield-directory-enforced-consistency-spec-fa",
        "activation_status": "active_design_rule",
        "rule_type": "operating_discipline",
        "summary": "When top options tie, aggregate document value into proposition basket for founder accept/reject.",
        "implementation_target": "workflow_runtime",
    },
    {
        "rule_key": "agent-least-privilege-scoped-identity",
        "domain": "noetfield_agent_catalog",
        "source_document_key": "noetfield-agent-catalog-bank-grade-v1",
        "activation_status": "active_design_rule",
        "rule_type": "agent_governance",
        "summary": "Each agent runs minimal IAM scope; violations quarantine agent and generate Evidence Pack.",
        "implementation_target": "policy_runtime",
    },
    {
        "rule_key": "human-gatekeeper-hsm-sign-approval",
        "domain": "noetfield_human_gatekeeper_ui",
        "source_document_key": "noetfield-human-gatekeeper-ui-wireframe-v1",
        "activation_status": "active_design_rule",
        "rule_type": "ui_governance",
        "summary": "Production approvals flow through Gatekeeper UI with HSM signing and append to event store.",
        "implementation_target": "copilot_governance",
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (BATCH_DIR / doc["file"]).write_text(BODIES[doc["file"]].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-011

Temporal execution kernel canonical spec, v2 Temporal Governance OS (bank-grade),
agent catalog, Evidence Pack schema, Human Gatekeeper UI, 6-week sprint, and
directory-enforced operating discipline (Persian).

## Active SOT domains

- `noetfield_execution_kernel_spec` — temporal event-sourced kernel
- `noetfield_temporal_governance_v2` — v2 product architecture (≠ v3.1 ambient)
- `noetfield_evidence_pack_schema` — signed audit packs
- `noetfield_agent_catalog` — bank-grade agent roster
- `noetfield_operating_discipline` — SOT-first responses + value basket (FA)

## Lineage

- Complements batch 010 Postgres stack + RFC/LangGraph specs
- Aligns with `governed-execution-system-mvp-blueprint-v1` and Trust Ledger wedge
- Duplicate v2 executive summaries superseded by bank-grade design doc
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inv_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {"batch_id": "2026-05-011", "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-011"}
    )

    for doc in DOCS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-011/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-011",
            }
        )

    replace_domains = {d["domain"] for d in NEW_SOT}
    sot["decisions"] = [d for d in sot["decisions"] if d["domain"] not in replace_domains]
    sot["decisions"].extend(NEW_SOT)
    sot["registry_version"] = "2026-05-29-sot-8"

    rules["registry_version"] = "2026-05-29-rules-8"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"documents: {len(inventory['documents'])}")
    print(f"decisions: {len(sot['decisions'])}")
    print(f"rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
