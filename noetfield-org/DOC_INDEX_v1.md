# NOETFIELD-ORG DOC INDEX v1

**Agents: read this file first.**  
**Canonical root:** `noetfeld-OS/noetfield-org/` (inside NOOS repo only)

---

## DO NOT READ (stale / wrong paths)

| Path | Why |
|------|-----|
| `Noetfield-Systems/noetfield-org/` at workspace root | Misplaced drafts — **empty except stale pointer** |
| Any doc outside `noetfeld-OS/noetfield-org/` for NOOS strategy | Not canonical |
| Files containing tokens in `FORBIDDEN_MARKERS.txt` | Invalid / obsolete platform references |

**If you find strategy drafts at workspace-root `noetfield-org/`, ignore them.** Use `noetfeld-OS/noetfield-org/` only.

---

## Current — use these

| Document | Purpose |
|----------|---------|
| `DOC_INDEX_v1.md` | **This file — read first** |
| `FORBIDDEN_MARKERS.txt` | Tokens that must not appear in new docs or agent plans |
| `LIVING_SYSTEM_UPGRADE_PROPAGATION_v1.md` | **LSUP design — how laws propagate across all nodes** |
| `system-laws/SYSTEM_LAW_REGISTRY_v1.json` | Active system laws + blast radius templates |
| `scripts/noos_law_drift_check_v1.py` | LSUP v0.1 forbidden-token drift scanner |
| `REPO_REGISTRY.md` | Repo registry |
| `ROUTING_MATRIX.md` | Execution routing |
| `LOOP_STATE.json` | Loop / integrator state |
| `SYNC_RECEIPTS.md` | Sync ledger |
| `AGENT_REGISTRY.md` | Agent roles |
| `SERVICE_LANES.md` | Service lane registry |
| `NOOS_CONTROL_PANEL_AUTHORITY_REPORT_2026-07-04.md` | NOOS path authority |
| `NOOS_LOCK_RECEIPT_v1.json` | Brain taxonomy lock |
| `NOETFIELD_COMPANY_STRATEGY_v1_BLUEPRINT.md` | Company strategy (not SG-ratified) |
| `WWW_IMPLEMENTATION_STATUS_v1.md` | **Live www route truth — read before gate edits** |
| `NOETFIELD_STRATEGY_LOCK_RECEIPT_v1.json` | Strategy + publish rules |
| `proof-page-draft/` | Case Study #1 content drafts |

### proof-page-draft/

| File | Purpose |
|------|---------|
| `INVESTOR_CASE_STUDY_MODEL_v1.md` | Case study framework |
| `CASE_STUDY_TEMPLATE_v1.md` | Template for SourceA, SourceB, etc. |
| `noetfield.json` | Case Study #1 evidence bundle |
| `noetfield.html.md` | Case Study #1 page content |
| `noetfield_public_evidence_bundle_v1.schema.json` | Public JSON schema |
| `PUBLISH_PLAN.md` | Agent deploy execution steps |
| `CONTENT_READINESS_v1.md` | Pre-deploy checklist (EXECUTION_READY) |

---

## Locked rules

1. **Agents deploy** via approved Noetfield www production path (`Noetfield/scripts/deploy-www-cloudflare.sh` → Cloudflare Pages `noetfield-www`).
2. **Deploy fence:** clean `main` synced with `origin/main` (see deploy script).
3. **Canonical docs:** `noetfeld-OS/noetfield-org/` only.
4. **No public "holding company" or `/protocol` marketing** until commissioned.
5. **Brain taxonomy:** no unqualified "Brain" in public copy.
6. **Forbidden tokens:** see `FORBIDDEN_MARKERS.txt` — do not introduce them in new text.

---

## Superseded names (do not recreate)

| Old | Use instead |
|-----|-------------|
| `NOETFIELD_HOLDING_STRATEGY_*` | `NOETFIELD_COMPANY_STRATEGY_v1_BLUEPRINT.md` |
| `BUILD_PLAN.md` | `PUBLISH_PLAN.md` |
| `EXECUTION_READINESS_v1.md` | `CONTENT_READINESS_v1.md` |
| Workspace-root `noetfield-org/` | `noetfeld-OS/noetfield-org/` |

---

## www production truth (single line)

**Noetfield www:** Cloudflare static www — see `SERVICE_LANES.md` and `docs/ops/NOOS_CLOUDFLARE_WWW_DEPLOY_v1.md`.

---

**Next agent action:** Read `WWW_IMPLEMENTATION_STATUS_v1.md` before www edits. Case Study #1 is live at `/proof/noetfield/`; direction gate at `/` is founder-approved — do not downgrade to marketing homepage.
