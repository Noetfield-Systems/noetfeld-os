# Engineering done manifest

**Synced from:** `os/plan.json` + `sync-prompt-pack-status.py`  
**Agent tag:** `NF-CLOUD-AGENT`

Shipped capabilities mapped to registry indices. Run `python3 scripts/sync-prompt-pack-status.py` after each ship session.

---

## Waves 023–042 (GTM + Trust Ledger product)

| plan.json id | Capability | Evidence |
|--------------|------------|----------|
| nf-pilot-p1-9-023 | Copilot pilot E2E + checklist | `scripts/copilot-pilot-e2e.sh`, `copilot/pilot/` |
| nf-pdf-board-pack-024 | PDF board pack export | `governance-console/backend/services/board_pack_pdf.py` |
| nf-m365-oauth-025 | M365 connector OAuth skeleton | `governance-console/backend/routes/connectors.py` |
| nf-workspace-rbac-026 | Workspace RBAC viewer vs approver | `governance-console/backend/services/rbac.py` |
| nf-staging-deploy-027 | Staging demo path | `docs/ops/STAGING_DEMO.md` |
| nf-m365-connect-e2e-028 | M365 connect → auto evidence | `scripts/copilot-pilot-e2e.sh` |
| nf-procurement-pack-zip-034 | Procurement zip export | `scripts/procurement-pack-e2e.sh` |
| nf-demo-page-confidence-035 | 5-min demo page | `copilot/demo/index.html` |
| nf-public-demo-url-036 | Public demo URL | `scripts/print-demo-url.sh` |
| nf-procurement-buyer-pack-037 | Procurement buyer page | `copilot/procurement/` |
| nf-workspace-diligence-038 | Workspace diligence UX | `governance-console/frontend/app/workspace/` |
| nf-gtm-pre-demo-verify-039 | `make verify-gtm` | `scripts/verify-gtm.sh` |
| nf-design-partner-sow-040 | Design partner SOW | `docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md` |
| nf-copilot-hub-gtm-041 | Copilot hub GTM | `copilot/index.html` |
| nf-homepage-design-partner-042 | Homepage design-partner CTA | `index.html` |

---

## PLAN WITH NO ASF iterations 1–3

| next_tasks id | Shipped | Evidence |
|---------------|---------|----------|
| ship-audit-export-ux-001 | Audit export CTA + event count | `governance-console/frontend/app/audit/page.tsx` |
| ship-demo-confidence-002 | Confidence on result + dashboard | `app/result/[rid]/page.tsx`, `cognitive-dashboard/` |
| ship-www-tle-copy-003 | trust-ledger www CTAs | `trust-ledger/index.html` |
| ship-result-confidence-e2e-004 | E2E confidence assertion | `scripts/verify-ui-e2e.sh` |
| ship-copilot-demo-links-005 | Demo CTA 200 checks | `scripts/verify-copilot-demo-links.sh` |
| ship-plan-with-no-asf-script-006 | Verify bundle script | `scripts/plan-with-no-asf-verify.sh` |
| ship-pilot-e2e-verify-007 | Pilot e2e in bundle | `scripts/plan-with-no-asf-verify.sh` |
| ship-audit-export-api-e2e-008 | Audit export JSON verify | `scripts/verify-audit-export.sh` |
| ship-procurement-e2e-verify-009 | Procurement e2e in bundle | `scripts/plan-with-no-asf-verify.sh` |

---

## nf-future T0 done (phase-0-ship-ops)

- nf-future-0002 (workspace), 0003 (export), 0004 (copilot), 0005 (agent)
- nf-future-0011 (pilot), 0016 (audit), 0024 (procurement)

---

## PLAN WITH NO ASF iterations 4–5

| next_tasks id | Shipped | Evidence |
|---------------|---------|----------|
| ship-gtm-ops-www-wire-013 | GTM ops docs www wire | `scripts/verify-gtm-ops-docs.sh` |
| ship-buyer-debrief-template-014 | Buyer debrief template | `docs/copilot/BUYER_DEBRIEF_TEMPLATE_v1.md` |
| ship-tier-gate-verify-015 | Tier-gate verify guard | `scripts/verify-tier-gate.sh` |
| ship-bc-ai-for-all-outreach-016 | BC AI outreach doc | `docs/strategy/channel-outreach/bc-ai-for-all-2026.md` |

