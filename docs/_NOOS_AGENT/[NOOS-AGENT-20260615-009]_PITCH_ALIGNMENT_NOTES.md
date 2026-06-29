# [NOOS-AGENT-20260615-009] Pitch & PDF Alignment Notes

<!--
NOOS-AGENT-DOC
agent_id: noetfeld-os-cursor-chat
agent_lane: NOETFELD-OS
trace_id: NOOS-AGENT-20260615-009
doc_type: ALIGNMENT_AUDIT
workspace_root: /Users/sinakazemnezhad/Projects/noetfeld-os
classification: INTERNAL — grant/pitch drift flags (Step 0008)
-->

**Step:** 0008 — Align pitch deck PDFs with positioning; flag engineering drift

---

## Canonical positioning source

`NOOS-AGENT-20260529-002` — Business, product & client definition

**External one-liner (use in all PDFs):**

> Noetfield OS evaluates policy, scores risk, and produces audit-ready evidence before your systems execute.

---

## Known drift (fix before external send)

| Issue | PDF / deck location | Code truth | Action |
|-------|---------------------|------------|--------|
| **SQLite vs Postgres** | Grant narrative may claim Postgres append-only audit | `database.py` uses SQLite WAL | Footnote: "Pilot: SQLite; production target: Postgres Phase 3" OR update PDF to match prototype |
| **Production readiness** | Pitch may overstate scale/SLA beyond current GEL | `api.noetfield.com` health/readiness is live on Railway; runtime remains pilot/prototype-grade with SQLite WAL | Say "live GEL pilot runtime" and avoid enterprise SLA, multi-region, or Postgres claims until shipped |
| **Golden Edge v3** | Some slides reference Golden Edge as core | SSOT: Golden Edge = optional scoring at `:8001` | Remove or demote to optional integration slide |
| **TrustField conflation** | Avoid implying TrustField is inside Noetfield OS | Separate peer company | Use identity separation table from portfolio SSOT v3.1 |
| **Custody language** | Any "process payments" wording | Non-custodial GEL only | Replace with "governance signals" |

---

## Regenerate after fixes

```bash
pip install fpdf2 python-pptx
python docs/scripts/build_documents.py
```

Outputs: `docs/output/external/` · `docs/output/internal/`

---

## ASF sign-off (Steps 0009–0010)

- [ ] ASF 30-min positioning review scheduled
- [ ] Decision recorded in `ROADMAP_MANIFEST.json` under `asf_signoff`
- [ ] If approved: publish `NOOS-AGENT-20260529-002-rev1` changelog entry

---

*End alignment notes — `NOOS-AGENT-20260615-009`*
