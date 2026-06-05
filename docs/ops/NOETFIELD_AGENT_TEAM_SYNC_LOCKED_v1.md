# Noetfield agent team sync (LOCKED v1)

| Field | Value |
|-------|--------|
| **Agent tag** | `NF-CLOUD-AGENT` |
| **Agent id** | `noetfield_cloud` |
| **Doc trace** | `NF-CLOUD-BRIDGE-001` |
| **Not** | `NF-LOCAL-AGENT` · `noetfield_local` |
| Status | **LOCKED v1** — cloud-safe bridge (committed) |
| Audience | `noetfield_cloud` + `noetfield_local` |
| Full private canon | `ops/private/agent-reference/` (gitignored — on disk when workspace synced) |
| Updated | 2026-06-06 |

**Purpose:** Cloud agents cannot read `~/Desktop/SourceA` or founder Mac paths. This file is the **minimum committed mirror** so cloud and local stay aligned without publishing `ops/private/`.

---

## Conflict order (authority stack)

On conflict, higher tier wins. Private L4 **never** overrides public LOCKED without ASF.

| Tier | Maps to | Governs |
|------|---------|---------|
| **T0 Law** | L0–L1 public locks | `NORTH_STAR.md`, `PRODUCT_TRUTH.md`, `OFFERINGS_LOCKED.md`, `PROJECT_BOUNDARIES_LOCKED.md` |
| **T1 Ship** | L3 execution | `os/plan.json`, `os/SHIP_NOW.md`, `docs/ops/plans/no-asf/QUICK_PICK.md` |
| **T2 Reference** | L2 diligence | `docs/references/*_LOCKED_v1.md` |
| **T3 Spec** | L2 product | `docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md` |
| **T4 Private** | L4 synthesis | `ops/private/agent-reference/` (scope, reputation, drift, UKE/NKUE) |
| **T5 Archive** | Superseded | `ops/private/agent-reference/archive/` — not for decisions |

---

## Repo truth (verify — do not trust chat memory)

| Topic | Canonical |
|-------|-----------|
| Merge/deploy verify | **`make ship-verify`** |
| `make verify-gtm` | **Does not exist** in `Makefile` |
| PLAN WITH NO ASF queue | **`docs/ops/plans/no-asf/QUICK_PICK.md`** (exists) |
| Next agent plan | **NF-PLAN-0111** (www GTM webhooks) |
| Recently shipped | NF-PLAN-0102 … NF-PLAN-0110 |

When local and cloud chat disagree → **verify on disk** → record fix in private `REPO_TRUTH_CORRECTIONS.md` if `ops/private/` present.

---

## Session start (both agents)

### Cloud (no `ops/private/` or partial)

1. This file
2. [NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md](./NOETFIELD_AGENT_CONTEXT_AND_READ_ORDER_LOCKED_v1.md)
3. [os/plan.json](../../os/plan.json) · [plans/no-asf/QUICK_PICK.md](./plans/no-asf/QUICK_PICK.md)
4. [PROJECT_BOUNDARIES_LOCKED.md](../../PROJECT_BOUNDARIES_LOCKED.md)
5. GitHub Issues if private todolist missing

### Cloud or local (when `ops/private/agent-reference/` on disk)

1. `ops/private/agent-reference/IN_CHARGE_NOW.md`
2. `ops/private/agent-reference/plans/LOCKED_PLANS_INTERNAL.yaml`
3. `ops/private/agent-reference/AGENT_TEAM_STATE.yaml`
4. Then public read order above

---

## Self-healing team protocol

```
CLAIM → VERIFY (test -f, grep, Makefile) → CORRECT → UPDATE REGISTRY → LOG INTAKE
```

| Agent | After ship session |
|-------|-------------------|
| **Local (Mac)** | `make ship-verify` when code touched · Prompt OS ingest · update private `LOCKED_PLANS/` + `AGENT_TEAM_STATE.yaml` · sync SourceA mirror |
| **Cloud** | `make ship-verify` on PR branch · update private files **if on workspace disk** · set `founder_ingest_required: true` in `AGENT_TEAM_STATE.yaml` |

