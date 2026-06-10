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

## Verify command (all future ships)

```bash
./scripts/plan-with-no-asf-verify.sh
```
