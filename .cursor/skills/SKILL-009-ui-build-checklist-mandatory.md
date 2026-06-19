# SKILL-009 — UI build checklist (mandatory before any UI work)

**When:** Before editing **any** HTML, CSS, JS, React/Next page, form, or buyer-facing copy on Noetfield.

**Blocks:** If skipped, do not commit — `make verify-ui-build-checklist` will fail.

## Steps (in order)

1. Read [docs/ops/UI_BUILD_CHECKLIST_LOCKED_v1.md](../../docs/ops/UI_BUILD_CHECKLIST_LOCKED_v1.md) **in full**.
2. Read [docs/WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md](../../docs/WWW_V18_TIER1_UI_MASTERPLAN_LOCKED_v1.md) — declare UI-## upgrade ID.
3. Read [OFFERINGS_LOCKED.md](../../OFFERINGS_LOCKED.md) + [governance/FREEMIUM_POLICY_LOCKED_v1.md](../../governance/FREEMIUM_POLICY_LOCKED_v1.md).
4. Confirm **no invitation surfaces** — no calendar CTAs, no mandatory sales call, self-serve sandbox only.
5. Match shell contract (www `nf-www` vs nf26 `institutional-2026.css`).
6. Run `make verify-ui-build-checklist` after edits (offline-safe).
7. With dev stack: `make verify-ui-e2e` + `make verify-ui-visual`.

## Pass response (internal)

```
ui_checklist: PASS
upgrade_id: UI-##
shell: www|nf26
invitation_surfaces: none
```

## Fail response (to user)

```
Blocked — UI_BUILD_CHECKLIST_LOCKED_v1.md not applied.
Read SKILL-009 and run make verify-ui-build-checklist before shipping UI.
```
