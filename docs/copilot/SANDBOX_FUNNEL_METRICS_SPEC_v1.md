# Sandbox Funnel Metrics Spec

**Version:** 1.0.0 · **Plan:** pf-0033 · **Funnel:** `/start/` → evaluate → pilot CTA  
**Mode:** docs-only tracker · Hub reporting

---

## Stages

| Stage | Event | Signal |
|-------|-------|--------|
| S0 | `/start/` session start | Sandbox activated |
| S1 | First `evaluate` call | Product engagement |
| S2 | Export sample viewed | Export interest |
| S3 | `/copilot/pilot/` or intake click | Pilot CTA |
| S4 | Intake submitted `vector=copilot-governance` | Commercial intent |
| S5 | Board PDF in meeting | W3 success (post-pilot) |

---

## Conversion targets (orientation)

| Metric | Target |
|--------|--------|
| S0 → S1 | ≥ 40% within 7 days |
| S1 → S3 | ≥ 15% within 14 days |
| S3 → S4 | ≥ 25% of CTA clicks |
| S4 → deposit/LOI | W3 bar CAD ≥ $2K |

---

## Tracker row (per session)

```
session_id: ___
started_at: ___
evaluate_count: ___
export_viewed: Y/N
pilot_cta_clicked: Y/N
intake_submitted: Y/N
plan_id: pf-0033
```

---

## Hub report cadence

Weekly rollup to Hub card — no founder Terminal required.
