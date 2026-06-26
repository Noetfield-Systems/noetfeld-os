# Governance Runtime — API Docs Link Map

**Version:** 1.0.0 · **Plan:** pf-0061 · **SKU:** NF-QS (platform) · **Phase:** 5  
**Law:** Runtime/API is platform adjacency — **not** a fourth www contract SKU

---

## One line

`/runtime/` links to live evaluate API docs at `/docs/api/` — canonical map for `POST /api/v1/governance/evaluate`, OpenAPI, and sandbox upgrade path.

---

## Canonical URLs

| Surface | URL | Purpose |
|---------|-----|---------|
| Governance Runtime (www) | `/runtime/` | Product narrative · evaluate flow · template deploy |
| API reference (www) | `/docs/api/` | Human-readable endpoint table |
| OpenAPI JSON | `/docs/api/openapi.json` | Machine contract |
| OpenAPI YAML | `/docs/api/openapi.yaml` | Partner import |
| Partner pre-execution | `/docs/api/PARTNER_PRE_EXECUTION.md` | Shadow vs enforce sequence |

---

## Primary endpoint

```http
POST /api/v1/governance/evaluate
```

**Host (production):** `https://platform.noetfield.com`  
**Host (local dev):** `http://127.0.0.1:8787` (wrangler / worker)

**Decisions:** `PROCEED` · `REQUIRE_HUMAN_REVIEW` · `REJECT`

---

## Link map (runtime → API)

| Runtime section | API anchor |
|-----------------|------------|
| How it works · Evaluate | `POST /api/v1/governance/evaluate` |
| Trust Ledger | `GET /api/v1/governance/ledger` |
| Audit export | `GET /api/v1/governance/audit-export` |
| Sandbox trial | `/start/` → API key drawer → `/docs/api/` |

---

## www alignment

- `/runtime/index.html` — **Governance API** section with CTA to `/docs/api/`
- `/templates/index.html` — secondary link to `/docs/api/`
- `/start/index.html` — API drawer links to `/docs/api/`

---

## Not in scope

- Payment rails · custody · MSB execution
- TrustField RPAA program APIs
- Fourth contract SKU — three www offerings unchanged (Trust Brief · Copilot Pack · Bank Pilot)

---

## Verify

```bash
grep -q '/docs/api/' runtime/index.html
grep -q 'governance/evaluate' docs/runtime/NF_RUNTIME_API_DOCS_LINK_v1.md
```
