# Noetfield MCP Cloud Chain Plan — LOCKED v1 (111 steps)

**Version:** 1.0.0 · **Saved:** 2026-06-19T12:00:00Z · **Authority:** ASF suggestion from SourceA  
**Copy target:** `~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/os/plan-library/SOURCEA_SUGGESTION_MCP_CHAIN_LOCKED_v1.md`  
**Campus:** Governance / TLE · board go/no-go · Copilot readiness  
**Motor (read-only):** SourceA FBE · **Lead P2 gateway partner**

---

## 0. Chain position

| Role | Primary | Buyer |
|------|---------|-------|
| **Campus host** | `noetfield-governance` MCP | CISO · GRC · procurement |
| **Chain provider** | `evaluate_pick` · `export_board_line` | Enterprise board pack |
| **Gateway partner (P2)** | Policy + immutable audit behind Composio/enterprise gateway | Regulated buyers |

**One sentence:** Governed TLE eval with board-defensible receipts — not another GRC checkbox.

**Mac:** Control plane · procurement vault links only. **Cloud:** Azure Functions / Vercel + Supabase for TLE store.

---

## 1. Cloud architecture

```text
Cursor / Claude enterprise
    → Notion MCP (policy docs) · Linear MCP (GOV issues)
    → noetfield-governance MCP (cloud)
        → evaluate_pick · export_board_line · tle_receipt_status
    → Board PDF / JSON export → buyer GRC tool
P2: Enterprise MCP Gateway → Noetfield policy pack → receipt hash chain
```

---

## 2. MCP spec (`io.github.noetfield/noetfield-governance`)

```json
{
  "tools": [
    { "name": "evaluate_pick", "input": { "pick": "A|B|C|D", "subject": "string", "policy_pack_id": "string" }, "output": { "verdict": "GO|NO_GO|MOCK_ONLY", "tle_score": "number", "board_line": "string" } },
    { "name": "export_board_line", "input": { "receipt_id": "string", "format": "pdf|json" }, "output": { "export_url": "string", "watermark": "freemium|production" } },
    { "name": "tle_receipt_status", "input": { "receipt_id": "string" }, "output": { "status": "object" } },
    { "name": "list_factories", "input": {}, "output": { "factories": [], "specialist_teams": [] } }
  ]
}
```

**Marketplace card:** **Noetfield Governance** · Categories: **Agent Orchestration** · **Infrastructure**

---

## 3. Learn from market (applied)

| Insight | Noetfield action |
|---------|------------------|
| 92% MCP servers high security risk (MintMCP 2026) | Lead with read-mostly + policy pack + audit export |
| Enterprise registry needs SSO/RBAC/audit | P2 gateway partner — Noetfield policy pack |
| Cursor private team marketplace | Enterprise plugin with governance MCP scoped |
| Microsoft Agent Governance Toolkit (Apr 2026) | Position as operational TLE — not replacement |
| Notion MCP for policy capture | Consumer lane — research → TLE input |

---

## 4. Steps 001–111

### T01 Chain consumer (001–010)

| # | Cloud worker task |
|---|-------------------|
| 001 | Notion MCP auth — policy doc ingest read-only |
| 002 | Linear GOV SOURCEA mirror for governance issues |
| 003 | GitHub MCP for procurement repo evidence links |
| 004 | Never write `~/.sina` — TLE receipts to cloud bucket |
| 005 | `make nf-onboard` remains SSOT for local dev |
| 006 | MCP assists `pytest tests/unit/test_governance_runtime_10step.py` |
| 007 | Form pick bridge: SourceA `form_pick_parse` → `evaluate_pick` |
| 008 | Fixture `fixtures/board-pick-A.json` |
| 009 | Honest MOCK_ONLY on sandbox eval |
| 010 | `validate-noetfield-factory-catalog.sh` mcp section |

### T02 noetfield-governance MCP (011–020)

| # | Task |
|---|------|
| 011 | `packages/mcp-governance/` Python MCP (align with runtime) |
| 012 | `evaluate_pick` wraps 10-step governance runtime |
| 013 | 30s demo cap · watermarked freemium export |
| 014 | `export_board_line` PDF generator (cloud) |
| 015 | `tle_receipt_status` read Supabase |
| 016 | `list_factories` from REGISTRY.json |
| 017 | SSE on Vercel serverless |
| 018 | stdio for `python -m noetfield_mcp` |
| 019 | API key + org_id tenancy |
| 020 | OpenAPI `openapi/mcp-governance-v1.yaml` |

### T03 Campus catalog API (021–030)

| # | Task |
|---|------|
| 021 | Expose `/api/factory/catalog` from static site upgrade |
| 022 | `factory/index.html` fetch cloud API not local `/os/` path |
| 023 | Studio tab loads spec from CDN |
| 024 | Sandbox Bay calls `evaluate_pick` MCP proxy |
| 025 | Teams premium lock API flag |
| 026 | `noetfield-rent-line-v1.json` in catalog P2 |
| 027 | Copilot pack factory card API |
| 028 | Federation webhook to SourceA motor |
| 029 | Investors diligence vault link (read-only) |
| 030 | `make mcp-validate` target |

