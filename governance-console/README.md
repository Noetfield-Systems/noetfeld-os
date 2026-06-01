# Noetfield Governance Console (v1)

Pre-execution governance web app: submit operational intent, receive **allow / deny / review**, and browse immutable audit records by **RID**.

**Not** a payments, trading, wallet, or exchange product.

## Fully automated (one command)

**Docker (recommended — full stack + E2E smoke):**

```bash
cd governance-console
make e2e          # build postgres + api + web, run smoke, tear down
make up           # start stack and keep running
make down         # stop stack
```

From repo root:

```bash
make governance-console-e2e
make governance-console-up
```

**Without Docker (API-only smoke):**

```bash
cd governance-console
chmod +x scripts/e2e-local.sh
./scripts/e2e-local.sh
```

CI runs on every PR touching `governance-console/` via [.github/workflows/governance-console-e2e.yml](../.github/workflows/governance-console-e2e.yml).

---

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15 (App Router), TypeScript, TailwindCSS |
| Backend | FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| E2E | httpx smoke (`e2e/smoke.py`) |

## Manual dev

### Database

**PostgreSQL:**

```bash
docker compose up -d postgres
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/governance_console
```

**SQLite (no Docker):**

```bash
export DATABASE_URL=sqlite:///./governance_console.db
```

### Backend (port 8000)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (port 3000)

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:3000

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/evaluate` | Governance decision + persist audit row |
| `GET` | `/audit` | List evaluations (`?q=RID` optional) |
| `GET` | `/audit/{rid}` | Single record |
| `GET` | `/health` | Health + DB ping |
| `GET` | `/docs` | OpenAPI UI |

## Relation to main Noetfield platform

**Not the production pilot path.** This folder is a **local/dev sandbox** (Docker E2E in `.github/workflows/governance-console-e2e.yml`).

| Environment | Use |
|-------------|-----|
| **Production pilots** | `https://platform.noetfield.com` — `/api/v1/governance/*` in `services/governance` |
| **This repo app** | `make e2e` in `governance-console/` for UI/API experiments only |

See [docs/GOVERNANCE_PILOT_RUNBOOK.md](../docs/GOVERNANCE_PILOT_RUNBOOK.md).

## Tests

```bash
cd backend && PYTHONPATH=. python3 -m pytest tests -q
make e2e   # full Docker E2E
```
