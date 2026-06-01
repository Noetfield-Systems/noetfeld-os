# Auto-Conflict Engine v3 — Layer sovereignty (baseline doctrine)

**Status:** Baseline architecture doctrine for Noetfield + Sina ecosystem work.  
**Not:** A build plan, registry edit, or freeze on runtime evolution.

---

## Core principle

No single layer owns all truth. Each layer owns a different truth domain.  
They are **co-equal** — connected by **alignment artifacts** and **binding contract clauses**, not by hierarchy.

```text
  DESIGN (SSOT)     EXECUTION (Runtime)     DELIVERY (Repo)
         \                 |                    /
          \                |                   /
           -------- Alignment layer ----------
```

---

## Three planes

### Layer 1 — DESIGN (SSOT)

**Owns:** intent, boundaries, naming, definitions, ecosystem structure, long-term *target* architecture.  
**Question:** *What should exist?*  
**Does not own:** running processes, deployments, runtime state, product releases.

### Layer 2 — EXECUTION (Runtime)

**Owns:** running services, agents, live ports, DBs, queues, infrastructure state, actual behavior.  
**Question:** *What actually exists right now?*  
**Does not own:** ecosystem definitions, product positioning, registry structure.

Runtime is **authoritative for reality**. Divergence from SSOT ideal is not automatically “debt” — only **contract or boundary breaks** are critical.

### Layer 3 — DELIVERY (Repo)

**Owns:** product code, CI/CD, releases, features, public docs, product APIs.  
**Question:** *What is being shipped?*  
**Does not own:** ecosystem architecture, SSOT definitions, runtime observations.

**[DELIVERY]** Noetfield GitHub may ship without waiting for mono registry or ANNOUNCEMENT_BOARD. Registry **records** execution; it is a **ledger**, not a gate (G5 replacement).

---

## Binding contract (SSOT ↔ Repo)

| Clause | DESIGN / mono | DELIVERY (this repo) | On conflict |
|--------|---------------|----------------------|-------------|
| **C1 — Public product scope** | Aligns to governance pre-execution | **`PRODUCT_TRUTH`, `POSITIONING`, `OFFERINGS_LOCKED` govern product scope** | Delivery locks for www/API/GTM; SSOT for ecosystem map |
| **C2 — Executable instance** | Mono path may be docs-only | GitHub repo is the shipping product | Dual instance until ASF registers bridge |
| **C3 — Standalone** | Noetfield ≠ Runtime submodule | Separate git remote | Both true |
| **C4 — Topology** | Ideal spine (e.g. :8000 in mono) | Regimes: `platform` :8001, `console-mvp` :8000 | Label regime in docs; SSOT = target |
| **C5 — Agents** | No structural SSOT edits | Implement under locks + Issues | Agents never edit Desktop SourceA |
| **C6 — LLM** | G8 cloud-first (mono ops) | Prod = OpenRouter/Gemini; Mac Ollama = dev only | Environment-scoped |
| **C7 — Truth updates** | ASF → registry → board (mono structure) | ASF → PR → public locks (product) | Two valid paths |

Operational summary: `ops/private/sourceA/NOETFIELD_REPO_ALIGNMENT.md` (gitignored mirror).

---

## Conflict resolution rules

**Rule 1 — SSOT vs Runtime**  
Do not assume Runtime is wrong. Log a **drift record** (status, owner). Example: SSOT target = one spine; Runtime = four services → *Accepted drift, owner: Runtime*.

**Rule 2 — Repo vs SSOT**  
If **boundary** violated → **Conflict** (Type C). If boundaries preserved → **Evolution**, not conflict.

**Rule 3 — Runtime vs Repo**  
Runtime wins for **reality**; Repo wins for **intent-to-ship**. Feature in repo but not deployed is normal, not contradiction.

**Rule 4 — Criticality**  
Only boundary violations are critical (e.g. Noetfield as Runtime submodule, payment routing on public surface, `PRODUCT_TRUTH` breach). Ports, extra services, PM2 names, temporary drift → non-critical unless contract broken.

---

## Drift classification

| Type | Meaning | Examples |
|------|---------|----------|
| **A — Informational** | No action | Naming, port, deploy drift |
| **B — Structural** | ASF review | New subsystem, product class |
| **C — Boundary** | Immediate review | Identity collapse, authority collapse, ecosystem breach |

---

## Agent rules (deterministic)

| ID | Rule |
|----|------|
| R1 | In Noetfield GitHub → sovereign = **DELIVERY** (locks + alignment note). |
| R2 | In SinaaiMonoRepo → sovereign = **DESIGN** + **EXECUTION**. |
| R3 | SSOT does not veto repo merge/CI unless **C1** or boundary broken. |
| R4 | Runtime is reality; SSOT ideal is for gap documentation, not shame. |
| R5 | Label “debt” only when contract, boundary, or safety broken. |
| R6 | Registry **records** promotions; optional sync when GitHub is canonical instance. |
| R7 | Docs name topology **regime** (`mono-spine`, `platform`, `console-mvp`). |
| R8 | Desktop SourceA = read-only for agents; ASF edits only. |
| **R9** | Cross-plane statements must declare plane tag: `[DESIGN]` `[EXECUTION]` `[DELIVERY]`. |

**R9 example**

```text
❌  Noetfield is docs-only.                    (ambiguous)

✅  [DESIGN]  Mono noetfield path is docs-only.
✅  [DELIVERY] Noetfield GitHub product is executable.
```

Agents may: ship, refactor, deploy, improve, propose.  
Agents may not: redefine SSOT, redefine product identity, rewrite boundaries, declare registry promotions.

---

## Alignment layer (bridge artifacts)

Layers do not write into each other. Artifacts synchronize:

| Artifact | Role |
|----------|------|
| `PRODUCT_TRUTH.md` | Delivery — public product scope |
| `docs/strategy/auto-conflict-engine-v3.md` | This doctrine |
| `ops/private/sourceA/NOETFIELD_REPO_ALIGNMENT.md` | C1–C7 operational bridge |
| `ops/private/DRIFT_REGISTER.md` | Optional; Type A/B/C drift log (founder) |
| Desktop `SINA_OS_SSOT_LOCKED.md` | Design — ASF only |
| Phase 1 forensic / runtime audit | Execution — observed disk |

---

## Success condition

- SSOT describes intent.  
- Runtime describes reality.  
- Repo describes delivery.  
- Differences are **visible** and **labeled**.  
- Boundaries stay intact.  
- Velocity stays high.  
- No forced architectural freeze.  
- No fake single source of truth.

From here: **execute and learn** — naming, registry sync, and phase labels are hygiene, not architectural contradiction.
