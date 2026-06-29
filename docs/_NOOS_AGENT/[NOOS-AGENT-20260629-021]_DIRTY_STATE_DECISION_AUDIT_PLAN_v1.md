<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260629-021
doc_type: DIRTY_STATE_DECISION_AUDIT_PLAN
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL - dirty state audit and future decision register
-->

# Dirty State Decision Audit Plan - v1

**Created:** 2026-06-29  
**Scope:** `/Users/sinakazemnezhad/Projects/noetfeld-os` dirty tree after live-sync and factory-loop work  
**Purpose:** classify every dirty file into obvious action, generated/defer, or founder decision before commit/deploy.

---

## Current Gate Read

Command:

```bash
python3 scripts/noos_live_sync_gate.py --json
```

Result:

- Gate: `DEGRADED`
- Required Noetfield surfaces usable: **yes**
- Required green nodes: `NOOS_REPO`, `WEBSITE_LIVE_NERVE`, `GEL_RUNTIME`, `PUBLIC_WEBSITE`, `STUDIO_SUPABASE_BOUNDARY`
- Warnings:
  - `sourcea_session_gate_not_green`
  - `website_intelligence_page_404`

Interpretation: safe to use this receipt as current NOOS truth, but do not claim the full ecosystem is completely green until warnings are repaired.

---

## Decision Classes

| Class | Meaning | Who decides |
|---|---|---|
| `OBVIOUS_KEEP` | Consistent with locked docs and current live truth; agent can commit after checks. | Agent |
| `VERIFY_THEN_KEEP` | Looks correct, but needs a command/check before commit. | Agent |
| `GENERATED_DEFER` | Generated or high-churn receipt/state; do not commit automatically. | Founder or explicit receipt policy |
| `FOUNDER_DECISION` | Strategic/product direction or public meaning is ambiguous. | Founder |
| `CROSS_REPO` | Must be handled in website/studio/source repo, not NOOS alone. | Owning repo/agent |

---

## Dirty File Classification

### A. Live Sync Gate - `OBVIOUS_KEEP`

These files create or document the NOOS-side live sync gate. They match `PRODUCT_TRUTH.md` and the website/NOOS sync handoff.

| File | Decision | Reason | Verify |
|---|---|---|---|
| `scripts/noos_live_sync_gate.py` | `OBVIOUS_KEEP` | Repo-local reader for website nerve, GEL health, SourceA nerve, and Studio boundary. | `python3 scripts/noos_live_sync_gate.py --json` |
| `scripts/check_noos_live_sync_gate.sh` | `OBVIOUS_KEEP` | Stable wrapper that writes/validates the receipt. | `bash scripts/check_noos_live_sync_gate.sh` |
| `.cursor/rules/noetfeld-os-agent-vault.mdc` | `OBVIOUS_KEEP` | Adds live-sync read rule before live-state claims. | Manual review |
| `AGENTS.md` | `OBVIOUS_KEEP` | Adds live sync / SAVE routing instructions for this repo. | Manual review |
| `docs/_NOOS_AGENT/README.md` | `OBVIOUS_KEEP` | Clarifies pathless Noetfield SAVE/LOCK routing. | `bash scripts/check_noos_agent_docs.sh` |
| `docs/_NOOS_AGENT/PRODUCT_TRUTH.md` | `OBVIOUS_KEEP` | Adds current live-sync gate status and warnings. | `python3 scripts/noos_live_sync_gate.py --json` |
| `docs/_NOOS_AGENT/[NOOS-AGENT-20260628-019]_WEBSITE_NOOS_REAL_SYNC_HANDOFF_LOCKED_v1.md` | `OBVIOUS_KEEP` | Adds NOOS live sync gate section and warning semantics. | `bash scripts/check_noos_agent_docs.sh` |

### B. Live-State Doc Refresh - `VERIFY_THEN_KEEP`

These refresh stale Phase 1/cloud wording to current live GEL/API truth.

| File | Decision | Reason | Verify |
|---|---|---|---|
| `docs/_NOOS_AGENT/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md` | `VERIFY_THEN_KEEP` | Updates Location 3 from prototype/Phase 1 to live Phase 3 GEL runtime. | `bash scripts/check_noos_agent_docs.sh` |
| `docs/_NOOS_AGENT/[NOOS-AGENT-20260615-010]_BUSINESS_STRATEGY_PROOF_DENSITY_v1.md` | `VERIFY_THEN_KEEP` | Updates demo/API status from DNS blocker to live `api.noetfield.com`. | `bash scripts/check_noos_agent_docs.sh` |
| `docs/_NOOS_AGENT/[NOOS-AGENT-20260626-015]_NOETFIELD_CLOUD_ORGANIZE_MASTER_PLAN_LOCKED_v1.md` | `VERIFY_THEN_KEEP` | Updates cloud plan backlog now that `api.noetfield.com` is live. | `bash scripts/check_noos_agent_docs.sh` |

### C. Public Site Identity Copy - `FOUNDER_DECISION`

These files are inside `noetfeld-os/public_site`, not the active website repo. They make product/company identity claims and should not be silently committed unless the public-site generator is still authoritative.

| File | Decision | Reason | Needed decision |
|---|---|---|---|
| `public_site/content/trust-ledger/index.md` | `FOUNDER_DECISION` | Adds Noetfield Systems / SourceA / TrustField corporate relationship copy. | Confirm whether this static `public_site` tree is active or legacy. |
| `public_site/templates/base.html` | `FOUNDER_DECISION` | Changes footer to parent operating company / SourceA flagship wording. | Confirm whether public footer should say this and whether SourceA should be named. |

