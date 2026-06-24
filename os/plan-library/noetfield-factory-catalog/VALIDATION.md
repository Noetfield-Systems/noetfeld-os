# Noetfield Factory Catalog — validation matrix

**Saved:** 2026-06-19T06:30:00Z · **Lock:** [`../NOETFIELD-FACTORY-CATALOG-LOCK.md`](../NOETFIELD-FACTORY-CATALOG-LOCK.md)

## Machine checks

```bash
bash scripts/validate-noetfield-factory-catalog.sh
```

## Required on disk

| File | Assert |
|------|--------|
| `REGISTRY.json` | `schema=noetfield-factory-catalog-v1` · ≥1 factory |
| `specs/noetfield-governance-factory-v1.json` | `demo_seconds=30` · `receipt_emitter=scripts/emit-governance-receipt.py` |
| `../NOETFIELD-FACTORY-CATALOG-LOCK.md` | LOCKED header |
| `../BUILD_FACTORY_TAB_IA_v1.md` | 4 sections Catalog/Studio/Sandbox/Teams |
| `../NOETFIELD-WORKERS-PLAN-LOCK.md` | points at plan.json |
| `scripts/emit-governance-receipt.py` | exists |

## Site wire

| Surface | Path |
|---------|------|
| Build Factory page | `factory/index.html` |

## Tier honesty

- Sandbox/freemium runs emit `MOCK_ONLY` until premium unlock
- `governance.delivery_mode: mock_only` on governance spec