**Cloud cannot:** run founder ingest, edit Desktop SourceA, assume hub :13020.

**Local cannot:** assume cloud PR state without `git fetch`.

---

## Product one-liner

Noetfield = governance execution & AI policy enforcement **before** external execution. No payments, custody, generic AI platform. **Noetfield only** — not TrustField / VIRLUX product work.

---

## Shipped vs roadmap (honest)

| Capability | Status |
|------------|--------|
| TLE, RID, audit-export, confidence factors | Shipped |
| Connector `last_sync`, workspace auth + rate limits | Shipped |
| `observability_*` schema (migration 0008) | Shipped |
| Observability middleware → tables | Roadmap |
| OPA on evaluate | Roadmap |

---

## Private paths (gitignored — not in this commit)

```text
ops/private/agent-reference/
  IN_CHARGE_NOW.md
  NOETFIELD_AUTHORITY_REGISTRY.yaml
  UNIFYING_KNOWLEDGE_ENGINE.md          # alias: NKUE
  NOETFIELD_KNOWLEDGE_UNIFICATION_ENGINE.md
  LOCAL_CLOUD_AGENT_COORDINATION_LOCKED.md
  AGENT_TEAM_PROTOCOL.md
  AGENT_TEAM_STATE.yaml
  CLOUD_LOCAL_PARITY.md
  plans/LOCKED_PLANS_INTERNAL.yaml
  LOCKED_PLANS/
  intake/ · archive/ · REPO_TRUTH_CORRECTIONS.md
```

Founder checklists (stay separate): `ops/private/docs/GO_LIVE_CHECKLIST.md`, `LEGAL_REVIEW_CHECKLIST.md`.

---

## Agent document tags (do not mix agents)

| Agent | Tag | Writes |
|-------|-----|--------|
| **Cloud / repo ship** | `NF-CLOUD-AGENT` | This file, `os/LOCKED_REFERENCE_INDEX.md`, cloud-pass private docs |
| **Mac / local** | `NF-LOCAL-AGENT` | Mac-only private docs — local agent must tag |

Every agent-authored doc includes **Agent tag**, **Agent id**, **Doc trace** (`NF-CLOUD-<AREA>-<NNN>`).  
Private spec: `ops/private/agent-reference/AGENT_DOCUMENT_TAGGING_LOCKED.md` (when on disk).

**Grep:** `rg 'NF-CLOUD-AGENT' docs/ops/ ops/private/agent-reference/`

---

## Drift blueprints (local + cloud)

| Role | Doc | Tag |
|------|-----|-----|
| Taxonomy | `docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md` | existing LOCKED |
| Product | `docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md` | existing LOCKED |
| Hub + 4 supplements | `docs/references/GOVERNANCE_DRIFT_*_BLUEPRINT_*` | `NF-LOCAL-REPO-AGENT` |
| Cloud read order | `docs/ops/NOETFIELD_DRIFT_BLUEPRINTS_CLOUD_READ_ORDER_LOCKED_v1.md` | `NF-CLOUD-AGENT` |
| Code truth | `ops/private/.../NOETFIELD_DRIFT_IMPLEMENTATION_MAP.md` | `NF-CLOUD-AGENT` |

**Pull local blueprints:** `cursor/bank-grade-fullstack-37f0` after push. **Wrong path:** `docs/reference/` → redirect to `docs/references/`.

---

## Knowledge intake (founder batches)

When founder sends rules, essays, governance, or docs:

1. Save under `ops/private/agent-reference/intake/`
2. Run NKUE/UKE pipeline (score → merge → archive → reject)
3. Update registry + this sync doc only if **public** facts change (via ASF)

---

| v1 | 2026-06-06 | Cloud bridge — complements private agent-reference |
