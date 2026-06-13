#!/usr/bin/env python3
"""Generate 1000 concrete Noetfield agent prompts (10 phases × 4 tiers × 25). LOCKED pack."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "os" / "plan-library" / "noetfield-1000"
PROMPTS = PACK / "prompts"

PHASES = [
    ("phase-0-ship-ops", "Ship ops, ingest, agent read-order, plan.json hygiene"),
    ("phase-1-tle-core", "Trust Ledger core, digests, exports, drift contract"),
    ("phase-2-evidence-connectors", "Evidence index, M365/Google connectors, intake"),
    ("phase-3-workspace-enterprise", "RBAC, SSO, multi-tenant, audit export"),
    ("phase-4-agents-automation", "Agent manifests, workflows, copilot governance runs"),
    ("phase-5-knowledge-rag", "RAG, knowledge ingestion, policy packs"),
    ("phase-6-compliance-scale", "Controls catalog, risk registers, compliance dashboard"),
    ("phase-7-pilot-gtm", "Design partners, procurement, demos, pricing narrative"),
    ("phase-8-staging-prod", "Staging, deploy smoke, observability, SLOs"),
    ("phase-9-ecosystem-bridge", "SourceA sync, Prompt OS ingest, cloud/local parity"),
]

TIERS = [
    ("T0", "Critical — agent can verify without founder"),
    ("T1", "High — next sprint candidate"),
    ("T2", "Medium — quarterly hardening"),
    ("T3", "Low — research / polish"),
]

# 25 concrete tasks per phase (synthesized from GTM, blueprint P0, waves 028-042, critics)
PHASE_TASKS: list[list[str]] = [
    [  # phase-0 ship-ops
        "Run python3 ~/Desktop/SourceA/scripts/cursor_agent_self_audit.py session-start before edits",
        "Run make verify-gtm; fix first failing step only",
        "Add agent_tag to reports/cursor-reply-latest.txt front matter and YAML footer",
        "Run ingest-cursor-reply.sh noetfield on latest cursor-reply after verify PASS",
        "Run ./scripts/sync-sourceA-desktop.sh after ingest",
        "Run python3 scripts/pick-noetfield-no-asf-plan.py --tier T0 --limit 1 smoke",
        "Run python3 scripts/validate-noetfield-1000-sources.py; fix registry gaps",
        "Extend scripts/verify_agent_reply_yaml.py check for agent_tag field",
        "Document PLAN WITH NO ASF trigger in os/SHIP_NOW.md one line only",
        "Add make pick-no-asf-plan to verify-gtm preflight when library exists",
        "Read docs/ops/AGENT_READ_LINKS_LOCKED_v1.md section for cloud vs local",
        "Read docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md before closeout",
        "Append REPO_TRUTH_CORRECTIONS row when chat disagrees with disk",
        "Run make ship-verify alias equals verify-gtm smoke",
        "Harden scripts/verify-ui-e2e.sh for new static routes only",
        "Add procurement-pack-e2e to verify-gtm if not already chained",
        "Sync os/plan.json updated_at after wave closeout",
        "Keep next_tasks empty unless founder says PLAN WITH NO ASF repopulate",
        "Grep committed docs for TrustField implementation tasks — reject",
        "Grep www copy for third-party vendor names — reject",
        "Run session-close via cursor_agent_self_audit for noetfield_cloud agent",
        "Update LOCKED_MANIFEST.md generated_at after regen",
        "Mirror noetfield-1000 index to ~/.cursor/plans/noetfield-os/README.md",
        "Run sync-noetfield-plans-status.py after marking nf-* done",
        "Validate 1000 count and 10×4×25 grid in REGISTRY.json",
    ],
    [  # phase-1 tle-core
        "Implement Drift Contract v0 fields on TLE draft API (drift_class, baseline_tle_id)",
        "Add evaluate-vs-last-TLE diff helper endpoint or service stub",
        "Add risk_summary to confidence factors in evaluate response",
        "Regression: make procurement-pack-e2e after TLE export change",
        "Extend test_tle_flow.py for drift contract fields",
        "Harden board_pack_export signature_block chain",
        "Add delta_summary and severity to drift export JSON",
        "Document Drift Contract v0 in docs/spec phase note only",
        "Wire workspace UI badge when drift_class present",
        "Validate TLE sample YAML still passes schema",
        "Run pytest test_tle_flow.py -q after TLE service edits",
        "Add audit_digest linkage in board pack JSON export",
        "Ensure confidence score visible on PDF cover regression test",
        "Add copilot-pilot-e2e step asserting confidence in export",
        "Cross-check GOVERNANCE_DRIFT_BLUEPRINTS_INDEX P0 gaps list",
        "Compare TLE v1 fields to TRUST_LEDGER_PRODUCT_BLUEPRINT locked spec",
        "Add drift metrics placeholder in cognitive dashboard copy",
        "Validate /trust-ledger/sample-report/ still 200",
        "Extend tle-smoke.sh for optional drift fields when shipped",
        "Add README-procurement.txt citation to governance sources book",
        "Harden KMS digest v2 signature_block in export path",
        "Add unit test for evaluate vs baseline diff empty state",
        "Document evaluate-vs-TLE as partial in REPO_TRUTH if not full",
        "Reject Lane C payment fields in TLE schema edits",
        "Run make verify-gtm after any tle_service.py change",
    ],
    [  # phase-2 evidence-connectors
        "Regression: M365 OAuth mock ingest in copilot-pilot-e2e",
        "Harden evidence hash on ingest in connector service",
        "Fix workspace/connectors OAuth redirect to workspace list",
        "Add verify-ui-e2e check for connectors page content",
        "Document 3 evidence types in copilot demo step copy",
        "Extend seed-m365-evidence-stub.sh idempotency",
        "Validate evidence index API returns tenant_id",
        "Add pytest for connector connected state persistence",
        "Improve connector error message for missing env",
        "Cross-check GOVERNANCE_SOURCES_BOOK M365 citation in buyer docs",
        "Add evidence type icons or labels on workspace only",
        "Run make copilot-pilot-e2e after connector route change",
        "Validate audit export includes connector events when present",
        "Add stub Google Workspace connector doc stub in docs/spec",
        "Tier B gate: do not add real Google OAuth without customer",
        "Harden /api/readiness style gate for connector subsystem",
        "Add connector status to workspace list row",
        "Test OAuth callback does not 500 on repeat connect",
        "Document mock vs real M365 in LOCAL_DEV.md one paragraph",
        "Add evidence slice to procurement zip when source_rid set",
        "Validate evaluate uses ingested evidence count in factors",
        "Add shell test for corridors or evidence list API",
        "Reject production Azure AD secrets in repo grep CI",
        "Compare Purview evidence narrative to mock connector UX",
        "Run make verify-local-dev after connector UI change",
    ],
    [  # phase-3 workspace-enterprise
        "Regression: workspace diligence UX confidence badge in verify-ui-e2e",
        "Harden RBAC chain test in test_tle_flow or dedicated test",
        "Add workspace list link to procurement buyer page",
        "Validate TLE detail ZIP link returns application/zip",
        "Improve workspace empty state CTA to copilot demo",
        "Add audit export slice test for tenant events",
        "Extend workspace/[tle_id] export links JSON HTML PDF ZIP",
        "Run verify-ui-e2e tle detail confidence badge check",
        "Document multi-tenant hardening as Tier C defer in comment",
        "Add SSO research note in T3 only — no SSO ship",
        "Validate cognitive-dashboard loads via proxy 13080",
        "Harden tenant header enforcement on TLE routes",
        "Add workspace timeline component regression",
        "Cross-check enterprise RBAC roadmap vs 60-day fence",
        "Add pytest for approval chain ordering",
        "Validate board pack HTML export content-type",
        "Improve workspace list sort by updated_at",
        "Add link from demo page to workspace connectors",
        "Run procurement-pack-e2e after workspace export UI change",
        "Document RBAC shipped vs roadmap in REPO_TRUTH if needed",
        "Add shellcheck on workspace-related scripts only",
        "Validate /workspace/connectors not captured by [tle_id] route",
        "Document enterprise ITSM evidence handoff pattern for 5-min TLE path (doc)",
        "Reject member portal routes in scope grep",
        "Run make verify-gtm after workspace frontend change",
    ],
    [  # phase-4 agents-automation
        "Regression: make copilot-pilot-e2e full chain green",
        "Harden ai-automation/index.html governance-first copy",
        "Add verify-local-dev check for /ai-automation/ route",
        "Extend verify-ui-e2e for ai-automation operator page",
        "Wire sitemap.xml for new static marketing routes only",
        "Document agent manifest v1 stub path in docs/spec",
        "Add copilot hub link from homepage hero regression",
        "Validate copilot/index.html GTM one-liner present",
        "Run smoke_bank_grade_html.py after static page edits",
        "Add agent workflow DSL research spike doc T3 only",
        "Cross-check NOETFIELD_COPILOT_SME_SYSTEM_DESIGN lane A domains",
        "Harden scripts/verify-gtm.sh step ordering",
        "Add design partner CTA on pilot page regression",
        "Validate demo script locked narrative on /copilot/demo/",
        "Document automation SKU forbidden on public hero grep",
        "Add pytest or script for openapi health if touched",
        "Improve copilot/pilot deep links to workspace paths",
        "Run tle-smoke after governance evaluate change",
        "Add agent self-audit mention in AGENT_TRACKING.md one line",
        "Reject Trust Brief implementation in Noetfield repo grep",
        "Document verifiable status surface pattern vs /status-system (doc)",
        "Add operating-plan static page boundary check",
        "Validate newpagename or ops pages do not violate OFFERINGS lock",
        "Document 10% code bucket from GTM lock in commit message template",
        "Run make verify-ui-e2e after copilot static change",
    ],
    [  # phase-5 knowledge-rag
        "Document RAG design nf-rag-design-010 scope in docs/spec stub",
        "Align policy pack placeholder with GOVERNANCE_SOURCES_BOOK",
        "Add knowledge ingestion research note — no vector DB ship",
        "Cross-check lane_a_sprint_map rag item vs 60-day fence",
        "Document copilot governance knowledge boundary",
        "Add docs/reference link from demo page footer only",
        "Validate no new repos for knowledge layer grep",
        "Add T3 compare: enterprise RAG vs TLE evidence wedge",
        "Harden docs/spec README index for agent read order",
        "Add policy schema copilot-006 pointer in sprint map comment",
        "Document workflow-copilot-dsl-007 as deferred",
        "Add verify step that docs compile links resolve",
        "Cross-check OECD AI principles citation format",
        "Add NIST AI RMF mapping table draft in internal spec only",
        "Reject over-build of embedding pipeline in T0/T1 prompts",
        "Add shell script to list broken markdown links in docs/reference",
        "Document knowledge graph as post-revenue in GTM Tier C",
        "Add copilot hub FAQ stub for evidence vs chat RAG",
        "Validate TRUST_LEDGER positioning mentions evidence not RAG hero",
        "Add research prompt: chunk size for board pack citations",
        "Compare GPT enterprise retrieval to Noetfield evidence index",
        "Document agent manifest fields without implementing vectors",
        "Add pytest noop for rag module if missing",
        "Harden .cursor rules against new knowledge microservices",
        "Run make validate-noetfield-1000 after docs-only rag pass",
    ],
    [  # phase-6 compliance-scale
        "Harden board pack PDF governance citations — primary URLs only",
        "Add controls catalog stub markdown in docs/reference annex",
        "Document risk register template for design partners",
        "Cross-check EU AI Act Art 72 monitoring cite in drift sources",
        "Add compliance dashboard research T3 — no full GRC ship",
        "Validate PROCUREMENT_ONE_PAGER NIST mapping lines",
        "Extend board_pack_pdf.py regression for confidence prominence",
        "Add verify grep for legal advice forbidden phrases",
        "Document ISO 42001-style evidence fields on TLE",
        "Add drift metrics doc cross-link in blueprints index",
        "Harden README-procurement.txt framework alignment text",
        "Add shell test for sample-report YAML download",
        "Compare enterprise GRC 12-month rollout vs 5-min demo wedge",
        "Document continuous monitoring without new product surface",
        "Add OPA policy research note in drift detection sources",
        "Validate audit export JSON schema stability",
        "Add compliance page static copy boundary check",
        "Cross-check OWASP LLM cite in governance book usage",
        "Reject FINTRAC filing claims in www grep",
        "Add controls-to-TLE field mapping research table",
        "Document CA-7 continuous monitoring cite usage",
        "Harden terms/privacy pages if linked from workspace",
        "Add pytest for compliance export redaction if PII paths exist",
        "Validate Microsoft Purview mention is connector not product claim",
        "Run make verify-gtm after compliance doc edits",
    ],
    [  # phase-7 pilot-gtm
        "Regression: procurement-pack-e2e one-click zip export",
        "Regression: /copilot/demo/ 5-minute demo page verify-ui-e2e",
        "Regression: make demo-url prints tunnel or staging instructions",
        "Regression: copilot/procurement buyer pack page links",
        "Regression: DESIGN_PARTNER_SOW_OUTLINE linked from pilot page",
        "Regression: copilot/index.html GTM hub hero and demo CTAs",
        "Regression: homepage design partner primary CTA verify-ui-e2e",
        "Regression: make verify-gtm pre-demo bundle",
        "Add GTM category one-liner grep on homepage and copilot hub",
        "Document public demo URL founder steps in STAGING_DEMO.md",
        "Harden print-demo-url.sh NF_STAGING_URL branch",
        "Add dev-local-tunnel-bg instructions without secrets",
        "Cross-check GTM scorecard honest rows in commit notes only",
        "Add procurement ZIP button label regression on workspace",
        "Validate confidence score called out in demo step 4 copy",
        "Document Tier A complete vs Tier B M365 real connector gate",
        "Add outreach email snippet cross-link in docs/gtm only",
        "Reject $6K hero pricing on homepage grep",
        "Compare buyer zone grid pattern without third-party vendor names",
        "Document 70/20/10 time allocation in agent closeout template",
        "Add founder-only: customer logo row marked skip in pick script",
        "Validate OFFERINGS_LOCKED three SKUs unchanged",
        "Add Vancouver SMB governance as Lane B doc only not www",
        "Document first customer success signal from GTM lock",
        "Run make verify-gtm after any GTM static page change",
    ],
    [  # phase-8 staging-prod
        "Run make staging-smoke when NF_STAGING_URL set (document only if unset)",
        "Harden scripts/staging-smoke.sh for copilot demo path",
        "Document Render deploy as founder-only in STAGING_DEMO.md",
        "Add observability migration 0008 follow-up research note",
        "Validate alembic history documented in LOCAL_DEV.md",
        "Add postgres phase-1b doc alignment without credit card deploy",
        "Harden dev-local-tunnel-bg script docs",
        "Add .dev-tunnel-url.txt gitignore check",
        "Document NF_PUBLIC_DEMO_URL static injection optional",
        "Cross-check production OAuth secrets forbidden in repo",
        "Add smoke for trust-ledger sample on staging URL",
        "Validate sitemap committed script in ship-verify",
        "Add playwright or curl staging checklist row",
        "Document SLO research T3 without Datadog ship",
        "Harden verify-local-dev for console proxy routes",
        "Add migration skeleton doc without running prod DB",
        "Compare staging-smoke to industry preview env norms",
        "Document cloudflare/render choice as founder decision",
        "Add PR checklist row for staging-smoke in docs/ops",
        "Validate no tunnel URLs committed grep",
        "Add health endpoint check to staging-smoke if missing",
        "Document observability middleware roadmap partial truth",
        "Reject full prod deploy execution in agent T0 tasks",
        "Add rate limits NF-0110 regression mention in REPO_TRUTH",
        "Run make verify-local-dev after staging script change",
    ],
    [  # phase-9 ecosystem-bridge
        "Run ./scripts/sync-sourceA-desktop.sh and verify mirror timestamps",
        "Validate ingest-cursor-reply.sh exits 0 on tagged reply",
        "Run python3 scripts/verify_agent_reply_yaml.py on cursor-reply-latest",
        "Sync noetfield lane to ~/.cursor/plans/no-asf-library via sync script",
        "Update docs/ops/NOETFIELD_AGENT_TEAM_SYNC revision row only if needed",
        "Document cloud agent nf-cloud-repo-agent tagging rule",
        "Harden package-ops-private-for-cloud.sh docs for founder rsync",
        "Add AGENT_READ_LINKS row for 1000 library without cloud paragraph edits",
        "Validate SourceA REPO_EXECUTION_LOGS ingest path exists after ingest",
        "Cross-check Prompt OS read-only rule in agent tracking",
        "Add ecosystem bridge research: mono hub without implementing",
        "Document noetfield_local vs noetfield_cloud workspace forbidden roots",
        "Run sync-noetfield-plans-status.py nf-future to nf-1000 mapping",
        "Add global REGISTRY lanes.noetfield metadata refresh",
        "Validate cursor plans noetfield-os mirror README links",
        "Compare agent team self-heal to best-practice agent memory loops",
        "Document INCIDENT context memory law read order",
        "Add pick script integration test in validate-noetfield-1000",
        "Harden founder repo-agent-notices mirror after sync",
        "Reject edits to SinaPromptOS code grep in agent session",
        "Reject edits to Desktop SourceA from noetfield agent grep",
        "Add CHANGELOG row for noetfield-1000 generation date",
        "Document 1000 prompt diff vs generic nf-future stubs",
        "Schedule next PLAN WITH NO ASF via make pick-no-asf-plan",
        "Run validate-noetfield-1000-sources.py exit 0 after ecosystem sync",
    ],
]

TIER_DEPTH = {
    "T0": "Do now. Minimal scope. Run verify gate before close.",
    "T1": "Next sprint. Ship with evidence in plan.json done.",
    "T2": "Quarterly hardening. Refactor only if verify stays green.",
    "T3": "Research spike. Document in tagged doc; optional code.",
}

VERIFY = {
    "T0": "make verify-gtm",
    "T1": "make verify-local-dev && make verify-ui-e2e && make copilot-pilot-e2e",
    "T2": "make procurement-pack-e2e && make verify-ui-e2e",
    "T3": "python3 scripts/validate-noetfield-1000-sources.py",
}

SOURCES_BY_PHASE = {
    "phase-0-ship-ops": [
        "docs/ops/AGENT_READ_LINKS_LOCKED_v1.md",
        "docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md",
        "os/SHIP_NOW.md",
        "os/plan.json",
    ],
    "phase-1-tle-core": [
        "docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md",
        "docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md",
        "governance-console/backend/services/tle_service.py",
    ],
    "phase-2-evidence-connectors": [
        "docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md",
        "scripts/copilot-pilot-e2e.sh",
        "governance-console/frontend/app/workspace/connectors/",
    ],
    "phase-3-workspace-enterprise": [
        "governance-console/frontend/app/workspace/",
        "governance-console/backend/tests/test_tle_flow.py",
    ],
    "phase-4-agents-automation": [
        "docs/strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md",
        "copilot/index.html",
        "scripts/verify-gtm.sh",
    ],
    "phase-5-knowledge-rag": [
        "docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md",
        "os/plan.json",
    ],
    "phase-6-compliance-scale": [
        "docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md",
        "governance-console/backend/services/board_pack_pdf.py",
    ],
    "phase-7-pilot-gtm": [
        "docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md",
        "docs/copilot/DESIGN_PARTNER_SOW_OUTLINE.md",
        "scripts/print-demo-url.sh",
    ],
    "phase-8-staging-prod": [
        "docs/ops/STAGING_DEMO.md",
        "docs/LOCAL_DEV.md",
        "scripts/staging-smoke.sh",
    ],
    "phase-9-ecosystem-bridge": [
        "docs/ops/NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md",
        "reports/cursor-reply-latest.txt",
        "~/.cursor/plans/no-asf-library/README.md",
    ],
}

GLOBAL_SOURCES = [
    {"doc_id": "gtm-60-day", "path": "docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md", "optional": False},
    {"doc_id": "tle-positioning", "path": "docs/strategy/NOETFIELD_TRUST_LEDGER_POSITIONING_LOCKED_v1.2.md", "optional": False},
    {"doc_id": "tle-blueprint", "path": "docs/spec/TRUST_LEDGER_PRODUCT_BLUEPRINT_v1.2_LOCKED.md", "optional": False},
    {"doc_id": "governance-sources", "path": "docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md", "optional": False},
    {"doc_id": "drift-sources", "path": "docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md", "optional": False},
    {"doc_id": "drift-blueprints", "path": "docs/references/GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md", "optional": False},
    {"doc_id": "agent-sync", "path": "docs/ops/NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md", "optional": False},
    {"doc_id": "execution-truth", "path": "docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md", "optional": False},
    {"doc_id": "context-incident", "path": "~/Desktop/SourceA/CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md", "optional": True},
    {"doc_id": "repo-truth", "path": "ops/private/agent-reference/REPO_TRUTH_CORRECTIONS.md", "optional": True},
    {"doc_id": "private-todolist", "path": "ops/private/todolist/NEXT_MOVES.md", "optional": True},
]

# Tasks containing these (phase-7 + regressions) → status done on first generation
DONE_TASK_MARKERS = [
    "Regression: procurement-pack-e2e",
    "Regression: /copilot/demo/",
    "Regression: make demo-url",
    "Regression: copilot/procurement",
    "Regression: DESIGN_PARTNER_SOW",
    "Regression: copilot/index.html",
    "Regression: homepage design partner",
    "Regression: make verify-gtm pre-demo",
    "Regression: M365 OAuth mock",
    "Regression: workspace diligence",
    "Harden board_pack_export signature_block",
    "Add KMS digest v2 signature_block",
    "Document alembic history",
    "Add observability migration 0008 follow-up research",
]

# nf-future stub mapping (wave id → future seq approximate)
FUTURE_STUB_MAP = {
    "nf-procurement-pack-zip-034": "nf-future-0703",
    "nf-demo-page-confidence-035": "nf-future-0704",
    "nf-public-demo-url-036": "nf-future-0707",
}


def agent_prompt_text(pid: str, task: str, tier: str) -> str:
    return (
        f"PLAN WITH NO ASF — Noetfield agent prompt {pid}. "
        f"{task} ({TIER_DEPTH[tier]}). "
        f"Pre-flight: read docs/ops/AGENT_READ_LINKS_LOCKED_v1.md and os/SHIP_NOW.md. "
        f"Tag new docs [NF-LOCAL-REPO-AGENT] + authored_at. Do not edit [NF-CLOUD-AGENT] sections. "
        f"Post-flight: make verify-gtm, cursor-reply with reported_at, ingest, sync-sourceA."
    )


def prompt_body(pid: str, phase: str, phase_desc: str, tier: str, task: str, slot: int, status: str) -> str:
    priority = {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}[tier]
    sources = SOURCES_BY_PHASE.get(phase, GLOBAL_SOURCES[:4])
    if isinstance(sources[0], dict):
        src_lines = "\n".join(f"- `{s['path']}`" for s in sources)
    else:
        src_lines = "\n".join(f"- `{s}`" for s in sources)
    ap = agent_prompt_text(pid, task, tier)
    return f"""---
