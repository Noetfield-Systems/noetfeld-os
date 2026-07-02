# Production environment — P4 prep (founder enables in GitHub UI)

Status: **PREP ONLY** — `deploy-noos-cloud-workers-v1.yml` uses `environment: production`; enforcement inactive until founder completes P4.

## Founder steps (≈5 min)

1. GitHub → **Settings** → **Environments** → **New environment** → name: `production`
2. Enable **Required reviewers** → add founder account (mobile approval)
3. Optional: deployment branch rule → `main` only
4. Re-run `deploy-noos-cloud-workers-v1` workflow_dispatch to confirm approval prompt

## Sequencing law (spec §7)

P4 (this) before P7 (Copilot Kaizen pilot).

## Hand-rolled code retired when active

| Before | After |
|--------|-------|
| Agent/deploy scripts run without founder gate | CF worker deploy blocked until founder approves in GitHub mobile UI |
| Deploy truth inferred from local shell receipts | Environment deployment URL is admissible deploy evidence |
