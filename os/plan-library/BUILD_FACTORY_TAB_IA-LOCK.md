# Build Factory Tab IA — LOCKED v1 (Noetfield)

**Status:** LOCKED · **Saved:** 2026-06-19T06:30:00Z  
**Canonical IA:** [`BUILD_FACTORY_TAB_IA_v1.md`](BUILD_FACTORY_TAB_IA_v1.md)  
**Site route:** `/factory/index.html`

## Screen map (locked)

```text
Build Factory (/factory/)
├── Catalog      P0 — governance + Copilot pack
├── Studio       P1 — read-only TLE spec
├── Sandbox Bay  P0 — mock eval · 30s · MOCK_ONLY
└── Teams        P2 — premium · specialist hire placeholder
```

## Shell copy

| Element | Locked copy |
|---------|-------------|
| Tab title | **Build Factory** |
| Subtitle | Governed governance factories — sandbox → freemium → premium |
| Primary CTA | **Run governance eval** |

## Wire to spec

| IA field | Spec path |
|----------|-----------|
| `catalog_ui.tab` | `noetfield-governance-factory-v1.json` |
| `demo_seconds` | 30 |
| `governance.delivery_mode` | `mock_only` |