## PLAN WITH NO ASF iterations 6–9

| next_tasks id | Shipped | Evidence |
|---------------|---------|----------|
| ship-registry-sync-iter6-017 | Registry sync iter 6 | `scripts/sync-prompt-pack-status.py` |
| ship-bc-ai-www-wire-018 | BC AI www wire | `scripts/verify-gtm-ops-docs.sh` |
| ship-dual-brand-boundary-019 | Dual-brand boundary | `docs/spec/trustfield-noetfield-conflict-matrix.md` |
| ship-registry-pattern-propagation-020 | QUICK_PICK dedup | `scripts/sync-prompt-pack-status.py` |
| ship-diligence-procurement-wire-021 | RPAA procurement wire | `copilot/procurement/` |
| ship-design-partner-bc-ai-022 | BC AI pipeline block | `docs/copilot/DESIGN_PARTNER_PIPELINE_v1.md` |
| ship-gtm-next-queue-023 | GTM_NEXT queue | `docs/ops/plans/no-asf/GTM_NEXT.md` |
| ship-staging-demo-www-wire-024 | STAGING_DEMO www wire | `docs/ops/STAGING_DEMO.md` |
| ship-security-buyer-tle-copy-025 | Security buyer TLE copy | `trust-ledger/index.html` |
| ship-procurement-one-pager-wire-027 | Procurement one-pager wire | `copilot/index.html`, `copilot/procurement/` |
| ship-governance-sources-www-028 | Sources Book on procurement | `copilot/procurement/index.html` |
| ship-homepage-demo-cta-029 | Homepage demo CTA verify | `scripts/verify-ui-e2e.sh` |

## PLAN WITH NO ASF — 10-phase audit fix (030–032)

| next_tasks id | Shipped | Evidence |
|---------------|---------|----------|
| ship-tunnel-smoke-verify-030 | Optional staging-smoke in verify | `scripts/plan-with-no-asf-verify.sh` |
| ship-governance-sources-handbook-031 | Handbook link on procurement | `copilot/procurement/index.html` |
| ship-copilot-hub-sources-032 | Sources Book on copilot hub | `copilot/index.html` |

## PLAN WITH NO ASF iter 11 (033–035)

| next_tasks id | Shipped | Evidence |
|---------------|---------|----------|
| ship-trust-brief-intake-wire-033 | Trust-brief intake on hub | `copilot/index.html`, `verify-gtm-ops-docs.sh` |
| ship-drift-sources-procurement-034 | Drift sources on procurement | `copilot/procurement/index.html` |
| ship-demo-rehearsal-hub-wire-035 | Demo rehearsal on hub | `copilot/index.html` |

## ID namespace note

`ship-*-NNN` (GTM `next_tasks`) and `nf-*-NNN` (product waves above) may share numeric suffixes — different namespaces, not duplicate shipped work.

## PLAN WITH NO ASF iter 15 (045–047)

| next_tasks id | Shipped | Evidence |
|---------------|---------|----------|
| ship-trust-brief-parity-audit-045 | Trust-brief parity loop (4 pages) | `scripts/verify-gtm-ops-docs.sh` |
| ship-merged-pr-open-prs-gate-046 | OPEN_PRS merged #41–#44 FAIL | `scripts/verify-no-asf-coherence.sh` |
| ship-demo-rehearsal-demo-047 | Demo rehearsal in script ol | `copilot/demo/index.html`, `verify-gtm-ops-docs.sh` |

## Seventh audit fix (post–PR #44 truth + iter 15)

| Area | Shipped | Evidence |
|------|---------|----------|
| Post-merge truth | OPEN_PRS #44 merged @ c2543b5 | `OPEN_PRS.md`, `COMPLETED_ON_MAIN.md` |
| Iter 15 verify + www | Trust-brief parity, merged PR gate, demo rehearsal ol | `verify-gtm-ops-docs.sh`, `PLATFORM_BLUEPRINT.md` §2 |

## PLAN WITH NO ASF iter 14 (042–044)

