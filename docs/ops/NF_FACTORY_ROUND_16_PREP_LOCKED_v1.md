# NF Factory Round 16 — Prep LOCKED v1

**Version:** 1.0.0 · **Status:** LOCKED · **Saved:** 2026-06-19  
**Plane:** Noetfield `noetfield_cloud` + portfolio library  
**SourceA:** read-only motor — **never edit** `~/Desktop/SourceA/` from this repo

---

## Disk truth (machine — Phase 16 scope)

| Surface | Value | Verify |
|---------|-------|--------|
| Portfolio 300 | **260/300 done · 40 backlog** | `validate-portfolio-300.py` PASS · Phase 16 **30/30** |
| TrustField lane | **50/50 done** | `--brand trustfield` → no backlog |
| Cross-portfolio XF-P2 | **10/10** target | `verify-xf-p2-wave.sh` PASS |
| Canada RWA CA-P2 | **10/10** target | `verify-ca-p2-wave.sh` PASS |
| Platform PL-P1 | **10/10** target | `verify-pl-p1-wave.sh` PASS |
| Anti-staleness MAX | shipped 2026-06-19 | `make verify-nf-anti-staleness-max` |
| Factory spine | `make nf-prove-factory-spine` **15/15 PASS** | |
| **operations@ inbox** | **ACTIVE** (Google Workspace) | direct email works |
| **Resend form send** | **DEFERRED post-factory** | not P0 — factory first |

**Product queue head:** Phase 17 prep (OPS-P1 + remaining XF/CA/PL) — see [GTM_NEXT.md](../plans/no-asf/GTM_NEXT.md)  
**Phase 16 LOCK:** `~/Desktop/1 PAGER/PORTFOLIO_300_PHASE16_10_STEP_LOCKED_v1.md`

---

## Round 16 wave order

| Priority | Wave | Plans | Status |
|----------|------|-------|--------|
| 1 | **XF-P2** | pf-0011–pf-0020 | **done** |
| 2 | **CA-P2** | pf-0246–pf-0255 | **done** |
| 3 | **PL-P1** | pf-0266–pf-0275 | **done** |

---

## Next factory round (Phase 17 prep)

| Priority | Wave | Plans | Brand |
|----------|------|-------|-------|
| 1 | **XF-P2b** | pf-0021–pf-0025 | cross-portfolio |
| 2 | **CA-P2b** | pf-0256–pf-0265 | canada-rwa |
| 3 | **OPS-P1** | pf-0291–pf-0300 | ops |
| 4 | **PL-P2** | pf-0276–pf-0290 | platform |

---

## Mandatory gates (every www / factory session)

```bash
make nf-onboard
make verify-nf-anti-staleness-max
make nf-prove-factory-spine
make nf-ui-checklist
```

**UI law:** [NF_UI_BUILD_CHECKLIST_LOCKED_v1.md](../../www/NF_UI_BUILD_CHECKLIST_LOCKED_v1.md) · [NF_WWW_LANGUAGE_LAYERS_LOCKED_v1.md](../../www/NF_WWW_LANGUAGE_LAYERS_LOCKED_v1.md)

---

## Verify Phase 16 closeout

```bash
bash ~/Desktop/1\ PAGER/portfolio-300-locked/scripts/verify-portfolio-300-phase16.sh
make verify-nf-anti-staleness-max
make nf-ui-checklist
make verify-nf-gaos-w3
```
