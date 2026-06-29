# [NOOS-AGENT-20260615-010] Business Strategy — Proof Density & Commercial Motion

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260615-010
doc_type: BUSINESS_STRATEGY
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — commercial motion for Noetfield GEL lane
authority: SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md (wins on conflict)
sources_merged: Desktop/2 PAGER/SOURCEA_NOETFIELD_STRATEGY_PACK_2026-06-15_v1.md
related_docs: NOOS-AGENT-20260615-011, NOOS-AGENT-20260615-013, NOOS-AGENT-20260615-006, NOOS-AGENT-20260529-002
-->

**Status:** Active · 2026-06-15  
**Product surface:** Noetfield (buyer) · Noetfield OS / GEL (runtime in this repo)

> **Reconciliation note.** Merged from outside-eye consolidation (`Desktop/2 PAGER/`). Locked equivalents on disk — `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md`, `NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md`, `SOURCEA_ICP_MARKET_IDENTITY_LOCKED_v1.md`. **Where this conflicts with a LOCKED doc, the locked doc wins.**

---

## 1. Big picture

**Category.** SourceA is **Runtime Governance Infrastructure** — pre-LLM governed execution. Every agent action is gated by policy *at dispatch*, written to a signed, replayable ledger, and protected by tamper detection — **before** the model acts.

**Two layers, separate buyers and revenue.**

| Layer | What | Buyer surface |
|-------|------|---------------|
| Infrastructure | Policy-at-dispatch, receipt ledger, replay, tamper-evidence | SourceA |
| Application | Compliance/governance buyer surface (**primary**) | **Noetfield** |

TrustField, Forge, AgentField are adjacent surfaces — each layer carries its own buyer and revenue line.

**Noetfield OS (GEL)** in this repo is the **runtime**: pre-execution `decide()` → audit → TLE export.

**The wedge — why now.** Enterprises put agents into production faster than they built controls. Static policy at session start is insufficient — governance must run at the **request level, on every action**.

**The differentiator — proof density.** Cold start → full chain visible in **<5 min**:

```text
request → policy evaluation → decision → enforcement → signed receipt → replay → tamper-FAIL → signed audit chain
```

Prospects who **watch** the chain beat any slide. W1 script: `~/Desktop/SourceA/scripts/demo-enforcement-5min-v1.sh` (runs clean).

**Operating focus.** One engine. Noetfield primary; TrustField parallel (not P0 build). Buyer-1 GTM runs **in parallel** with the engine, never sequenced behind it.

**The motion.** Agents open conversations; recorded proof closes them; the founder approves only irreversible steps (send, book, spend, sign). Pre-revenue, the fundable signal is **an active design partner running the system in a real workflow**.

**Buyer sequencing (law).** Platform engineering **NOW** → Embed (orchestrator / partner integration) → Enterprise (procurement, SOC 2). Do **not** fight enterprise procurement pre-revenue.

---

## 2. Two parallel GTM lanes (do not merge on calls)

| Lane | Buyer | Motion | Attach / link |
|------|-------|--------|----------------|
| **NW1** | Copilot / compliance / CISO | One hand-run email + 15-min live demo | Battle card §16 + **`NOOS-AGENT-20260615-011`** (Copilot one-pager) |
| **SW1** | AI-native platform engineer | Repo / demo link, no deck | **`NOOS-AGENT-20260615-013`** + `noetfield gate` / GEL in <5 min |

**Law:** One NW1 + one SW1 on Day 1. **No** 20/day blast before first reply proves message.

---

## 3. Roadmap (pre-revenue)

Currency: **proof + first paid design partner.** Design-partner active usage = pre-seed/seed validation; ~$1–3M ARR = Series A repeatability bar. Optimize for the first signal.

### Phase 0 — Unblock (this week)

| # | Artifact | Disk signal |
|---|----------|-------------|
| 1 | NW1 **sent** | `~/.sina/nw1-outbound-send-receipt-v1.json` · screenshot |
| 2 | W1 **recorded** | Video file · <5 min full chain |
| 3 | SW1 **link** | Message sent · README / gate runs <5 min |

