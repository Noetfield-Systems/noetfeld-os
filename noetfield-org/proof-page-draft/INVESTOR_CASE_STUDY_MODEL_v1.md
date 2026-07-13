# INVESTOR CASE STUDY MODEL v1 (LOCKED)

**Status:** LOCKED FOR CONTENT  
**Canonical path:** `noetfeld-OS/noetfield-org/proof-page-draft/INVESTOR_CASE_STUDY_MODEL_v1.md`  
**Lock receipt:** `../NOETFIELD_STRATEGY_LOCK_RECEIPT_v1.json`  
**Purpose:** Define how Noetfield uses itself and its products as live diligence case studies.

---

## Core thesis (locked)

Noetfield publishes **honest, evidence-linked case studies** on itself and its products. Investors experience the **Investor Workflow** on real material. They see gaps, timeline, roadmap, and attachments — not a pitch deck. Two outcomes emerge naturally:

1. **Product proof** — "This diagnosis system works for my deal flow."
2. **Soft fundraise** — "I can evaluate this company properly through evidence."

---

## Investor journey (locked)

```
LinkedIn / referral
    → /proof or /proof/noetfield
    → Case Study #1 (Noetfield Systems Inc.)
    → Claims · Evidence · Diagnosis · Timeline · Roadmap · Capital unlocks
    → Optional: fetch noetfield.json
    → Primary CTA: Run audit on your company/deal
    → Tertiary: /investors evaluation path
```

---

## Case study profile schema (locked)

Every entity uses identical structure:

| Section | Content |
|---------|---------|
| **Identity** | Legal/trade name, role, commercial field |
| **Story** | 2–3 sentences: why exists, current stage |
| **Claims** | Numbered public statements |
| **Evidence** | PUBLIC_URL or PUBLIC_STATEMENT only |
| **Diagnosis** | Status per claim + gaps |
| **Timeline** | Dated progress log |
| **Roadmap** | Milestones + receipt targets |
| **Capital unlock** | Optional; subtle; receipt-linked |
| **JSON** | `noetfield_public_evidence_bundle_v1` |

---

## Status vocabulary (locked)

```
PROVEN | PARTIALLY PROVEN | CLAIMED — NOT VERIFIED | MISSING | STALE | BLOCKED | CONTRADICTED
```

---

## Evidence tiers (locked)

| Tier | Use in public JSON |
|------|-------------------|
| PUBLIC_URL | Required for PROVEN or PARTIALLY PROVEN with external verification |
| PUBLIC_STATEMENT | Allowed; must be labeled |
| INTERNAL_COMMISSIONING | Never in public bundle |

---

## Entity rollout (locked)

| # | Entity | Route | Version |
|---|--------|-------|---------|
| 1 | Noetfield Systems Inc. | `/proof/noetfield` | v0.1 — **EXECUTION_READY; agent deploy** |
| 2 | SourceA | `/proof/sourcea` | v0.2 |
| 3 | SourceB | `/proof/sourceb` | v0.3 |
| 4 | Noetfield Motor / OS | `/proof/motor` | v0.4 |
| 5 | TrustField | `/proof/trustfield` | v0.5 — legal separation only |

---

## CTA hierarchy (locked)

1. **Primary:** Run an evidence audit on your company/deal (Field 3)
2. **Secondary:** Explore case studies (`/proof`)
3. **Tertiary:** Company evaluation (`/investors`) — assembled, not pitch

---

## What this is NOT

- Not a fundraising landing page
- Not a pitch deck replacement with nicer fonts
- Not raw NOOS receipt export
- Not portfolio claim for TrustField
- Not public "protocol" or "holding company" marketing

---

## Verdict

**LOCKED.** Case Study #1 content ready (`noetfield.json` + `noetfield.html.md`). Agent deploys via `PUBLISH_PLAN.md` when checklist green.
