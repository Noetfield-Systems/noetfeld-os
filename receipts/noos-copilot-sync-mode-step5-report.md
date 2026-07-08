NOOS Copilot Sync Mode Patch — Step 5 Report

Summary of changes applied
- Replaced binary cloud_write_allowed with scoped cloud_sync_mode and cloud_write_scope authority model.
- Files added/updated:
  - docs/NOOS_COPILOT_DISPATCHER_AUTHORITY.md
  - data/noos-copilot-dispatcher-mode-v1.json
  - data/noos-integrator-role-v1.json (added modes and dispatcher_authority_rules)
  - receipts/noos-copilot-dispatcher-mode-patch-20260703T195800Z.json

SG pointer / package-map updates required
1) SG (sina-governance) pointer update
- Action: add pointer in the governance SSOT to reference the new machine record and authority doc so SG can reference the authoritative dispatcher policy.
- Files to update (recommended):
  - sina-governance-SSOT (SSOT repo or file): add entry pointing to data/noos-copilot-dispatcher-mode-v1.json and docs/NOOS_COPILOT_DISPATCHER_AUTHORITY.md
  - noetfield-org/REPO_REGISTRY.md: add a note under relevant repos (noetfeld-os, sina-governance-SSOT) that the dispatcher authority record exists at data/noos-copilot-dispatcher-mode-v1.json

2) Package map / registry updates
- Action: ensure package registry or package map includes the machine record so CI/runtimes can locate it.
- Files to update (recommended):
  - packages map (if present): add an entry mapping key "noos-copilot-dispatcher-mode" -> "data/noos-copilot-dispatcher-mode-v1.json". If using a central package map (e.g., packages/* or .noetfield/manifest), register the record there.
  - noetfield-org/SYNC_RECEIPTS.md or similar registry files: reference the new schema name "noos-copilot-dispatcher-mode-v1" and where to find it.

3) CI enforcement
- Action: add a CI job that reads data/noos-copilot-dispatcher-mode-v1.json to refuse merges where a dispatch attempt sets cloud_sync_mode to fleet_rollout or writes to main without validator receipt.
- File suggestion: .github/workflows/enforce-dispatcher-modes.yml (implementation not included in this patch).

Operational notes
- Keep fleet_propagation_allowed=false until validators and bounded PR promotion path are implemented and tested.
- Runtime dispatchers must be updated to read the machine record (data/noos-copilot-dispatcher-mode-v1.json) before acting. This is a follow-up runtime change and must be done via a bounded PR and review.

Receipt
- Patch receipt: receipts/noos-copilot-dispatcher-mode-patch-20260703T195800Z.json

Stop: no further changes made.
