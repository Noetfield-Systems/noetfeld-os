---
service_id: acg-v1
service_name: Agentic Cost Governance
doc_id: acg-integration-checklist-v1
created: "2026-07-05"
author: "[NF-LOCAL-REPO-AGENT]"
---

# Service Integration Checklist — Agentic Cost Governance (ACG-v1)

**Status:** DRAFT (integration not yet started)

**Purpose:** Gate for publication. All items must be VERIFIED before service goes live.

---

## Phase 1: Repo & Code Integration ✓ BLOCKED_BY_RECONCILE

- [ ] **Repo reconciliation:** Noetfield main synced with origin/main
  - Blocker: Currently 5 commits ahead; awaiting Vercel verification and NOOS clear before push
  - Timeline: After NOOS coordination signal

- [ ] **Service page component:** `apps/web/app/services-draft-acg.tsx`
  - Status: ✅ DRAFTED (file exists, not yet live)
  - Verification: Component has draft warning banner; no live routes wired

- [ ] **Service documentation:** `docs/services/agentic-cost-governance-draft-v1.md`
  - Status: ✅ DRAFTED (file exists)
  - Verification: LOCKED as draft; non-claims verified

- [ ] **Service specification JSON:** `docs/services/service-draft-specification-acg-v1.json`
  - Status: ✅ DRAFTED (file exists)
  - Verification: Machine-readable spec with dependency tracking

- [ ] **No live routing wired:**
  - Verification: Service component NOT imported in layout.tsx or page.tsx
  - Verification: No /services/agentic-cost-governance route in next.config or vercel.json

---

## Phase 2: Noetfield Reconciliation Dependent ✅ IN_PROGRESS

- [ ] **Repo reconciliation complete:**
  - Current status: 5 commits ahead of origin/main (reconciliation + receipts)
  - Blocker: Must complete merge and NOOS signal before touching live routes
  - Timeline: After NOOS coordination receives lane receipt

- [ ] **Vercel live deployment verified:**
  - Blocker: Cannot confirm live deployment state from config alone
  - Action required: Check Vercel console (active deployment, DNS, health)
  - Timeline: Before any messaging/www updates

- [ ] **NOOS receives lane receipt:**
  - Lane status: acg-v1 DRAFT
  - Payload: Service draft positioned, governance-only, awaiting reconciliation clear
  - Timeline: After repo reconciliation and Vercel verification

- [ ] **NOOS coordination signal received:**
  - Blocker: Must receive "clear" signal from NOOS before publication
  - Timeline: After NOOS processes lane update

---

## Phase 3: Governance & Alignment Verification ✅ COMPLETE

### SG (Sina Governance) Alignment

- [x] **No payment custody claims**
  - Verified: Service brief states governance-only, no payment authority
  - Verified: Non-claims section explicitly lists "Not a payment custody service"

- [x] **No PSP/MSB (Payment Service Provider / Money Services Business) claims**
  - Verified: Service brief excludes PSP/MSB claims
  - Verified: Non-claims section explicitly states "Not a PSP or MSB"

- [x] **No banking authority claims**
  - Verified: Service is cost tracking + policy layer only
  - Verified: No settlement, transfer, or financial institution role claimed

- [x] **Governance-only scope maintained**
  - Verified: Service described as "governance + audit + policy layer"
  - Verified: Customer systems enforce policies; Noetfield provides intelligence

- [x] **TrustField/VIRLUX boundary respected**
  - Verified: Service does not mention or depend on TrustField/VIRLUX code
  - Verified: No cross-repo contamination

- [x] **Project boundaries respected**
  - Verified: SERVICE IN NOETFIELD REPO ONLY (no TrustField, VIRLUX, SourceA edits)
  - Verified: No payment rails, no MSB positioning, no execution authority claims

### Non-Claims Verification

- [x] "Not a payment custody or banking service" — explicit in brief
- [x] "Not a PSP or Money Services Business (MSB)" — explicit in brief
- [x] "Not a full agentic platform" — explicitly governance + audit only
- [x] "Not a deployment platform" — explicitly recommends, customer deploys
- [x] "Not financial advisory" — operational cost control only
- [x] "Not replacement for CFO/Finance" — works alongside
- [x] "Not substitute for budget authority" — companies set budgets; Noetfield enforces

---

## Phase 4: Buyer-Audience Team Review ⏸️ PENDING

- [ ] **Messaging review:** Buyer-facing positioning
  - Artifact: Commercial one-liner + pain points
  - Action required: Buyer-audience team reviews messaging
  - Approval required: ✅ YES (must pass `verify-www-buyer-audience.sh` gate)

- [ ] **Copy audit:** No vendor names, no competitor tables, no jargon bleed
  - Verification: Scan service brief and page component for forbidden patterns
  - Forbidden: Vendor names (except Microsoft when factual), competitor comparisons
  - Safe: "GitHub, Copilot, Cursor, Claude, OpenAI" (factual integrations, not competitors)

- [ ] **Tone verification:** Enterprise-appropriate, not overselling
  - Verification: No "scarcity invites," no "join us" funnel language
  - Safe: Clear problem statement + capability description

---

## Phase 5: Founder/Stakeholder Review ⏸️ PENDING

- [ ] **Service positioning approved**
  - Artifact: Commercial one-liner, buyer pain, value promise
  - Action required: Founder reviews and approves

- [ ] **Buyer value clear and defensible**
  - Artifact: Before/after table + deliverables
  - Verification: No overclaiming; realistic timelines for modules

