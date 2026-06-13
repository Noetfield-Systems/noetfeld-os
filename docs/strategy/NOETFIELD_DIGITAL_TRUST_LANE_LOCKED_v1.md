# Noetfield Digital Trust Lane (LOCKED v1)

| Field | Value |
|-------|--------|
| **Doc id** | `noetfield-digital-trust-lane-v1` |
| **Locked** | 2026-06-02 |
| **Authority** | Subordinate to [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](./NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md) · [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md) |
| **Not for** | Vendor comparison pages, “vs” teardowns, or third-party positioning docs on public www |

---

## 0. Operating principle (GTM)

**Learn · Add · Implement · Earn** — study tier-1 conversion patterns (Sumsub trial OS, Stripe proof-in-hero, ShareID assurance ladder), ship them on Noetfield www and product, drive revenue through Copilot Governance Pack intake.

- **Learn** — reference design goals in [DESIGN_REFERENCE_GOALS_LOCKED_v1.md](../DESIGN_REFERENCE_GOALS_LOCKED_v1.md)
- **Add** — receipt-first proof, milestone pricing, pilot apply form, assurance levels, revenue path strip
- **Implement** — `scripts/rebuild-www-v6.py` + verify + deploy
- **Earn** — W3 signal: deposit ≥ CAD 2K or signed LOI · board PDF in governance meeting

Never publish vendor comparison tables or “vs {name}” copy on public www.

---

## 1. Lane definition

Noetfield occupies **regulated digital trust for Microsoft 365 Copilot rollout decisions**:

| Layer | What Noetfield receipts | Buyer | Trust mechanism |
|-------|-------------------------|-------|-----------------|
| **Noetfield wedge** | Copilot go/no-go evidence before production scope | CISO, GRC, procurement, board | Signed TLE + board PDF + procurement ZIP · metadata-only M365 |

**Whitespace:** Board-defensible Copilot governance artifacts in the Microsoft stack — evaluate → signed receipt → export for audit.

**We do not sell:** Identity verification at onboarding · generic LLM proxy logging · payment custody · MSB execution.

---

## 2. North star (public — homepage + `/copilot/pilot/`)

> For regulated EU and US institutions rolling out Microsoft 365 Copilot: Noetfield produces board-grade, tamper-evident go/no-go receipts — signed Trust Ledger Entries, confidence scores, and procurement exports — before production scope opens.

**Commercial entry:** Copilot Governance Pack · $2k–10k · 90 days · success signal = **board PDF in a real governance meeting**.

**Land SKU (not lead):** Trust Brief $10k · 6 weeks · diagnostic before scale.

**Self-serve (access, not contract):** Free sandbox · 14-day · 50 evaluates · `/start/`.

---

## 3. Regulated buyer map (EU + US)

| Trigger | Region / sector | Buyer need | Noetfield deliverable |
|---------|-----------------|--------------|------------------------|
| EU AI Act Art. 12 (Aug 2026 orientation) | EU | Automatic tamper-evident decision records | TLE + fail-closed export |
| DORA / NIS2 | EU financial | Incident evidence · audit trails | Board PDF + procurement ZIP |
| NIST AI RMF / ISO 42001 | US | Govern · manage · evidence | Framework orientation in exports |
| FFIEC / OSFI / GC ADM | US/CA public & bank | Board oversight · metadata-only | Federal + bank-pilot lanes |
| Copilot enterprise rollout | Both | Signed go/no-go before production | Copilot Governance Pack |

**ICP:** Regulated mid-market and enterprise — bank, insurer, law/accounting, health, GC/agency Copilot pilots, MSP-served tenants.

---

## 4. Commercial funnel architecture

```text
Regulated buyer
  → /copilot/pilot/ (Copilot Governance Pack $2k–10k)
  → 5-min demo OR free sandbox
  → Pilot intake / SOW (interest=pilot)
  → 90d: TLE + board PDF + procurement ZIP
  → Reference → Trust Brief $10k OR expand seats / export cadence
```

**Homepage hierarchy (locked):**

1. Headline — audit trail your Copilot deployment will be asked for later  
2. Sub — EU + US regulated institutions · M365 Copilot · board-grade exports  
3. Primary CTA — Apply for pilot ($2k–10k)  
4. Secondary — 5-minute demo · Start sandbox  
5. Tertiary — Trust Brief ($10k) · diagnostic before scale  

---

## 5. Honest moat (diligence — claim / evidence / do not claim)

| Claim | Evidence | Status |
|-------|----------|--------|
| Signed go/no-go receipt per Copilot decision | TLE v1 + evaluate API | Available |
| Board + procurement exports | Board PDF · procurement ZIP | Available |
| M365-native evidence index | Purview · Entra · audit metadata | Available |
| Fail-closed export integrity | `/trust-ledger/verify/` | Available |
| Fixed-fee institutional pilot | Copilot Governance Pack $2k–10k | Available |
| Ed25519 / Merkle transparency log | Verify page orientation | Planned |

**Do not claim:** ISO/SOC/eIDAS certification · identity/KYC · Article 12 compliance certifier · platform ARR · logo wall.

---

## 6. Agentic positioning (lane-native)

Noetfield governs **policy-bound Copilot workflows** — agents execute investigate → triage → draft TLE → act on low-risk paths. Not a generic chatbot catalog.

Three verbs: **Evaluate · Record · Export**

---

## 7. Public www implementation

| Block | Route | Rebuild helper |
|-------|-------|----------------|
| Digital trust lane | `/` | `digital_trust_lane_block()` |
| Regulated buyer map | `/` · `/copilot/pilot/` | `regulated_buyer_triggers_block()` |
| Governance gaps | `/` | `copilot_governance_gaps_section()` |
| Delivery outcomes | `/` · `/pricing/` | `buyer_delivery_outcomes_table()` |
| Honest moat | `/` · `/copilot/pilot/` | `honest_moat_grid()` |
| Assurance levels | `/` · `/copilot/pilot/` | `assurance_levels_block()` |

**Verify:** No vendor comparison tables on public www · `./scripts/verify-static-www.sh`

---

## 8. Related locks

- [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](./NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md)
- [NOETFIELD_GTM_60_DAY_LOCKED_v1.md](./NOETFIELD_GTM_60_DAY_LOCKED_v1.md)
- [docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md](../copilot/DESIGN_PARTNER_SOW_OUTLINE.md) — pilot deliverables + success signals
- [docs/GTM_COPYBOOK.md](../GTM_COPYBOOK.md)
