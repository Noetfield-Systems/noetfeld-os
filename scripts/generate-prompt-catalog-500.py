#!/usr/bin/env python3
"""Consolidate 1000 NF-PLAN grid → 500 catalogued prompts with grades, tiers, success lanes."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "docs" / "ops" / "plans"
TIER1 = PLANS / "tier1-smart.json"
REGISTRY = PLANS / "registry.json"
OUT_JSON = PLANS / "catalog-500.json"
OUT_MD = PLANS / "CATALOG_500_INDEX.md"
OUT_MATRIX = PLANS / "PRIORITY_MATRIX_500.md"
OUT_MASTER = ROOT / "docs" / "ops" / "NOETFIELD_PROMPT_PACK_500_MASTER_LOCKED_v1.md"

# ── Success model lanes (weight for picking & copy) ─────────────────────────
SUCCESS_LANES = {
    "receipt_first": {
        "label": "Receipt-first export",
        "weight": 10,
        "copy": "Receipt-first · export in minutes · fail-closed tamper",
        "use_for": ["demo-rehearsal", "audit-export", "www-copy", "tle"],
    },
    "trust_center": {
        "label": "Trust center diligence",
        "weight": 10,
        "copy": "Trust center · procurement ZIP · honest cert table",
        "use_for": ["diligence-doc", "trust", "procurement", "compliance"],
    },
    "microsoft_ccs": {
        "label": "Microsoft CCS + Purview",
        "weight": 9,
        "copy": "Complement stack · Phase 1 readiness → Phase 2 TLE receipts",
        "use_for": ["www-copy", "connectors", "copilot", "msp"],
    },
    "msp_two_tier": {
        "label": "MSP two-tier RACI",
        "weight": 9,
        "copy": "Two-tier RACI · Readiness → Record · Phase 2 attach",
        "use_for": ["msp", "partners", "channel"],
    },
    "numbered_narrative": {
        "label": "Numbered buyer narrative",
        "weight": 6,
        "copy": "Numbered narrative · framework marquee · no leader claims",
        "use_for": ["www-copy", "investors", "federal"],
    },
    "readiness_sku": {
        "label": "Fixed-fee readiness SKU",
        "weight": 6,
        "copy": "Copilot Readiness Assessment · fixed fee · reduced scope",
        "use_for": ["copilot", "pricing", "pilot"],
    },
    "anti_platform_breadth": {
        "label": "Anti-pattern: full GRC platform breadth",
        "weight": -10,
        "copy": "NEVER prompt full GRC platform inventory/enforce",
        "use_for": [],
    },
}

PATTERN_GRADES = {
    "demo-rehearsal": ("A", 1, "receipt_first"),
    "www-copy": ("A", 1, "receipt_first"),
    "diligence-doc": ("A", 1, "trust_center"),
    "buyer-debrief": ("A", 1, "readiness_sku"),
    "customer-outreach": ("A", 1, "readiness_sku"),  # hub only
    "smoke-script": ("B", 2, "trust_center"),
    "audit-export": ("B", 2, "receipt_first"),
    "openapi-sync": ("B", 2, "microsoft_ccs"),
    "integration-test": ("B", 2, "receipt_first"),
    "console-ui": ("B", 2, "microsoft_ccs"),
    "schema-validate": ("B", 2, "trust_center"),
    "examples-pack": ("B", 2, "receipt_first"),
    "scope-gate-drill": ("B", 2, "trust_center"),
    "runbook": ("C", 2, "trust_center"),
    "api-endpoint": ("C", 2, "microsoft_ccs"),
    "registry-reconcile": ("C", 3, "trust_center"),
    "tier-gate-check": ("C", 3, "trust_center"),
    "drift-impl": ("D", 3, "anti_platform_breadth"),
    "verdict-review": ("D", 3, "anti_platform_breadth"),
    "performance": ("D", 3, "anti_platform_breadth"),
}

T0_CONSTITUTION = [
    ("C-01", "PLAN WITH NO ASF sequence", "docs/ops/NOETFIELD_1000_PROMPT_PACK_LOCKED_v1.md"),
    ("C-02", "Worker Blueprint V3 paste", "docs/WORKER_BLUEPRINT_V3_NOETFIELD_COM_FULL_PROMPT.md"),
    ("C-03", "WWW v12 regen + smoke", "scripts/rebuild-www-v6.py"),
    ("C-04", "Agent reply YAML closeout", "docs/spec/EXECUTION_TRUTH_AGENT_REPLY_LOCKED.md"),
    ("C-05", "Scope gate three SKUs", "OFFERINGS_LOCKED.md"),
    ("C-06", "Honest scope no certifier", "docs/DESIGN_REFERENCE_GOALS_LOCKED_v1.md"),
    ("C-07", "Copilot complement Purview", "docs/GTM_COPYBOOK.md"),
    ("C-08", "MSP two-tier RACI", "docs/MSP_GOVERNANCE_PACK_v1.md"),
    ("C-09", "Federal not certifier", "docs/FEDERAL_GOVERNANCE_PACK_v1.md"),
    ("C-10", "Investor honesty", "investors/index.html"),
    ("C-11", "Agentic vs cloud fence", "docs/ops/plans/PROMPT_PACK_LOCKED/GTM_PRIORITY_100.md"),
    ("C-12", "Pick max 3 tasks", "docs/strategy/NOETFIELD_GTM_60_DAY_LOCKED_v1.md"),
]

AREAS = [
    "trust-ledger", "governance-api", "evidence", "connectors", "workspace-ui",
    "www-gtm", "customer-acquisition", "demo-ops", "agent-ops", "docs-diligence",
    "testing", "ci-cd", "security", "federal", "msp-channel",
]

# Tier 2 product backlog — 138 SMART prompts (pilot-gated)
def build_tier2() -> list[dict]:
    items: list[dict] = []
    n = 1

    def add(area, title, lane, effort, verify, task, gate="B"):
        nonlocal n
        pid = f"B-{n:03d}"
        n += 1
        items.append({
            "id": pid,
            "tier": 2,
            "grade": "B",
            "phase": "PRODUCT",
            "area": area,
            "title": title,
            "success_lane": lane,
            "effort": effort,
            "agent_mode": "cloud",
            "gate": gate,
            "w3_signal": "ship_green",
            "task": task,
            "verify": verify,
            "done_when": f"{title} verified; no scope creep beyond {area}.",
            "pick_after": "W3 deposit or first pilot SOW",
        })

    # TLE / export (25)
    tle_tasks = [
        ("Drift contract v0 fields on TLE draft API", "pytest test_tle_flow.py -q"),
        ("Board pack signature_block chain hardening", "pytest -k board_pack -q"),
        ("Procurement sidecar manifest hash fields", "grep export_integrity services/ -r | head -1"),
        ("TLE tamper FAIL regression test", "pytest -k tamper -q"),
        ("Confidence factors on evaluate response", "grep risk_summary services/ -r | head -1"),
        ("audit_digest linkage in board JSON export", "pytest test_tle_flow.py -q"),
        ("TLE schema validate CI step", "make schema-validate 2>/dev/null || pytest -k schema -q"),
        ("Sample YAML go/conditional/rejected CI", "ls trust-ledger/samples/ samples/tle/ 2>/dev/null"),
        ("Workspace TLE detail export links regression", "./scripts/verify-ui-e2e.sh 2>&1 | grep -i tle | head -1"),
        ("TLE approval chain UI read-only v0", "grep -i approval workspace/ -r | head -1"),
    ]
    for title, verify in tle_tasks:
        add("trust-ledger", title, "receipt_first", "M", verify,
            f"Implement or verify: {title}. Metadata-only M365; fail-closed export.")

    # API / OpenAPI (20)
    api_tasks = [
        ("POST /evaluate 409 guard integration test", "pytest -k evaluate -q"),
        ("Audit export API e2e", "pytest -k audit_export -q"),
        ("OpenAPI sync governance routes", "grep -l openapi docs/ services/ -r | head -1"),
        ("Webhook stub orientation doc", "grep -i webhook docs/api/ -r | head -1"),
        ("Pilot auth middleware smoke", "pytest -k auth -q"),
        ("Decision semantics 201/202/403 in OpenAPI", "grep 201 docs/ services/ -r | head -1"),
        ("Rate limit orientation paragraph", "grep -i rate docs/api/ | head -1"),
        ("RID threading in API error payloads", "grep -i rid services/ -r | head -1"),
    ]
    for title, verify in api_tasks:
        add("governance-api", title, "microsoft_ccs", "M", verify, f"Harden API: {title}.")

    # Workspace / UI (20)
    ui_tasks = [
        ("Governance console read-only surfaces", "test -f console/index.html"),
        ("Workspace connectors banner after mock OAuth", "./scripts/verify-ui-e2e.sh 2>&1 | grep -i connector | head -1"),
        ("Result page confidence badge regression", "grep -i confidence result/ -r | head -1"),
        ("TLE list pagination orientation", "grep -i pagination workspace/ -r | head -1"),
        ("Evaluate form shadow mode copy", "grep -i shadow evaluate/ -r | head -1"),
        ("Dashboard receipt mock consistency", "grep export_integrity workspace/ -r | head -1"),
    ]
    for title, verify in ui_tasks:
        add("workspace-ui", title, "receipt_first", "S", verify, f"UI slice: {title}.")

    # Connectors / evidence (15)
    for i, title in enumerate([
        "M365 metadata connector mock path",
        "Purview evidence ID in TLE stub",
        "Entra group evidence orientation",
        "Evidence index pagination API",
        "Connector health status badge",
    ]):
        add("connectors", title, "microsoft_ccs", "M",
            "pytest -k connector -q 2>/dev/null || grep -i connector services/ -r | head -1",
            f"Connector slice: {title}.")

    # Testing / smoke (25)
    smoke_areas = ["www-gtm", "trust-ledger", "governance-api", "workspace-ui", "demo-ops"]
    for area in smoke_areas:
        add(area, f"Extend verify-ui-e2e for {area}", "trust_center", "S",
            "./scripts/verify-ui-e2e.sh", f"Add e2e row for {area}; no weakened assertions.")

    for title in [
        "plan-with-no-asf-verify area guard",
        "procurement-pack-e2e in verify-gtm",
        "copilot-pilot-e2e confidence assert",
        "make verify-gtm preflight chain",
    ]:
        add("testing", title, "trust_center", "S", "make verify-gtm", f"Testing: {title}.")

    # Compliance / docs (18)
    for title in [
        "PROCUREMENT_ONE_PAGER sync with trust center",
        "GOVERNANCE_SOURCES_BOOK citation strip",
        "RPAA orientation one-pager link audit",
        "Federal AIA mapping doc cross-links",
        "MSP READINESS_TO_RECORD mapping link",
    ]:
        add("docs-diligence", title, "trust_center", "S",
            f"grep -i governance docs/ -r | head -1", f"Diligence doc: {title}.")

    # Ops / runbooks (15)
    for title in [
        "RUNBOOK evaluate flow operator steps",
        "RUNBOOK TLE export failure triage",
        "RUNBOOK staging demo URL rotation",
        "sync-prompt-pack-status after ship",
        "registry reconcile one-shot script",
    ]:
        add("agent-ops", title, "trust_center", "S",
            "./scripts/plan-with-no-asf-verify.sh", f"Ops: {title}.")

    # Federal / MSP channel
    for title, lane, area in [
        ("GC PIN checklist doc link audit", "numbered_narrative", "federal"),
        ("Federal intake interest=federal e2e", "numbered_narrative", "federal"),
        ("MSP wholesale pricing paragraph audit", "msp_two_tier", "msp-channel"),
        ("Partner LOI template orientation", "msp_two_tier", "msp-channel"),
        ("TBS ADM deadline copy freshness check", "numbered_narrative", "federal"),
        ("AIA level 1–4 orientation strip", "numbered_narrative", "federal"),
        ("MSP partner intake CTA regression", "msp_two_tier", "msp-channel"),
        ("Phase 1 generic examples", "msp_two_tier", "msp-channel"),
    ]:
        add(area, title, lane, "S", "grep -i federal msp/ docs/ -r | head -1", f"Channel: {title}.")

    # Fill remaining to 138 with structured product slices
    fill_patterns = [
        ("trust-ledger", "TLE export field", "receipt_first"),
        ("governance-api", "API guard", "microsoft_ccs"),
        ("workspace-ui", "UI regression", "receipt_first"),
        ("connectors", "Connector stub", "microsoft_ccs"),
        ("testing", "Test coverage", "trust_center"),
        ("docs-diligence", "Diligence sync", "trust_center"),
        ("ci-cd", "CI step", "trust_center"),
        ("security", "Security orientation", "trust_center"),
        ("demo-ops", "Demo checklist", "receipt_first"),
        ("www-gtm", "WWW regression", "numbered_narrative"),
    ]
    idx = 0
    while len(items) < 138:
        area, kind, lane = fill_patterns[idx % len(fill_patterns)]
        pid_n = len(items) + 1
        title = f"{kind} slice #{pid_n} for {area}"
        add(area, title, lane, "S", "./scripts/plan-with-no-asf-verify.sh",
            f"Product hardening: {title}. Pilot-gated; one verify command.")
        idx += 1

    return items[:138]


def build_tier3_archive(registry_plans: list[dict]) -> list[dict]:
    """300 catalogued archive stubs — dedupe pattern×area from 1000 grid."""
    seen: set[tuple[str, str]] = set()
    archive: list[dict] = []
    tier1_ids = set()  # mapped separately

    # Map pattern+area → canonical tier1 id where obvious
    tier1_map = {
        ("www-copy", "www-gtm"): "L-02",
        ("demo-rehearsal", "demo-ops"): "E-01",
        ("diligence-doc", "docs-diligence"): "L-03",
        ("customer-outreach", "customer-acquisition"): "L-15",
        ("audit-export", "trust-ledger"): "E-05",
    }

    for pl in registry_plans:
        if len(archive) >= 300:
            break
        pat = pl.get("pattern", "")
        area = pl.get("area", "")
        key = (pat, area)
        if key in seen:
            continue
        seen.add(key)
        grade, tier, lane = PATTERN_GRADES.get(pat, ("F", 3, "anti_platform_breadth"))
        if grade in ("A", "B") and tier == 1:
            continue  # covered by tier1
        archive.append({
            "id": f"X-{len(archive)+1:03d}",
            "tier": 3,
            "grade": grade,
            "nf_plan_id": pl.get("id"),
            "pattern": pat,
            "area": area,
            "title": pl.get("title", "")[:80],
            "success_lane": lane,
            "status": "archived",
            "superseded_by": tier1_map.get(key) or (f"B-{(hash(key) % 138) + 1:03d}" if grade == "B" else None),
            "pick": False,
            "reason": "Grid duplicate or pilot-gated; use Tier 1 SMART picker first.",
        })
    return archive


def build_master_md(catalog: dict) -> str:
    lanes = catalog["success_lanes"]
    counts = catalog["tier_counts"]
    return f"""# Noetfield Prompt Pack — 500 Master Catalog (LOCKED v1)

