# GTM_NEXT — Tier A queue (post–1000-pack)

When the NF-PLAN registry is fully synced (`1000/1000 done`), pick the next **≤3** agent tasks from here or `os/plan.json` `next_tasks`.

**Authority:** [NOETFIELD_GTM_60_DAY_LOCKED_v1.md](../../../strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md)  
**Verify:** `./scripts/plan-with-no-asf-verify.sh`

## Next GTM Tier A (agent-maintained)

1. **ship-gtm-next-queue-023** · Registry complete → GTM_NEXT queue + QUICK_PICK fallback  
   Outcome: PLAN WITH NO ASF has actionable picks after 1000-pack sync.  
   Verify: `./scripts/verify-quick-pick-fresh.sh`

1. **ship-staging-demo-www-wire-024** · Public demo URL / staging runbook on buyer www  
   Outcome: Founder shares external demo from copilot pilot/demo without ops doc hunt.  
   Evidence: `docs/ops/STAGING_DEMO.md`, `make demo-url`

1. **ship-security-buyer-tle-copy-025** · CISO / security buyer line on trust-ledger www  
   Outcome: Security reviewers get metadata-only + no custody claims on landing page.  
   Evidence: `trust-ledger/index.html`, `docs/diligence/rpaa-positioning-onepager.md`

1. **ship-design-partner-outreach-026** · Founder runs design-partner pipeline with BC AI + debrief  
   Outcome: One named CIO contact + demo URL sent (founder-owned execution).  
   Evidence: `docs/copilot/DESIGN_PARTNER_PIPELINE_v1.md`

1. **ship-procurement-one-pager-wire-027** · Link PROCUREMENT_ONE_PAGER from copilot hub + procurement  
   Outcome: Buyer pack md reachable from www surfaces.  
   Evidence: `docs/copilot/PROCUREMENT_ONE_PAGER.md`

1. **ship-governance-sources-www-028** · Href GOVERNANCE_SOURCES_BOOK from procurement buyer page  
   Outcome: Framework citations clickable for legal/procurement reviewers.

1. **ship-homepage-demo-cta-029** · Homepage secondary CTA to 5-minute demo (not only design partner)  
   Outcome: Category one-liner + demo path for cold traffic.

1. **ship-tunnel-smoke-verify-030** · Optional `make staging-smoke` in GTM verify when NF_STAGING_URL set  
   Outcome: Staging health check before founder shares URL.

## Recently shipped (iter 7–8)

| ID | Shipped |
|----|---------|
| ship-registry-pattern-propagation-020 | QUICK_PICK dedup |
| ship-diligence-procurement-wire-021 | RPAA one-pager www wire |
| ship-design-partner-bc-ai-022 | BC AI pipeline block |
