# Strategic lock

**Status:** Binding for product, engineering, public copy, and partner materials.  
**Supremacy:** GCIP v4 (L0) on conflict with any other document.

---

## System boundaries

1. **No payments or custody logic** exists in the Noetfield product surface or runtime positioning.
2. The system is a **strictly pre-execution governance layer** — policy and audit before external execution.
3. **Noetfield never executes financial value movement** — no initiation, authorization, routing, or settlement of funds.
4. The platform **only produces** decisions (allow / reject / review), audits, and compliance traces.

---

## Product surface lock

| Surface | Role |
|---------|------|
| **Institutional site** (`noetfield.com`) | Sales narrative · three offerings · governance brief CTA |
| **Governance Simulation** (`/console` on platform host) | Contract demo — submit intent · view decision · audit trail |
| **Golden Edge runtime** | Source of truth for evaluation and immutable ledger (not marketed as architecture on public pages) |

---

## Narrative lock

- **One product line:** Governance Execution & AI Policy Enforcement Infrastructure  
- **One sentence:** See [PRODUCT_TRUTH.md](PRODUCT_TRUTH.md)  
- **Three offerings only:** See [OFFERINGS_LOCKED.md](OFFERINGS_LOCKED.md)  

---

## Brand palettes

| Mode | Use |
|------|-----|
| **Digital shell** | Gold + dark (`noetfield-shell.css`) — public site, simulation UI |
| **Institutional print** | White / navy / charcoal (`noetfield-print.css`) — Trust Brief PDFs, board packs, audit exports |

---

## Verification

```bash
python3 scripts/audit_final_system_lock.py
pytest tests/unit/test_public_gtm_alignment.py -q
```

Report: [docs/PRODUCTION_READINESS_REPORT.md](docs/PRODUCTION_READINESS_REPORT.md)
