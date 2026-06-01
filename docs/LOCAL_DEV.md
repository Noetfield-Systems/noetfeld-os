# Local development (localhost)

## Why your Mac shows “connection refused”

`make dev-local` runs inside the **Cursor remote workspace** (a Linux VM), not on your Mac. When you type `http://localhost:8001` or `http://localhost:3000` in **Safari/Chrome on your Mac**, the browser talks to **your Mac’s** loopback — where nothing is listening — unless you bridge the VM.

**Fix (pick one):**

1. **Cursor Ports (recommended in Cloud)**  
   Open the **Ports** panel → forward **13080** (and optionally **8001**) → click the **globe** icon. Use the forwarded URL Cursor gives you (often still labeled `localhost` but tunneled through Cursor).

2. **Run on your Mac**  
   Clone the repo locally, install deps, run `make dev-local` in a terminal on your machine. Then `http://localhost:13080/` works in your browser.

3. **Public tunnel (fallback)**  
   With dev already up in the workspace: `make dev-local-tunnel` — opens an HTTPS link you can paste in any browser.

**Do not use port 3000** for the full site — use **13080** (unified proxy). Port 3000 only redirects to 13080 when the redirect service wins the port; an old Next process on 3000 will mislead you.

## One command

```bash
make dev-local
```

Stops stale processes, starts all backends, runs health checks.

```bash
make dev-local-down     # stop everything
make dev-local-status   # ports + HTTP health summary
make verify-local-dev   # health check only
make dev-local-tunnel   # foreground public HTTPS URL
make dev-local-tunnel-bg  # background tunnel → .dev-tunnel-url.txt
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
