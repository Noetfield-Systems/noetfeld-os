# NOOS Authority References — commit-pinned

Status: ACTIVE (NOOS operational binding, Claude Code surface)
Authored against this repo @ `638b015e97f4e7e4b5a7c7619d3d3012b89d08e0` (2026-07-10);
custody pins refreshed post-custody-commit (see §7) on 2026-07-10.
Machine-readable pin registry: `noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json`.
Verify all pins with `bash scripts/noos_claude_activation_doctor_v1.sh`.

Pins are historical anchors: they prove what was authoritative when this surface
was installed. A pinned SHA staying resolvable is required; authority moving
forward is expected — reconcile forward, never rewrite pins.

## 1. Master SSOT — sina-governance-SSOT

- Repo: `https://github.com/Noetfield-Systems/sina-governance-SSOT.git`
  · local sibling `~/Desktop/Noetfield-Systems/sina-governance-SSOT`
- Pin: `0e2c1ea2849823a9c642ae4fe4f9ec8e52d5482e` (main — "Install
  founder-reasoning custody chain and Option C advisor absorption",
  2026-07-10; supersedes lineage pin `c280ff7ebf548ff3a1784502a46436fa0e7bf9c0`)
- Anchor files at pin:
  - `ssot/strategy-ssot-v6-split.md` — Level 0 constitution + D1–D5 domain SSOTs;
    stamped REMOTE CANONICAL, LOCKED/CANONICAL (2026-07-05)
  - `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md` — LOCKED (2026-07-02) actor→repo routing;
    NOOS row: role "GEL gate/log/audit + docs/_NOOS_AGENT/", never website source,
    never SourceA default-save
  - `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md` — LOCKED (2026-07-03) lane law L1–L5;
    task cell "NOOS doctrine append" sole writer = noos_agent → noetfeld-os
  - `ssot/noos-doctrine-trustfield-v1.md` — LOCKED **SG mirror only**; canonical
    append lives in this repo's `docs/_NOOS_AGENT/`
- What SG is authoritative for over NOOS: routing, verification, lane law,
  dispatch governance (P0-PGR v1.1, status DECLARED). It routes; it does not build.

## 2. SG Canonical Library

- Location: `SG-Canonical-Library/noetfield-library/` **inside the SG repo** (pinned above)
- Version: **v0.9-SG-RATIFIED** (ratified 2026-07-05, merged 2026-07-06)
- Registry of record: `SG-Canonical-Library/LIBRARY_REGISTRY.json` **in the SG repo**.
  The Desktop-level `~/Desktop/Noetfield-Systems/SG-Canonical-Library/LIBRARY_REGISTRY.json`
  is a stale v0.8 intake record — never resolve authority from it.
- Artifact pins: zip `noetfield-library-v0.9-SG-RATIFIED-2026-07-05.zip`
  sha256 `929d449364c6b4d88931e71f44352953ee243e4cd6e2b6b7e7495ff2d0662cc1`;
  per-file manifest `P99-LEDGER/FILE_MANIFEST_SHA256.json` (143 files).
- Precedence: lower P-number wins (P0 > P1 > … > P99); DISK/SG-registered ACTIVE
  truth beats chat text; repo authority for product lanes beats SG mirror copies.

## 3. FOUNDER_CANON — canonical text

- Canonical: SG library `P1-CANON/FOUNDER_CANON_v1.md` (v1.0, machine_wired),
  committed to sina-governance-SSOT in `6c13aa2765dbb129bc4981da4f25ef1a8a96b84d`
  (2026-07-07).
- The Desktop file `FOUNDER_CANON (1).md` is a stale pre-commit draft (2026-07-03,
  one line behind). Do not cite it as authority.

## 4. Founder reasoning binding — reconciliation record

`docs/_NOOS_AGENT/[NOOS-AGENT-20260703-005]_FOUNDER_CANON_INTERFACE_v1.md`
(Cursor-authored, v1.1, Status ACTIVE) is **preserved as the NOOS operational
binding** of FOUNDER_CANON — an interface, not independent doctrine.
Pin: `c36aaf142719ece6e82dc1490cdac34e53e0885c` (last touch).

Reconciliation (2026-07-10, this surface):
- Its "Upstream canon: Desktop `FOUNDER_CANON (1).md` — full text authority until
  committed to sina-governance-SSOT" clause **has been satisfied**: the commit
  condition was met 2026-07-07 (`6c13aa27`). Upstream authority is now the SG
  library copy in §3. The interface doc text is preserved unmodified; this file
  is the forward pointer.
- Its operative strings remain NOOS law, verbatim (do not "fix" v1 → v1.1):
  - Dispatch line: `LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.`
    (present in all four `.agent-policy/dispatch-templates/*.json`)
  - Receipt stamp: `canon_version: FOUNDER_CANON_v1+MACHINE_LOOPS_v1`
    (present in `data/noos-machine-loops-config-v1.json`)
