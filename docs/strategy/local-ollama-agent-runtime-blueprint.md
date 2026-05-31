# Local Ollama & Agent Runtime Blueprint (LOCKED PLAN)

**Status:** LOCKED — founder workstation & local agent development only  
**Supersedes:** Informal chat notes on model choice and Ollama tuning  
**Does not override:** [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md), [POSITIONING.md](../../POSITIONING.md), production chat ([CHATBOT_SETUP.md](../CHATBOT_SETUP.md))  
**Scope:** Apple Silicon MacBook Pro (M5 Pro, 48 GB unified memory) · Ollama · Cursor/agent loops  
**Not in scope:** Noetfield public GTM, payments, custody, settlement, or production `platform.noetfield.com` chat

**Companion files:** [ollama.env.example](./ollama.env.example) · [scripts/local-ollama-bootstrap.sh](../../scripts/local-ollama-bootstrap.sh)

---

## 1. Purpose

This document is the **single English source of truth** for how the founder runs local LLMs while building Noetfield:

- Which models to pull and which to avoid for 24/7 agent use  
- How to tune Ollama for thermals, RAM, and fan noise on 48 GB Apple Silicon  
- When Ollama must be on vs off (on-demand, not always-on)  
- How this relates to the **Noetfield repo stack** (cloud LLM in production, Ollama in local dev only)

---

## 2. Design principles (locked)

| Rule | Rationale |
|------|-----------|
| **On-demand, not 24/7** | Always-on large models keep GPU/ANE busy → fan noise, heat, battery drain |
| **Smallest model that passes agent tasks** | Agent loops multiply tokens; latency and RAM beat benchmark maximums |
| **Production stays cloud** | Public chat, Telegram, and pilots use OpenRouter/Gemini — not laptop Ollama |
| **Unload when idle** | `OLLAMA_KEEP_ALIVE=5m` and/or `ollama stop` when agents finish |
| **No financial execution narrative** | Local stack supports **governance/dev work**, not payments or routing products |

> **One line:** Local Ollama is a **development inference utility**, not an always-on “Agent OS” production brain.

---

## 3. Target hardware (locked profile)

| Item | Locked value |
|------|----------------|
| Machine | MacBook Pro, Apple **M5 Pro** |
| Unified memory | **48 GB** |
| Role | Cursor agents, repo development, optional offline inference |
| Explicitly not | 24/7 datacenter substitute; production Noetfield traffic |

---

## 4. Ollama application version (install target)

