# NOETFIELD Workers Plan — LOCKED v1

**Status:** LOCKED · **Saved:** 2026-06-19T06:00:00Z

| Layer | Path |
|-------|------|
| Ship state | `os/plan.json` |
| GTM queue | `os/plan.json` GTM_NEXT |
| Plans library | `os/plan-library/noetfield-1000/` |
| Factory catalog | `noetfield-factory-catalog/REGISTRY.json` |

## Loop

```bash
make nf-onboard
pytest tests/unit/test_governance_runtime_10step.py -q
python3 scripts/emit-governance-receipt.py
```

## Law

SourceA motor read-only · Noetfield owns TLE receipts · never edit SourceA disk.