**Guard:** Do not build automation to send one already-drafted email.

### Phase 1 — First paid design partner (0–60 days)

- **Shadow pilot:** CAD **$2K deposit** · 30–60 days · one workflow / one agent fleet · one success metric · conversion clause · refund if metric missed.
- **NF-RD band (NW1):** CAD **$5–10K** founding-customer Copilot Readiness Pilot when buyer is compliance-led.
- Hit metric → convert → capture **what in message + demo closed** → case study + reference.

**Milestone:** 1 paid design partner + 1 reference logo.

### Phase 2 — Templatize (60–120 days)

- Repeat proven outreach only · approval-gated · **3 DPs** target.
- Mac automation **one lane at a time** (commercial first, factory second). Hub tap on send/book/spend.
- Never automate a motion you haven't proven by hand.

**Milestone:** 3 DPs, repeatable motion, raise narrative.

### Phase 3 — Embed + widen (120d+)

- Orchestrator / partner integration (Embed buyer).
- Open-core enforcement core **post-Eval-1, once core is stable.**
- SOC 2 path **only when pulled by real enterprise demand.**

**Milestone:** embed design partner(s) + inbound from open-core adoption.

### Standing guardrails (all phases)

- **Frozen zone:** no new architecture layers before outreach is sent.
- **Proof-density bar:** every demo / pilot / deck shows full chain in <5 min, cold start.
- **Separation law:** Noetfield speaks compliance/board; SourceA speaks infrastructure.
- **CASL-safe outreach:** identified sender, consent/relationship basis, unsubscribe path; one quality message over volume blast.
- **Human approval** on every irreversible action (send / book / spend / sign).

---

## 4. ICP — Buyer 1 (Platform / AI-Infra Engineering) — SW1 lane

**One-liner:** Teams that *already run AI agents in production* and *lack provable, per-action governance* — small enough that one technical champion can approve a CAD $2K pilot without procurement.

### Firmographic profile

- **Stage/size:** Seed–Series C, or one autonomous platform team in a larger org (~50–2,000 employees).
- **AI maturity:** agents in production or serious pilot — not "exploring AI."
- **Budget:** technical champion with discretionary spend up to a few thousand; avoid formal procurement at first touch.
- **Regulatory exposure:** regulated or sensitive data, or sells into regulated buyers.

### Priority segments (ranked)

1. **AI-native / agent-platform startups** — agent builders, vertical AI agents, autonomous workflow tools.
2. **Fintech & financial-services platform teams** — money movement, underwriting, customer data.
3. **Healthtech & insurance** — PHI/claims; HIPAA-class liability.
4. **Legal / compliance tech** — drafting/filing where wrong action is malpractice-grade.
5. **Dev-tools & data-platform companies** shipping agentic features internally.

### Champion persona

- **Primary:** Head of Platform Engineering · Head of AI Infrastructure · Staff+ platform engineer · founder/CTO at agent-native startups.
- **Influencers (later):** Head of Compliance, CISO — **Enterprise phase**, not Buyer 1 first touch.
- **Anti-persona:** procurement, generic IT, innovation lab with no production system.

### Trigger signals (hot if ≥2)

- Recently shipped/announced agentic feature.
- Public agent incident, near-miss, or governance concern.
- Hiring for AI safety / governance / ML-platform roles.
- Built on LangGraph, CrewAI, AutoGen, MCP stacks.
- SOC 2 / regulatory pressure or selling into regulated buyers.
- Recently raised to scale AI.

### Disqualifiers

- No agents in production · pure prompt-wrapper · vendor bundles governance · 9-month procurement at first contact.

### Fit scorecard (pursue ≥7/12)

| Dimension | 0 | 1 | 2 |
|-----------|---|---|---|
| Agents in production | none | piloting | live in prod |
| Governance gap | solved | partial | none / acute |
| Regulatory exposure | low | medium | high |
| Champion access | procurement-only | influencer | platform owner w/ budget |
| Trigger signals | 0 | 1 | ≥2 |
| Deal velocity | procurement | committee | single-signer pilot |

