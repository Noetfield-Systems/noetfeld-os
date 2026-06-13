# SHIP NOW — Noetfield

**Ship rule:** Bounded founder `implement` + [GTM_NEXT.md](docs/ops/plans/no-asf/GTM_NEXT.md) queue — see `os/plan.json` `ship_rule`. Ingest required after VERIFY. No self-start (R-007/R-011).

## Active queue (`next_tasks`)

**Packaging v16 + www v18 (2026-06-13):** Self-serve sandbox — `/start/` · `/pricing/` · tier-1 UI · [WWW_V16_PACKAGING_PLAN_LOCKED_v1.md](docs/WWW_V16_PACKAGING_PLAN_LOCKED_v1.md) · [WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md](docs/WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md).

**Shipped tenth audit (PR #48 @ b822423):** iter 18 on main — checkpoint verify hardening, OpenAPI bridge, MERGED_WINDOW config.

**Cloud GTM iter 19:** see [GTM_NEXT.md](docs/ops/plans/no-asf/GTM_NEXT.md) (server-side sandbox optional, agentic manifest wire, doc-ssot guards, OpenAPI verify).

**Shipped ninth audit (PR #47 @ 46a36a3):** iter 17 on main.

**Local repo (Mac):** Say **PLAN WITH NO ASF** → `make pick-no-asf-plan` (locked 1000: `os/plan-library/noetfield-1000/`).

**Wise picker:** `make pick-wise` — W3 funnel starts at **S-01 sandbox** ([V14 WISE](docs/ops/NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md)).

## Active commercial P0 (agentic — Hub only)

| ID | Owner | Handoff |
|----|-------|---------|
| **ship-design-partner-outreach-026** | Agentic layer | [AGENTIC_COMMERCIAL_HANDOFF_v1.md](docs/ops/AGENTIC_COMMERCIAL_HANDOFF_v1.md) |
| **ship-sandbox-nurture-060** | Agentic layer | [COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md](docs/ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md) |

NF-CLOUD ships product + www on disk; founder Hub approves outbound. See R-011 + `os/plan.json` `agentic_queue`.

## W3 funnel (v16)

```text
/start/ (S0) → evaluate (S1) → export sample (S2) → /copilot/pilot/ (S3) → board PDF (S4)
```

## NO ASF closeout cadence

1. Merge ship PR to `main` (if open)
2. Founder **`implement`** → bounded ≤3 tasks
3. `./scripts/plan-with-no-asf-verify.sh`
4. `python3 scripts/sync-prompt-pack-status.py`
5. `reports/cursor-reply-latest.txt`
6. **ASK** founder next move (Hub ingest = agentic layer)

## Shipped waves

| Wave | IDs | Highlights |
|------|-----|------------|
| **v16 packaging** | 057–059 | /start/ · /pricing/ · prompt pack · inbox · e2e |
| 040–042 | Customer acquisition | design partner SOW, copilot hub, homepage CTA |
| 034–039 | GTM demo polish | procurement zip, verify-gtm |
| **Locks** | Packaging + GTM | `WWW_V16_PACKAGING_PLAN_LOCKED_v1.md`, `NOETFIELD_GTM_60_DAY_LOCKED_v1.md` |

## Agent references

| Doc | Path |
|-----|------|
| **Packaging v16** | `docs/WWW_V16_PACKAGING_PLAN_LOCKED_v1.md` |
| **Inbox routing** | `docs/ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md` |
| GTM copybook | `docs/GTM_COPYBOOK.md` |
| Commercial SSOT | `docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md` |
| Agentic commercial law | `docs/ops/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` |

## Verify

```bash
make verify-gtm
make verify-doc-ssot
./scripts/plan-with-no-asf-verify.sh
```