### T04 Cloud worker runtime (031–042)

| # | Task |
|---|------|
| 031 | **PICK** — deploy `mcp-governance` to Azure Functions or Vercel |
| 032 | Supabase project Noetfield-only TLE tables |
| 033 | `emit-governance-receipt.py` cloud upload mode |
| 034 | CI: pytest + validate-noetfield-factory-catalog |
| 035 | Preview deploy per PR |
| 036 | Structured audit logs |
| 037 | Cron TLE retention policy job |
| 038 | Idempotent evaluate_pick |
| 039 | p99 < 2s read status |
| 040 | Degrade MOCK_ONLY if policy pack missing |
| 041 | Mac README cloud endpoints only |
| 042 | `make mcp-chain-pick STEP=N` |

### T05 Registry (043–050)

| # | Task |
|---|------|
| 043 | PyPI/npm dual publish `@noetfield/mcp-governance` |
| 044 | Official MCP Registry |
| 045 | `io.github.noetfield/noetfield-governance` |
| 046 | Glama: "governance receipt TLE" |
| 047 | README procurement-grade tone |
| 048 | SECURITY.md ABAC doc |
| 049 | v1.0.0 tag |
| 050 | Linear MCP-PUBLISH-noetfield |

### T06 Cursor plugin (051–060)

| # | Task |
|---|------|
| 051 | Plugin manifest governance + skills |
| 052 | Skill: conscious-recovery for board lines |
| 053 | Rules: no chat SSOT |
| 054 | mcp.json fragment |
| 055 | Demo: pick eval → board PDF |
| 056 | Agent Orchestration category |
| 057 | Enterprise private marketplace doc |
| 058 | Cloud Agent "GRC Eval" preset |
| 059 | Allowlist evaluate_pick |
| 060 | T1 disclosure only |

### T07 GitHub + Linear (061–070)

| # | Task |
|---|------|
| 061 | GitHub Action board line on governance PR |
| 062 | PR comment GO/NO_GO |
| 063 | Linear GOV issues for TLE regressions |
| 064 | Label `tle-receipt` |
| 065 | GTM mirror weekly |
| 066 | Procurement issue template |
| 067 | Cursor↔Linear official |
| 068 | No Noetfield queue in Linear |
| 069 | Integration Leverage |
| 070 | CISO partner one-liner |

### T08 Supabase + Vercel (071–080)

| # | Task |
|---|------|
| 071 | Supabase `tle_receipts` table |
| 072 | RLS org_id |
| 073 | Vercel deploy MCP + `/factory/` static |
| 074 | Edge auth |
| 075 | Not SourceA SSOT |
| 076 | Signed PDF export URL |
| 077 | Watermark freemium exports |
| 078 | Preview federation |
| 079 | Free tier |
| 080 | Stripe ROI gate P3 |

### T09 Receipt schemas (081–091)

| # | Task |
|---|------|
| 081 | `noetfield-tle-receipt-v1` |
| 082 | `board_line` required field |
| 083 | Verdict GO/NO_GO/MOCK_ONLY |
| 084 | export_url PDF + JSON |
| 085 | Federation envelope |
| 086 | emit-governance-receipt cloud |
| 087 | Fixtures from 10-step test |
| 088 | Board pack ZIP |
| 089 | NIST AI RMF mapping |
| 090 | Copilot readiness line |
| 091 | Incident on watermark bypass |

### T10 Monetization (092–101)

| # | Task |
|---|------|
| 092 | Sandbox $0 MOCK_ONLY |
| 093 | Freemium capped evals |
| 094 | Premium full TLE + PDF |
| 095 | Team hire governance crew |
| 096 | Rent line P2 |
| 097 | Stripe billing copy platform-neutral |
| 098 | CAD discovery path link |
| 099 | 30s demo video |
| 100 | `/factory/` MCP install CTA |
| 101 | plan.json factory_campus phase update |

### T11 Gateway partner LEAD (102–111)

| # | Task |
|---|------|
| 102 | **LEAD** Composio/enterprise gateway partner brief |
| 103 | Policy pack YAML `policy-packs/enterprise-default.yaml` |
| 104 | Immutable audit log schema |
| 105 | Gateway middleware PoC |
| 106 | ABAC tool allowlist per agent |
| 107 | Tamper-evident hash chain |
| 108 | MintMCP enterprise registry study |
| 109 | SOC2 direction appendix |
| 110 | 1 GRC design partner |
| 111 | **SHIP:** Registry + gateway PoC + board export demo |

---

## 5. Cloud worker first command

```bash
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield
make mcp-chain-pick STEP=031
```

**P2 ownership:** Noetfield leads gateway partner track T11 for entire stack.
