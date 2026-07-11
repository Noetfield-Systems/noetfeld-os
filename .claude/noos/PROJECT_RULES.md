# NOOS Project Rules — Claude Code surface

Status: ACTIVE (NOOS operational binding, Claude Code surface)
These restate, for Claude Code, the rules Cursor sessions get from
`.cursor/rules/*.mdc` and `.cursor/hooks.json` (which Claude Code does not load).
The canonical law texts stay where they are — this file binds, it does not fork.

## Session flow

1. `git status --short`; confirm branch; classify any dirty files as
   COMMIT | RESTORE | DELETE | SNAPSHOT | QUARANTINE | LEAVE before working.
2. State the target lane. Lane cap 20–40 files, **one atomic commit per coherent lane**.
3. Claim before edit (L-P5): `make local-lane TASK=NOOS-LANE-<id> SCOPE=path1,path2`
   or `AGENT_ID=claude-code-noos IDE=claude-code bash scripts/noos_local_claim_lane_v1.sh <task-id> <paths...>`.
   Run `python3 scripts/noos_agent_conflict_check_v1.py --json` before parallel work —
   exit 1 means another non-stale agent owns the scope; do not proceed silently.
4. Heartbeat long sessions: `make local-heartbeat TASK=<id>` (claims stale at 30 min).
5. Closeout (L-P7): validators/tests pass → `bash scripts/check_noos_clean_tree.sh` →
   `make local-closeout TASK=<id>`. Never leave stale claims.

## Edit walls

- Direct chat edits: ≤5 files / ≤200 lines. Larger changes route through the
  worker kernel (`make local-patch-proposal`); patches land only under
  `.noos-runtime/worker-kernel/patches/`.
- Forbidden edit targets without founder gate: `scripts/verify_*`, laws docs
  (`docs/GOVERNED_AUTORUN_LAWS_v3.md`), `data/*.json` registries and locks,
  `noetfield_gate/`, `.github/CODEOWNERS`, Supabase migrations.
- No force push. No direct main mutation without PR + approval. No retroactive
  mutation of the `receipts/proof/` archive. Commit before deploy (L6).
- Do not commit run-patch execution churn from `docs/run_patches/execution/*`;
  treat generated/evidence outputs as snapshot + manifest.

## Conflict law (MANDATORY, LOCKED)

Before resolving any merge conflict or UU file: load
`.cursor/skills/pr-conflict-resolver/SKILL.md`; classify every conflicted file as
registry | receipt | LOCKED | generated | code; STOP on duplicate-ownership or
LOCKED canon; never blind `git checkout --ours/--theirs` on `data/*.json`,
`receipts/proof/`, `*_LOCKED.md`; never commit conflict markers; validate with
`python3 scripts/verify_pr_conflict_resolution_v1.py --json`; write
`receipts/proof/noos-pr-conflict-resolution-<UTC>.json` before claiming merge-ready.
Verify wiring: `make pr-conflict-verify`.

## Vault discipline (docs/_NOOS_AGENT/)

- Read order for orientation: `[NOOS-AGENT-20260608-005]_ORIENTATION_START_HERE.md`;
  cross-check the stale-doc register `[NOOS-AGENT-20260706-032]` before executing
  older plans.
- Every new vault doc needs a `NOOS-AGENT-DOC` comment block, a
  `[NOOS-AGENT-YYYYMMDD-NNN]_` filename, and a 4-key row
  (`trace_id, path, doc_type, title`) appended to `docs/_NOOS_AGENT/MANIFEST.json`
  (bump `updated_at`). Validate: `bash scripts/check_noos_agent_docs.sh`.
- Other repos' agents never edit this vault; this repo's agents never author
  NOOS doctrine in the SG repo (SG holds a LOCKED mirror).

## Truth and vocabulary

- Truth order: Live SSOT → repo state → dispatch → receipt → chat. Hidden state
  is a wall violation.
- Builders write **"SUBMITTED for independent verification"**. PASS / FAIL /
  BLOCKED verdicts come only from deterministic gates or independent verifiers
  (author ≠ subject). No DONE without receipt_id. Absence of a receipt = FAIL.
- Before claiming live/local/online state:
  `bash scripts/check_noos_live_sync_gate.sh` (scope with
  `NOOS_LIVE_SYNC_SCOPE=runtime|public|studio|foundation|ecosystem|all`).
  DEGRADED ≠ fully green — say so.
- Founder-blocked items are surfaced, never processed or cancelled (L7).

## Tier vocabulary — disambiguate or contradict

Three different "T0–T3" scales coexist. Name the scale when you use one:

| Scale | Source | Meaning |
|---|---|---|
| Executor tiers | `noetfield-org/ROUTING_MATRIX.md` | T0 GH Actions · T1 Copilot · T2 Cursor/local Mac · T3 reasoning/advisory |
| Model-cost tiers | `config/model-router.yml` | T0 deterministic $0 · T1 cheap · T2 bounded patch · T3 premium (founder token) |
| Merge change-classes | `data/noos-machine-loops-config-v1.json` | T0 docs/tests · T1 scoped code · T2 deps/config (+critic) · T3 schema/governance (founder only) |

A Claude Code session doing local work operates as a T2-class executor
(local Mac surface) under the routing matrix.

## Public surface gate

Research/audit findings never ship to noetfield.com or bulk HTML without the
verdict pipeline; P1+ copy/IA changes are founder-gated. Machine outputs go to
`receipts/proof/` or `docs/_NOOS_AGENT/` only.

## Machine loops (route failures here, not to the founder)

`make machine-status` · `make machine-reconcile` · `make machine-audit` ·
`make machine-validate-merge` · `make machine-critic RECEIPT=...` ·
`make machine-research QUESTION="..."`. Failure flow: detect → contain →
critique → audit → research → repair → validate → receipt → continue.
Founder touchpoints are only: capital/legal, irreversible L5, phase unlock.

## Delegation (L-P4)

Do not re-run from chat what a registered machine owns: trigger sweeps, curl
smokes, `autorun_status`, determinism gates (see `delegates_machine_to` in
`data/noos-parallel-agent-registry-v1.json`). Read their receipts instead.
