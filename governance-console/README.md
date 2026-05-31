# Noetfield Governance Console (v1)

Pre-execution governance web app: submit operational intent, receive **allow / deny / review**, and browse immutable audit records by **RID**.

**Not** a payments, trading, wallet, or exchange product.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 15 (App Router), TypeScript, TailwindCSS |
| Backend | FastAPI, SQLAlchemy |
| Database | PostgreSQL |

## Quick start

### 1. Database

**PostgreSQL (recommended):**

```bash
cd governance-console
docker compose up -d postgres
```

**Local dev without Docker:** use SQLite:

```bash
export DATABASE_URL=sqlite:///./governance_console.db
```

### 2. Backend (port 8000)

```bash
cd governance-console/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/governance_console
uvicorn main:app --reload --port 8000
```

### 3. Frontend (port 3000)

```bash
cd governance-console/frontend
npm install
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:3000 — submit intent, view result, browse `/audit`.

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/evaluate` | Governance decision + persist audit row |
| `GET` | `/audit` | List evaluations (`?q=RID` optional) |
| `GET` | `/audit/{rid}` | Single record |
| `GET` | `/health` | Health check |

## Relation to main Noetfield platform

This folder is a **standalone MVP** for the Governance Console product spec. Production pilots on `platform.noetfield.com` also expose `/api/v1/governance/*` and `governance-console-v1.html` in the main `services/governance` package — merge or proxy when promoting to production.

## Tests

```bash
cd governance-console/backend
PYTHONPATH=. pytest tests -q
```
