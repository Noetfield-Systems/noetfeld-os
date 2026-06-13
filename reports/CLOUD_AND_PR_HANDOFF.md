---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-02"
doc_id: cloud-and-pr-handoff-all-lanes
---

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-06-02

# Cloud orders + draft PR handoff

## Track A — Draft PR (local push done)

**Branch pushed:** `cursor/bank-grade-fullstack-37f0` @ `a6a4f52` (and later nf-0210 commit)

**Open draft PR (founder one-click):**

https://github.com/kazemnezhadsina144-dot/Noetfield/compare/main...cursor/bank-grade-fullstack-37f0?expand=1

**Title:** `Phase 2 evidence-connectors: nf-0202–nf-0209 (local repo agent)`

**Body:** use bullets from plan (nf-0202 through nf-0209). Mark **draft**. Note ~88 commits behind main; rebase after PR #48.

---

## Track B — Paste to `noetfield_cloud` (merge #48 only)

```
Bounded order — merge PR #48 only.

Repo: kazemnezhadsina144-dot/Noetfield
PR: https://github.com/kazemnezhadsina144-dot/Noetfield/pull/48
Branch: cursor/tenth-audit-iter18-37f0 → main

Pre: Local verify PASS on tenth-audit branch (coherence bundle).
Post-merge: Confirm main OPEN_PRS pending row = none; cursor-reply reflects iter 18; GTM_NEXT iter 19 seed live.

Do NOT merge PR #49 or local bank-grade PR in this order.
ASK before any other merge.
```

---

## Track C — Paste to `noetfield_cloud` (debug #49 CI)

```
Bounded order — debug PR #49 CI only (no merge until green).

PR: https://github.com/kazemnezhadsina144-dot/Noetfield/pull/49
Branch: cursor/design-token-migration-37f0
Head: 973e619b

Failed checks: unit, Governance Console E2E
Local cloud report: npm run build PASS; 172 unit tests PASS locally

Tasks:
1. Pull CI logs for unit + E2E workflows on design-token branch
2. Fix root cause (likely env/bootstrap vs tailwind/css import path)
3. Re-run CI; report pass/fail in cursor-reply
4. Do NOT merge until unit + www-health green; E2E may be skipped if policy allows

Out of scope: bank-grade PR, TrustField, legacy HTML shell wave
```

---

## Track D — nf-0210

Local agent implements on same branch; amends draft PR after closeout.

**Post-#48:** rebase `cursor/bank-grade-fullstack-37f0` onto main and resolve conflicts before marking PR ready.