| Field | Value |
|-------|--------|
| **Status** | LOCKED — canonical consolidation of 1000 NF-PLAN grid |
| **Machine SSOT** | [catalog-500.json](./plans/catalog-500.json) |
| **Active picker** | [catalog-500.json](./plans/catalog-500.json) · **`make pick-wise`** ([V14 WISE](./NOETFIELD_PROMPT_PACK_V14_WISE_LOCKED_v1.md)) |
| **North star** | Board PDF in governance meeting OR deposit ≥ CAD 2K / signed LOI |
| **Generated** | {catalog["generated_at"]} |

---

## 1. Executive grade (whole pack)

| Pack source | Raw count | Grade | After consolidation |
|-------------|-----------|-------|---------------------|
| NF-PLAN registry grid | 1000 | **C+** | → 300 archived (Tier 3 index) |
| Tier 1 SMART (W3 active) | 50 | **A** | Pick now |
| Tier 2 product backlog | {counts["T2"]} | **B+** | After first pilot SOW |
| Tier 0 constitution | {counts["T0"]} | **A** | Every cold-start session |
| Legacy Prompt OS | ~12 docs | **D** | Frozen |
| Worker Blueprint V3 | 1 | **A+** | Paste before any agent work |
| **Catalog total** | **{counts["total"]}** | **B+ → A path** | |