| next_tasks id | Shipped | Evidence |
|---------------|---------|----------|
| ship-trust-brief-demo-042 | Trust-brief on demo | `copilot/demo/index.html`, `verify-gtm-ops-docs.sh` |
| ship-demo-rehearsal-pilot-043 | Rehearsal in pilot checklist ol | `copilot/pilot/index.html` |
| ship-open-prs-autocheck-044 | OPEN_PRS vs gh FAIL gate | `scripts/verify-no-asf-coherence.sh` |

## Sixth audit fix (post–PR #43 truth + iter 14)

| Area | Shipped | Evidence |
|------|---------|----------|
| Post-merge truth | OPEN_PRS #43 merged @ 9f0e3f7 | `OPEN_PRS.md`, `COMPLETED_ON_MAIN.md` |
| Iter 14 www + verify | Demo trust-brief, pilot rehearsal ol, OPEN_PRS autocheck | `copilot/demo/`, `verify-no-asf-coherence.sh` |

## PLAN WITH NO ASF iter 13 (039–041)

| next_tasks id | Shipped | Evidence |
|---------------|---------|----------|
| ship-trust-brief-pilot-039 | Trust-brief on pilot | `copilot/pilot/index.html`, `verify-gtm-ops-docs.sh` |
| ship-procurement-cta-homepage-040 | Homepage procurement verify | `index.html`, `verify-ui-e2e.sh`, `verify-gtm-ops-docs.sh` |
| ship-cursor-reply-coherence-041 | cursor-reply SHA FAIL gate | `scripts/verify-no-asf-coherence.sh` |

## Fifth audit fix (post–PR #42 truth + iter 13)

| Area | Shipped | Evidence |
|------|---------|----------|
| Post-merge truth | OPEN_PRS #42 merged, COMPLETED_ON_MAIN @ 43715a4 | `OPEN_PRS.md`, `COMPLETED_ON_MAIN.md` |
| Iter 13 www + verify | Pilot trust-brief, homepage procurement guard, coherence FAIL | `copilot/pilot/`, `verify-no-asf-coherence.sh` |

## PLAN WITH NO ASF iter 12 (036–038)

| next_tasks id | Shipped | Evidence |
|---------------|---------|----------|
| ship-trust-brief-procurement-036 | Trust-brief on procurement | `copilot/procurement/index.html`, `verify-gtm-ops-docs.sh` |
| ship-drift-blueprints-procurement-037 | Drift blueprints index on procurement | `copilot/procurement/index.html` |
| ship-demo-url-verify-038 | demo-url verify guard | `scripts/verify-demo-url.sh`, `plan-with-no-asf-verify.sh` |

## Fourth audit fix (third-audit bundle + iter 12)

| Area | Shipped | Evidence |
|------|---------|----------|
| Third-audit workflow | Canonical SHIP_NOW, registry fence, coherence | `README.md`, `registry.json`, `verify-no-asf-coherence.sh` |
| Iter 12 www + verify | Procurement trust-brief, drift blueprints, demo-url | `copilot/procurement/`, `verify-demo-url.sh` |

## Third audit fix (canonical SHIP_NOW + registry fence)

| Area | Shipped | Evidence |
|------|---------|----------|
| Canonical SHIP_NOW | README + AGENT_READ_LINKS → `os/SHIP_NOW.md` | `README.md`, `docs/SHIP_NOW.md` |
| Registry R-011 fence | `agentic_only` on customer-outreach | `registry.json`, `patch-registry-agentic-only.py` |
| Coherence hardening | SHIP_DONE_MAP + README gate | `scripts/verify-no-asf-coherence.sh` |

## Post-audit fix (workflow + paths + verify hardening)

| Area | Shipped | Evidence |
|------|---------|----------|
| Workflow reconcile | 1000-pack overlay, read-order rules, plan.json ship_rule | `NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md` |
| R-011 GTM_PRIORITY fence | Agentic-only banner + customer-outreach filter | `GTM_PRIORITY_100.md`, `sync-prompt-pack-status.py` |
| SHIP_DONE_MAP 023–035 | Registry propagation for iter 8–11 + audit | `scripts/sync-prompt-pack-status.py` |
| Path canonicalization | `docs/references/` in buyer md + procurement ZIP | `copilot/`, `procurement_pack.py` |
| Coherence hardening | Manifest + OPEN_PRS + path checks | `scripts/verify-no-asf-coherence.sh` |

## Verify command (all future ships)

```bash
./scripts/plan-with-no-asf-verify.sh
```