id: {pid}
phase: {phase}
tier: {tier}
priority: {priority}
status: {status}
lane: noetfield
library: noetfield-1000-locked
agent_tag: nf-local-repo-agent
slot: {slot}
generator: scripts/generate-noetfield-1000-prompts.py
locked: true
updated_at: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}
---

# {pid} — {task}

**Phase:** `{phase}` — {phase_desc}  
**Tier:** `{tier}` — {TIER_DEPTH[tier]}

## Agent prompt (copy to chat)

```
{ap}
```

## Task

{task}

## Sources (read first)

{src_lines}
- `docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md` (60-day fence)
- `os/plan-library/noetfield-1000/SOURCES_INDEX.yaml`

## Verify

```bash
{VERIFY[tier]}
```

## Closeout

1. Set `status: done` in this file front matter
2. `reports/cursor-reply-latest.txt` with `agent_tag` + `reported_at`
3. `~/Desktop/SinaPromptOS/scripts/ingest-cursor-reply.sh noetfield reports/cursor-reply-latest.txt`
4. `./scripts/sync-sourceA-desktop.sh`
5. `python3 scripts/sync-noetfield-plans-status.py` (optional nf-future mirror)
"""


def is_done_task(task: str, tier: str) -> bool:
    if tier != "T0":
        return False
    return any(m in task for m in DONE_TASK_MARKERS)


def build_sources_index(entries: list[dict]) -> dict:
    used: dict[str, set[str]] = {}
    for e in entries:
        for src in e.get("sources", []):
            used.setdefault(src, set()).add(e["id"])
    index = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(), "authorities": []}
    for g in GLOBAL_SOURCES:
        path = g["path"]
        exists = (ROOT / path).is_file() if not path.startswith("~") else Path(path).expanduser().is_file()
        index["authorities"].append({
            **g,
            "exists_on_disk": exists,
            "prompt_count": len(used.get(path.replace("~/Desktop/Noetfield/", ""), set())),
        })
    return index


def build_validation_matrix(entries: list[dict], done_count: int) -> str:
    backlog = sum(1 for e in entries if e["status"] == "backlog")
    t0_backlog = sum(1 for e in entries if e["status"] == "backlog" and e["tier"] == "T0")
    lines = [
        "---",
        "agent_tag: nf-local-repo-agent",
        'agent_display: "[NF-LOCAL-REPO-AGENT]"',
        'authored_at: "2026-06-06"',
        "doc_id: noetfield-1000-validation-matrix",
        "---",
        "",
        "> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-06-06",
        "",
        "# Noetfield 1000 — validation matrix",
        "",
        f"| Check | Status |",
        f"|-------|--------|",
        f"| Total prompts | {len(entries)} / 1000 |",
        f"| Pre-marked done (shipped waves) | {done_count} |",
        f"| Backlog | {backlog} |",
        f"| T0 backlog (pick script) | {t0_backlog} |",
        "",
        "## Source coverage",
        "",
    ]
    for g in GLOBAL_SOURCES:
        p = g["path"]
        ok = "optional" if g.get("optional") else "required"
        exists = (ROOT / p).is_file() if not p.startswith("~") else Path(p).expanduser().is_file()
        lines.append(f"- [{ok}] `{p}` — {'OK' if exists else 'MISSING'}")
    lines += [
        "",
        "## Shipped wave mapping (nf-future stubs)",
        "",
    ]
    for wave, stub in FUTURE_STUB_MAP.items():
        lines.append(f"- `{wave}` → `{stub}`")
    lines += [
        "",
        "## Critics embedded",
        "",
        "- GTM scorecard: proof > features (Tier A before B)",
        "- Repo truth: disk beats chat; ship-verify alias",
        "- Privacy: no vendor comparison tables on www",
        "- Boundary: no TrustField/VIRLUX implementation in repo",
        "- Self-audit: session-start/closeout before/after work",
        "",
        "## World-model patterns (T3 slots only — no vendor names)",
        "",
        "- Verifiable audit status surface pattern",
        "- Microsoft Purview evidence connector narrative",
        "- NIST AI RMF Govern/Manage mapping",
        "- Enterprise ITSM workflow vs 5-min board PDF wedge (buyer zones only)",
        "",
    ]
    return "\n".join(lines)


def build_locked_manifest(now: str, done_count: int) -> str:
    return f"""---
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-06"
doc_id: noetfield-1000-locked-manifest
---