| Item | Locked recommendation |
|------|------------------------|
| **Ollama app** | **Latest stable ≥ 0.24.0** from [https://ollama.com/download/mac](https://ollama.com/download/mac) or `brew install ollama` |
| **Verified upstream (May 2026)** | [v0.24.0](https://github.com/ollama/ollama/releases/tag/v0.24.0) — MLX sampler improvements on Apple Silicon |
| **Docker (repo dev stack)** | Pin `ollama/ollama:0.24.0` in `infrastructure/docker/docker-compose.yml` — do not use unpinned `:latest` in locked environments |
| **API endpoint** | `http://localhost:11434` (OpenAI-compatible: `http://localhost:11434/v1`) |

**After install, verify:**

```bash
ollama --version          # expect 0.24.x or newer
curl -s http://127.0.0.1:11434/api/version
```

**Install and bootstrap (Mac):**

```bash
./scripts/local-ollama-bootstrap.sh
```

---

## 5. Default model (locked)

| Field | Locked value |
|-------|----------------|
| **Primary model** | `qwen3:14b` (Ollama registry; quant defaults to **Q4_K_M**, ~9 GB) |
| **Pull once** | `ollama pull qwen3:14b` |
| **Warm run** | `ollama run qwen3:14b` (interactive) or HTTP API for Cursor |
| **Expected on 48 GB M5 Pro** | ~30–40 tokens/sec · ~9 GB model RAM · low–medium fan |

### Secondary models (optional, on-demand)

| Model | When to use |
|-------|-------------|
| `phi4` | Fast, cool — classification, short rewrites |
| `gemma3:12b` | Light, structured tasks |
| `qwen3:32b` | Harder reasoning session only — ~20 GB, medium thermals — **not** 24/7 default |

### Not recommended as always-loaded defaults

| Model | Reason |
|-------|--------|
| `qwen3:72b` | Too heavy; sustained high fan |
| `llama4-scout` (and similar large scouts) | Heavy for laptop agent loops |
| Llama **70B+** | RAM/thermals; poor fit for intermittent agents |
| Any **>40B** loaded 24/7 | Leaves insufficient headroom for IDE, Docker, browser |

Occasional one-off runs for experiments are allowed; they are excluded from **default operating policy**, not from the machine.

---

## 6. Ollama runtime environment (locked)

Apply via `~/.ollama/env`, shell profile, or [ollama.env.example](./ollama.env.example):

```bash
OLLAMA_NUM_GPU=20
OLLAMA_NUM_PARALLEL=1
OLLAMA_NUM_CTX=2048
OLLAMA_KEEP_ALIVE=5m
```

| Variable | Locked value | Effect |
|----------|--------------|--------|
| `OLLAMA_NUM_GPU` | `20` | Cap GPU offload — reduces sustained heat vs full offload |
| `OLLAMA_NUM_PARALLEL` | `1` | One inference at a time for predictable agent latency |
| `OLLAMA_NUM_CTX` | `2048` | Smaller KV cache — enough for most agent turns |
| `OLLAMA_KEEP_ALIVE` | `5m` | Unload weights after five minutes idle |

---

## 7. Operating schedule (locked)

### Mode A — On-demand (default)

| Phase | Action |
|-------|--------|
| Agent / Cursor session starts | Start Ollama if stopped: `ollama serve` or macOS app |
| During work | Inference against `localhost:11434` |
| Session ends | Wait for `OLLAMA_KEEP_ALIVE=5m` **or** run `ollama stop` |
| Overnight | **No** 24/7 daemon |

### Mode B — Optional daily rhythm

| Time | Action |
|------|--------|
| Morning | `ollama serve` + optional `ollama run qwen3:14b` warm-up |
| Workday | On-demand calls only |
| Evening | `ollama stop` (full shutdown) |

### Forbidden

- 24/7 loaded **Qwen3 32B/72B** as laptop “Agent OS server”  
- Pointing **production** Noetfield chat at laptop Ollama ([CHATBOT_SETUP.md](../CHATBOT_SETUP.md) forbids this pattern)

---

## 8. Resource budget (48 GB, default `qwen3:14b`)

| Configuration | RAM (approx.) | Headroom |
|---------------|---------------|----------|
| Qwen3 14B Q4_K_M + ctx 2048 | ~9 GB | ~39 GB for macOS, IDE, Docker, browser |
| Qwen3 32B Q4_K_M (session) | ~20 GB | ~28 GB — acceptable for focused work only |

---

## 9. Noetfield repository stack (current)

How local Ollama fits the **monorepo** today:

| Layer | Technology | Ollama role |
|-------|------------|-------------|
| **Public www** | Static HTML + shell | None — chat uses platform API |
| **Production platform** | FastAPI `noetfield_governance` | **OpenRouter / Gemini** (`PUBLIC_CHAT_PROVIDER`) |
| **Local `.env`** | `AI_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://localhost:11434` | Optional local platform dev |
| **Docker dev** | `infrastructure/docker/docker-compose.yml` | `ollama` service on `:11434` (pinned image) |
| **Governance Console MVP** | `governance-console/` | **No LLM** — deterministic rules v1 |
| **Phase 3 CI** | Postgres + pytest | No Ollama in CI |
| **L3 boundary** | [L3-external/README.md](../../L3-external/README.md) | Ollama = **local dev only**, not production authority |

**Production LLM path (locked):** keys in env → OpenRouter/Gemini → never commit keys → never use laptop Ollama for `www` visitor chat.

---

## 10. Current environment snapshot

Recorded for agents and founders comparing **cloud dev VMs** vs **target Mac**.

| Environment | Where | Ollama | RAM | Notes |
|-------------|-------|--------|-----|-------|
| **Target workstation** | M5 Pro MacBook, 48 GB | Install **0.24.x** per §4 | 48 GB | This plan applies here |
| **Typical cloud agent VM** (e.g. Cursor background) | Linux x86_64 | Often **not installed** | ~16 GB | Use cloud APIs for agents; do not assume Ollama |
| **This repo clone (example)** | Linux CI/dev | Not running | ~15 GB | Run `local-ollama-bootstrap.sh` only on Mac target |

Re-run snapshot on your Mac:

```bash
uname -m && sysctl hw.memsize 2>/dev/null
command -v ollama && ollama --version
curl -s http://127.0.0.1:11434/api/version || echo "Ollama not running"
ollama list 2>/dev/null || true
```

---

## 11. Quick reference card

```
LOCKED PLAN — Local agent runtime (M5 Pro 48 GB)
────────────────────────────────────────────────
Ollama:     >= 0.24.0 (install from ollama.com or Homebrew)
Model:      qwen3:14b  (Q4_K_M ~9 GB)
GPU cap:    OLLAMA_NUM_GPU=20
Parallel:   1
Context:    2048
Keep alive: 5m
24/7:       NO — on-demand YES
Production: OpenRouter/Gemini only (not Ollama)
```

---

## 12. Change control

| Change | Requires |
|--------|----------|
| New default local model | PR updating this file + §8 budget |
| Ollama version pin (Docker) | Update `docker-compose.yml` + this §4 |
| Production LLM provider | [CHATBOT_SETUP.md](../CHATBOT_SETUP.md), `.env.example`, RUNBOOK |
| Ollama in production CI/deploy | **Rejected** unless new infra ADR — conflicts L3 lock |

**Verification:**

```bash
ollama ps
curl -s http://localhost:11434/api/tags
make -C governance-console test-api   # unrelated API smoke; platform optional
```

---

## 13. Document hierarchy

| Topic | Authority |
|-------|-----------|
| Public product truth | [PRODUCT_TRUTH.md](../../PRODUCT_TRUTH.md) |
| Production website chat | [CHATBOT_SETUP.md](../CHATBOT_SETUP.md) |
| **Local Ollama + agent laptop** | **This file (LOCKED)** |
| Product horizons | [noetfield-future-path.md](./noetfield-future-path.md) |
| GTM copy | [GTM_COPYBOOK.md](./GTM_COPYBOOK.md) |
