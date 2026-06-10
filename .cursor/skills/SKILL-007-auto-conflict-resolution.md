# SKILL-007 — Auto conflict resolution (all agents)

**When:** Any time two or more rules, skills, cursor rules, or founder laws disagree — **before** first disk edit.

**Authority:** R-010 · INCIDENT-2026-06-06-002 · INCIDENT-2026-06-06-005

---

## Precedence ladder (highest wins)

| Tier | Source | Examples |
|------|--------|----------|
| **T0** | Founder **current message** explicit order | `implement X`, `PLAN WITH NO ASF iter 6 implement`, `WRITE DOWN incidents` |
| **T1** | Hard rules **R-001–R-011** | Noetfield only, no private commit, permission, always ask, SourceA block, no AUTO-RUN / agentic commercial fence |
| **T2** | Open **P0/P1 incidents** | Stop wrong scope; obey ask-first while 002/005 open |
| **T3** | Portfolio / Brain law | `execution_authority: false` — advise only unless T0 ship order |
| **T4** | Bounded **workflow triggers** (only after T0) | PLAN WITH NO ASF bundle, named implement task |
| **T5** | Ship-first / backlog convenience | `os/plan.json`, QUICK_PICK — **never** self-start edits |

**Golden resolver:** *If ship-first/no-ASF says "implement now" but R-007/R-008 say "ask first" → **R-007/R-008 win** until T0 founder order.*

---

## Auto-resolve algorithm

```
ON session start OR before first disk mutation:
  1. LOAD memory hard_rules + open incidents
  2. PARSE user message for T0 explicit order
  3. IF workflow rule says implement AND T0 missing:
       CONFLICT → go to step 5
  4. IF T0 present AND bounded:
       RESOLVE → T4 workflow allowed inside T0 bundle only
       PROCEED with SKILL-001 scope gate → edit
  5. CONFLICT HANDLER:
       a. Name both rules in one line each
       b. State winner per ladder above
       c. Propose options A/B/C (advise vs bounded implement)
       d. ASK founder — ZERO disk edits
  6. ON session end: if conflict occurred, note in summary
```

---

## Known conflict pairs (pre-resolved)

| Rule A | Rule B | Winner | Allowed path |
|--------|--------|--------|--------------|
| `noetfield-ship-first` — ship without waiting | R-007 / R-008 — ask + permission | **R-007/R-008** | Founder says session ship order first |
| `noetfield-no-asf-plans` — implement ≤3 tasks | R-008 — ask first | **R-008** until founder says `PLAN WITH NO ASF` + approves task list |
| Bare `IMPLEMENT` (no task name) | R-007 bounded order | **R-007** | Agent lists scope → ASK → founder confirms |
| `PLAN WITH NO ASF` (plan only) | implement step | **R-008** | Propose 3 tasks → ASK → founder `yes implement` |
| Mandatory SourceA file missing | Any ship order | **R-009** | BLOCK implement; sync or paste first |
| TrustField task | Any other rule | **R-001** | STOP always |
| Cursor AUTO-RUN / factory loop | R-007/R-008 or R-011 | **R-011** | Validators + bounded implement only |
| NF-CLOUD outreach send | R-011 agentic commercial | **R-011** | Handoff to agentic layer; www copy only |

---

## T0 triggers (founder permission examples)

| Founder says | Bounded bundle |
|--------------|----------------|
| `PLAN WITH NO ASF iter N implement` | Merge PR + ≤3 QUICK_PICK tasks + verify + PR |
| `implement: <single task>` | Only that task / named files |
| `WRITE DOWN incident reports` | `.cursor/incidents/` + registry + memory |
| `implement: auto conflict rule` | Rule/skill files for SKILL-007 only |
| `yes` / `go` after agent ASK | Only the option founder just approved |

**Not T0:** `plan.json` has tasks, QUICK_PICK queue, prior session `IMPLEMENT`, ship-first rule alone.

---

## Agent output template (on conflict)

```markdown
**RULE CONFLICT** — auto-resolved per SKILL-007

| Rule A | Rule B |
|--------|--------|
| <short> | <short> |

**Winner:** <T0–T5 + rule id>

**I will not edit disk until you choose:**
- A) Advise only
- B) <bounded implement option>
- C) <alternative>

Your next move?
```

---

## Integration

| Skill / rule | When |
|--------------|------|
| SKILL-006 | Ask step (always) |
| **SKILL-007** | **This — on conflict** |
| SKILL-001 | After T0 + conflict clear |
| `noetfield-rule-conflict-resolution.mdc` | alwaysApply pointer |

---

**END**
