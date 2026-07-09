# noetfield-gate

Graphify-class chain tool — gate before agent execution.  
**Full docs:** https://www.noetfield.com/gel/

---

## Install (PyPI)

```bash
pip install noetfield-gate
noetfield gate
```

Bundled default policies ship in the wheel. Receipts land in `~/.noetfield/gate-report-v1.json`.

## Install (dev / full runtime)

```bash
cd ~/Desktop/Noetfield-Systems/noetfeld-OS
pip install -e ".[dev]"
```

## One command: gate (PASS or BLOCK)

```bash
noetfield gate
# -> ~/.noetfield/gate-report-v1.json
# -> ~/.noetfield/gate-report-v1.md
```

Checks: policy pack · JSON valid · sqlite writable · optional API `/readiness` · PolicyRegistry when running from full repo checkout.

```bash
export NOETFIELD_API_URL=https://api.noetfield.com
noetfield gate
```

Exit code `0` = PASS, `1` = BLOCK.

## One command: decide (receipt on disk)

Hosted API default: `https://api.noetfield.com`. Local dev: `NOETFIELD_API_URL=http://127.0.0.1:8001`.

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
| `NOETFIELD_ROOT` | Full repo root (policies + PolicyRegistry) |
| `NOETFIELD_API_URL` | GEL base URL (default: `https://api.noetfield.com`) |
| `NOETFIELD_API_KEY` | `X-API-Key` for `/v1/decision` |

## Chain tool pattern

- One command in → one artifact out (JSON + optional `.md`)
- Runs at **every** execution boundary
- Open-source CLI; hosted API = `api.noetfield.com`

**Docs:** https://www.noetfield.com/gel/
