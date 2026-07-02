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
| `www.noetfield.com/gel/` | 200 · **update in progress** — flip to live `noetfield-gate` |
| `www.noetfield.com/ai-value-governance-os/` | 200 · Visual Polish v1 live |
| SourceA contract E2E | ALL PASS |
| `@noetfield/gate` npm | **NOT STARTED** |
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

## Phase B — PyPI org + publish hygiene (when org approved)

| Step | Action |
|------|--------|
| B-01 | Approve Noetfield PyPI organization |
| B-02 | Add `operations@noetfield.com` maintainers |
| B-03 | Transfer or republish `sourcea-boot` + `noetfield-gate` under org |
| B-04 | Enable GitHub trusted publishing (`publish-pypi.yml`) |
| B-05 | Revoke old account-scoped PyPI token after trusted publish works |

---

## Phase C — Commercial proof (highest ROI)

Research report + tracker agree: **public traction is thin; artifact spine is strong.**

| Step | Action | Success signal |
|------|--------|----------------|
| C-01 | Run one AI Value OS or Trust Brief briefing | Intake receipt + follow-up |
| C-02 | Share entity proof under NDA in active diligence | Procurement moves forward |
| C-03 | Keep synthetic proof case explicitly labeled | No fake customer claims |
| C-04 | Target: one org uses Board PDF in governance meeting | Research report proof threshold |

---

## Phase D — Developer packaging (after Phase A)

| Step | Action | Repo |
|------|--------|------|
| D-01 | Scaffold `@noetfield/gate` npm package | noetfeld-os |
| D-02 | Typed fetch wrapper for `POST /v1/decision` | noetfeld-os |
| D-03 | `DecisionReceipt` interface + sample | noetfeld-os |
| D-04 | Link `/gel/` to npm when published | Website |

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

1. **Execute Phase A** — gel + KB + deploy (in progress)
2. **Stop website churn** until one briefing/pilot is active (Phase C)
3. **PyPI org** — founder admin tomorrow

**Locked by:** noetfeld-os-cursor-chat · 2026-07-02
