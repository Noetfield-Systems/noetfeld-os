# WWW v16 — Self-serve packaging & agentic GTM (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED — supersedes v15-only narrative for commercial packaging |
| **Shipped** | 2026-06-13 |
| **Generator** | `scripts/rebuild-www-v6.py` · `WWW_VER=16` |
| **Benchmark** | Sumsub-style: async demo · published tiers · sandbox + production · agentic workflows |
| **Authority** | Subordinate to [OFFERINGS_LOCKED.md](../OFFERINGS_LOCKED.md) · [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](./strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md) |

---

## 1. North star (packaging funnel)

```text
Sign up (free) → Sandbox evaluate → TLE sample export → Design partner apply → Trust Brief / SOW
                     ↑ no sales call              ↑ named program              ↑ 3 contract SKUs
```

**W3 conversion signals (priority order):**

| Signal | Proof | Owner |
|--------|-------|-------|
| **S0 Sandbox start** | `/start/` form → console with tenant + evaluate | Product / NF-CLOUD |
| **S1 Async demo complete** | Evaluate → RID → confidence on result page | Product |
| **S2 Export artifact** | TLE YAML / orientation PDF / ZIP path touched | Product |
| **S3 Design partner apply** | `/copilot/pilot/` intake or deposit ≥ CAD 2K | Agentic + founder |
| **S4 Board PDF in meeting** | Referenceable org uses board pack | Agentic + delivery |

---

## 2. Access paths vs contract SKUs (do not conflate)

| Layer | Name | Price | Route | Contract? |
|-------|------|-------|-------|-------------|
| **Access** | Developer sandbox | $0 | `/start/` | No — product access tier |
| **Program** | Design partner (Copilot Pack) | $2k–10k · 90d | `/copilot/pilot/` | Yes — SKU #2 |
| **SKU** | Trust Brief | $10k · 6w | `/trust-brief/` | Yes — SKU #1 |
| **SKU** | Bank Pilot | Custom | `/bank-pilot/` | Yes — SKU #3 |

**Forbidden:** Fourth retail product card in `nf-offer-card` grid on homepage §06. Free tier uses `nf-pack-card` on `/start/` and `/pricing/` only.

---

## 3. Sandbox specification (Sumsub parity)

| Field | Value |
|-------|--------|
| Trial length | **14 days** |
| Evaluate limit | **50 calls** |
| M365 | **Mock OAuth only** — no production mailbox custody |
| Mode | **sandbox** (localStorage session via `noetfield-sandbox.js`) |
| Upgrade | Design partner program → **production** keys per SOW |

**Self-serve flow:**

1. Work email on `/start/`
2. Redirect → `/cognitive-dashboard/?sandbox=1&tenant=sandbox-…`
3. Evaluate → audit log → workspace TLE draft
4. CTA → `/pricing/` or `/copilot/pilot/`

---

## 4. Published tiers (`/pricing/`)

- Environment table: **Sandbox vs Production**
- Four-path grid: Developer access · Design partner · Trust Brief · Bank Pilot
- Honest line: sandbox is not a fourth contract SKU

**Nav:** Header **Start free · Demo · Pricing** · Footer **Get started** column.

---

## 5. Agentic autonomous (public language)

Not “AI assist” — **governance agents execute bounded workflows:**

| Step | Agent action | Human gate |
|------|--------------|------------|
| Investigate | Pull M365 metadata gaps (Purview · Entra · audit) | — |
| Triage | Confidence + policy → allow / review / deny | Review on high-risk |
| Draft TLE | Prepare YAML + approval chain + evidence index | Named approvers sign |
| Act low-risk | Auto-record sandbox allows per policy | Production requires partner keys |

**Do not claim:** autonomous SAR filing, payment execution, or unsupervised production Copilot rollout.

---

## 6. UI / E2E surfaces (shipped)

| URL | Role |
|-----|------|
| `/` | Self-serve rail · packaging §07 · agentic block |
| `/start/` | Signup form + async demo steps |
| `/pricing/` | Tier table + pack grid |
| `/docs/api/` | Sandbox-first CTA |
| `/console/` | Start sandbox primary |
| Product console | Sandbox banner · Start free in Shell |

**Verify:** `make verify-ui-e2e` · `make verify-static-www` (v16 needles)

---

## 7. CSS / assets

| File | Role |
|------|------|
| `assets/noetfield-v16-packaging.css` | Pack grid · sandbox form · agentic strip · mode toggle |
| `assets/noetfield-sandbox.js` | Session create · redirect |
| `assets/noetfield-www.css` | Imports v14 + v15 + v16 |

---

## 8. Agent execution checklist (NF-CLOUD)

When touching packaging:

- [ ] Three `nf-offer-card` SKUs unchanged on homepage §06
- [ ] Free tier only on `/start/` + `/pricing/` as `nf-pack-card`
- [ ] `verify-static-www` comparison-framing guard passes
- [ ] E2E needles for sandbox · pricing · agentic updated in same PR
- [ ] [COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md](./ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md) routing respected

---

## 9. Supersedes

- v15-only homepage IA (procurement-first hero CTAs) → **sandbox-first hero** with design partner retained
- “Pilot access keys only via intake” on API docs → **sandbox + production** dual mode

**Related:** [DESIGN_REFERENCE_GOALS_LOCKED_v1.md](./DESIGN_REFERENCE_GOALS_LOCKED_v1.md) R21–R25 · [GTM_COPYBOOK.md](./GTM_COPYBOOK.md) v16 spine
