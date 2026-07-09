# [NOOS-AGENT-20260615-007] Glossary, Plane Tags & Anti-ICP

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260615-007
doc_type: GLOSSARY
workspace_root: /Users/sinakazemnezhad/Desktop/Noetfield-Systems/noetfeld-OS
classification: INTERNAL — category vocabulary and cross-repo tagging
related_docs: NOOS-AGENT-20260529-002, NOOS-AGENT-20260615-006
-->

**Steps covered:** 0003 (GEL category) · 0004 (anti-ICP) · 0006 (plane tags)

---

## Category name (registered)

**Governance Execution Layer (GEL)**

> Infrastructure that evaluates versioned policy against structured decision intents **before** downstream systems execute, returns governance outcomes (APPROVE / REVIEW / DECLINE), and writes append-only audit evidence.

**Short names:** Noetfield GEL · Noetfield OS (engineering codename: `noetfeld-os`)

**We are not:** GRC suite · LLM host · LOS · payment processor · agent tool proxy for all SaaS APIs.

---

## Glossary

| Term | Definition |
|------|------------|
| **Decision intent** | Structured payload describing an operational decision request (e.g. credit application attributes) — no execution side effects |
| **Governance outcome** | APPROVE, REVIEW, or DECLINE — signal only; client actuators decide what to do |
| **Policy pack** | Versioned JSON rules (`base_policy.json`, `corridor_policy.json`, tenant packs) |
| **Corridor rule** | Bounded policy branch (e.g. max LTV, min score) evaluated after base policy |
| **Audit spine** | Append-only log of every evaluation with inputs, scores, versions, timestamps |
| **Trust Ledger** | Noetfield register / export destination for board-ready evidence (sibling service) |
| **Drift** | Detected change between policy baseline and live decision distribution (Phase 5) |
| **Replay** | Re-running same intent + policy version → identical outcome (determinism proof) |
| **Non-custodial** | No funds, accounts, or transactions initiated by Noetfield OS |
| **Pre-execution** | Evaluation occurs before client systems act on the decision |
| **Fail closed** | If gate unavailable, unchecked decisions must not proceed by default |

---

## Plane tags (Steps 0006)

Use on any cross-repo claim, commit message, or doc section that spans ecosystems.

| Tag | Authority | This repo |
|-----|-----------|-----------|
| `[DESIGN]` | `~/Desktop/SourceA/SINA_OS_SSOT_LOCKED.md` and portfolio SSOT | Read-only — cite, never override |
| `[EXECUTION]` | SinaaiMonoRepo runtime `:8000` | Isolated — never import or merge |
| `[DELIVERY]` | `noetfeld-os` code + `NOOS-AGENT-DOC` vault | **Canonical for our output** |

**Examples:**

- `[DELIVERY] POST /v1/decision returns APPROVE/REVIEW/DECLINE` — true for this repo
- `[EXECUTION] Telegram liaison bot on :8000` — mono runtime, not us
- `[DESIGN] Noetfield primary earner per portfolio SSOT v3.1` — cite SourceA, don't rewrite

**Identity separation (Noetfield vs SourceA vocabulary):**

| Layer | Use these words | Never use in Noetfield pitch |
|-------|-----------------|------------------------------|
| Noetfield / GEL | TLE, board pack, governance, audit trail, APPROVE/REVIEW/DECLINE | runs, SDK, replay, broker |
| SourceA | runs, events, SDK, policy gate, replay | TLE, Copilot pack, Trust Brief |

---

## Anti-ICP (Step 0004)

**Do not pursue** — use rejection script when qualifying.

| Anti-ICP | Why | Rejection script |
|----------|-----|------------------|
| Crypto / unregulated lending | No audit appetite; custody pressure | "We only serve regulated operators who need pre-execution evidence — we don't support auto-approve without audit." |
| Full LOS in 30 days | Out of scope — workflow + origination | "We're the governance layer, not your origination system. Your LOS calls our API before execution." |
| Custody or payment initiation | Non-custodial boundary | "We return governance signals only — we never move money or open accounts." |
| General ChatGPT / chatbot build | Wrong category | "We govern structured operational decisions, not conversational AI products." |
| Global GRC replacement | OneTrust-class rip-and-replace | "We integrate with your GRC stack as the per-decision enforcement log — we don't replace your control catalog." |

---

## Primary ICP (reminder)

**Regulated Decision Operator** — Canada-first, 50–5,000 employees, board/compliance asking for the log before execution. See `NOOS-AGENT-20260529-002` §5.

---

*End of glossary — `NOOS-AGENT-20260615-007`*
