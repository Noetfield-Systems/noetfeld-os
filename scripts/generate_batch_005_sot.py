#!/usr/bin/env python3
"""Generate batch 005 source-of-truth uploads and registry deltas."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-005"
REGISTRY_DIR = ROOT / "docs/SOURCE_OF_TRUTH/registry"

DOCUMENTS: list[dict] = [
    {
        "file": "aie-protocol-full-production-repo-structure.md",
        "document_key": "aie-protocol-full-production-repo-structure",
        "title": "AIE Protocol — Full Production Monorepo Structure",
        "domain": "aie_protocol",
        "version_label": "production-repo-v1",
        "classification": "active_repo_layout_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "body": """# AIE Protocol — Full Production Repo Structure

Document key: `aie-protocol-full-production-repo-structure`

## Normalized purpose

Defines the target monorepo layout for AIE Protocol spanning Ethereum contracts,
Cosmos SDK chain, agent-runtime, validator-network, bridge, SDK, frontend, and
infra layers.

## Top-level layout

- `contracts/` — Solidity core (AIEToken, TaskEscrow, StakeManager, Governance, BridgeAdapter)
- `cosmos/` — Cosmos SDK modules (`x/agent`, `x/task`, `x/execution`, `x/validation`, `x/reputation`, `x/economy`)
- `agent-runtime/` — off-chain cognitive engine (planner, executor, memory, critic, tools)
- `validator-network/` — consensus, scoring, slashing, validator API
- `bridge/` — ethereum-to-cosmos and cosmos-to-ethereum relayers
- `sdk/` — TypeScript/Python developer toolkit
- `frontend/` — dashboard and agent marketplace UI
- `infra/` — Kubernetes, Terraform, monitoring, CI/CD
- `specs/` and `docs/` — protocol truth and investor/developer documentation

## Three coordinated systems

1. Economic Layer (Ethereum) — tokens, staking, settlement, governance
2. Cognitive Layer (Cosmos) — agents, task graphs, validation, reputation
3. Execution Layer (off-chain) — AI runtime, tools, memory, orchestration

## Registry note

Separate protocol lineage from Noetfield. Use as implementation scaffold reference
only unless an AIE module is explicitly scoped.
""",
    },
    {
        "file": "aie-protocol-decentralized-cognitive-execution-network-deck.md",
        "document_key": "aie-protocol-decentralized-cognitive-execution-network-deck",
        "title": "AIE Protocol — Decentralized Cognitive Execution Network (Investor Deck)",
        "domain": "aie_protocol",
        "version_label": "investor-deck-v1",
        "classification": "active_investor_narrative_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "body": """# AIE Protocol — Decentralized Cognitive Execution Network

Document key: `aie-protocol-decentralized-cognitive-execution-network-deck`

## Core thesis

AIE is Agentic Intelligence Economy Infrastructure: autonomous agents execute,
validate, and settle cognitive work as a tokenized economy.

Flow: Human Intent → Agent Execution → Validation Network → Economic Settlement

## Primitives

- **Cognitive Work Unit (CWU)** — economic unit of machine reasoning work
- **Task DAG engine** — all work decomposes into validated directed acyclic graphs
- **Agent economy** — worker, planner, validator, oracle agent roles

## Stack

1. Economic Layer (Ethereum)
2. Cognitive Layer (Cosmos)
3. Execution Layer (off-chain agent runtime)

## Moat themes

Execution history graph, reputation system, agent specialization network,
cognitive DAG dataset.

## Registry note

Investor narrative companion to the technical whitepaper. Not Noetfield runtime authority.
""",
    },
    {
        "file": "aie-protocol-tokenomics-adaptive-supply-model.md",
        "document_key": "aie-protocol-tokenomics-adaptive-supply-model",
        "title": "AIE Protocol Tokenomics — Adaptive Supply and Equilibrium Dynamics",
        "domain": "aie_tokenomics",
        "version_label": "adaptive-supply-v1",
        "classification": "superseded_tokenomics_reference",
        "status": "superseded",
        "supersedes": [],
        "superseded_by": "aie-protocol-tokenomics-mathematical-model-v1",
        "body": """# AIE Protocol Tokenomics — Adaptive Supply Model

Document key: `aie-protocol-tokenomics-adaptive-supply-model`

## Core identity

S_{t+1} = S_t + I_t - B_t

## Emissions

I_t = λ · S_t · g(U_t) · h(Q_t) with g(U_t) = U_t / (1 + U_t) and h(Q_t) ∈ [0.5, 1.5]

