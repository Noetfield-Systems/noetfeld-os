# SINA Founder OS ↔ NOOS Integration Contract v1

**Upstream architecture authority:** `Noetfield-Systems/sina_founder_os` (private)  
**Company implementation:** `Noetfield-Systems/noetfeld-os`  
**Constitution:** `Noetfield-Systems/sina-governance-SSOT/ssot/strategy-ssot-v6-split.md`  
**State:** Contract and CI validation only. No live network dispatch is activated by this document.

## Boundary
Sina Founder OS owns personal founder context and cross-company portfolio prioritization. NOOS owns only Noetfield Systems Inc. company-specific workflow, policy, workforce and existing control loops. The Company Workforce Registry remains the authority for logical N-01…N-08 seats and their evidence-backed activation states.

## Ownership and adapter placement
Use the existing NOOS integrator, machine loops, worker kernel, L17 ROUTING_MATRIX, model router and receipt system. This contract does not add a scheduler, dispatcher, model router, agent registry, memory store, task arbitration system or independent event queue.

## Handoff
Founder OS may submit a `sina-founder-os.mission-envelope.v1` only after it carries:
- Noetfield `company_id` and one authorized `project_id`;
- objective, scope, constraints and acceptance criteria;
- explicit priority, request provenance and idempotency key;
- Executive Governor DecisionRecord reference;
- Next Action Compiler WorkPacket reference;
- A0–A3 authority, budget limit and expiry;
- resource/repository allowlists and evidence references.

NOOS must reject missing, expired, malformed, cross-company or mismatched permits. A Paperclip task or assignment does not establish authority. NOOS re-checks the permit before forwarding to the existing Runway adapter.

## Return projection
Return only company/project/task IDs, lifecycle state, blocker code, bounded actual-cost summary, Runway receipt reference and independent-verifier result. Do not export secrets, raw customer data, unrestricted company memory, prompts or private model reasoning.

## Current live boundary
SINA Governance currently records `NOT_DISPATCHED_SHADOW_ONLY`; its optional Paperclip bridge is default-off and backlog-only. This contract does not enable it. A live Founder OS→NOOS transport is NOT_ACTIVE until an existing endpoint is identified in deployed code, a least-privilege service identity is provisioned, and transport/auth/idempotency/tenant isolation/permit checks pass independently.

## Validation placement
The MissionEnvelope regression tests run inside the existing mapped `.github/workflows/gel-ci.yml` (`Founder OS MissionEnvelope contract validation`). The contract does not create a new unmapped GitHub Actions workflow or touch the frozen `data/noos-parallel-agent-registry-v1.json`.

## Required activation sequence
1. Consume the versioned JSON contract and schema in CI.
2. Verify the actual upstream contract commit/digest and schema compatibility.
3. Implement the adapter inside the existing integrator surface (not a second dispatcher).
4. Negative-test missing/expired permit, A4, tenant mismatch, resource mismatch, duplicate idempotency key, over-budget and unknown schema.
5. Keep network dispatch disabled until P0-PGR/Governor/NAC path and Paperclip ownership/provider/GitHub setup are verified.
6. Run one reversible pilot with one project, one builder, a separate verifier and a complete receipt.

## Canonical upstream
Repository: `Noetfield-Systems/sina_founder_os`  
Contract path: `integrations/noetfeld-os/mission-envelope-v1.json`  
Schema path: `schemas/mission-envelope.schema.json`

Do not change the SINA Constitution or Founder OS architecture from this repository. Policy changes belong to SINA Governance; cross-system architecture changes belong to Founder OS.
