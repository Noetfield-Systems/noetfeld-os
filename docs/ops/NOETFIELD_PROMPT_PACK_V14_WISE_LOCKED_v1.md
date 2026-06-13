# Noetfield Prompt Pack — v14 WISE (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED — supersedes v13 SMART for execution |
| **Framework** | **WISE** = Witness · Intent · Scope · Evidence |
| **500 catalog** | [NOETFIELD_PROMPT_PACK_500_MASTER_LOCKED_v1.md](./NOETFIELD_PROMPT_PACK_500_MASTER_LOCKED_v1.md) |
| **Tier 1 JSON** | [tier1-smart.json](./plans/tier1-smart.json) (v14-wise payloads) |
| **Picker** | `make pick-wise` or `python3 scripts/pick-wise.py --prompt` |
| **Regenerate** | `make generate-tier1-smart` |

---

## 1. WISE vs SMART (what changed in v14)

| Layer | v13 SMART | v14 WISE |
|-------|-----------|----------|
| Preflight | Static checklist | + read `tier1-status.json` deps |
| Reasoning | None | 4-step Witness→Evidence chain |
| Buyer proof | Implicit | Explicit one-liner per prompt |
| Self-check | None | Rubric checklist before closeout |
| Recovery | None | If verify fails — smallest diff, no scope creep |
| Dispatch | Manual `--bottleneck` | **Auto W3 maturity** + prerequisite chain |
| Session default | 3 tasks | **1 wise task** (quality over throughput) |

---

## 2. WISE agent frame (every Tier 1 prompt)

```
W — Witness   repo state + tier1-status deps before edits
I — Intent    one buyer-visible outcome (board PDF, trust page, demo)
S — Scope     max 5 files · forbidden list · stop_if
E — Evidence  verify command + self-check rubric + closeout
```

Shared library: `scripts/wise_prompt_lib.py`

---

## 3. W3 maturity auto-dispatch (v16 funnel)

| Stage | Label | Critical path % | Auto bottleneck | Meaning |
|-------|-------|-----------------|-----------------|---------|
| 0 | **SANDBOX** | 0% | `sandbox` | `/start/` live · self-serve signup |
| 1 | **DEMO** | 0–25% | `demo` | E-01 async demo · evaluate → RID |
| 2 | **EXPORT** | 25–50% | `export` | E-05/E-06 board PDF + ZIP |
| 3 | **TRUST/PROVE** | 50–75% | `trust` / `ship` | Trust center + e2e green |
| 4 | **CONVERT** | 75%+ | `pipeline` | Design partner apply · deposit ≥ CAD 2K |

**Critical path ids:** S-01 (sandbox) → E-01 → E-04 → E-05 → E-06 → L-03 → P-01

**Packaging SSOT:** [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](../WWW_V16_PACKAGING_PLAN_LOCKED_v1.md)

```bash
python3 scripts/pick-wise.py --maturity          # JSON maturity report
python3 scripts/pick-wise.py --prompt            # auto bottleneck + full WISE block
python3 scripts/pick-wise.py --id E-05 --prompt  # one id + prerequisite chain
python3 scripts/pick-wise.py --tier 2            # gated until stage ≥ 2
```

---

## 4. Prerequisite chain (wise picking)

When top pick is **BLOCKED**, picker prints:

```
Prerequisite chain: L-11 → E-01 → E-04 → E-05
```

**Rule:** Pick the **first unblocked** id in the chain — not the glamorous end state.

---

## 5. Tier architecture (unchanged counts)

| Tier | Count | Picker |
|------|-------|--------|
| T0 Constitution | 12 | Manual — C-02 Worker V3 |
| T1 WISE active | 50 | `pick-wise.py` |
| T2 Product | 138 | `pick-wise.py --tier 2` (gated) |
| T3 Archive | 300 | Never |

---

## 6. Self-check rubric (agent must answer before closeout)

Every prompt ends with:

- [ ] Does this help W3 (sandbox start OR board PDF in meeting OR deposit ≥ CAD 2K)?
- [ ] Stayed within 5-file context budget and three-SKU lock (free sandbox ≠ fourth SKU)?
- [ ] Verify command passed without weakened assertions?
- [ ] (+ phase/signal-specific checks)

---

## 7. Recovery protocol (if verify fails)

1. Read error output  
2. Fix **smallest diff** in context budget file only  
3. Re-run verify **once**  
4. If still blocked → `stop_if` → ask founder  
5. **Never** pick Tier 2/archive prompts to work around a Tier 1 failure  

---

## 8. Commands cheat sheet

```bash
make generate-tier1-smart     # regenerate 50 WISE prompts
make generate-catalog-500     # full 500 index
make pick-wise                # auto maturity + 1 prompt
make pick-tier1-smart         # alias → pick-wise
python3 scripts/sync-tier1-status.py --done E-01
```

---

## 9. Related

- [PRIORITY_MATRIX_500.md](./plans/PRIORITY_MATRIX_500.md)
- [TIER1_SMART_PROMPTS.md](./plans/TIER1_SMART_PROMPTS.md) (generated WISE blocks)
- [NOETFIELD_PROMPT_PACK_V13_SMART_LOCKED_v1.md](./NOETFIELD_PROMPT_PACK_V13_SMART_LOCKED_v1.md) (superseded)
