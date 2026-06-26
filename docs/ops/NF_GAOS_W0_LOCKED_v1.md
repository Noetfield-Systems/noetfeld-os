# NF-GAOS W0 — Governed Agent OS spine (LOCKED v1)

```yaml
agent_tag: nf-local-repo-agent
agent_display: "[NF-LOCAL-REPO-AGENT]"
authored_at: "2026-06-17"
status: LOCKED
schema_version: nf-gaos-w0-v1
```

| Field | Value |
|-------|--------|
| Plane | `[DELIVERY]` — Noetfield product repo |
| Supersedes for boot | Ad-hoc multi-doc read chains as **primary** entry — those docs remain appendices |
| Authority | Subordinate to `PROJECT_BOUNDARIES_LOCKED.md` · `NOETFIELD_CLOUD_GIT_AND_AGENT_ENTRY_UNIFIED_LOCKED_v1.md` (SourceA mirror) |

---

## One sentence

> **Mac Law → SourceA mirror → Noetfield SSOT → machines decide live truth → one role · one lane · one task — chat is never SSOT.**

---

## W0 deliverables (this lock)

| Asset | Path |
|-------|------|
| Role picker | `entry/START_HERE_LOCKED_v1.md` |
| Daily pin card | `ROUTING_CARD.md` |
| Routing graph | `os/NF_UNIFIED_ROUTING_GRAPH.json` |
| Session gate | `scripts/nf_session_gate_run_v1.py` |
| Live orient | `scripts/nf-live-orient-v1.sh` |
| Routing card machine | `scripts/nf_routing_card.sh` |
| Onboard ladder | `scripts/nf-onboard.sh` |
| Graph CLI | `scripts/nf-unified-routing.sh` |
| Stale guard | `scripts/nf_stale_guard_v1.py` |
| Live snapshot | `reports/agent-auto/LIVE-STATUS.md` (generated) |
| Boot | `make nf-onboard` |

---

## Boot ladder (never skip gate)

```bash
make nf-onboard              # cloud product lane
make nf-onboard-local        # docs-only lane (detect only)
make nf-live-orient            # refresh LIVE-STATUS only
make nf-session-gate           # gate receipt only
```

---

## Session start vs orientation

| Trigger | Machine | Auto on boot? |
|---------|---------|---------------|
| Session gate | `nf_session_gate_run_v1.py` | **Yes** |
| Live orient | `nf-live-orient-v1.sh` | **Yes** (via onboard) |
| Orient cascade | `nf_orient_v1.py` | No — W1 |
| Founder: orientation / hospital / maze | pipelines | No — founder word only |

---

## Verify W0 spine

```bash
make verify-nf-gaos-w0
```

**Baseline:** W0 green 2026-06-17 — stale guard PASS when `SHIP_NOW.md` includes live pending `next_tasks` head.

---

## Waves after W0

| Wave | Scope |
|------|--------|
| W1 | Rule collapse · anti-fragmentation verify · voyage integrity |
| W2 | Routing Panel `:8780` Noetfield tab · ecosystem registry row |
| W3 | Governance unification engine · optional founder-word pipelines |

---

*NF-GAOS W0 · locked 2026-06-17 · [NF-LOCAL-REPO-AGENT]*
