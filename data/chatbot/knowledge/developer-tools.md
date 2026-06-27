# Developer tools — chain tools and PyPI

## noetfield-gate (PyPI)

Public Python package: **`noetfield-gate`**

```bash
pip install noetfield-gate
noetfield gate          # local PASS/BLOCK → ~/.noetfield/gate-report-v1.json
noetfield decide --sample   # POST to api.noetfield.com (needs API key)
```

Docs landing: **https://www.noetfield.com/gel/**

Default hosted API: **`https://api.noetfield.com`**

Environment variables:

| Variable | Purpose |
|----------|---------|
| `NOETFIELD_API_URL` | GEL base URL (default `https://api.noetfield.com`) |
| `NOETFIELD_API_KEY` | `X-API-Key` for `/v1/decision` |
| `NOETFIELD_ROOT` | Full repo root when running from `noetfeld-os` checkout |

## PyPI Organization application (public guidance)

When registering a **PyPI Organization** for Noetfield packages:

**Organization description (example):**  
Noetfield Systems builds governable agent infrastructure — pre-execution policy gates, decision receipts, and audit exports. We publish Python CLI tools such as `noetfield-gate` for CI/CD and agent pipelines.

**Anticipated usage (example):**  
Publish Noetfield Python packages under one org account, use GitHub trusted publishing for releases, and add maintainers via org roles as we ship CLI and SDK updates.

This is **operational guidance for founders/developers** — not a contract SKU or pricing commitment.

## npm (planned)

JavaScript wrapper `@noetfield/gate` is on the roadmap; not yet published. Check `/gel/` for current status.

## Studio IDE

Internal/agent workbench (Noetfield Studio IDE) — not a public buyer SKU. Direct enterprise buyers to Copilot Governance Pack or sandbox at `/start/`.