## Burn

B_t = α · F_t · log(1 + U_t)

## Equilibrium target

lim |I_t - B_t| → 0 — usage-responsive emissions matched by execution-based burns.

## Supersession

Superseded by `aie-protocol-tokenomics-mathematical-model-v1` for staking yield
and stress-scenario detail. Retained for provenance.
""",
    },
    {
        "file": "aie-protocol-vc-technical-appendix.md",
        "document_key": "aie-protocol-vc-technical-appendix",
        "title": "AIE Protocol — VC Technical Appendix (Institutional Diligence)",
        "domain": "aie_protocol",
        "version_label": "vc-appendix-v1",
        "classification": "active_diligence_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "body": """# AIE Protocol — VC Technical Appendix

Document key: `aie-protocol-vc-technical-appendix`

## Classification

Decentralized Cognitive Execution Network (DCEN): blockchain settlement + multi-agent
AI execution + task graph networks + cryptoeconomic validation.

## Formal models

- Agent = (S, P, M, T) — state, policy, memory, tools
- Validation score V = Σ(w_i × v_i) with acceptance if V ≥ τ
- Supply dynamics and adversarial threat matrix (Sybil, collusion, bridge attacks)

## Performance boundary

| Layer | Determinism | Latency | Trust |
|-------|-------------|---------|-------|
| Ethereum | deterministic | high | cryptographic |
| Cosmos | semi-deterministic | medium | consensus |
| Off-chain | probabilistic | low | reputation + validation |

## Registry note

Diligence supplement; defers to whitepaper for normative protocol specification.
""",
    },
    {
        "file": "aie-protocol-tokenomics-mathematical-model-v1.md",
        "document_key": "aie-protocol-tokenomics-mathematical-model-v1",
        "title": "AIE Protocol Tokenomics Mathematical Model",
        "domain": "aie_tokenomics",
        "version_label": "mathematical-model-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": ["aie-protocol-tokenomics-adaptive-supply-model"],
        "superseded_by": None,
        "body": """# AIE Protocol Tokenomics Mathematical Model

Document key: `aie-protocol-tokenomics-mathematical-model-v1`

## Supply dynamics

S_{t+1} = S_t + I_t - B_t

## Inflation

I_t = λ · S_t · (U_t / (1 + U_t)) · V_t

## Burn

B_t = α · F_t · (1 + log(1 + U_t))

## Staking yield

R_t = (I_t + β · F_t) / St_t with equilibrium St* ≈ √((I_t + βF_t) / k)

## Net supply pressure

NSP_t = I_t - B_t — target lim NSP_t → 0

## Value capture

Token_Value ∝ (Network_Usage × Fee_Pressure) / Supply_Expansion

## Active tokenomics SOT

This document is the authoritative tokenomics reference for the AIE protocol lineage.
""",
    },
    {
        "file": "aie-protocol-full-technical-whitepaper.md",
        "document_key": "aie-protocol-full-technical-whitepaper",
        "title": "AIE Protocol — Full Technical Whitepaper (DCEN Specification)",
        "domain": "aie_protocol",
        "version_label": "whitepaper-v1",
        "classification": "active_source_of_truth",
        "status": "reference",
        "supersedes": [
            "aie-protocol-decentralized-cognitive-execution-network-deck",
        ],
        "superseded_by": None,
        "body": """# AIE Protocol — Full Technical Whitepaper

Document key: `aie-protocol-full-technical-whitepaper`

## Abstract

Decentralized infrastructure for autonomous AI agents to perform, validate, and
settle cognitive work as a tokenized economy (Decentralized Cognitive Execution
Networks — DCENs).

## Five protocol layers

0. Blockchain base (Ethereum / Cosmos)
1. Agent execution (off-chain runtime, sandbox, tools)
2. Task graph (DAG decomposition and scheduling)
3. Validation (multi-agent consensus, fraud detection)
4. Economic layer (staking, rewards, slashing, reputation)

## Core entities

Agent, Task, Execution Job, Reputation state with on-chain Merkle commitments.

## Token

$AIE — 1B fixed initial supply; dynamic emissions tied to network demand and
validation quality; fees split burn + treasury.

## Innovations

Cognitive work as economic primitive, agent identity as capital, Proof-of-Intelligence
Execution (PoIE).

## Active protocol SOT

