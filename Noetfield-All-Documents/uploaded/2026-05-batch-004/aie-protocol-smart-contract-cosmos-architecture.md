# AIE Protocol - Smart Contract and Cosmos Module Architecture

Document key: `aie-protocol-smart-contract-cosmos-architecture`

Source status: hybrid execution layer for agentic intelligence economies

## Normalized purpose

This document defines AIE as a dual-layer execution architecture for agentic
intelligence economies.

## Architecture

Layer A: EVM Layer

- token logic
- staking
- task escrow
- settlement
- governance

Layer B: Cosmos SDK Layer

- agent coordination
- task DAG orchestration
- reputation system
- validation consensus
- inter-agent messaging

## Core modules

Solidity:

- AIEToken
- StakeManager
- TaskEscrow
- Governance
- BridgeAdapter

Cosmos SDK:

- x/agent
- x/task
- x/execution
- x/validation
- x/reputation
- x/economy

## Registry classification

Classify as active AIE protocol reference and separate protocol lineage. It is
not part of the current Noetfield backend runtime unless an AIE module is
explicitly scoped later.

