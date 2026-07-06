<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260702-024
doc_type: ECOSYSTEM_NEXT_PLAN_LOCKED
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
locked_at: 2026-07-02
-->

# Ecosystem Next Plan — LOCKED v1

**Status:** LOCKED  
**Date:** 2026-07-02  
**Scope:** Noetfield OS + noetfield.com + SourceA contract surfaces  
**Note (2026-07-06):** Loop/autonomy rows superseded by `NOOS-AGENT-20260705-029`. PyPI/commercial rows remain valid.
**Source:** session status check, PyPI publish, research report synthesis

---

## Current truth (locked)

| Surface | State |
|---------|--------|
| PyPI `sourcea-boot` | **LIVE** v0.1.0 |
| PyPI `noetfield-gate` | **LIVE** v0.1.0 |
| PyPI Noetfield org | Request submitted — packages on maintainer account until approved |
| PyPI primary email | `operations@noetfield.com` (confirmed) |
| `www.noetfield.com/about/` | 200 · entity proof under NDA (no Pending publication) |
| `www.noetfield.com/trust/` | 200 · proof tiers + entity proof under NDA |
| `www.noetfield.com/gel/` | 200 · live `noetfield-gate` v0.1.0 on PyPI |
| `www.noetfield.com/ai-value-governance-os/` | 200 · Visual Polish v1 live |
| SourceA contract E2E | ALL PASS |
| `@noetfield/gate` npm | **SCAFFOLD** — `packages/gate/` (publish pending) |
| First real customer proof | **NOT PUBLIC** — synthetic case remains labeled |

---

## Locked decisions (carry-forward)

| ID | Lock |
|----|------|
| DEC-001 | Homepage = two-door entry (SME Intelligence vs Enterprise) |
| DEC-002 | First proof lane = Trust Brief / AI Value OS |
| DEC-003 | Ed25519 verify first; SOC 2 readiness second |
| DEC-004 | Enterprise lead = AI Value Governance OS |
| DEC-005 | Minimal `/intelligence/` hub built |

---

## Phase A — Publish truth sync (this week)

| Step | Owner | Action | Done when |
|------|-------|--------|-----------|
| A-01 | Website | Update `/gel/` for live `noetfield-gate` v0.1.0 | Page shows `pip install noetfield-gate` + PyPI link |
| A-02 | Website | Sync chatbot KB (`developer-tools`, `gel-runtime`, `faq`) | Manifest hashes pass |
| A-03 | Website | Sync AI Value OS proof block | No "publish pending" on live pages |
| A-04 | Website | Deploy + verify route inventory | `--live` PASS |
| A-05 | NOOS | Update `PRODUCT_TRUTH.md` PyPI line | Says both packages live |

---

## Phase B — PyPI org + publish hygiene (**DEFERRED — founder 2026-07-03**)

> **SKIP for agents.** Founder handles org approval + token rotation tomorrow.

| Step | Action |
|------|--------|
| B-01 | Approve Noetfield PyPI organization |
| B-02 | Add `operations@noetfield.com` maintainers |
| B-03 | Transfer or republish packages under org |
| B-04 | Enable GitHub trusted publishing |
| B-05 | Revoke old account-scoped PyPI token after trusted publish works |

---

## Phase A status — **COMPLETE** (2026-07-02)

All A-01 through A-05 closed. Website commit `30320c48`. NOOS commit `7667ccc`.

---

## Phase D — Developer packaging (**IN PROGRESS**)

| Step | Action | Status |
|------|--------|--------|
| D-01 | Scaffold `@noetfield/gate` npm package | **DONE** — `packages/gate/` |
| D-02 | Typed fetch wrapper for `POST /v1/decision` | **DONE** |
| D-03 | `DecisionReceipt` interface + sample | **DONE** |
| D-04 | Link `/gel/` to npm when published | Blocked on npm publish |

---

## 300-plan sprint (Phase 4 — active)

| UPG | Item | Status |
|-----|------|--------|
| 0021–0028 | GEL 5-min demo script + fixtures + `--sample-block` | **DONE** |
| 0165–0166 | `@noetfield/gate` npm scaffold | **DONE** |
| 0184 | Makefile (`make demo`, `make gate`, `make test`) | **DONE** |
| 0018 | `check_production_urls.sh` | **DONE** |
| 0001–0007 | NW1/SW1 outbound + W1 video | **Founder** |
| 0167 | npm publish | After legal/org |

## Phase C — Commercial proof (highest ROI — **NEXT for founder**)

Research report + tracker agree: **public traction is thin; artifact spine is strong.**

| Step | Action | Success signal |
|------|--------|----------------|
| C-01 | Run one AI Value OS or Trust Brief briefing | Intake receipt + follow-up |
| C-02 | Share entity proof under NDA in active diligence | Procurement moves forward |
| C-03 | Keep synthetic proof case explicitly labeled | No fake customer claims |
| C-04 | Target: one org uses Board PDF in governance meeting | Research report proof threshold |

---

## Phase E — Deferred (do not start until C-01 in motion)

- Full nav dropdown refactor
- AI Value OS architecture diagram
- SOC 2 / Ed25519 public capability claims
- BC registry public extract (without NDA)
- SourceA brain bundle refresh (unless brain lane active)

---

## Secret rotation policy (locked)

| Secret | Rotate? | Trigger |
|--------|---------|---------|
| CF cache purge token (line 174) | **No** (optional) | Only if shared beyond local machine |
| PyPI API token | **After org/trusted publish** | Token pasted in chat or org migration complete |
| Full vault reset | **No** | No evidence of broad leak |

---

## Verification commands

```bash
# PyPI
curl -sS https://pypi.org/pypi/noetfield-gate/json | python3 -m json.tool | head
curl -sS https://pypi.org/pypi/sourcea-boot/json | python3 -m json.tool | head

# Website
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
bash scripts/verify-static-www.sh
python3 scripts/verify-route-inventory.py --live

# SourceA contract pack
cd ~/Desktop/SourceA
bash scripts/validate-sourcea-contract-pages-e2e-v1.sh
SOURCEA_E2E_STRICT_NOETFIELD=1 bash scripts/validate-sourcea-contract-pages-e2e-v1.sh
```

---

## Next action (immediate)

1. **Founder tomorrow:** PyPI org (Phase B) — agents skip
2. **Founder now:** Phase C — run one Trust Brief / AI Value OS briefing (UPG-0001 motion)
3. **Agent done this pass:** Phase 4 demo + npm scaffold (UPG-0021–0028, 0165–0166, 0184)
4. **Optional founder:** `bash scripts/demo-gel-5min-v1.sh` + record W1 video (UPG-0005, 0029)

**Locked by:** noetfeld-os-cursor-chat · 2026-07-02