Supersedes investor deck for normative specification. Complements
`aie-protocol-smart-contract-cosmos-architecture` module-level detail from batch 004.
""",
    },
    {
        "file": "aie-tokenized-agentic-network-design.md",
        "document_key": "aie-tokenized-agentic-network-design",
        "title": "Tokenized Agentic Network Design (AIE Protocol)",
        "domain": "aie_protocol",
        "version_label": "network-design-v1",
        "classification": "active_product_design_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "body": """# Tokenized Agentic Network Design

Document key: `aie-tokenized-agentic-network-design`

## Four layers

1. Agent Layer — reason, plan, execute, use tools
2. Task Market Layer — tasks, workflows, constraints
3. Execution Layer — sandboxed job runs
4. Settlement Layer — value measurement, token distribution, reputation

## Trust model

Reputation R = f(success_rate, validation_score, stake_at_risk, historical_consistency).
Trust is computed, not assumed.

## Multi-agent economy

Architect proposes; workers execute variations; validators audit; rewards split
proportionally.

## Registry note

Product and market mechanism design reference under the AIE lineage.
""",
    },
    {
        "file": "aiis-investor-whitepaper-agentic-intelligence-infrastructure.md",
        "document_key": "aiis-investor-whitepaper-agentic-intelligence-infrastructure",
        "title": "AIIS — Agentic Intelligence Infrastructure Systems (Investor Whitepaper)",
        "domain": "aiis_platform",
        "version_label": "investor-whitepaper-v1",
        "classification": "separate_product_lineage_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "body": """# AIIS — Agentic Intelligence Infrastructure Systems

Document key: `aiis-investor-whitepaper-agentic-intelligence-infrastructure`

## Positioning

Enterprise cognitive infrastructure for autonomous AI agents — not an application
layer. Intent-to-Execution Computing.

## Five layers

Intent, Reasoning, Execution, Memory, Governance.

## Business model

SaaS + infrastructure hybrid: per-agent compute, orchestration licensing,
workflow fees, governance subscription.

## Separation from Noetfield and AIE

AIIS is a distinct enterprise infrastructure narrative. Do not merge into
Noetfield Postgres runtime or AIE tokenomics without explicit product scope.
""",
    },
    {
        "file": "manifesto-agentic-systems-design.md",
        "document_key": "manifesto-agentic-systems-design",
        "title": "Manifesto for Agentic Systems Design",
        "domain": "agentic_systems_theory",
        "version_label": "manifesto-v1",
        "classification": "active_theory_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "body": """# Manifesto for Agentic Systems Design

Document key: `manifesto-agentic-systems-design`

## Core doctrines

- Intelligence is constraint-driven, not scale-driven alone
- The agent is a loop (perceive → interpret → decompose → act → evaluate → memory)
- Context is the operating system of cognition
- Tools are extensions of cognition; memory is identity persistence
- Failure is a first-class system signal
- Multi-agent systems are cognitive ecosystems

## Human role

Intent architects of cognitive systems — define constraints, shape objectives,
design feedback loops.

## Registry note

Cross-cutting design doctrine. Informs Noetfield governance posture but is not
executable runtime policy by itself.
""",
    },
    {
        "file": "architecture-of-meaning-book-proposal.md",
        "document_key": "architecture-of-meaning-book-proposal",
        "title": "The Architecture of Meaning — Book Proposal and Publishing Blueprint",
        "domain": "cognitive_publishing",
        "version_label": "book-proposal-v1",
        "classification": "separate_knowledge_product_reference",
        "status": "reference",
        "supersedes": [],
        "superseded_by": None,
        "body": """# The Architecture of Meaning — Book Proposal

Document key: `architecture-of-meaning-book-proposal`

## Thesis

Context architecture is the elite engineering bottleneck for bank-grade deterministic
execution from non-deterministic language models (semantic superconductivity).

## Structure

Part I: Latent Matrix | Part II: Superconductive State | Part III: Sovereign Imperative

Key artifacts: Constraint-Density Index, HALT Protocol, Event-Driven Agentic Runtime,
Thermodynamic Information Matrix.

## Registry note

