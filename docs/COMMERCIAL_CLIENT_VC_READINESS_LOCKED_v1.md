# Client & VC Readiness Checklist (LOCKED v1)

| Field | Value |
|-------|--------|
| **Audience** | Founders, design partners, investors, procurement |
| **Authority** | [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](./strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md) · [OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md) |
| **UI program** | [WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md](./WWW_V13_INSTITUTIONAL_100_PLAN_LOCKED_v1.md) |
| **Founder roadmap** | `ops/private/MARKET_SUCCESS_1000_ROADMAP_LOCKED_v3.md` (never public — vendor names OK internal only) |

---

## What we sell (three contracts only)

| SKU | Price | Buyer outcome |
|-----|-------|---------------|
| **Trust Brief** | $10,000 · 6 weeks | Governance diagnostic + board-ready summary |
| **Copilot Governance Pack** | $2k–10k design partner | TLE v1 + board PDF + procurement ZIP |
| **Bank Pilot** | Custom | Shadow read-only simulation |

**Sub-pages (not SKUs):** `/copilot/sme/`, `/ai-automation/` — orientation under Copilot Pack.

**Primary CTA:** [Request Governance Brief](https://www.noetfield.com/trust-brief/intake/) · `operations@noetfield.com` · footer **RID**

**W3 proof bar:** Board PDF used in governance meeting **or** deposit ≥ CAD 2K / signed LOI.

---

## What investors should see (honest)

- Product demoable in **≤5 minutes** (`/copilot/demo/`)
- **No** fake ARR, logo walls, or analyst stat drops
- **No** SOC2/ISO claims unless independently true
- Category zones without vendor names (`/investors/`)
- Capital use: **first contracted design partner** + referenceable board PDF

---

## What procurement should see (self-serve)

| Asset | URL |
|-------|-----|
| Trust center | `/trust/` |
| Procurement pack | `/copilot/procurement/` |
| TLE samples | `/trust-ledger/sample-report/` |
| Verify walkthrough | `/trust-ledger/verify/` |
| Status | `/status/` |

Metadata-only M365 · fail-closed export · no custody.

---

## Verify before external share

```bash
make verify-www          # static HTML + regen
make verify-no-vendor-names
make verify-gtm          # full stack + e2e (requires make dev-local)
```

---

## Forbidden on public surfaces

Vendor names · comparison pages · fourth SKU · Trust Ledger SaaS checkout · MSB/payment lead on Noetfield www
