# NOOS System Identity — Claude Code binding

Status: ACTIVE (NOOS operational binding, Claude Code surface)
Scope: identity only — authority pins live in `AUTHORITY.md`, rules in `PROJECT_RULES.md`.

## What NOOS is

NOOS (noetfeld-OS) is the Noetfield **execution and integration control plane**.
It is the DELIVERY-lane runtime-control repo of the Noetfield-Systems org:

- **Execution plane** — it hosts the loop motor's code and doctrine
  (CF clock → Railway executor → receipts → Supabase sink), the machine loops
  (worker / critic / repair / research / audit), the gate runtime
  (`noetfield_gate/`, GEL decisioning prototype), and the governed-autorun laws.
- **Integration plane** — it is the org's coordination anchor: repo/agent
  registries, routing matrix, service lanes, loop state, sync receipts
  (`noetfield-org/`), plus the local multi-agent integrator protocol
  (`scripts/noos_integrator_sync_v1.py`, claims, heartbeats, mutex groups).
- **Receipt custodian** — proof-grade evidence lands in `receipts/proof/`;
  cross-repo sync lands as receipts and registry rows, never as new doctrine.

## Place in the custody chain

```
Master SSOT (sina-governance-SSOT)  — anchors constitution + routing law
        ↓
SG Canonical Library (P0…P99)       — defines canon, doctrine, machine loops
        ↓
NOOS (this repo)                    — operationalizes: loops, lanes, gates, receipts
        ↓
Product runtime                     — executes (api.noetfield.com runtime truth)
        ↓
Independent verifier                — proves (external CI, deterministic gates)
```

Constitution invariant 0.7 binds its motor-escalation continuity to this repo's
`noetfield-org/` directory (commit-pinned) — NOOS is the operational binding of
the constitution's continuity law.

## What NOOS owns

- `gel_runtime` — gate/log/audit runtime and its control process
- `docs/_NOOS_AGENT/` — NOOS canonical doctrine vault (sole append authority:
  `noos_agent` lane; the SG copy is a LOCKED mirror)
- The 24/7 loop fleet configuration and its receipts
- Org-sync control files under `noetfield-org/`
- Local task arbitration state for parallel IDE agents on this Mac

## What NOOS must NOT own

- **Product definition** — SG canon (sina-governance-SSOT + SG Library)
- **Buyer UX / website source** — Noetfield.com (`must_not_own: noetfield_website_source`)
- **Delivery implementation** — SourceA (never default-save there:
  `must_not_own: sourcea_default_save`)
- **TrustField** architecture, deploy, compliance, or messaging
- **Founder decisions** — capital/legal, irreversible L5, phase unlocks

## Identity facts a session must not confuse

- Repo name is `noetfeld-OS` (no "i" in noetfeld); the org-sync directory inside
  it is `noetfield-org/` (with "i"). Both spellings are correct where they stand.
- This checkout may be a worktree (e.g. `noetfeld-OS-claude-noos`) of the
  canonical local repo `~/Desktop/Noetfield-Systems/noetfeld-OS`, same origin
  `https://github.com/Noetfield-Systems/noetfeld-OS.git`. One-writer law (L1)
  applies across worktrees — claim lanes before editing shared paths.
- NOOS coordinates; it does not poll on timers from chat sessions. State updates
  happen on explicit ticks/reports through the motor, not through ad-hoc loops.
- This repo is `[DELIVERY]` plane. Do not merge it into SinaaiRuntime `:8000`.