Separate knowledge product from Noetfield platform, POSA, AIE, and AIIS. Reference only.
""",
    },
]

NEW_SOT_DECISIONS = [
    {
        "domain": "aie_protocol",
        "active_document_key": "aie-protocol-full-technical-whitepaper",
        "active_version": "whitepaper-v1",
        "decision": "active_source_of_truth",
        "rationale": "The full technical whitepaper is the normative DCEN specification. Batch 004 module architecture remains a supporting module reference.",
        "confidence": 0.93,
    },
    {
        "domain": "aie_tokenomics",
        "active_document_key": "aie-protocol-tokenomics-mathematical-model-v1",
        "active_version": "mathematical-model-v1",
        "decision": "active_source_of_truth",
        "rationale": "The mathematical model document supersedes the earlier adaptive-supply tokenomics upload with staking yield equilibrium and stress scenarios.",
        "confidence": 0.9,
    },
    {
        "domain": "aie_repo_layout",
        "active_document_key": "aie-protocol-full-production-repo-structure",
        "active_version": "production-repo-v1",
        "decision": "active_implementation_scaffold_reference",
        "rationale": "Monorepo structure defines where contracts, cosmos modules, agent-runtime, and infra live when AIE implementation is scoped.",
        "confidence": 0.85,
    },
    {
        "domain": "aiis_platform",
        "active_document_key": "aiis-investor-whitepaper-agentic-intelligence-infrastructure",
        "active_version": "investor-whitepaper-v1",
        "decision": "separate_product_lineage_reference",
        "rationale": "AIIS is enterprise agent infrastructure positioning, distinct from Noetfield governance runtime and AIE tokenized agent economy.",
        "confidence": 0.88,
    },
    {
        "domain": "agentic_systems_theory",
        "active_document_key": "manifesto-agentic-systems-design",
        "active_version": "manifesto-v1",
        "decision": "active_theory_reference",
        "rationale": "Manifesto encodes constraint-driven agent design doctrine that aligns with Noetfield governance posture without being executable policy.",
        "confidence": 0.82,
    },
    {
        "domain": "cognitive_publishing",
        "active_document_key": "architecture-of-meaning-book-proposal",
        "active_version": "book-proposal-v1",
        "decision": "separate_knowledge_product_reference",
        "rationale": "Book proposal is a standalone publishing product about context engineering, not platform source-of-truth.",
        "confidence": 0.95,
    },
]

NEW_RULES = [
    {
        "rule_key": "aie-cwu-as-economic-primitive",
        "domain": "aie_protocol",
        "source_document_key": "aie-protocol-decentralized-cognitive-execution-network-deck",
        "activation_status": "reference_only",
        "rule_type": "economic_primitive",
        "summary": "Cognitive Work Units tie task DAG execution to verified output and token settlement.",
        "implementation_target": None,
    },
    {
        "rule_key": "aie-validation-weighted-consensus",
        "domain": "aie_protocol",
        "source_document_key": "aie-protocol-full-technical-whitepaper",
        "activation_status": "reference_only",
        "rule_type": "validation_consensus",
        "summary": "Results require weighted validator quorum; sub-threshold scores trigger re-execution.",
        "implementation_target": None,
    },
    {
        "rule_key": "aie-supply-equilibrium-nsp-target",
        "domain": "aie_tokenomics",
        "source_document_key": "aie-protocol-tokenomics-mathematical-model-v1",
        "activation_status": "reference_only",
        "rule_type": "tokenomics",
        "summary": "Protocol targets net supply pressure NSP_t = I_t - B_t approaching zero at steady state.",
        "implementation_target": None,
    },
    {
        "rule_key": "aie-agent-stake-before-high-value-tasks",
        "domain": "aie_protocol",
        "source_document_key": "aie-tokenized-agentic-network-design",
        "activation_status": "reference_only",
        "rule_type": "staking",
        "summary": "Agents stake AIE before high-value execution, validation, or elite pool participation.",
        "implementation_target": None,
    },
    {
        "rule_key": "manifesto-intelligence-is-constraint-driven",
        "domain": "agentic_systems_theory",
        "source_document_key": "manifesto-agentic-systems-design",
        "activation_status": "active_design_rule",
        "rule_type": "cognitive_architecture",
        "summary": "Structured constraints applied to probabilistic reasoning reduce entropy and hallucination risk.",
        "implementation_target": "governance_policy_runtime",
    },
    {
        "rule_key": "manifesto-agent-loop-fundamental-primitive",
        "domain": "agentic_systems_theory",
        "source_document_key": "manifesto-agentic-systems-design",
        "activation_status": "active_design_rule",
        "rule_type": "agent_runtime",
        "summary": "Agent behavior is a closed loop over perception, planning, execution, evaluation, and memory — not a single inference call.",
        "implementation_target": "inspector_runtime",
    },
    {
        "rule_key": "manifesto-failure-first-class-signal",
        "domain": "agentic_systems_theory",
        "source_document_key": "manifesto-agentic-systems-design",
        "activation_status": "active_design_rule",
        "rule_type": "governance",
        "summary": "Failures are constraint-violation signals that must feed audit and correction paths.",
        "implementation_target": "audit_ledger_runtime",
    },
    {
        "rule_key": "aiis-governance-layer-required-for-enterprise",
        "domain": "aiis_platform",
        "source_document_key": "aiis-investor-whitepaper-agentic-intelligence-infrastructure",
        "activation_status": "reference_only",
        "rule_type": "enterprise_governance",
        "summary": "Enterprise agent deployment requires governance layer with permissions, audit logs, and rollback.",
        "implementation_target": None,
    },
]


def main() -> None:
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    for doc in DOCUMENTS:
        path = BATCH_DIR / doc["file"]
        path.write_text(doc["body"].strip() + "\n", encoding="utf-8")

    readme = """# Uploaded Source Document Batch 2026-05-005