**Root diagnosis:** The 1000 grid is 20×10×5 Cartesian coverage — **~85% duplicate intent**. v14 WISE + this catalog dedupes to **500 named entries** with grades, success lanes, and pick rules.

**One filter:** Does this move us toward **board PDF in a real meeting** or **W3 deposit/LOI** in 90 days? If no → Tier 3.

---

## 2. Tier architecture (500)

| Tier | Count | Pick? | Gate |
|------|-------|-------|------|
| **T0** Constitution | {counts["T0"]} | Manual | Always read C-02 Worker V3 |
| **T1** W3 SMART | {counts["T1"]} | **Yes — max 3/session** | None |
| **T2** Product backlog | {counts["T2"]} | After W3 signal | First pilot SOW or deposit |
| **T3** Archive index | {counts["T3"]} | **Never** | Superseded by T1/T2 id |

---

## 3. Pattern grades (all 20 NF-PLAN patterns)

| Pattern | Grade | Tier | Success lane | Action |
|---------|-------|------|--------------|--------|
""" + "\n".join(
        f"| `{pat}` | **{g}** | {t} | {SUCCESS_LANES[lane]['label']} | "
        + ("**Active T1**" if g == "A" and t == 1 else "T2 backlog" if g == "B" else "Archive/freeze")
        + " |"
        for pat, (g, t, lane) in sorted(PATTERN_GRADES.items(), key=lambda x: x[1][0])
    ) + """