Recommended default: do **not** commit these two until the active public website ownership is confirmed. Website repo owns `www.noetfield.com`; NOOS should only provide GEL/runtime truth.

### D. Run Patch Execution State - `GENERATED_DEFER`

These files are generated run/factory state. They are large and can churn whenever the factory runner executes.

| File | Decision | Reason | Needed decision |
|---|---|---|---|
| `docs/run_patches/execution/noetfield_factory_cycles_v1.jsonl` | `GENERATED_DEFER` | Runtime cycle log. | Commit snapshots only when explicitly closing a run. |
| `docs/run_patches/execution/noetfield_factory_heartbeat_v1.json` | `GENERATED_DEFER` | Heartbeat/state file. | Usually do not commit routine heartbeat churn. |
| `docs/run_patches/execution/noetfield_factory_state_v1.json` | `GENERATED_DEFER` | Runtime state. | Commit only if state is intended as official receipt. |
| `docs/run_patches/execution/noetfield_run_patch_execution_receipts_v1.jsonl` | `GENERATED_DEFER` | 10,100 receipt lines reorder/rewrite. | Needs explicit receipt snapshot policy. |
| `docs/run_patches/execution/noetfield_run_patch_execution_state_v1.json` | `GENERATED_DEFER` | Generated state. | Commit only with snapshot policy. |
| `docs/run_patches/noetfield_run_patch_manifest_10100_v1.json` | `GENERATED_DEFER` for `latest_trigger_run` only | Pack definition is source; `latest_trigger_run` is mutable runtime metadata. | Split static manifest metadata from latest-run state in future. |

Recommended default: do not commit generated execution churn. Future cleanup should separate immutable pack source from mutable execution receipts.

### E. Live Sync Receipt - `VERIFY_THEN_KEEP`

| File | Decision | Reason | Verify |
|---|---|---|---|
| `docs/_NOOS_AGENT/live_sync/NOOS_LIVE_SYNC_RECEIPT.json` | `VERIFY_THEN_KEEP` | Current machine-readable receipt for NOOS live truth. Less noisy than factory receipts. | `bash scripts/check_noos_live_sync_gate.sh` |

Recommended default: commit one current receipt with the gate script, then update only when live-state docs change materially.

---

## Remaining Jobs

### Agent-obvious jobs

1. Run:
   ```bash
   bash scripts/check_noos_agent_docs.sh
   bash scripts/check_noos_live_sync_gate.sh
   .venv/bin/python -m pytest -q
   ```
2. Commit only classes `OBVIOUS_KEEP`, `VERIFY_THEN_KEEP`, and this audit plan if checks pass.
3. Exclude or revert generated factory execution churn unless founder chooses a receipt snapshot policy.

### Founder-decision jobs

1. Decide whether `/public_site` in `noetfeld-os` is active or legacy.
2. Decide whether public copy may say:
   - "Noetfield Systems Inc. is the parent operating company"
   - "SourceA is the flagship product"
   - "TrustField Technologies Inc. is a separate product lane"
3. Decide whether generated run-patch execution receipts belong in git, or only source pack + runner scripts belong in git.
4. Decide website nav direction from handoff:
   - rename `Intelligence` to `Home`, or
   - build a real `/intelligence/` hub in the website repo.

### Cross-repo jobs

1. Website repo owns `/intelligence/` 404 repair or nav rename.
2. SourceA session gate warning must be repaired in SourceA, not NOOS.
3. Studio boundary stays in Studio repo; NOOS only records the handoff.

---

## Recommended Commit Plan

### Commit 1 - NOOS live sync gate

Include:

- `.cursor/rules/noetfeld-os-agent-vault.mdc`
- `AGENTS.md`
- `scripts/noos_live_sync_gate.py`
- `scripts/check_noos_live_sync_gate.sh`
- `docs/_NOOS_AGENT/live_sync/NOOS_LIVE_SYNC_RECEIPT.json`
- `docs/_NOOS_AGENT/PRODUCT_TRUTH.md`
- `docs/_NOOS_AGENT/README.md`
- `docs/_NOOS_AGENT/[NOOS-AGENT-20260628-019]_WEBSITE_NOOS_REAL_SYNC_HANDOFF_LOCKED_v1.md`
- `docs/_NOOS_AGENT/[NOOS-AGENT-20260629-021]_DIRTY_STATE_DECISION_AUDIT_PLAN_v1.md`
- `docs/_NOOS_AGENT/MANIFEST.json`

### Commit 2 - Live-state wording refresh

Include after review:

- `docs/_NOOS_AGENT/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md`
- `docs/_NOOS_AGENT/[NOOS-AGENT-20260615-010]_BUSINESS_STRATEGY_PROOF_DENSITY_v1.md`
- `docs/_NOOS_AGENT/[NOOS-AGENT-20260626-015]_NOETFIELD_CLOUD_ORGANIZE_MASTER_PLAN_LOCKED_v1.md`

### Do Not Commit Yet

- `public_site/content/trust-ledger/index.md`
- `public_site/templates/base.html`
- `docs/run_patches/execution/*`
- `docs/run_patches/noetfield_run_patch_manifest_10100_v1.json` latest-run churn

