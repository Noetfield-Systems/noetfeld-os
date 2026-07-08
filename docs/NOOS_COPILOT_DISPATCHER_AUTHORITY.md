NOOS Copilot — P2 Dispatcher Sync Mode Patch

Overview

This document replaces the previous binary cloud_write_allowed rule with a scoped cloud_sync_mode + cloud_write_scope authority model for NOOS Copilot (P2 cross-repo sync dispatcher).

Scope
- Applies to repos and lanes: sina-governance-SSOT, noetfeld-os, SourceA, Noetfield, TrustField-Technologies
- Applies to NOOS Copilot dispatcher behavior only; does NOT grant policy ownership.

New model

1) cloud_sync_mode (ordered capability list)
 - read_status
 - publish_receipt
 - publish_status
 - publish_drift_report
 - prepare_draft_branch
 - prepare_pr
 - fleet_rollout

2) cloud_write_scope (granular write scopes)
 - none
 - receipts_only
 - status_only
 - drift_report_only
 - draft_branch
 - pr_ready
 - release_candidate

Authority rules
- Do NOT use a single cloud_write_allowed boolean.
- Dispatcher decisions must be expressed as a tuple: (cloud_sync_mode, cloud_write_scope).
- Allowed modes for NOOS Copilot by default: read_status, publish_receipt, publish_status, publish_drift_report, prepare_draft_branch, prepare_pr.
- Blocked/unavailable modes by default: fleet_rollout, ACTIVE promotion, direct main write, policy/law mutation, publishing audit-pending registry as active fleet truth.
- fleet_propagation_allowed MUST remain false until validator PASS + receipt + bounded PR path are present.
- main_write_allowed MUST remain false.
- NOOS Copilot MAY dispatch sync/status/receipt/PR-prep work but MAY NOT become policy owner or run recurring Copilot automation.

Operational notes
- Every dispatch that requests a write-capable mode must produce a validator receipt with fields: validator_id, validation_status, receipt_path, timestamp, and cost_policy_pass where applicable.
- Transition to fleet_rollout or release_candidate requires an explicit PR review and a separate promotion workflow with human approval.
- Any request to expand cloud_write_scope must be proposed via a bounded PR and include a test fixture showing negative-proof checks for forbidden classes.

Audit & Enforcement
- The dispatcher machine record (data/noos-copilot-dispatcher-mode-v1.json) must be the source of truth for allowed modes for automated enforcement.
- CI checks should refuse merges that attempt to set cloud_sync_mode to fleet_rollout without the required validator receipt and PR path.