- Its intent filter (5 questions), authority chain (canon → work order → dispatch),
  failure routing (detect → contain → critique → audit → research → repair →
  validate → receipt → continue), and the three founder touchpoints
  (capital/legal, irreversible L5, phase unlock) bind every Claude Code session here.

## 5. In-repo authority docs (pinned to last-touch commit)

| Doc | Pin |
|---|---|
| `docs/_NOOS_AGENT/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md` | `146e8fe1acee1748cd6b51352e062432e081aa6d` |
| `docs/_NOOS_AGENT/NOETFIELD_OS_SSOT_v1_LOCKED.md` | `146e8fe1acee1748cd6b51352e062432e081aa6d` |
| `docs/_NOOS_AGENT/PRODUCT_TRUTH.md` | `404e4c7193af79b555cdababe8ab668b30e81441` |
| `docs/_NOOS_AGENT/[NOOS-AGENT-20260703-005]_FOUNDER_CANON_INTERFACE_v1.md` | `c36aaf142719ece6e82dc1490cdac34e53e0885c` |

Unpinned but binding in-repo law (versioned by their own LOCKED status):
`docs/GOVERNED_AUTORUN_LAWS_v3.md` (L1–L13 + D1–D8),
`noetfield-org/ROUTING_MATRIX.md` (L17-exclusive tool routing),
`data/noos-motor-executor-wiring-v1.json` (LOCKED_v1 motor wiring),
`data/noos-pr-conflict-skill-lock-v1.json` (PR-conflict law lock),
`noetfield-org/FORBIDDEN_MARKERS.txt` (slug law).

## 6. Known authority-drift facts (recorded, not repaired here)

- SG LOCKED docs still cite `~/Projects/...` paths; actual root is
  `~/Desktop/Noetfield-Systems/`. SG docs are amended only via SG append + receipt.
- `noetfield-org/NOOS_LOCK_RECEIPT_v1.json` is two concatenated JSON objects
  (not machine-parseable as one document).
- `noetfield-org/LOOP_STATE.json` motor fields lag `data/noos-24-7-loops-v1.json`
  (Railway executor is CANONICAL_LIVE since 2026-07-06).
- RESOLVED 2026-07-10: the previously uncommitted SG LOCKED docs (P2 custody
  matrix, P8 continuation/commissioning, P10 cost doctrine) are now committed
  and covered by the `0e2c1ea2` pin — see §7.

## 7. Founder-reasoning custody chain (post-custody pins, 2026-07-10)

The SG and NOOS custody lanes committed the founder-reasoning custody chain.
Machine-readable pins: `noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json` (v1.2.0 —
both repo pins refreshed here after its own "re-pin after commit" notes; every
artifact blob SHA verified at the pinned commits).

- **SG custody pin `0e2c1ea2849823a9c642ae4fe4f9ec8e52d5482e`** carries, verified:
  - Master SSOT `ssot/strategy-ssot-v6-split.md` **§0.7 — Motor escalation
    continuity (99/1)** (also mirrored in the library P0 spine)
  - `P2-SSOT/LIBRARY_CUSTODY_MATRIX_LOCKED_v1.md` and
    `P2-SSOT/AUTHORITY_GRAPH_FOUNDER_REASONING_LOCKED_v1.md`
  - `P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md` §11–§12 (founder-reasoning motor
    terms: `WAITING_FOR_FOUNDER_REASONING`, `COST-T0`/`COST-T1`/`COST-T2`, alias map)
  - `P8-MACHINE-LOOPS/founder-reasoning-continuation-doctrine-LOCKED_v1.md` and
    `P8-MACHINE-LOOPS/MOTOR_COMMISSIONING_AND_ACCEPTANCE_STANDARD_LOCKED_v1.md`
  - `P10-PRODUCT-LAYERS/COST_EXECUTION_DOCTRINE_LOCKED_v1.md`
  - Custody receipts `receipts/custody/CUSTODY_ABSORPTION_ADVISOR_PACKAGE_OPTION_C_v1.json`,
    `receipts/custody/CUSTODY_WIRING_FOUNDER_REASONING_v1.json`, and verifier
    `scripts/verify_founder_reasoning_custody_chain_v1.py` (all SG-repo paths)
- **NOOS operational custody pin `c7f39ff39e971a6e10f3bd97e57c16d79d59652a`**
  (this repo's main; parent of the activation commit) carries, verified:
  - `noetfield-org/FOUNDER_REASONING_MOTOR_OPERATIONAL_BINDING_v1.md`
    (OPERATIONAL_BINDING, LOCKED — implements SG §0.7 + D5; not Library SSOT)
  - `noetfield-org/schemas/SCHEMA_INDEX_v1.md` + the four motor schemas
    (founder_reasoning_packet / founder_reasoning_result / motor_job_contract /
    private_worker_binding, all v1)
- Staleness law: if either upstream main moves past its pin, refresh pins +
  wiring receipt before claiming custody compliance — the activation doctor
  reports stale pins loudly and refuses a clean PASS.
