# WP-03 - NPL Formal Grammar and Execution Semantics

Document key: `wp03-npl-formal-grammar-2026-05-npl-1`

Version: `2026-05-NPL-1`

Role: Policy Engine Compiler Contract

Status in source: Production-Hardened, Implementation-Ready

## Normalized purpose

This document defines the Noetfield Policy Language (NPL) as the declarative,
side-effect-free governance rule language for the Noetfield Developer OS.

NPL expresses governance, risk, regulatory, capital, jurisdiction, and
multi-agent execution constraints. It binds those constraints to Context Graph
snapshots and produces deterministic decisions for the Orchestration Kernel.

## Key source claims

- NPL is not a general programming language.
- NPL is declarative and side-effect free.
- The same graph snapshot and policy set must produce the same result.
- Policies are grouped into packs and versioned.
- Policy decisions are explainable and auditable.
- Policy packs are signed artifacts in production.

## Grammar coverage

The source defines:

- `npl_program`
- imports
- packs
- policies
- type aliases
- action blocks
- allow, deny, approval, route, mask, degrade, assert, log actions
- expressions
- literals
- function calls
- qualified references
- type expressions
- capital, jurisdiction, time, and risk primitives

## AST coverage

The source defines AST nodes for:

- Program
- PackDecl
- PolicyDecl
- Action sum type
- Expr tree
- TypeAliasDecl
- TypeExpr

All AST nodes must carry source location, policy pack, and policy version.

## Execution semantics

Evaluation order:

1. Load active policies by pack, scope, and version.
2. Evaluate every relevant policy.
3. Collect actions into a Decision Set.
4. Apply conflict resolution.
5. Produce a final Policy Decision for the Orchestration Kernel.

Conflict priority:

1. deny
2. require_approval
3. allow
4. route_to / degrade_capabilities / mask_context refinements

## Active-rule relevance

This is the strongest uploaded NPL artifact and should be treated as the active
source-of-truth for the NPL compiler/runtime contract until superseded by an
implemented parser and conformance suite.

