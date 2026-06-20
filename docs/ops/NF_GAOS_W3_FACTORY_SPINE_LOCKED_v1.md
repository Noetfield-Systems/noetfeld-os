# NF-GAOS W3 — Factory Spine LOCKED

**Version:** 1.0.0 · **Status:** LOCKED · **Saved:** 2026-06-18  
**Plane:** Noetfield product (`noetfield_cloud`)  
**Parent:** [`NF_GAOS_W1_LOCKED_v1.md`](./NF_GAOS_W1_LOCKED_v1.md) · [`ROUTING_CARD.md`](../ROUTING_CARD.md)  
**SourceA pattern:** session gate → live surfaces → receipt cascade → execution gatekeeper (read-only mirror)

## One sentence

> **Disk is SSOT.** NF-GAOS W3 adds SourceA-grade **live surfaces**, **truth bundle**, **receipt cascade**, and **execution gatekeeper** — orientation stays manual; implement requires gate PASS + founder `implement`.

## Mental model

```text
make nf-onboard
  → mono_nerve (SourceA defer + ~/.sina wires) → session_gate → live_orient
  → routing_card → stale_guard → voyage
  → live_surfaces (product_now_line + email_send_defer_line) → receipt_cascade → gatekeeper (advisory)
  → panel export

Before first edit:
  NF_FOUNDER_IMPLEMENT=1 make nf-gatekeeper --require-implement
```

## Mono nerve (W3.1 — fail-closed)

| Asset | Path |
|-------|------|
| Wiring SSOT | `data/nf_mono_nerve_wiring_v1.json` |
| Mono nerve script | `scripts/nf_mono_nerve_v1.py` |
| Defer SSOT (read-only) | `~/Desktop/SourceA/data/commercial-email-send-defer-v1.json` |
| Defer receipt | `~/.sina/commercial-email-send-defer-receipt-v1.json` |
| Operations inbox receipt | `~/.sina/noetfield-operations-inbox-active-v1.json` |
| Mono receipt | `~/.sina/nf-mono-nerve-v1.json` |

**Law:** `email_send_defer_line` required on every boot. Gatekeeper **DENY** (`EMAIL_SEND_DEFERRED`) if pending task touches Resend/email/outreach while defer ON.

**Maximum fix set:** [NF_ANTI_STALENESS_MAXIMUM_FIX_SET_LOCKED_v1.md](./NF_ANTI_STALENESS_MAXIMUM_FIX_SET_LOCKED_v1.md) · `make verify-nf-anti-staleness-max`

## New artifacts (W3)

| Asset | Path |
|-------|------|
| Orient SSOT | `data/nf_orient_routing_v1.json` |
| UI checklist LOCK | `docs/www/NF_UI_BUILD_CHECKLIST_LOCKED_v1.md` |
| Factory Round 15 | `docs/ops/NF_FACTORY_ROUND_15_PREP_LOCKED_v1.md` |
| Live surfaces | `~/.sina/nf-live-surfaces-v1.json` |
| Truth bundle | `~/.sina/nf-truth-bundle-v1.json` |
| Receipt cascade | `~/.sina/nf-receipt-cascade-v1.json` |
| Gatekeeper | `~/.sina/nf-gatekeeper-receipt-v1.json` |
| Repo map | `os/NF_REPO_CAPABILITY_MAP.json` |

## Agent quote rule (mandatory)

Every substantive reply quotes **`product_now_line`** and **`email_send_defer_line`** from `nf-live-surfaces-v1.json` — not chat memory.

## Commercial inbox sequencing (founder 2026-06-18)

| Layer | Status |
|-------|--------|
| Google Workspace `operations@noetfield.com` | **ACTIVE** — direct email |
| Resend / www form auto-send | **DEFERRED post-factory** — not session boot |
| P0 | Factory spine + portfolio waves |

## Laws

- **Never** auto-run `make nf-orient` on session start
- **Never** mix `sa-*` / `mx-*` in nf cloud session (RF-010)
- **Never** edit `~/Desktop/SourceA/` from this repo
- **Never** open visible Chrome — curl/headless verify only
- Gatekeeper FAIL → **EXECUTION DENIED** — no file edits

## Verify (machine proof — not prose)

```bash
make nf-prove-factory-spine    # scripts/prove-nf-factory-spine-v1.py
make verify-nf-gaos-w3         # full W3 gate + proof harness
pytest tests/unit/test_nf_factory_spine_v1.py -q
```

Proof receipt: `~/.sina/nf-factory-spine-proof-v1.json` · `reports/agent-auto/events/nf-factory-spine-proof-v1.json`

## Cross-plane note

SourceA Worker keeps `factory-now-v1.json` + `agent-live-surfaces-v1.json`. Noetfield keeps **nf-** prefixed mirrors. Mono `repo-find.sh` remains ecosystem router.
