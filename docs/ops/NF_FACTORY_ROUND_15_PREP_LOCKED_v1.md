# NF Factory Round 15 — Prep LOCKED v1

**Version:** 1.0.0 · **Status:** LOCKED · **Saved:** 2026-06-18  
**Plane:** Noetfield `noetfield_cloud` + portfolio library  
**SourceA:** read-only motor — **never edit** `~/Desktop/SourceA/` from this repo

---

## Disk truth (machine — 2026-06-18 closeout)

| Surface | Value | Verify |
|---------|-------|--------|
| Portfolio 300 | **197/300 done · 103 backlog** | `validate-portfolio-300.py` PASS · Phase 15 **30/30** |
| Noetfield lane | **50/50 done** | `--brand noetfield` → no backlog |
| Cross-portfolio XF-P1 | **10/10 done** | `verify-xf-p1-wave.sh` PASS |
| Virlux V-P2 | **10/10 done** | `verify-vp2-wave.sh` PASS |
| Canada RWA CA-P1 | **10/10 done** | `verify-ca-p1-wave.sh` PASS (Hub queue only) |
| Product ship-057 | **done** · `ship-sandbox-server-side-057` | `governance-console/backend/routes/sandbox.py` |
| GTM 059–062 | **done** | `verify-doc-ssot.sh` · `verify-gtm-ops-docs.sh` |
| Factory spine | `make nf-prove-factory-spine` **9/9 PASS** | |
| WWW client guard | `make nf-ui-checklist` **PASS** | |
| **operations@ inbox** | **ACTIVE** (Google Workspace 2026-06-18) | direct email works |
| **Resend form send** | **DEFERRED post-factory** | not P0 — factory first |

**Product queue head:** Phase 17 prep (OPS-P1 + XF-P2b + CA-P2b + PL-P2) — see [GTM_NEXT.md](../plans/no-asf/GTM_NEXT.md)  
**Phase 16 LOCK:** `~/Desktop/1 PAGER/PORTFOLIO_300_PHASE16_10_STEP_LOCKED_v1.md` (shipped 2026-06-19)

---

## Round 15 wave order (shipped)

| Priority | Wave | Plans | Status |
|----------|------|-------|--------|
| 1 | **XF-P1** | pf-0001–pf-0010 | **done** |
| 2 | **V-P2** | pf-0226–pf-0235 | **done** |
| 3 | **CA-P1** | pf-0236–pf-0245 | **done** |

---

## Next factory round (Phase 16 prep)

| Priority | Wave | Plans | Brand |
|----------|------|-------|-------|
| 1 | **TF-P3** | TrustField backlog | trustfield |
| 2 | **PL-P1** | pf-0266–pf-0275 | platform |
| 3 | **OPS-P1** | Ops-verify | noetfield |

---

## Mandatory gates (every www / factory session)

```bash
make nf-onboard
make nf-prove-factory-spine
make nf-ui-checklist
```

**UI law:** [NF_UI_BUILD_CHECKLIST_LOCKED_v1.md](../../www/NF_UI_BUILD_CHECKLIST_LOCKED_v1.md) · [NF_WWW_LANGUAGE_LAYERS_LOCKED_v1.md](../../www/NF_WWW_LANGUAGE_LAYERS_LOCKED_v1.md)

---

## Verify Phase 15 closeout

```bash
bash ~/Desktop/1\ PAGER/portfolio-300-locked/scripts/verify-portfolio-300-phase15.sh
make nf-ui-checklist
make verify-nf-gaos-w3
```
