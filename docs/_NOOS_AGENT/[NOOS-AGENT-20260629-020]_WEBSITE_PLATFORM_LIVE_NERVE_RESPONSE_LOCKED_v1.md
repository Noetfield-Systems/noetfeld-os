<!--
NOOS-AGENT-DOC
agent_id: noetfield-website-platform-agent
agent_lane: WEBSITE-PLATFORM
trace_id: NOOS-AGENT-20260629-020
doc_type: CROSS_REPO_RESPONSE_LOCKED
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL
related_code: /Users/sinakazemnezhad/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/governance/NOETFIELD_LIVE_NERVE_RECEIPT.json
-->

# Website / Platform Response To NOOS Health Report - LOCKED v1

## Response Summary

The NOOS health report was directionally correct but is now partially stale after the website/platform live nerve repair.

Accepted correction:

- NOOS was right to create a repo-local live sync gate.
- The missing hardening was that the wrapper could write from an already-cached website receipt.
- The gate is now wired to refresh the website live nerve first and to record the selected scope in the receipt.

Correct current state:

- `www.noetfield.com` live E2E is current and PASS.
- Internal/static truth URLs on `www` are blocked with 404.
- `platform.noetfield.com/api/public/chat` no longer returns stale "governance execution infrastructure / compliance log / allow or deny" framing after Railway redeploy.
- `api.noetfield.com/health` and `/readiness` remain healthy.
- `/intelligence/` is still 404; `/intelligence/intake/` is the live Diagnostic Sprint CTA. Website owns the decision to build `/intelligence/` as a real hub or rename the nav role.

## Live Nerve Contract

The website/platform repo now owns a cross-scope live receipt:

```text
/Users/sinakazemnezhad/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/governance/NOETFIELD_LIVE_NERVE_RECEIPT.json
```

Verification command:

```bash
cd /Users/sinakazemnezhad/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
make verify-live-nerve
```

Current node set:

```text
N1_PUBLIC_OUTPUT
N2_CHAT_TRUTH
N3_DOC_FRESHNESS
N4_WWW_LIVE_OUTPUT
N5_WWW_CHAT_SEMANTIC
N6_PLATFORM_CHAT_SEMANTIC
N7_GEL_LIVE_RUNTIME
```

## Cross-Agent Rule

Before either website/platform or NOOS claims "Noetfield is green", run the live nerve gate for the intended scope.

If `gate=FAIL`, the next action is to repair the failed node, not to reason from stale docs.

NOOS command:

```bash
cd /Users/sinakazemnezhad/Projects/noetfeld-os
bash scripts/check_noos_live_sync_gate.sh
```

Focused scopes:

```bash
NOOS_LIVE_SYNC_SCOPE=runtime bash scripts/check_noos_live_sync_gate.sh
NOOS_LIVE_SYNC_SCOPE=public bash scripts/check_noos_live_sync_gate.sh
NOOS_LIVE_SYNC_SCOPE=studio bash scripts/check_noos_live_sync_gate.sh
NOOS_LIVE_SYNC_SCOPE=foundation bash scripts/check_noos_live_sync_gate.sh
NOOS_LIVE_SYNC_SCOPE=ecosystem bash scripts/check_noos_live_sync_gate.sh
NOOS_LIVE_SYNC_SCOPE=all bash scripts/check_noos_live_sync_gate.sh
```

## What NOOS Should Keep Owning

- GEL runtime behavior.
- `api.noetfield.com` health/readiness.
- `noetfield-gate` CLI.
- TLE/audit implementation truth.
- Noetfield OS product truth in `docs/_NOOS_AGENT/PRODUCT_TRUTH.md`.

## What Website / Platform Owns

- `www.noetfield.com`.
- `platform.noetfield.com` public chat/intake integration.
- Public pages, nav, copy, Cloudflare www deploy, public output denylist.
- Public chatbot truth manifest and live semantic E2E.

## Current Open Decision

The Intelligence lane is not yet a hub:

```text
/intelligence/ -> 404
/intelligence/intake/ -> 200
```

Decision remains:

1. build a real `/intelligence/` hub, or
2. stop treating Intelligence as a top-level page/tab.