- [ ] **Non-claims understood and approved**
  - Artifact: Non-claims section (explicit governance-only positioning)
  - Verification: Founder confirms compliance with SG boundaries

- [ ] **Revenue model clarity**
  - TBD: Pricing, packaging, engagement model (not in this draft, to be determined)
  - Note: Service draft is positioning only; commercial terms TBD

---

## Phase 6: Buyer-Audience Verification Gate ✅ GATE AVAILABLE

**Gate:** `verify-www-buyer-audience.sh` (Noetfield mandate)

- [ ] **Must pass buyer-audience verification:**
  - Command: `bash scripts/verify-www-buyer-audience.sh`
  - Scope: Service page component, messaging, claims validation
  - Blocker: Service cannot go live without passing this gate
  - Timeline: Run before pushing to remote

---

## Phase 7: Live Route Integration ⏸️ BLOCKED

- [ ] **Add service page to layout/routing:**
  - File: `apps/web/app/layout.tsx` (add service link to nav)
  - File: `next.config.ts` (add /services route if needed)
  - Blocker: ONLY after NOOS coordination clear + buyer-audience pass

- [ ] **Update homepage service listing:**
  - File: `apps/web/app/page.tsx`
  - Add: Link/card for Agentic Cost Governance service
  - Blocker: ONLY after NOOS coordination clear + buyer-audience pass

- [ ] **Add service to sitemap/robots:**
  - File: Verify service URL in sitemap generation
  - File: Ensure /services/agentic-cost-governance indexed correctly
  - Blocker: ONLY after NOOS coordination clear + buyer-audience pass

---

## Phase 8: Deployment & Messaging Coordination ⏸️ BLOCKED

- [ ] **No deploy until reconciliation + verification complete:**
  - Blocker: Noetfield repo 5 commits ahead; awaiting NOOS signal
  - Blocker: Vercel live state unverified
  - Blocker: Email defer ON (cannot send messaging until after factory signal)

- [ ] **No messaging until NOOS coordination clear:**
  - Blocker: Service draft, not published
  - Blocker: Email defer ON; awaiting LIFT signal
  - Timeline: After NOOS processes lane update and signals clear

- [ ] **No push to remote until Vercel verified:**
  - Blocker: Currently 5 commits ahead; awaiting Vercel console check
  - Timeline: After Vercel production state confirmed

---

## Approval Sign-Off Checklist

Required approvals before publication:

| Approval | Status | Notes |
|----------|--------|-------|
| SG Alignment (governance-only, non-claims) | ✅ VERIFIED | Service remains pre-execution governance layer |
| Founder/Stakeholder Review | ⏸️ PENDING | Must approve positioning, value, non-claims |
| Buyer-Audience Team Review | ⏸️ PENDING | Must approve messaging, tone, compliance |
| Noetfield Repo Reconciliation | ✅ IN_PROGRESS | 5 commits ready; awaiting NOOS clear before push |
| Vercel Live Verification | ⏸️ PENDING | Console check required (cannot verify from config) |
| NOOS Coordination Clear | ⏸️ PENDING | Signal required before service publication |
| Buyer-Audience Verification Gate | ⏸️ PENDING | Must run `verify-www-buyer-audience.sh` before deploy |

---

## Timeline & Critical Path

**Week 1 (Current):**
- ✅ Service draft complete (brief, page, specs)
- ✅ SG alignment verified
- ⏸️ Await Noetfield repo reconciliation complete
- ⏸️ Await NOOS coordination clear

**Week 2 (After Reconcile Clear):**
- ⏸️ Founder/stakeholder review
- ⏸️ Buyer-audience team review
- ⏸️ Run buyer-audience verification gate
- ⏸️ Vercel live deployment verification

**Week 3 (After Approvals):**
- ⏸️ Wire live routes
- ⏸️ Add to homepage/navigation
- ⏸️ Prepare messaging coordination
- ⏸️ Deploy to production (only after NOOS clear + Vercel verified)

---

## Blockers & Dependencies Summary

🚨 **BLOCKING ISSUES (must resolve before publication):**

1. **Noetfield repo reconciliation:** Currently 5 commits ahead; awaiting NOOS signal to push
2. **Vercel live verification:** Console check required before any deploy
3. **NOOS coordination clear:** Must receive "safe" signal before service goes public
4. **Founder approval:** Must approve positioning, value, non-claims
5. **Buyer-audience approval:** Must pass messaging review + verification gate
6. **Email defer OFF:** Currently ON; must await factory signal before messaging update

✅ **CLEARED ITEMS:**

- SG alignment verified (governance-only, no payment/PSP/banking claims)
- Service draft complete (brief, page, specs all prepared)
- Non-claims verified (explicit about what service is NOT)
- Project boundaries respected (Noetfield repo only, no cross-repo contamination)

---

## Next Action (Owner: [NF-LOCAL-REPO-AGENT])

1. ✅ Service draft prepared and committed to repo
2. ⏸️ Awaiting Noetfield repo reconciliation to complete (currently in progress)
3. ⏸️ Awaiting Vercel live deployment verification
4. ⏸️ Awaiting NOOS coordination clear signal
5. ⏸️ Founder to review and approve service positioning
6. ⏸️ Buyer-audience team to review and approve messaging
7. ⏸️ Run buyer-audience verification gate before any deploy

**Do NOT publish until:**
- All blockers above are resolved
- All approvals obtained
- Reconciliation complete + Vercel verified + NOOS clear

---

**Status:** DRAFT  
**Last Updated:** 2026-07-05  
**Next Review:** After Noetfield reconciliation complete
