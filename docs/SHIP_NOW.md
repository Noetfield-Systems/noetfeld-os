# SHIP NOW — historical ASF direction (superseded)

> **Canonical ship queue:** [os/SHIP_NOW.md](../os/SHIP_NOW.md) — use that file for PLAN WITH NO ASF closeout.
>
> **Post-audit law:** Bounded founder `implement` only (R-007/R-011). Do **not** self-start from `plan.json` or "ship immediately" below.

**Canonical short form:** [os/SHIP_NOW.md](../os/SHIP_NOW.md)

---

## Historical note (pre–2026-06-10)

The sections below are retained for context. Cloud agents follow `os/SHIP_NOW.md`, [GTM_NEXT.md](ops/plans/no-asf/GTM_NEXT.md), and R-011 agentic commercial law.

## Two different things

| What it is | Blocks shipping? |
|------------|------------------|
| **Ingest** — send answer to system (YAML + reports / `noetfield-latest.txt`) | **No** — required reporting **after** you ship |
| **Waiting for the next order** — stop until Prompt OS / M8 / dispatch sends another prompt | **Yes** — ASF said **not** to do this |

**Do not weaken Sina Prompt OS.** **Do not edit Prompt OS code.** Ingest stays **required**.

**Mode:** **DELIVERY** — ship what buyers can buy and pilots can run **this week**.

This repo's law is:

1. [PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md) · [PROJECT_BOUNDARIES_LOCKED.md](../PROJECT_BOUNDARIES_LOCKED.md)
2. [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](./spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md)
3. [WAVE0_SHIP_CHECKLIST.md](./WAVE0_SHIP_CHECKLIST.md) · [GO_LIVE.md](./GO_LIVE.md)

---

## Locked positioning (ship message)

**Noetfield** = AI Governance & Evidence for **Microsoft 365 Copilot adoption**.  
**Buyer line:** *We produce the audit trail your Copilot deployment will be asked for later.*  
**Ship unit:** every paid engagement → ≥1 **Trust Ledger Entry (TLE v1)** or production **RID + audit-export**.

---

## Single command — am I shippable?

```bash
./scripts/plan-with-no-asf-verify.sh
```

Exit **0** = repo ready for merge/deploy; founder still runs production smoke on live host.
