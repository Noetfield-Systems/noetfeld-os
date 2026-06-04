# SHIP NOW — Noetfield (canonical)

**Plane:** DELIVERY · **Authority:** ASF

## Two different things

| What it is | Blocks shipping? |
|------------|------------------|
| **Ingest** — send answer to system (YAML + reports / `noetfield-latest.txt`) | **No** — required reporting after you ship |
| **Waiting for the next order** — stop until Prompt OS / M8 / dispatch sends another prompt | **Yes** — ASF said not to do this |

## Rules

1. Ship from **this repo’s plan** immediately: [plan.json](./plan.json) · [../docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md](../docs/spec/SPRINT_BACKLOG_WEEKS_0-8.md)
2. Do **not** idle until a new Prompt OS order arrives.
3. **Do** ingest every completed session (YAML with `reported_at`).
4. Do **not** edit Sina Prompt OS code.

Full checklist: [../docs/SHIP_NOW.md](../docs/SHIP_NOW.md)

## Verify

```bash
make ship-verify
```
