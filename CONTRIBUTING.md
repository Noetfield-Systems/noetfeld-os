# Contributing — noetfeld-os

**Product:** Noetfield OS (Governance Execution Layer)  
**Owner:** Noetfield Systems Inc.

---

## Agent lanes

| Lane | May edit | Must not edit |
|------|----------|---------------|
| `noetfeld-os-cursor-chat` | Code, `docs/_NOOS_AGENT/**` (tagged) | Mono runtime, SourceA SSOT |
| Other agents | Their own repos/tags | `docs/_NOOS_AGENT/**` without merge task |

Search agent docs: `grep -r "NOOS-AGENT-DOC" docs/_NOOS_AGENT/`

---

## Document vault rules

1. All agent intelligence lives in `docs/_NOOS_AGENT/` with `NOOS-AGENT-DOC` tag blocks.
2. Grant PDFs and pitch decks live in `docs/output/` — **not** in the agent vault.
3. Update `docs/_NOOS_AGENT/MANIFEST.json` when adding vault documents.
4. Mark completed roadmap steps in `docs/_NOOS_AGENT/ROADMAP_MANIFEST.json`.
5. Run before commit:

```bash
bash scripts/check_noos_agent_docs.sh
```

---

## Code guidelines

- **Non-custodial:** governance signals only (APPROVE / REVIEW / DECLINE).
- **Pre-execution:** never trigger downstream execution from this API.
- **Fail closed:** policy/DB failures must not allow unchecked decisions.
- **Isolation:** do not import or depend on SinaaiMonoRepo `:8000` runtime.

---

## Plane tags

Use `[DESIGN]`, `[EXECUTION]`, `[DELIVERY]` on cross-repo claims. See `docs/_NOOS_AGENT/[NOOS-AGENT-20260615-007]_GLOSSARY_AND_PLANE_TAGS.md`.

---

## Local setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn run:app --reload --port 8001
```

Use port **8001** locally if mono runtime occupies `:8000`.

### Phase 2 API (auth required)

```bash
python3 scripts/mint_api_key.py   # creates api_keys.local.json
.venv/bin/uvicorn run:app --reload --port 8001

curl -s http://127.0.0.1:8001/health | python3 -m json.tool
curl -s -X POST http://127.0.0.1:8001/v1/decision \
  -H 'Content-Type: application/json' \
  -H "X-API-Key: $(python3 -c "import json; print('see mint output')")" \
  -d '{"applicant_id":"demo","credit_score":720,"monthly_debt":1200,"monthly_income":6000,"loan_amount":250000,"collateral_value":320000,"employment_history_years":4,"liquid_reserves_months":6}'
```

Run tests: `.venv/bin/pytest tests/ -v`

**Note:** Delete `noetfeld.db` once if upgrading from pre-Phase-2 schema.

---

*Proprietary — see LICENSE*
