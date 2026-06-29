---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-29"
doc_id: noetfield-system-nerve-upgrade-100-plans-locked-v1
status: LOCKED
scope: website-platform-noos-sync
---

# Noetfield System Nerve Upgrade - 100 Plans LOCKED v1

## Purpose

This file is the disk record for the 100-plan upgrade request. Chat is not the system of record.

Current execution rule:

```text
live receipts -> current source -> validators -> docs -> chat summaries
```

## P0 Execution Register

P0 is not "ideas". P0 means the system must fail closed when public output, route truth, chatbot truth, or ownership sync drifts.

### Executed In This Pass

1. Create this disk plan as the durable planning artifact.
2. Create one shared public denylist source for public leak paths.
3. Wire production E2E and live nerve to read that shared denylist.
4. Add a denylist sync validator so `.vercelignore`, `vercel.json`, live nerve, and E2E cannot drift silently.
5. Add route/nav truth gating for the known `/intelligence/` issue.

### Remaining P0 Decisions

1. Decide whether `/intelligence/` becomes a real hub or the nav label changes to Home.
2. Decide whether NOOS live-sync generated receipts are committed every run or only at milestone snapshots.
3. Repair SourceA foundation drift in SourceA, not the Noetfield website repo.

## 100 Upgrade Plans

1. Make `NOETFIELD_LIVE_NERVE_RECEIPT.json` the first-read law for all website/platform work.
2. Make `NOOS_LIVE_SYNC_RECEIPT.json` the first-read law for NOOS runtime work.
3. Use one shared public denylist source for `.vercelignore`, `vercel.json`, E2E, and live nerve.
4. Fail validation when denylist coverage differs across files.
5. Fail live nerve when stale public chatbot framing returns.
6. Mark RCA/history docs as historical so agents do not reuse bad examples.
7. Add `historical_do_not_reuse` metadata to docs that quote bad wording.
8. Require chatbot knowledge manifest visibility, hash, freshness, and public label.
9. Probe direct platform chat, not only the www proxy.
10. Add live leak probes for every private/internal root.
11. Decide `/intelligence/`: real hub or not a top-level page.
12. If hub, make `/intelligence/` the proof, insight, teardown, and diagnostic route.
13. If no hub, rename the nav role to Home.
14. Fail static verification when a primary nav label points to `/` but is not Home.
15. Align homepage title, CTA, chatbot KB, sitemap, and nav around the same Intelligence decision.
16. Add route inventory for live 200, 404, redirect, and owner.
17. Add NOOS mirror update after route/nav decisions.
18. Add public copy rule: no page-like noun unless route exists.
19. Add route receipt: route, owner, purpose, proof URL, validator.
20. Add primary nav weight law: every primary item is conversion, proof, or product hub.
21. Require scope before work: website, platform, runtime, studio, foundation, ecosystem.
22. Add scope to live nerve receipts.
23. Make "ecosystem green" impossible while any required scope is fail or unnamed degraded.
24. Keep SourceA as foundation pattern, not Noetfield implementation storage.
25. Add handoff agreement validator between website and NOOS docs.
26. Make NOOS wrapper refresh website live nerve before writing NOOS truth.
27. Use `PASS`, `DEGRADED`, `FAIL`, not vague healthy language.
28. Add dirty-tree warning before any green claim.
29. Keep SourceA warnings separate from Noetfield runtime failures.
30. Track SourceA mirror poison, worker gate, UI first-check, and graph drift separately.
31. Add foundation warning field to NOOS receipt.
32. Do not block www deployment only because SourceA foundation is degraded.
33. Do not claim full ecosystem green while SourceA session gate is not green.
34. Report SourceA drift through allowed channels only.
35. Add SourceA proof-spine pointer in NOOS receipt.
36. Add inherited-pattern vs implementation-owned flag for SourceA-derived rules.
37. Prevent SourceA vocabulary from public Noetfield copy.
38. Escalate only SourceA drift that impacts Noetfield product behavior.
39. Build a validator registry with owner, scope, command, and receipt path.
40. Add dependency graph for validators.
41. Add max age to all generated receipts.
42. Fail when a receipt is too old.
43. Make E2E write JSON receipt.
44. Validate orphan docs not indexed in active manifests.
45. Validate docs with conflicting ownership claims.
46. Validate public/private classification.
47. Validate public docs that mention internal repo paths.
48. Validate nav route exists and returns expected status.
49. Validate route in sitemap has owner.
50. Validate route owner maps to repo.
51. Keep subject tracking and entity retrieval in chatbot kernel.
52. Add tests for retired/renamed/deprecated/removed cross-entity confusion.
53. Test both www and direct platform chat for source leaks.
54. Add source expiry per chatbot knowledge record.
55. Add "missing detail" behavior: do not borrow from wrong entity.
56. Add tone tests: natural, buyer-safe, no odd defensive disclaimers.
57. Add internal retrieval trace receipts.
58. Restrict source labels to public names, never filenames.
59. Expose chat bundle version in health and live nerve.
60. Add pgvector/distill only after manifest gate stays green.
61. Create Noetfield node catalog independent from SourceA.
62. Map N1-N7 current live nerve nodes to files and commands.
63. Add N8 route inventory.
64. Add N9 ownership sync.
65. Add N10 NOOS runtime.
66. Add N11 Studio boundary.
67. Add N12 SourceA foundation warning.
68. Add node graph validator for Noetfield.
69. Add directory map: every node points to scripts, receipts, docs.
70. Ban orphan validators.
71. Add active/archive doc separation.
72. Add doc frontmatter: owner, scope, freshness, supersedes, superseded_by.
73. Validate missing doc owner/scope.
74. Validate docs that claim public status but live under private roots.
75. Move prohibited uploaded strategy docs out of active agent read path.
76. Make active docs index the only read chain after live receipts.
77. Add "do not use for implementation" banner to RCA docs.
78. Add daily doc freshness receipt.
79. Add Railway deploy status node for `platform-api`.
80. Add Vercel deploy status node for www.
81. Add Railway deploy/version node for `gel-api`.
82. Compare GitHub SHA, Vercel SHA, Railway deployment, and receipt SHA.
83. Alert when live bundle version differs from repo manifest.
84. Add canary chat prompt set after deploy.
85. Run live nerve after every deploy.
86. Put rollback instruction into failed live nerve receipt.
87. Block push/deploy when denylist drift exists.
88. Keep scheduled verification headless/no visible browser.
89. Build `/intelligence/` if chosen.
90. Build safe public status page from public subset of receipts.
91. Build internal receipt dashboard for agents.
92. Tie Trust Ledger sample to live GEL health.
93. Tie API sandbox proof to `api.noetfield.com/readiness`.
94. Add Studio boundary receipt to NOOS sync gate.
95. Add Studio Supabase boundary validator to Studio CI.
96. Add public copy dictionary for buyer-safe language.
97. Add founder decision queue for ambiguous nav/product choices.
98. Add weekly truth audit: leaks, stale docs, route drift, validator drift, node health.
99. Split generated execution state from source manifests.
100. Require every "green" claim to cite receipt path and command.