This folder preserves and normalizes the fifth resource batch: AIE Protocol
expansion, tokenomics, VC appendix, AIIS investor materials, agentic systems
manifesto, and Architecture of Meaning book proposal.

## Contents

- AIE full production monorepo structure
- AIE decentralized cognitive execution network (investor deck)
- AIE tokenomics (adaptive supply — superseded)
- AIE VC technical appendix
- AIE tokenomics mathematical model (active tokenomics SOT)
- AIE full technical whitepaper (active protocol SOT)
- Tokenized agentic network design
- AIIS investor whitepaper (separate product lineage)
- Manifesto for agentic systems design
- Architecture of Meaning book proposal (separate knowledge product)

## Lineage

- AIE protocol SOT: `aie-protocol-full-technical-whitepaper`
- AIE tokenomics SOT: `aie-protocol-tokenomics-mathematical-model-v1`
- Batch 004 `aie-protocol-smart-contract-cosmos-architecture` remains module-level reference
- Noetfield runtime authority unchanged
"""
    (BATCH_DIR / "README.md").write_text(readme, encoding="utf-8")

    inventory_path = REGISTRY_DIR / "source_document_inventory.json"
    sot_path = REGISTRY_DIR / "source_of_truth_registry.json"
    rules_path = REGISTRY_DIR / "active_rule_candidates.json"

    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    sot = json.loads(sot_path.read_text(encoding="utf-8"))
    rules = json.loads(rules_path.read_text(encoding="utf-8"))

    inventory["batches"].append(
        {
            "batch_id": "2026-05-005",
            "source_folder": "docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-005",
        }
    )

    for doc in DOCUMENTS:
        inventory["documents"].append(
            {
                "document_key": doc["document_key"],
                "title": doc["title"],
                "domain": doc["domain"],
                "work_package": None,
                "version_label": doc["version_label"],
                "source_path": f"docs/SOURCE_OF_TRUTH/uploaded/2026-05-batch-005/{doc['file']}",
                "classification": doc["classification"],
                "status": doc["status"],
                "supersedes": doc["supersedes"],
                "superseded_by": doc["superseded_by"],
                "upload_batch": "2026-05-005",
            }
        )

    # Update batch 004 AIE module doc — supporting under whitepaper
    for document in inventory["documents"]:
        if document["document_key"] == "aie-protocol-smart-contract-cosmos-architecture":
            document["classification"] = "active_protocol_module_reference"
            document["superseded_by"] = "aie-protocol-full-technical-whitepaper"
        if document["document_key"] == "aie-protocol-decentralized-cognitive-execution-network-deck":
            pass  # added in batch 005 with supersedes from whitepaper in inventory entry

    # Replace old aie_protocol decision
    sot["decisions"] = [
        d for d in sot["decisions"] if d["domain"] != "aie_protocol"
    ] + [d for d in NEW_SOT_DECISIONS if d["domain"] == "aie_protocol"]
    sot["decisions"].extend([d for d in NEW_SOT_DECISIONS if d["domain"] != "aie_protocol"])
    sot["registry_version"] = "2026-05-29-sot-2"

    rules["registry_version"] = "2026-05-29-rules-2"
    rules["active_rule_candidates"].extend(NEW_RULES)

    inventory_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    sot_path.write_text(json.dumps(sot, indent=2) + "\n", encoding="utf-8")
    rules_path.write_text(json.dumps(rules, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(DOCUMENTS)} documents to {BATCH_DIR}")
    print(f"Total documents: {len(inventory['documents'])}")
    print(f"SOT decisions: {len(sot['decisions'])}")
    print(f"Rules: {len(rules['active_rule_candidates'])}")


if __name__ == "__main__":
    main()
