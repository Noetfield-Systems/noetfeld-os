# noetfield-gate

Graphify-class chain tool for **Noetfield OS** — sits between your agent and execution.

## Install (dev)

```bash
cd ~/Projects/noetfeld-os
pip install -e .
```

## One command: gate (PASS or BLOCK)

```bash
noetfield gate
# -> ~/.noetfield/gate-report-v1.json
# -> ~/.noetfield/gate-report-v1.md
```

Checks: policy pack on disk · JSON valid · sqlite writable · PolicyRegistry load · optional API `/readiness`.

```bash
export NOETFIELD_API_URL=http://127.0.0.1:8001
noetfield gate
```

Exit code `0` = PASS, `1` = BLOCK.

## One command: decide (receipt on disk)

Start API: `python3 run.py` (port **8001**)

```bash
export NOETFIELD_API_KEY=your-key
noetfield decide --sample
# -> ./noetfield-decision-<id>.json
```

Or from file:

```bash
noetfield decide --file intent.json --out DECISION_RECEIPT.json
```

## Environment

| Variable | Purpose |
|----------|---------|
| `NOETFIELD_ROOT` | Repo root if auto-detect fails |
| `NOETFIELD_API_URL` | Remote or local GEL base URL |
| `NOETFIELD_API_KEY` | `X-API-Key` for `/v1/decision` |

## Chain tool pattern

- One command in → one artifact out (JSON + optional `.md`)
- Runs at **every** execution boundary
- Open-source CLI; hosted API = `api.noetfield.com` (Phase 7)

**Related:** SourceA `critic_boot_v1.py` (portfolio boot) · Noetfield `POST /v1/decision` (policy gate).
