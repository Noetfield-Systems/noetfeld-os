# SHIP NOW — Noetfield primary direction (ASF)

**Authority:** ASF — Prompt OS does **not** block product progress.  
**Mode:** **DELIVERY** — ship what buyers can buy and pilots can run **this week**.

Prompt OS / MonoRepo `os/plan.json` on Desktop is **optional telemetry**. This repo’s law is:

1. [PRODUCT_TRUTH.md](../PRODUCT_TRUTH.md) · [PROJECT_BOUNDARIES_LOCKED.md](../PROJECT_BOUNDARIES_LOCKED.md)
2. [TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md](./spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md)
3. [WAVE0_SHIP_CHECKLIST.md](./WAVE0_SHIP_CHECKLIST.md) · [GO_LIVE.md](./GO_LIVE.md)

---

## Locked positioning (ship message)

**Noetfield** = AI Governance & Evidence for **Microsoft 365 Copilot adoption**.  
**Buyer line:** *We produce the audit trail your Copilot deployment will be asked for later.*  
**Ship unit:** every paid engagement → ≥1 **Trust Ledger Entry (TLE v1)** or production **RID + audit-export**.

---

## P0 — ship this week (engineering + GTM)

| # | Deliverable | Owner | Verify |
|---|-------------|-------|--------|
| P0.1 | Production DNS/TLS + platform smoke | Founder | `PLATFORM_HEALTH_BASE=... ./scripts/deploy_platform_smoke.sh` exit 0 |
| P0.2 | Homepage + `/trust-ledger/` Copilot headline aligned | Engineering | Pages live; copy matches blueprint |
| P0.3 | Publish TLE v1 examples (YAML) + sample PDF path | Engineering | `docs/spec/examples/tle-v1-*.yaml` linked from trust-ledger |
| P0.4 | Evidence Intake Contract v1 (procurement) | Product | `docs/diligence/EVIDENCE_INTAKE_CONTRACT_v1.md` |
| P0.5 | Local dev one-liner for demos | Engineering | `make dev-local` + `make verify-local-dev` |
| P0.6 | Merge bank-grade branch → `main` | Engineering | PR #15 green |
| P0.7 | One Shadow Week RID in production | Founder | [SHADOW_WEEK_DEMO.md](./SHADOW_WEEK_DEMO.md) |

---

## P1 — weeks 3–6 (product layer)

Trust Ledger Core DB · Evidence Index · M365 metadata connectors · Workspace UI v0 · TLE Generator + Confidence Score.

See [spec/SPRINT_BACKLOG_WEEKS_0-8.md](./spec/SPRINT_BACKLOG_WEEKS_0-8.md).

---

## What we do NOT wait for

- Prompt OS ingest YAML / `reported_at` on every reply
- External MonoRepo file sync before shipping www + platform
- Full TLE product code before Wave 0 revenue (sell Trust Brief + Bank Pilot + Copilot pack **now**)

---

## Single command — am I shippable?

```bash
make ship-verify
```

Exit **0** = repo ready for merge/deploy; founder still runs production smoke on live host.
