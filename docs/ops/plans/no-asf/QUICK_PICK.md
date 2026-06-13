# PLAN WITH NO ASF — quick pick (v14 WISE)

When the founder says **PLAN WITH NO ASF**, start here.

## Primary picker (recommended)

```bash
make pick-wise                    # auto W3 maturity + 1 WISE prompt
python3 scripts/pick-wise.py --maturity
python3 scripts/pick-wise.py --bottleneck export --prompt
python3 scripts/pick-wise.py --id E-05 --prompt
```

**SSOT:** [NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md](../../NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md) · [500 master](../../NOETFIELD_PROMPT_PACK_500_MASTER_LOCKED_v1.md) · [catalog-500.json](../catalog-500.json)

**Packaging SSOT:** [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](../../../WWW_V16_PACKAGING_PLAN_LOCKED_v1.md) · funnel starts **S-01 sandbox** on `/start/`

**After ship:** `python3 scripts/sync-tier1-status.py --done S-01`

---

## WISE frame

| Step | Action |
|------|--------|
| **W**itness | `pick-wise --maturity` · read tier1-status deps |
| **I**ntent | One buyer-visible outcome per session |
| **S**cope | Max 5 files · forbidden list |
| **E**vidence | Verify + self-check · sync status |

**Default:** 1 task/session (not 3) · prerequisite chain shown when blocked

---

## Auto bottleneck by W3 stage (v16)

| Stage | Pick |
|-------|------|
| 0 SANDBOX | `--bottleneck sandbox` · `/start/` |
| 1 DEMO | `--bottleneck demo` |
| 2 EXPORT | `--bottleneck export` |
| 3+ PROVE | `--bottleneck ship` or `trust` |
| 4 CONVERT | `--bottleneck pipeline` |

Critical path: **E-01 → E-04 → E-05 → E-06 → L-03 → P-01**

---

## Ops fallback

`make pick-no-asf-plan` (nf-1000 hygiene) · [GTM_NEXT.md](./GTM_NEXT.md) micro-queue
