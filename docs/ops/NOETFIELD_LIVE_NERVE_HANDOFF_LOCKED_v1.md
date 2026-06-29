---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-29"
doc_id: noetfield-live-nerve-handoff-locked-v1
status: LOCKED
---

# Noetfield Live Nerve Handoff - LOCKED v1

## Purpose

Noetfield agents, chatbot behavior, and deploy checks must not treat stale static docs or prior chat summaries as live truth.

The current machine truth is:

```text
governance/NOETFIELD_LIVE_NERVE_RECEIPT.json
```

If this receipt is missing or `gate=FAIL`, repair the live nerve before using docs as truth.

## Required First Read

Before implementation work in the website/platform repo:

```bash
make verify-live-nerve
```

Then read:

```text
governance/NOETFIELD_LIVE_NERVE_RECEIPT.json
```

## What The Receipt Proves

- `N1_PUBLIC_OUTPUT`: generated `.vercel/output/static` does not expose internal truth surfaces.
- `N2_CHAT_TRUTH`: public chatbot knowledge is manifest-gated, public, fresh, and hash-matched.
- `N3_DOC_FRESHNESS`: public Markdown exposure is accounted for and raw internal docs are blocked from output.
- `N4_WWW_LIVE_OUTPUT`: live `www.noetfield.com` blocks internal/static truth URLs.
- `N5_WWW_CHAT_SEMANTIC`: live `www` public chat does not return stale source/internal language.
- `N6_PLATFORM_CHAT_SEMANTIC`: direct `platform.noetfield.com` public chat does not return stale source/internal language.
- `N7_GEL_LIVE_RUNTIME`: `api.noetfield.com` health/readiness are live and ready.

## Agent Rule

Use this order:

```text
live nerve receipt -> current source files -> validators -> docs -> chat summaries
```

Do not use:

```text
old reports, stale generated output, raw docs/ops, prior chat summaries
```

as implementation truth unless the live nerve says the relevant source is current.

## Gates

The live nerve is wired through:

```bash
make verify-live-nerve
make verify-static-www
make ship-verify
```

The cross-scope production E2E is:

```bash
make verify-www-e2e
```

The public-output scanner is:

```bash
python3 scripts/verify-public-output-allowlist.py
```

The chatbot truth scanner is:

```bash
bash scripts/verify-public-chat-truth.sh
```
