# [NOOS-AGENT-20260615-012] Chain Tools Strategy — Graphify Pattern for Noetfield

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260615-012
doc_type: CHAIN_TOOLS_STRATEGY
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL
related_docs: NOOS-AGENT-20260615-010, NOOS-AGENT-20260529-002
-->

**Status:** Active · 2026-06-15

---

## Pattern (Graphify-class)

Chain tools sit **between** the developer and the AI — not as the AI.

| Property | Noetfield implementation |
|----------|-------------------------|
| One command in | `noetfield gate` · `noetfield decide` |
| One artifact out | `gate-report-v1.json` + `.md` · `decision-receipt.json` |
| Every execution | Run gate before agent dispatch; decide before side effects |
| Zero config default | Auto-detect repo root; optional env overrides |
| Open core | `pip install -e .` from this repo |
| Paid tier (later) | Hosted `api.noetfield.com` + API keys |

---

## Three publishable tools (portfolio map)

| Tool | Lane | Status on disk |
|------|------|----------------|
| `critic_boot_v1.py` | SourceA portfolio boot | SourceA repo |
| `noetfield gate` | GEL pre-flight | **This repo — `noetfield_gate/`** |
| `POST /v1/decision` | Policy gate API | FastAPI `:8001` |
| `noetfield decide` | CLI → API → receipt | **This repo — `noetfield_gate/decide.py`** |

SourceA `sourcea-boot` (pip) remains **SourceA Worker scope** — do not merge into Noetfield ship runtime.

---

## SW1 / Buyer 1 motion

```bash
pip install -e ~/Projects/noetfeld-os
python3 run.py &   # :8001
export NOETFIELD_API_KEY=$(python3 scripts/mint_api_key.py --print-key 2>/dev/null || echo $KEY)
noetfield gate
noetfield decide --sample
```

**TTFD target:** <5 minutes to PASS gate + one receipt on disk.

---

## Build checklist (future PyPI)

1. Pain: agents execute without policy proof
2. Smallest fix: `noetfield gate` + `noetfield decide`
3. Persistent output: JSON receipts
4. Publish: `noetfield-gate` on PyPI (name TBD legal)
5. npm SDK for `POST /v1/decision` — Phase 7 with `api.noetfield.com`

---

## Files

| Path | Role |
|------|------|
| `noetfield_gate/` | Package source |
| `pyproject.toml` | `pip install -e .` |
| `packages/noetfield-gate/README.md` | 3-line developer README |
| `tests/test_noetfield_gate.py` | CLI unit tests |
