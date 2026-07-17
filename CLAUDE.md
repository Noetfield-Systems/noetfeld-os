# CLAUDE.md — noetfeld-OS (NOOS) · Claude Code activation surface

NOOS is the Noetfield **execution and integration control plane**: it turns
governance canon into running loops, lanes, routing, and receipts, and it
integrates the Noetfield-Systems repos through registries and receipts — it
does not own product definition (SG canon), buyer UX (Noetfield.com), or
delivery implementation (SourceA). Custody chain: **Master SSOT anchors →
SG Library defines → NOOS operationalizes → product runtime executes →
verifier proves.**

## Session start (in order)

1. This file, then `AGENTS.md` (shared agent canon — surface-neutral, binding).
2. Before ANY broad read: `graph-out/GRAPH_REPORT.md` (L0 broad-read gate),
   then `python3 scripts/query_repo_graph_v1.py <term>`. Never blind-scan the repo.
3. On demand:
   - `.claude/noos/SYSTEM_IDENTITY.md` — what NOOS is, owns, and must not own
   - `.claude/noos/AUTHORITY.md` — commit-pinned authority references
   - `.claude/noos/RUNTIME_MAP.md` — the motor, mapped (never redesigned)
   - `.claude/noos/PROJECT_RULES.md` — full working rules for this repo

## Hard rules (non-negotiable)

- **Claim before edit (L-P5).** Before mutating shared paths:
  `make local-lane TASK=NOOS-LANE-<id> SCOPE=path1,path2` (or
  `AGENT_ID=claude-code-noos IDE=claude-code bash scripts/noos_local_claim_lane_v1.sh <task-id> <paths...>`).
  Heartbeat sessions >20 min (`make local-heartbeat TASK=<id>`); close out with
  `make local-closeout TASK=<id>` — never leave stale claims (L-P7).
- **Merge conflicts are LOCKED law.** Load `.cursor/skills/pr-conflict-resolver/SKILL.md`
  before touching any conflict; classify each file (registry/receipt/LOCKED/generated/code);
  never blind `--ours`/`--theirs` on `data/*.json`, `receipts/proof/`, `*_LOCKED.md`;
  validate with `python3 scripts/verify_pr_conflict_resolution_v1.py --json` and write a receipt.
- **Verifier freeze (L5).** Never edit `scripts/verify_*`, laws docs, `data/*.json`
  registries/locks, `noetfield_gate/`, or Supabase migrations without a founder gate.
  A failing agent fixes the system, never weakens the test.
- **Receipts, not prose.** Proof-grade receipts live in `receipts/proof/` only.
  Builders write **"SUBMITTED for independent verification"** — PASS/DONE verdicts
  come only from deterministic gates or independent verifiers (author ≠ subject).
  No DONE claim without a receipt_id.
- **The motor is not yours to redesign.** Wiring is LOCKED
  (`data/noos-motor-executor-wiring-v1.json`). Map it, verify it, never rebuild it.
- **Runtime separation.** NOOS is not TrustField, not SourceA, not the public site.
  No product-file imports unless a documented interface; connect via contracts,
  exports, and manifests only.
- **Slug law.** The legacy org slug (see `noetfield-org/FORBIDDEN_MARKERS.txt`)
  must never appear in active config. Current org slug: `Noetfield-Systems`.
- **Founder gates.** Deploy, merge to main, spend, external/commercial sends,
  L5/verifier changes, schema/governance (T3-class) merges, and phase unlocks
  are founder-gated. Failures route to the scheduled loops (`make machine-reconcile`),
  never to the founder by default.
- **Dispatched work carries the canon line verbatim:**
  `LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.`
  Receipts carry `canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1`.

## Authority (pinned — full detail in `.claude/noos/AUTHORITY.md`)

| Authority | Where | Pin |
|---|---|---|
| Master SSOT (incl. §0.7) | `sina-governance-SSOT` (sibling repo) `ssot/strategy-ssot-v6-split.md` | `dc6080d8` |
| SG Library | `SG-Canonical-Library/noetfield-library` in the SG repo | `v0.9-SG-RATIFIED` |
| FOUNDER_CANON | SG library `P1-CANON/FOUNDER_CANON_v1.md` | `6c13aa27` |
| Custody chain (machine-readable) | `noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json` | NOOS `a4bdf1f3` |
| NOOS canon binding | `docs/_NOOS_AGENT/[NOOS-AGENT-20260703-005]_FOUNDER_CANON_INTERFACE_v1.md` | `c36aaf14` |
| Unified Master + Product SSOT | `docs/_NOOS_AGENT/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md` · `NOETFIELD_OS_SSOT_v1_LOCKED.md` | `146e8fe1` |
| Autorun laws | `docs/GOVERNED_AUTORUN_LAWS_v3.md` (L1–L13, D1–D8) | in-repo |
| Tool routing | `noetfield-org/ROUTING_MATRIX.md` (L17-exclusive) | in-repo |

NOOS canonical doctrine appends happen only in this repo (`docs/_NOOS_AGENT/`);
the SG copy is a LOCKED mirror. Never author NOOS doctrine in the SG repo.

## Agents

- `noos-architect` — authority reconciliation, binding/doc design, control-plane structure
- `noos-integrator` — integrator sync, claims/conflicts, org-sync receipts, lane state

## Verify this surface

`bash scripts/noos_claude_activation_doctor_v1.sh` — instruction-load + authority
doctor; writes `receipts/noos-claude-activation-doctor-<UTC>.json`, exits non-zero on FAIL.