**Sourcing:** agent-framework GitHub orgs, AI-engineering communities, recent agentic launches/funding — **build named list from research against scorecard**; CASL means researched, identified, relationship-based first messages, not scraped blast.

---

## 5. Pilot economics

| Term | NW1 (Copilot) | SW1 (platform) |
|------|---------------|----------------|
| SKU | **NF-RD** Copilot Readiness Pilot | Founding shadow pilot |
| Deposit | **CAD $2,000** (refund if metric missed) | **CAD $2,000** |
| Full band | **CAD $5,000–$10,000** NF-RD | Agreed at close |
| Mode | **Shadow** — parallel to existing stack | Same |
| Deliverables (NW1) | TLE v1 · board PDF · procurement ZIP | — |
| Success metric | One number agreed up front | Same |

---

## 6. Demo & runtime URLs (2026-06-15)

| Surface | URL | Status |
|---------|-----|--------|
| Pilot page | https://www.noetfield.com/copilot/pilot/ | Live (marketing) |
| Compliance demo | https://www.noetfield.com/copilot/demo/ | Live |
| GEL local | http://127.0.0.1:8001 | Start: `python3 run.py` |
| GEL hosted | https://api.noetfield.com | Railway `gel-api` |
| SW1 chain tool | `noetfield gate` · `noetfield decide --sample` | `packages/noetfield-gate/README.md` |
| GEL health | `/health` `/readiness` `/v1/meta` | Policy `noetfeld-credit-v1` @ 1.0.0 |

**DNS state:** `www.noetfield.com` is live on Vercel project `noetfield`; `api.noetfield.com` is live on Railway `gel-api`.

---

## 7. Separation law (FM-2)

| On Noetfield calls | Never lead with |
|--------------------|-----------------|
| Copilot Governance Pack · TLE · board PDF · shadow pilot | SourceA · SDK · Temporal · hub · n8n |

**One bridge line max:** “Under the hood, governed execution spine — you buy **Noetfield**.”

---

## 8. Frozen zone (until NW1 + SW1 sent)

- New architecture layers · parallel CRM/n8n stack · whitepaper-first · 20/day outbound automation
- In scope: K1 receipt hardening · W1 film · NW1/SW1 send · GEL export (this repo)

---

## 9. Deal signals on disk

| Code | Proof |
|------|--------|
| **NW1** | First design partner signed / deposit |
| **W1** | Filmed 5-min proof demo |
| **W3** | CAD ≥2K economic signal |
| **SW2** | First Buyer 1 credit card (SourceA lane) |

---

## 10. Parent authority & buyer attach

| Doc | Path | Use |
|-----|------|-----|
| Portfolio SSOT | `~/Desktop/SourceA/SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` | Law |
| NW1 battle card | `~/Desktop/SourceA/NOETFIELD_NW1_BATTLE_CARD_LOCKED_v1.md` | Email body |
| Locked one-pager | `~/Desktop/SourceA/NOETFIELD_FOUNDING_CUSTOMER_PILOT_ONEPAGER_LOCKED_v1.md` | Parent |
| NW1 attach (Copilot) | `docs/_NOOS_AGENT/[NOOS-AGENT-20260615-011]_FOUNDING_PILOT_ONEPAGER_EXTERNAL_v1.md` | NW1 email attach |
| SW1 attach (agents) | `docs/_NOOS_AGENT/[NOOS-AGENT-20260615-013]_FOUNDING_PILOT_ONEPAGER_AGENTS_v1.md` | SW1 outreach |
| NW1 send script | `~/Desktop/SourceA/scripts/send_nw1_single_v1.py` | Mail.app draft |
| Strategy source | `~/Desktop/2 PAGER/SOURCEA_NOETFIELD_STRATEGY_PACK_2026-06-15_v1.md` | Merged here |

**Conflict rule:** LOCKED parent docs win. This doc is **Noetfield OS agent vault** strategy overlay only.
