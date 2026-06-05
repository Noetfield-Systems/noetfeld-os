# Knowledge Ingestion Pipeline v1 (design)

**Global control:** No assertive answer without `verification_status: verified` and at least one source in `rag-answer.schema.json`.

## Source corpora (Lane A)

| Corpus | Path | Use |
|--------|------|-----|
| Source of truth | `docs/SOURCE_OF_TRUTH/` | Policy minutes, institutional narrative |
| Evaluate exports | `GET /audit/export` | RID-linked decisions |
| Policy packs | `docs/spec/samples/*.json` | Control binding |
| Locked strategy | `docs/strategy/NOETFIELD_COPILOT_SME_SYSTEM_DESIGN_LOCKED_v1.md` | Scope guard |

## Pipeline stages

1. **Extract** — Markdown/JSON → chunks with `tenant_id` tag (pilot: single tenant).
2. **Hash** — SHA-256 per chunk; store alongside `integrity_hash` alignment.
3. **Index** — Offline prototype: local JSON index (defer vector DB until RLS proven).
4. **Retrieve** — Top-k by keyword + metadata filter (`control_id`, `rid`).
5. **Answer** — Emit `rag-answer` JSON only; block publish if `verification_status != verified`.

## Prototype script (optional post–Phase 1B)

`scripts/rag-index-sot-prototype.py` — index 10–20 docs from `docs/SOURCE_OF_TRUTH` (not required for pilot gate).

## Deferred

- Production pgvector / external vector store
- Cross-tenant retrieval (forbidden until tenant RLS on audit + policy)
