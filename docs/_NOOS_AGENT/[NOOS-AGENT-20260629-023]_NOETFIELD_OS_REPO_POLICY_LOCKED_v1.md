<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260629-023
doc_type: NOETFIELD_OS_REPO_POLICY_LOCKED
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL - repo boundary and lane policy
-->

# Noetfield OS Repo Policy - Locked v1

**Status:** LOCKED  
**Created:** 2026-06-29  
**Scope:** Noetfield OS runtime/control repository policy

## Core Boundary

Noetfield OS is a separate operating/runtime system. It is not TrustField and not SourceA.

This repo owns:

- GEL/runtime
- gates
- logs
- TLE
- control process
- runtime docs
- operating-system-level governance mechanics

## Hard Rules

- Do not mix Noetfield OS with TrustField architecture, deploy, compliance, or messaging.
- Do not use SourceA as active storage.
- Do not import product-specific Noetfield or TrustField files unless explicitly documented as an interface.
- Noetfield OS may connect through contracts, exports, and manifests only.
- Work lane-by-lane only.
- Limit each pass to 20-40 files.
- Use one atomic commit per coherent lane.
- Generated/evidence outputs must be snapshot plus manifest.

## Required Start Check

Before work in this repo:

1. Run `git status --short`.
2. Confirm branch and dirty count.
3. State target lane.
4. Classify dirty files as one of:
   - `COMMIT`
   - `RESTORE`
   - `DELETE`
   - `SNAPSHOT`
   - `QUARANTINE`
   - `LEAVE`
5. Quarantine SourceA, Noetfield product, or TrustField product files if found unless the file is explicitly documented as an interface.

## Interface Rule

Allowed cross-system contact is by contract only:

- exported JSON manifest
- explicit receipt
- schema/interface file
- documented handoff
- runtime API boundary

No direct storage inheritance, no product-doc copy/paste as implementation law, and no mixed deploy/compliance lane.