> **Authored by:** [NF-LOCAL-REPO-AGENT] — 2026-06-06

# Noetfield 1000 LOCKED manifest

**Library:** `noetfield-1000-locked`  
**Generated:** {now}  
**Grid:** 10 phases × 4 tiers × 25 prompts = 1000  
**Trigger:** `PLAN WITH NO ASF`  
**Pick:** `python3 scripts/pick-noetfield-no-asf-plan.py --tier T0 --limit 1`  
**Pre-marked done:** {done_count} prompts (shipped waves / regressions)

Canonical: `~/Desktop/Noetfield/os/plan-library/noetfield-1000/REGISTRY.json`
"""


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries: list[dict] = []
    seq = 0
    done_count = 0

    for p_idx, (phase, phase_desc) in enumerate(PHASES):
        tasks = PHASE_TASKS[p_idx]
        phase_sources = SOURCES_BY_PHASE.get(phase, [])
        for tier, _tier_desc in TIERS:
            tier_dir = PROMPTS / phase / tier
            tier_dir.mkdir(parents=True, exist_ok=True)
            for slot in range(25):
                seq += 1
                pid = f"nf-{seq:04d}"
                task = tasks[slot]
                status = "done" if is_done_task(task, tier) else "backlog"
                if status == "done":
                    done_count += 1
                rel = f"prompts/{phase}/{tier}/{pid}.md"
                path = PACK / rel
                path.write_text(
                    prompt_body(pid, phase, phase_desc, tier, task, slot, status),
                    encoding="utf-8",
                )
                entries.append(
                    {
                        "id": pid,
                        "phase": phase,
                        "tier": tier,
                        "priority": {"T0": "P0", "T1": "P1", "T2": "P2", "T3": "P3"}[tier],
                        "lane": "noetfield",
                        "slot": slot,
                        "title": task[:100],
                        "path": f"os/plan-library/noetfield-1000/{rel}",
                        "status": status,
                        "verify": VERIFY[tier],
                        "sources": phase_sources if phase_sources else [g["path"] for g in GLOBAL_SOURCES[:4]],
                        "agent_prompt": f"PLAN WITH NO ASF — {pid}: {task}",
                        "future_stub_map": FUTURE_STUB_MAP if phase == "phase-7-pilot-gtm" and slot < 8 else None,
                    }
                )

    registry = {
        "schema_version": 1,
        "library": "noetfield-1000-locked",
        "locked": True,
        "count": len(entries),
        "generated_at": now,
        "agent_tag": "nf-local-repo-agent",
        "agent_display": "[NF-LOCAL-REPO-AGENT]",
        "repo": "noetfield",
        "grid": "10 phases × 4 tiers × 25 prompts = 1000",
        "trigger": "PLAN WITH NO ASF",
        "pick_script": "scripts/pick-noetfield-no-asf-plan.py",
        "validate_script": "scripts/validate-noetfield-1000-sources.py",
        "global_pack": str(Path.home() / ".cursor/plans/no-asf-library"),
        "canonical": str(PACK),
        "sources": [g["path"] for g in GLOBAL_SOURCES],
        "future_stub_map": FUTURE_STUB_MAP,
        "phases": [{"id": p, "description": d} for p, d in PHASES],
        "tiers": [{"id": t, "description": d} for t, d in TIERS],
        "plans": entries,
        "stats": {"done": done_count, "backlog": len(entries) - done_count},
    }

    PACK.mkdir(parents=True, exist_ok=True)
    (PACK / "REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    reg_md = [
        "# Noetfield 1000 registry",
        "",
        f"**Count:** {len(entries)} | **Done:** {done_count} | **Generated:** {now}",
        "",
        "## Pick next",
        "",
        "```bash",
        "make pick-no-asf-plan",
        "```",
        "",
        "## Phases",
        "",
    ]
    for p, d in PHASES:
        reg_md.append(f"- `{p}` — {d}")
    (PACK / "REGISTRY.md").write_text("\n".join(reg_md) + "\n", encoding="utf-8")

    src_index = build_sources_index(entries)
    (PACK / "SOURCES_INDEX.json").write_text(json.dumps(src_index, indent=2) + "\n", encoding="utf-8")
    yaml_lines = ["schema_version: 1", f"generated_at: {src_index['generated_at']}", "authorities:"]
    for a in src_index["authorities"]:
        yaml_lines.append(f"  - doc_id: {a['doc_id']}")
        yaml_lines.append(f"    path: \"{a['path']}\"")
        yaml_lines.append(f"    optional: {str(a.get('optional', False)).lower()}")
        yaml_lines.append(f"    exists_on_disk: {str(a['exists_on_disk']).lower()}")
    (PACK / "SOURCES_INDEX.yaml").write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")

    (PACK / "VALIDATION_MATRIX.md").write_text(build_validation_matrix(entries, done_count), encoding="utf-8")
    (PACK / "LOCKED_MANIFEST.md").write_text(build_locked_manifest(now, done_count), encoding="utf-8")

    assert len(entries) == 1000, f"expected 1000 got {len(entries)}"
    print(f"LOCKED {len(entries)} Noetfield prompts → {PACK / 'REGISTRY.json'} (done={done_count})")


if __name__ == "__main__":
    main()
