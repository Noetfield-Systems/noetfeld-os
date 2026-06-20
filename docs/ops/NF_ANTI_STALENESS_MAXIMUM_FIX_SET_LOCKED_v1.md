# NF Anti-Staleness — Maximum Fix Set (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED |
| **Saved** | 2026-06-19 |
| **Parent** | [NF_GAOS_W3_FACTORY_SPINE_LOCKED_v1.md](./NF_GAOS_W3_FACTORY_SPINE_LOCKED_v1.md) |
| **Machine SSOT** | `data/nf_anti_staleness_max_v1.json` |
| **Orchestrator** | `scripts/nf_anti_staleness_max_v1.py` |

## One sentence

> **Chat is never SSOT.** Maximum anti-staleness wires SourceA mono nerves → Noetfield boot → TrustField fleet → founder cascade disk sync → cascade → gatekeeper DENY — skip any layer = FAIL.

---

## Minimum vs maximum

| # | Fix | Minimum (shipped) | Maximum (this doc) |
|---|-----|-------------------|---------------------|
| 1 | Mono defer line every boot | `nf_mono_nerve` step 1 | + ecosystem receipt + TF fleet pulse |
| 2 | Founder-input → disk | `nf_founder_input_sync` step 2 | + orient read chain validate |
| 3 | Stale guard mono timestamps | `nf_stale_guard` | + parent/nerve TTL + sync receipt |
| 4 | Gatekeeper email DENY | `EMAIL_SEND_DEFERRED` | + `nf_email_lane_guard` on edit paths |
| 5 | — | — | `nf_anti_staleness_max` orchestrator |
| 6 | — | — | `verify-nf-anti-staleness-max` superset |
| 7 | — | — | `agent-session-start` fail-closed |
| 8 | — | — | Three email gates separated in SSOT |

---

## Boot ladder (12 steps — skip none)

```text
make nf-onboard
  1.  nf_mono_nerve          — defer assess + TF fleet + ecosystem nerve
  2.  nf_founder_input_sync  — cascade → INBOX + SHIP_NOW + receipt
  3.  nf_session_gate         — mono receipts required
  4.  nf-live-orient          — LIVE-STATUS + defer line
  5.  nf_routing_card
  6.  nf_stale_guard          — mono timestamps + founder sync
  7.  nf_voyage_integrity
  8.  nf_live_surfaces        — email_send_defer_line required
  9.  nf_receipt_cascade      — all nodes incl. mono + founder
  10. nf_gatekeeper           — advisory on boot
  11. nf_panel_export
  12. UI checklist + nf_anti_staleness_max — final superset PASS
```

**Before first edit:**

```bash
NF_FOUNDER_IMPLEMENT=1 bash scripts/nf_assert_implement_allowed.sh
```

**Before email/Resend path edit:**

```bash
NF_EMAIL_LANE_EDIT=1 python3 scripts/nf_email_lane_guard_v1.py --json
```

---

## Three email gates (never conflate)

| Gate | Meaning | Receipt |
|------|---------|---------|
| **inbox_receive** | `operations@` GW can receive | `~/.sina/noetfield-operations-inbox-active-v1.json` |
| **form_autonotify** | Resend www form auto-send | **DEFERRED post-factory** |
| **outbound_send** | W3 commercial send lane | `~/.sina/commercial-email-send-defer-receipt-v1.json` |

`hello@` / Mail FROM active ≠ send lane open.

---

## Cross-plane nerve map

```mermaid
flowchart LR
  SA[SourceA defer SSOT]
  MONO[~/.sina agent-live-surfaces]
  NF[nf-mono-nerve]
  TF[tf-live-surfaces]
  ECO[ecosystem-live-nerve]
  SURF[nf-live-surfaces]
  GK[nf-gatekeeper]

  SA --> NF
  MONO --> NF
  NF --> TF
  NF --> ECO
  NF --> SURF
  SURF --> GK
  ECO --> GK
```

---

## Deny rules (gatekeeper + email lane guard)

- `MONO_NERVE_FAIL` — mono wire broken
- `CONTEXT_STALE` — stale guard true
- `MISSING_EMAIL_SEND_DEFER_LINE` — no defer line on surfaces
- `EMAIL_SEND_DEFERRED` — defer ON + task touches Resend/email/outreach
- `EMAIL_LANE_EDIT_BLOCKED` — defer ON + edit targets email lane paths

---

## Verify (machine)

```bash
make verify-nf-anti-staleness-max   # superset
make nf-prove-factory-spine         # positive + negative proofs
make verify-nf-mono-nerve-wire       # cross-plane wire
```

Receipt: `~/.sina/nf-anti-staleness-max-v1.json`

---

## Heal

```bash
make nf-onboard
```

If founder pivot in chat: ensure `founder-input-cascade` event exists, then re-run onboard (step 2 patches INBOX + SHIP_NOW).

---

## Quote rule (every agent reply)

Read `~/.sina/nf-live-surfaces-v1.json` → quote **`product_now_line`** and **`email_send_defer_line`**.