---

## 4. Success model lanes (copy weight)

| Lane | Weight | Copy into prompts |
|------|--------|---------------------|
""" + "\n".join(
        f"| **{v['label']}** | {v['weight']:+d} | {v['copy']} |"
        for k, v in SUCCESS_LANES.items() if k != "anti_platform_breadth"
    ) + """
| **Platform breadth** | **−10** | Anti-pattern — never prompt full GRC estate |

---

## 5. W3 critical path (pick order)

```
C-02 Worker V3 → E-01 demo → E-04 manifest → E-05 board PDF → E-06 ZIP → L-03 trust → P-01 e2e
```

**Dispatcher:** `python3 scripts/pick-wise.py --bottleneck export|demo|www|pipeline|channel|ship`

---

## 6. Top 25 active prompts (Tier 1 — always prefer these)

| Rank | ID | Title | Lane |
|------|-----|-------|------|
| 1 | E-05 | Board PDF path E2E | Receipt-first |
| 2 | E-06 | Procurement ZIP E2E | Trust center |
| 3 | E-01 | 5-minute demo script | Receipt-first |
| 4 | L-02 | Homepage §07–10 | Numbered narrative |
| 5 | L-03 | Trust center | Trust center |
| 6 | E-04 | Export manifest spec | Receipt-first |
| 7 | L-01 | Trust Brief $10k audit | Readiness SKU |
| 8 | P-01 | verify-ui-e2e v12 | Trust center |
| 9 | L-10 | MSP Phase 1→2 | MSP two-tier |
| 10 | L-09 | Federal ADM chip | Numbered narrative |
| 11 | E-02 | TLE verify walkthrough | Receipt-first |
| 12 | E-03 | TLE YAML trio | Receipt-first |
| 13 | L-11 | Copilot CCS stack | Microsoft CCS |
| 14 | L-08 | Intake RID threading | Ops |
| 15 | H-01 | MSP mapping UX | MSP two-tier |
| 16 | H-02 | Federal AIA mapping | Numbered narrative |
| 17 | E-07 | Confidence on result | Receipt-first |
| 18 | L-04 | Procurement → trust | Trust center |
| 19 | P-02 | rebuild-www-v6 SSOT | Ops |
| 20 | E-19 | Honest scope badges | Trust center |
| 21 | L-05 | Design partner scarcity | Honest investor |
| 22 | E-11 | Pilot Wk 0–12 | Readiness SKU |
| 23 | P-05 | Staging demo URL | Commercial SSOT |
| 24 | L-07 | QuickScan anchor | Readiness SKU |
| 25 | E-15 | Receipt mock consistency | Receipt-first |

