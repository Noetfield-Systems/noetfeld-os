# Staging & buyer demo path

## Local (founder Mac)

```bash
cd ~/Desktop/Noetfield
make bootstrap    # once
make dev-local
make verify-local-dev
make tle-smoke
make copilot-pilot-e2e
./scripts/seed-m365-evidence-stub.sh
```

| URL | Purpose |
|-----|---------|
| http://localhost:13080/ | Homepage v1.2 |
| http://localhost:13080/cognitive-dashboard | Evaluate intent |
| http://localhost:13080/workspace | Trust Ledger |
| http://localhost:13080/workspace/connectors | M365 connector (dev OAuth) |
| http://localhost:13080/copilot/pilot/ | Design-partner pilot + program |
| http://localhost:13080/copilot/ | Copilot hub (GTM one-liner) |
| http://localhost:13080/copilot/demo/ | 5-minute GTM demo script |
| http://localhost:13080/trust-ledger/sample-report/ | TLE YAML downloads |
| http://localhost:13080/copilot/ | Copilot pack |

### Workspace roles (local)

```bash
export NF_DEV_ROLE=viewer          # API: read/export only; approve → 403
export NEXT_PUBLIC_NF_DEV_ROLE=viewer   # Next workspace: hide approve buttons
make dev-local
```

## Staging deploy (founder-only detail)

Private checklist (if bootstrapped): `ops/private/docs/GO_LIVE_CHECKLIST.md`

Public references (link only — no secrets in repo):

| Doc | Use |
|-----|-----|
| `docs/ops/RENDER_STAGING.md` | Render service checklist (if present) |
| `docs/MSB_DEPLOY_AND_PILOT.md` | MSB pilot deploy notes |
| Cloudflare / DNS | Per founder ops vault |

**Render checklist (summary):**

1. Create web service from `cursor/bank-grade-fullstack-37f0` branch.
2. Set env: `DATABASE_URL`, `NF_PUBLIC_BASE_URL`, `NF_M365_MOCK_TOKEN` (staging vault only).
3. Build: governance-console backend + Next workspace per existing deploy doc.
4. Health: `GET /health` returns 200.
5. Smoke: `make staging-smoke` or `NF_STAGING_URL=https://… ./scripts/staging-smoke.sh`

Agents: document code changes here; do not paste secrets. Deploy secrets stay in founder vault only.

## PR / pre-merge checklist (NO ASF)

Before merging `cursor/bank-grade-fullstack-37f0` (or opening demo PR):

- [ ] `pytest governance-console/backend/tests/test_tle_flow.py -q`
- [ ] `make verify-local-dev && make tle-smoke && make copilot-pilot-e2e`
- [ ] `reports/cursor-reply-latest.txt` ingested (`ingest-cursor-reply.sh noetfield`)
- [ ] If staging URL available: `export NF_STAGING_URL=… && make staging-smoke`
- [ ] No secrets in diff (`.env`, tokens, production `DATABASE_URL`)

## Share demo in 2 commands (local tunnel)

```bash
make dev-local
make dev-local-tunnel-bg && make demo-url
```

Prints a public HTTPS URL + `/copilot/demo/` path. For staging: `export NF_STAGING_URL=https://… && make demo-url`.

## Smoke before demo

```bash
make verify-gtm
```

Runs pytest, `verify-local-dev`, `verify-ui-e2e`, `copilot-pilot-e2e`, and `procurement-pack-e2e`. Then `make demo-url` for the shareable link.

**NO ASF verify bundle:** `./scripts/plan-with-no-asf-verify.sh` includes `scripts/verify-demo-url.sh` when the dev stack is up (SKIP if no tunnel or `NF_STAGING_URL` configured).

```bash
python3 scripts/validate-tle-samples.py
```

## Optional public staging smoke

```bash
export NF_STAGING_URL="https://your-staging-host"
make staging-smoke
```
