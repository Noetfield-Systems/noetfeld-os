# NF UI Build Checklist — LOCKED v1 (mandatory)

**Law:** No agent may change **any** UI — www page, form, app shell, console, intake — without reading this checklist and passing machine gates.

**Strategy:** Stable client-facing system with guards — **no invitation copy**, no founder factory language on public surfaces.

---

## 0 — Read before edit (every session)

1. This checklist (`docs/www/NF_UI_BUILD_CHECKLIST_LOCKED_v1.md`)
2. Language layers (`docs/www/NF_WWW_LANGUAGE_LAYERS_LOCKED_v1.md`)
3. Design reference (`docs/DESIGN_REFERENCE_GOALS_LOCKED_v1.md`) — patterns R1–R8 minimum for www
4. Commercial SSOT (`docs/strategy/NOETFIELD_COMMERCIAL_SSOT_LOCKED_v1.md`) — three SKUs only

```bash
make nf-ui-checklist   # must PASS before ship
```

---

## 1 — Four language layers (public www)

| Layer | Audience | Allowed on www |
|-------|----------|----------------|
| Founder / internal | Agents, ops | **Never** on buyer heroes, sticky CTAs, forms |
| Client commercial | SMB CIO, pilot | Outcomes, pricing, sandbox, board PDF success |
| Client institutional | Federal, bank, VC | Diligence, procurement, honest scope |
| Developer | API / sandbox | `/start/`, `/docs/api/`, `/runtime/`, demo widget |

**Banned on public www:** `W3 economic signal`, `Lane SSOT`, `nurture SSOT`, `commercial SSOT`, `SSOT: <a`, `SourceA`, `REGISTRY.json`, `OFFERINGS_LOCKED` in body, `docs/ops/` links, invitation language.

**No invitation:** No “design partner”, “Become a…”, “Accepting design partners”, “You’re invited”, scarcity invites. Use **Apply for pilot**, **Start sandbox**, **Request Trust Brief** — stable program CTAs only.

---

## 2 — Build law (www)

| Action | Rule |
|--------|------|
| Marketing HTML hubs | Regenerate via `python3 scripts/rebuild-www-v6.py` — **never** hand-edit generated pages |
| Templates / runtime | Edit source HTML only when not in rebuild script; then run `make verify-www` |
| Forms / intake | RID-threaded async only; sticky CTA = commercial copy, no SSOT doc links |
| `/factory/` | `noindex` — sandbox sample only |

---

## 3 — Design patterns (minimum bar)

- **R1** Receipt-first proof in hero or adjacent panel
- **R3** Honest scope badges (Available / Orientation / Planned / Out of scope)
- **R7** Three SKUs only — no fourth contract card on homepage
- **R8** Mega CTA close on every hub
- **R21** Self-serve rail where applicable (`/start/`, demo, API)
- **R26–R27** Live proof / trial OS where shipped

Full bar: [WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md](../WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md)

---

## 4 — Machine gates (fail-closed)

```bash
bash scripts/verify-ui-build-checklist.sh   # umbrella — agents run this
make verify-www                            # language + static www
make site-health                           # GTM alignment + simplification tests
```

Wired into: `make nf-onboard` · `plan-with-no-asf-verify.sh` · `make verify-all-static`

---

## 5 — Agent rule

Cursor rule: `.cursor/rules/nf-ui-checklist-mandatory.mdc` (`alwaysApply: true`)

**If gates fail:** fix copy or regenerate www — do not bypass with `--no-verify`.

**Locked:** 2026-06-17