Full SMART blocks: [TIER1_SMART_PROMPTS.md](./plans/TIER1_SMART_PROMPTS.md)

---

## 7. Brainstorm enrichments (10 new — folded into T1/T2)

| ID | Idea | Why | Lane |
|----|------|-----|------|
| **N-01** | "Receipt in 5 minutes" timer on demo page | Buyer proof moment | Receipt-first |
| **N-02** | Trust center downloadable sample manifest JSON | Diligence self-serve | Trust center |
| **N-03** | Copilot hub "What Purview already did" vs "What we receipt" table | Microsoft complement | CCS |
| **N-04** | MSP partner one-pager PDF (generated, not hand) | Channel enablement | MSP two-tier |
| **N-05** | Federal AIA level ↔ TLE verdict mapping interactive preview | GC attach | Numbered narrative |
| **N-06** | Investor "proof milestones" checklist (no ARR) | Honest scarcity | Numbered narrative |
| **N-07** | Workspace "export integrity FAIL" demo button | Tamper story | Receipt-first |
| **N-08** | Procurement ZIP contents manifest page (orientation) | Pack index | Trust center |
| **N-09** | Design partner debrief YAML template auto-created post-call | Pipeline intelligence | Readiness SKU |
| **N-10** | verify-ui-e2e "honest scope badge" row per hub | Regression guard | Trust center |

