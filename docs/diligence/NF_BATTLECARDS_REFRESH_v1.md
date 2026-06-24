# Battle Cards Refresh — Purview · Credo · Securiti

**Version:** 1.0.0 · **Plan:** pf-0070 · **SKU:** — (platform) · **Phase:** 6  
**Law:** Competitive enablement for procurement — assume Purview deployed, Noetfield = receipt layer

---

## One line

Refresh index for three locked battle cards — wired from `/copilot/procurement/` to `docs/diligence/battlecards/`.

---

## Card index

| Competitor | Card path | Win theme |
|------------|-----------|-----------|
| Microsoft Purview / Copilot Control | [BATTLECARD_VS_PURVIEW_LOCKED_v1.md](./battlecards/BATTLECARD_VS_PURVIEW_LOCKED_v1.md) | Receipt layer — Purview logs ≠ board go/no-go |
| Credo AI | [BATTLECARD_VS_CREDO_LOCKED_v1.md](./battlecards/BATTLECARD_VS_CREDO_LOCKED_v1.md) | Copilot wedge · 90-day pilot vs program RFP |
| Securiti AI | [BATTLECARD_VS_SECURITI_LOCKED_v1.md](./battlecards/BATTLECARD_VS_SECURITI_LOCKED_v1.md) | Estate-wide platform vs Copilot evaluate spine |

**Master index:** [COMPETITIVE_LANDSCAPE_LOCKED_v1.md](./COMPETITIVE_LANDSCAPE_LOCKED_v1.md)

---

## Public www wire

| Surface | Links |
|---------|-------|
| `/copilot/procurement/` | Battle cards section → three card paths above |
| `/copilot/governance-audit-trail/` | SEO audit-trail narrative |
| `/trust/` | Honest cert posture |

---

## Refresh checklist (2026-06)

- [x] Purview Copilot Control System positioning — assume deployed
- [x] Credo enterprise AI GRC — parallel program scope
- [x] Securiti data+AI security — estate-wide vs Copilot wedge
- [x] Procurement FAQ cross-link [PROCUREMENT_COMPETITIVE_FAQ_v1.md](../copilot/PROCUREMENT_COMPETITIVE_FAQ_v1.md)

---

## Not in scope

- Naming competitors on homepage hero
- Disparaging Microsoft — Purview is Phase 1 assume-deployed
- TrustField regulatory cards in Copilot procurement pack

---

## Verify

```bash
test -f docs/diligence/battlecards/BATTLECARD_VS_PURVIEW_LOCKED_v1.md
grep -q 'BATTLECARD_VS_PURVIEW' copilot/procurement/index.html
grep -q 'BATTLECARD_VS_CREDO' copilot/procurement/index.html
grep -q 'BATTLECARD_VS_SECURITI' copilot/procurement/index.html
```
