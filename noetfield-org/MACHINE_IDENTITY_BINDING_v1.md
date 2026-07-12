# Machine Identity — OPERATIONAL BINDING v1

**Document class:** OPERATIONAL_BINDING (not Library SSOT)
**Status:** **INSTALLED + PROVEN (2026-07-12)** — was DESIGN_LOCKED / install PENDING_FOUNDER; the founder gates are now complete (see §7 Activation). Design record below is preserved as authored.
**Language:** English
**Authored:** 2026-07-11
**Owner layer:** NOOS / noetfeld-OS integrator
**Implements:** SG P8 commissioning standard — closes blocker `standing_machine_identity_repo_credential`
**Custody pins:** `CUSTODY_AUTHORITY_PINS_v1.json` (this directory) — pin refresh deferred to integrator lane; this binding is additive and modifies no pinned artifact.

---

## 1. What the machine identity is

The motor's standing identity is an **org-owned GitHub App** (`noetfield-motor`),
not a personal credential. It exists so the motor can act continuously —
push receipts, open PRs, dispatch workflows — as `noetfield-motor[bot]`,
with the founder touched only at real decision gates.

```text
App private key (founder custody, org secret)
  -> App JWT (<=10 min)
    -> installation token (<=1h, scoped)
      -> motor acts on every repo that does the tasks
```

Identity-first: the App's webhook is registered **inactive**. Activating the
event-driven brain later is an App-settings toggle, not a re-registration.

## 2. Credential law (binding)

| Rule | Statement |
|---|---|
| Custody | Private key exists only in org secret `MOTOR_APP_PRIVATE_KEY` and founder's local secrets dir. Never in a repo, receipt, log, or canonical doc. |
| Reference | Canon and code use credential refs only: `MOTOR_APP_ID` (org variable), `MOTOR_APP_PRIVATE_KEY` (org secret). |
| Token life | Installation tokens expire ≤ 1 hour; jobs may down-scope per repo/permission. |
| Actor | Motor-authored commits/PRs/issues use `noetfield-motor[bot]`. |
| Forbidden | Personal access tokens as standing identity; key material in receipts; long-lived tokens; scope wider than the job. |
| Rotation | Key rotation is a founder gate. On rotation: generate new key in App settings, update org secret, revoke old key, record a rotation receipt. |

## 3. Scope (installed on all repos that do the tasks)

Installation target is the `Noetfield-Systems` org — **all repositories**
(or at minimum: `noetfield-sandbox-private`, `noetfeld-os`,
`sina-governance-SSOT`, `TrustField-Technologies`).

Permissions (least privilege, identity-first): `contents:write`,
`pull_requests:write`, `issues:write`, `actions:write`, `checks:write`,
`workflows:write`, `metadata:read`. No webhook events subscribed.

## 4. Runtime surfaces

| Surface | Mint mechanism |
|---|---|
| GitHub Actions | `actions/create-github-app-token@v2` |
| Other runtimes (service host, edge verifier, local tick) | `motor/identity/app_identity.py` adapter (sandbox-private runtime repo) |

Proof workflow: `noetfield-sandbox-private/.github/workflows/motor-identity-proof-v1.yml`
— deterministic COST-T0 / W-DET run whose PASS receipt re-proves the proof1
failed assert (PR creation) under the App identity.

## 5. Commissioning effect

| Blocker (P8 commissioning) | Effect of this binding |
|---|---|
| Standing machine identity / repo credential | **Closed** once founder completes install gates and `motor-identity-proof-v1` passes |
| Durable state store activation | Unaffected (separate blocker) |
| Independent verifier | Enabled to publish `checks:write` under its own token scope |
| Final cold proof runs | Re-run proof1 after install — the PR-creation assert should now pass |

Status remains `NOT_OPERATIONAL` for the motor overall until P8 cold proofs A+B pass.

## 6. Founder gates (account-level, cannot be automated)

1. Register the App via the manifest page (one click, permissions pre-filled).
2. Convert the manifest code (`convert_manifest_code.sh`) — stores credential refs.
3. Install the App on the org (all repositories).
4. Trigger `motor-identity-proof-v1` and judge the receipt.

Schema: `schemas/machine_identity_binding.v1.schema.json` ·
Config example (non-canonical): `config/examples/machine_identity.private.example.yaml` ·
Install receipt: `receipts/NOOS_MACHINE_IDENTITY_BINDING_INSTALL_RECEIPT_2026-07-11.json`

---

## 7. Activation (2026-07-12) — INSTALLED + PROVEN

The four founder gates in §6 are complete. The standing identity is live.

| Fact | Value / evidence |
|---|---|
| App | `noetfield-motor`, **App ID 4275961**, installed org-wide, webhook inactive (identity-first) |
| Credential placement | **repo-level** in `noetfield-sandbox-private` (`MOTOR_APP_ID` var + `MOTOR_APP_PRIVATE_KEY` secret) — the `gh` CLI token lacked `admin:org`; resolves identically in `vars.`/`secrets.` and is tighter than org-wide. Promote later via `gh auth refresh -s admin:org`. Private key secured at `~/.noetfield-secrets/` (600) |
| Cold proof (identity) | `motor-identity-proof-v1` [run 29173419218](https://github.com/Noetfield-Systems/noetfield-sandbox-private/actions/runs/29173419218) — receipt **PASS**; PR opened+closed by `noetfield-motor[bot]`, closing the proof1 assert (Actions token blocked from PRs) |
| Cross-repo proof | [run 29173604498](https://github.com/Noetfield-Systems/noetfield-sandbox-private/actions/runs/29173604498) — SourceB PR #15 by the bot; token scope `[noetfield-sandbox-private, SourceB]` asserted |
| Motor wired on identity | intake / tick / executor (org-wide) / proof / watchdog / panel / commission-selftest all mint `create-github-app-token@v2`; two cold proofs green (runs 29174463135, 29174513162) |
| Permission reconciliation | Binding §3 requested `checks:write`; **actual install grants `statuses:write`** (Commit Statuses). Installed reality wins — `statuses:write` serves the independent-verifier publish intent. The locked instance records `statuses:write` |
| Bundle bugfix | The shipped `motor-identity-proof-v1.yml` lost its receipt on `--delete-branch` (HEAD switch to main); fixed with a `RUNNER_TEMP` stash. Deployed version supersedes the v2 zip's |
| Real locked instance | `config/machine_identity.noetfield-systems.locked.yaml` (status PROVEN, schema-valid) |
| Proven receipt | `receipts/NOOS_MACHINE_IDENTITY_BINDING_PROVEN_RECEIPT_2026-07-12.json` (supersedes the 2026-07-11 install receipt by reference) |

**Still open for full motor commissioning (separate blockers, not identity):** durable state
activation (`MOTOR_DB_URL`/`MOTOR_DB_KEY` — DurableStore code verified against a PostgREST mock,
all CAS conformance PASS) and independent edge-verifier deploy (`MOTOR_EDGE_VERIFIER_URL`). Both
are one command each in `noetfield-sandbox-private/motor/install/FINISH_COMMISSIONING.sh`, confirmed
by `motor-commission-selftest-v1`.

---

*Operational binding v1 — implements SG custody chain; additive; not a substitute for Master SSOT or Library doctrine. Activation §7 appended 2026-07-12; design record §1–6 preserved as authored.*
