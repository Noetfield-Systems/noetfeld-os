# Local development (localhost)

## One command

```bash
make dev-local
```

Stops stale processes, starts all backends, runs health checks.

```bash
make dev-local-down   # stop everything
make verify-local-dev # health check only
```

## URLs (use after Cursor **Ports** forward)

| Surface | URL |
|---------|-----|
| **Website (www)** | http://localhost:13080/ |
| **Governance console** | http://localhost:8001/console or http://localhost:13080/console |
| **Cognitive dashboard** | http://localhost:13080/cognitive-dashboard |

Legacy port **3000** redirects to **13080** (same path).

## Cursor Cloud

The server runs in the **remote workspace**. Your Mac browser only sees `localhost` after you **forward** ports in the **Ports** tab:

1. Forward **13080** (website + proxied apps)
2. Forward **8001** (direct governance console)
3. Click the **globe** icon to open

## Ports (defaults)

| Port | Service |
|------|---------|
| 13080 | Public unified proxy (www + routes) |
| 8001 | Platform API + `/console` |
| 13000 | Next.js cognitive dashboard (internal) |
| 18002 | Governance-console dev API (internal) |

Override via `scripts/dev-ports.sh`.

## Logs

- `.dev-proxy.log` — unified proxy
- `.platform-console.log` — platform API
- `.cognitive-dashboard.log` — Next dashboard
- `.local-dev-urls.txt` — generated URLs
