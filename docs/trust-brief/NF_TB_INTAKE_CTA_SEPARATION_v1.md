# Trust Brief Intake — Separate from Pilot CTA

**Version:** 1.0.0 · **Plan:** pf-0047 · **SKU:** NF-TB  
**Law:** Copilot Governance Pack remains **lead wedge** · Trust Brief is secondary CTA

---

## CTA hierarchy (locked)

| Priority | SKU | CTA label | URL |
|----------|-----|-----------|-----|
| **Primary** | NF-RD | Apply for pilot ($2k–$10k) | `/trust-brief/intake/?interest=pilot&vector=copilot-governance` |
| **Secondary** | NF-TB | Request Trust Brief ($10k) | `/trust-brief/intake/` or `?interest=trust-brief` |
| **Tertiary** | Sandbox | Start sandbox | `/start/` |

**Regression test:** Trust Brief must **not** be sole primary CTA on `/copilot/` or homepage mega-CTA.

---

## Intake form routing

| `interest` param | Vector | SKU routed |
|------------------|--------|------------|
| `pilot` | `copilot-governance` | NF-RD |
| (default / trust-brief) | `trust-brief` | NF-TB |
| `msp` | `msp` | MSP partner |

---

## Surface audit (must pass)

| Page | Primary button | Secondary button |
|------|----------------|------------------|
| `/` homepage | Apply for pilot | Request Trust Brief |
| `/copilot/pilot/` | Apply for pilot | Trust Brief card (after pilot) |
| `/trust-brief/` | Request Trust Brief | Apply for pilot first |
| `/trust-brief/intake/` | Pilot band selector + Trust Brief path | Both visible |

---

## Verify command

```bash
grep -l 'Apply for pilot' trust-brief/index.html copilot/pilot/index.html index.html
grep 'Request Trust Brief' trust-brief/index.html
```

Pilot primary on copilot hubs · Trust Brief primary only on `/trust-brief/` sell page.

---

## Anti-paths

- No SKU creep · three contract SKUs only
- Separate autoresponders: [NF_TB_TO_NF_RD_UPGRADE_AUTORESPONDER_v1.md](./NF_TB_TO_NF_RD_UPGRADE_AUTORESPONDER_v1.md)
