# Noetfield — Documentation

## Agent-owned docs (this Cursor chat only)

**Search token:** `NOOS-AGENT-DOC`  
**Vault:** `docs/_NOOS_AGENT/`  
**Index:** `docs/_NOOS_AGENT/MANIFEST.json`  
**Entrypoint:** `AGENTS.md` (repo root)

Other agents: do not edit tagged files without an explicit merge task. Use your own tag in your own lane.

---

## Grant & pitch PDFs

Generated PDFs and slide decks for **internal** and **external** audiences.

## Build

```bash
pip install fpdf2 python-pptx
python docs/scripts/build_documents.py
```

## Output layout

```
docs/output/
├── external/          # IRAP reviewers, partners, prospects
│   ├── grant-core-narrative.pdf
│   ├── loi-template.pdf
│   ├── budget-breakdown.pdf
│   ├── strategic-positioning.pdf
│   ├── pitch-deck-noetfield-gel.pptx
│   └── pitch-deck-handout.pdf
└── internal/          # team, sales, engineering
    ├── grant-core-narrative.pdf      (+ build status appendix)
    ├── loi-template.pdf              (+ sales notes)
    ├── budget-breakdown.pdf            (+ commercial ladder)
    ├── strategic-positioning.pdf       (+ moat & messaging)
    ├── reality-check.pdf               (internal only)
    ├── pitch-deck-noetfield-gel.pptx   (+ slide 11 reality/commercial)
    └── pitch-deck-handout.pdf
```

## Audience guide

| Document | External use | Internal use |
|---|---|---|
| Grant core narrative | IRAP / BC Innovation submission | Same + engineering truth table |
| LOI template | Send to pilot partners | + sales follow-up playbook |
| Budget breakdown | Funder-facing $120K model | + $10K / $50K / $120K ladder |
| Strategic positioning | Partner one-pager | + competitive moat & do/don't |
| Reality check | — | Engineering + 30-day priorities |
| Pitch deck (.pptx) | IRAP / partner meetings | + build & commercial slide |

## Regenerate after edits

Edit `docs/scripts/build_documents.py` and re-run the build command.
