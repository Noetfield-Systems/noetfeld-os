# UOS-RI v1.0 — live commissioning (existing Runtime only)

**Owner:** Company OS supervision adapter. **Execution:** existing Runway Runtime / MOTOR. **Model choice:** existing HDIR provider adapters. No replacement queue, receipt authority or worker is created here.

## Mission

Prove one authorized WorkPacket from intake to execution read-back without treating model text, fake HTTP responses, an API usage counter or a green deployment as success. This implementation adds a **live-only commissioning CLI and regression tests**; it does not claim an E2E production pass until a real run is recorded.

## Command

Create a private JSON file with the existing canonical intake fields: `tenant_id`, `entitlement_id`, `runway_id`, `recipe_id`, `recipe_version`, `idempotency_key` (at least 16 characters), `budget_usd` (positive authorized number) and `input` with the actual allowed recipe payload. Do not commit this input or any credentials. The adapter sends the **same** WorkPacket to the existing `POST /v1/intake`, then reads the exact job through `GET /v1/jobs/{id}`, `GET /v1/jobs/{id}/events` and `GET /v1/jobs/{id}/result`.

Environment on the executor that already operates the Company OS adapter:

- `NOETFIELD_RUNWAY_API_URL` — authorized HMAC runtime gateway
- `NOETFIELD_RUNWAY_API_SECRET` — existing HMAC secret
- `NOETFIELD_RUNWAY_API_KEY_ID` — corresponding key ID

Run:

```sh
python3 scripts/noos_uos_ri_commission_v1.py \
  --packet /secure/authorized-workpacket.json \
  --checks 24 --poll-seconds 10 \
  --output .noos-runtime/uos-ri/commissioning-observation.json
```

The output is a **sanitized local observation**, not a new canonical job ledger. The command exits nonzero unless an independent verification receipt with a distinct verifier identity and artifact checksum is read back. No arbitrary Founder's approval is requested for a previously authorized, bounded packet.

## What is and is not proved

| Check | Evidence requirement |
| --- | --- |
| HMAC configured | Existing supervisor preflight (configuration only) |
| Runtime dispatch | An actual returned Runtime job ID |
| Repeated intake | Same idempotency key returns the same job ID, not another job |
| Job terminal | Authenticated Runtime readback shows a terminal state |
| Model used | Actual model identity and token usage reported in result (not billing proof) |
| Independent acceptance | Separate verifier identity, distinct builder, PASS verdict and SHA-256 artifact digest |
| Billed cost | Explicit reconciled billing record; otherwise `null`, **never zero** |
| Realized ROI | Only attributed realized economic benefits and measured costs; currently `null` |
| Worker crash/restart recovery | **Not proved** by repeated intake; requires controlled worker interruption + durable lease/claim readback |
| HDIR remote model route | **Not proved** by this CLI alone; requires configured live HDIR and same WorkPacket's provider lineage |

**Fail-closed rules:** missing HMAC, missing job ID, a different replay job ID, unreadable events/results, an unverified receipt or a pending job never receives a successful E2E verdict.

The model pin in Company OS `data/noetfield-runway-contract-v1.json` now uses official `deepseek-flash` (the current V4.1 Flash API alias). This is distinct from confirming a real paid call.

## Commissioning acceptance

1. Run the new contract tests in the GitHub UOS-RI workflow.
2. Enable HDIR live provider in an authorized execution environment with its inference-only secret; observe provider request ID and usage. Do not route credentials through browser UI.
3. Execute a scoped, approved WorkPacket using the existing Company OS HMAC adapter and Runtime. Save the sanitized observation and canonical Runtime job/receipt references.
4. Reconcile provider billing to receipt and measured runtime costs; only compute cost per verified success after multiple independently verified outcomes.
5. Test a controlled restart during a leased task. Check that the same idempotency key maps to one external effect and that the durable executor resumes or reaches a safely classified terminal state.

**Status at code merge:** proof-path tooling ready for live commissioning, not a claimed live end-to-end success.