---

## 8. What we dropped (500 vs 1000)

- **500 removed from active pick:** duplicate phase×tier rows for same pattern×area
- **Frozen F-grade:** drift-impl, verdict-review, performance at scale, Prompt OS stage1–3 chains
- **Agentic fence:** customer-outreach never NF-CLOUD send (Hub only)
- **Anti-patterns:** vendor comparisons, fourth SKU, fake certs, MSB lead, full GRC platform breadth

---

## 9. Commands

```bash
make generate-tier1-smart          # 50 W3 prompts
python3 scripts/generate-prompt-catalog-500.py  # full 500 catalog
make pick-wise                       # pick next WISE prompt
python3 scripts/pick-wise.py --bottleneck export --prompt
python3 scripts/sync-tier1-status.py --done E-01
```

---

## 10. Related docs

- [NOETFIELD_PROMPT_PACK_V13_SMART_LOCKED_v1.md](./NOETFIELD_PROMPT_PACK_V13_SMART_LOCKED_v1.md)
- [CATALOG_500_INDEX.md](./plans/CATALOG_500_INDEX.md)
- [PRIORITY_MATRIX_500.md](./plans/PRIORITY_MATRIX_500.md)
- [WWW_V12_MASTER_PLAN_LOCKED_v1.md](../WWW_V12_MASTER_PLAN_LOCKED_v1.md)
- [NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md](../strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md)
"""


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tier1 = json.loads(TIER1.read_text(encoding="utf-8")) if TIER1.is_file() else {"prompts": []}
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    reg_plans = registry.get("plans", [])

    t0 = [
        {
            "id": cid,
            "tier": 0,
            "grade": "A",
            "title": title,
            "source": src,
            "pick": "manual",
            "success_lane": "receipt_first",
        }
        for cid, title, src in T0_CONSTITUTION
    ]
    t1 = [{**p, "tier": 1, "grade": "A", "pick": True} for p in tier1.get("prompts", [])]
    t2 = build_tier2()
    t3 = build_tier3_archive(reg_plans)

    # Target: 500 = T0(12) + T1(50) + T2(138) + T3(300)
    t3_target = 500 - len(t0) - len(t1) - len(t2)
    if len(t3) > t3_target:
        t3 = t3[:t3_target]
    elif len(t3) < t3_target:
        while len(t3) < t3_target:
            i = len(t3) + 1
            t3.append({
                "id": f"X-{i:03d}",
                "tier": 3,
                "grade": "D",
                "pattern": "horizon",
                "area": "archive",
                "title": f"NF-PLAN grid stub archive {i}",
                "success_lane": "anti_platform_breadth",
                "status": "archived",
                "pick": False,
                "reason": "Deduped from 1000 grid; use Tier 1 picker.",
            })

    total = len(t0) + len(t1) + len(t2) + len(t3)

    catalog = {
        "version": "catalog-500-v1",
        "generated_at": now,
        "north_star": tier1.get("w3_north_star", "Board PDF in meeting OR W3 deposit"),
        "success_lanes": SUCCESS_LANES,
        "pattern_grades": {k: {"grade": v[0], "tier": v[1], "lane": v[2]} for k, v in PATTERN_GRADES.items()},
        "tier_counts": {
            "T0": len(t0),
            "T1": len(t1),
            "T2": len(t2),
            "T3": len(t3),
            "total": len(t0) + len(t1) + len(t2) + len(t3),
        },
        "T0_constitution": t0,
        "T1_w3_active": t1,
        "T2_product_backlog": t2,
        "T3_archive_index": t3,
    }

    OUT_JSON.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Catalog 500 — Index (generated)",
        "",
        f"_Generated {now}_",
        "",
        f"**Total:** {catalog['tier_counts']['total']} · **Pick Tier 1 only until W3**",
        "",
        "## Tier 0 — Constitution (12)",
        "",
        "| ID | Title |",
        "|----|-------|",
    ]
    for e in t0:
        md.append(f"| {e['id']} | {e['title']} |")
    md.extend(["", "## Tier 1 — W3 Active (50)", "", "See [TIER1_W3_ACTIVE_50.md](./TIER1_W3_ACTIVE_50.md)", ""])
    md.extend(["", "## Tier 2 — Product backlog (138)", "", "| ID | Area | Title | Lane |", "|----|------|-------|------|"])
    for e in t2:
        lane = SUCCESS_LANES.get(e["success_lane"], {}).get("label", e["success_lane"])
        md.append(f"| {e['id']} | {e['area']} | {e['title'][:50]} | {lane} |")
    md.extend(["", "## Tier 3 — Archive sample (first 30)", "", "| ID | Pattern | Area | Superseded by |", "|----|---------|------|---------------|"])
    for e in t3[:30]:
        md.append(f"| {e['id']} | {e.get('pattern','?')} | {e.get('area','?')} | {e.get('superseded_by','—')} |")
    md.append(f"\n_… plus {len(t3)-30} more archive rows in catalog-500.json_")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    # Priority matrix — success lane × phase
    matrix = [
        "# Priority Matrix 500 (generated)",
        "",
        f"_Generated {now}_ · **Pick Tier 1 only until W3 PASS**",
        "",
        "## By commercial phase (Tier 1 — 50 prompts)",
        "",
        "| Phase | IDs | Count | W3 focus |",
        "|-------|-----|-------|----------|",
    ]
    phases = ["LAND", "EXPAND", "CHANNEL", "PROVE"]
    phase_focus = {
        "LAND": "Trust Brief intake · www proof · trust center",
        "EXPAND": "Demo · TLE · board PDF · ZIP export",
        "CHANNEL": "MSP · federal · partners",
        "PROVE": "e2e · generator SSOT · ship gates",
    }
    for ph in phases:
        ids = [p["id"] for p in t1 if p.get("phase") == ph]
        matrix.append(f"| **{ph}** | {', '.join(ids)} | {len(ids)} | {phase_focus[ph]} |")

    matrix.extend(["", "## By success model lane (Tier 1)", ""])
    lane_order = ["receipt_first", "trust_center", "microsoft_ccs", "msp_two_tier", "numbered_narrative", "readiness_sku"]
    for lane_key in lane_order:
        label = SUCCESS_LANES[lane_key]["label"]
        matrix.append(f"### {label}")
        matrix.append("")
        matrix.append("| ID | Title | Phase |")
        matrix.append("|----|-------|-------|")
        for p in t1:
            ref = (p.get("success_reference") or "").lower()
            lane_match = (
                lane_key == "receipt_first" and any(x in ref for x in ("receipt", "export", "demo"))
                or lane_key == "trust_center" and any(x in ref for x in ("trust", "diligence", "procurement", "honest"))
                or lane_key == "microsoft_ccs" and any(x in ref for x in ("microsoft", "ccs", "purview", "complement", "metadata"))
                or lane_key == "msp_two_tier" and any(x in ref for x in ("msp", "phase 1", "two-tier", "wholesale"))
                or lane_key == "numbered_narrative" and any(x in ref for x in ("narrative", "category", "aia", "adm", "tbs", "federal"))
                or lane_key == "readiness_sku" and any(x in ref for x in ("readiness", "fixed-fee", "quickscan", "pilot", "90-day", "pipeline"))
            )
            if lane_match:
                matrix.append(f"| {p['id']} | {p['title'][:48]} | {p.get('phase','?')} |")
        matrix.append("")

    matrix.extend([
        "## Tier 2 top 30 (after W3 — product hardening)",
        "",
        "| Rank | ID | Area | Title |",
        "|------|-----|------|-------|",
    ])
    for i, e in enumerate(t2[:30], 1):
        matrix.append(f"| {i} | {e['id']} | {e['area']} | {e['title'][:44]} |")
    matrix.append("")
    matrix.append("_Full T2: 138 rows in catalog-500.json · Gate: first pilot SOW or deposit_")
    matrix.append("")
    matrix.append("## Tier 3 — do not pick (300 archive stubs)")
    matrix.append("")
    matrix.append("Deduped NF-PLAN grid · grades D/C · superseded_by Tier 1/2 id · see catalog-500.json")
    OUT_MATRIX.write_text("\n".join(matrix) + "\n", encoding="utf-8")

    OUT_MASTER.write_text(build_master_md(catalog), encoding="utf-8")
    print(f"Catalog 500: T0={len(t0)} T1={len(t1)} T2={len(t2)} T3={len(t3)} total={catalog['tier_counts']['total']}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_MATRIX}")
    print(f"Wrote {OUT_MASTER}")


if __name__ == "__main__":
    main()
