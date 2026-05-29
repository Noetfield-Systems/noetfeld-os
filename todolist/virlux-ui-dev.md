# VIRLUX — UI & local dev (separate repo)

Marketing: `http://localhost:3100` · Dashboard: `http://localhost:3001`

## Shipped (2026 B2B fintech sales motion) — reference

| Area | Done |
|------|------|
| Design | Plus Jakarta Sans, navy + blue glow, glass cards, btn-primary/secondary |
| Marketing | Sticky header, hero, live calculator, stats, pillars, 4-step flow, bank vs VIRLUX table, corridors, pricing, FAQ, demo CTA, Ontario footer |
| Dashboard | Split login, sidebar, overview tiles, shared tokens with marketing |

## Dev environment — known issues & fixes

| ID | Item | Status | Notes |
|----|------|--------|-------|
| VL-UI-01 | Port 3100 stale Next.js → HTTP 500 (missing `.next` manifests) | done | Root cause: ENOENT on `app-paths-manifest.json` |
| VL-UI-02 | `apps/web/scripts/dev.sh` — kill stale 3100, fresh dev | done | |
| VL-UI-03 | `npm run dev:web` — marketing only | done | |
| VL-UI-04 | `npm run dev` → `dev:safe` for web app | done | |
| VL-UI-05 | Wrong cwd (old Wirelux path) causes confusion | todo | founder | Run from `/Users/.../Virlux` (or actual repo root) |
| VL-UI-06 | `npm run dev:clean -w @virlux/web` if 3100 acts up | todo | ops | Wipe `.next` and restart |

### Repro evidence (archived)

- Before fix: `curl localhost:3100` → 500
- After fix: → 200 with full HTML
- Deleting `.next` while server running → 500 + ENOENT manifests

## Future UI (nice to have)

| ID | Item | Status | Owner | Type |
|----|------|--------|-------|------|
| VL-UI-10 | Light-mode variant | todo | engineering | nice_to_have |
| VL-UI-11 | Animated corridor map | todo | engineering | nice_to_have |
| VL-UI-12 | Dedicated `/pricing` page for paid ads | todo | engineering | nice_to_have |
