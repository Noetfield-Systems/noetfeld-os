# L2 Knowledge Architecture

## Layout

| Path | Purpose |
|------|---------|
| `strategy/full/` | Complete mirror of all uploaded batches |
| `strategy/noetfield/` | Production runtime + GTM knowledge only |
| `strategy/reference-products/` | POSA, AIE, SLF, PAIOS, theory — **must not drive Noetfield runtime** |
| `perplexity-ai-native-development-guidelines.md` | Operator/dev guidelines (L2 root) |

## Archived tooling (FINAL LOCK — must not influence Noetfield runtime)

- **n8n** — archived workflow experiments (no runtime wiring)
- **Ollama** — local dev inference only in `docker-compose`; not production authority · blueprint: [docs/strategy/local-ollama-agent-runtime-blueprint.md](../docs/strategy/local-ollama-agent-runtime-blueprint.md)
- **PAIOS** — `reference-products/` only; must not drive `services/governance` or Golden Edge v3

## Supremacy

`NORTH_STAR.md` and GCIP v4 override this tree on conflict.
