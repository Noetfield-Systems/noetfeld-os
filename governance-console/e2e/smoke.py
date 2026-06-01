#!/usr/bin/env python3
"""End-to-end smoke: API evaluate → audit → web pages respond."""

from __future__ import annotations

import os
import sys
import time

import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
WEB_URL = os.getenv("WEB_URL", os.getenv("COGNITIVE_DASHBOARD_URL", "http://localhost:3010")).rstrip("/")
MAX_WAIT_S = int(os.getenv("E2E_MAX_WAIT_S", "120"))


def wait_ok(client: httpx.Client, url: str, label: str, *, follow_redirects: bool = False) -> None:
    deadline = time.time() + MAX_WAIT_S
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            r = client.get(url, timeout=5.0, follow_redirects=follow_redirects)
            if r.status_code == 200:
                print(f"OK  {label} {url}")
                return
            last_err = RuntimeError(f"status {r.status_code}")
        except Exception as exc:  # noqa: BLE001
            last_err = exc
        time.sleep(2)
    raise SystemExit(f"Timeout waiting for {label} at {url}: {last_err}")


def main() -> int:
    with httpx.Client() as client:
        wait_ok(client, f"{API_URL}/health", "api-health")
        if WEB_URL:
            wait_ok(client, f"{WEB_URL}/cognitive-dashboard", "web-cognitive-dashboard")
            wait_ok(client, WEB_URL, "web-root-redirect", follow_redirects=True)
        else:
            print("SKIP web (WEB_URL unset)")

        payload = {
            "actor": "e2e:automation",
            "action": "generate_governance_report",
            "context": "automated end-to-end test with policy references attached",
            "metadata": {"source": "e2e-smoke"},
        }
        ev = client.post(f"{API_URL}/evaluate", json=payload, timeout=30.0)
        ev.raise_for_status()
        body = ev.json()
        rid = body["rid"]
        assert body["decision"] in {"allow", "deny", "review"}
        assert 0 <= body["risk_score"] <= 100
        print(f"OK  evaluate decision={body['decision']} rid={rid}")

        one = client.get(f"{API_URL}/audit/{rid}", timeout=15.0)
        one.raise_for_status()
        assert one.json()["rid"] == rid
        print(f"OK  audit/{rid}")

        listing = client.get(f"{API_URL}/audit", timeout=15.0)
        listing.raise_for_status()
        rows = listing.json()
        assert any(r["rid"] == rid for r in rows)
        print(f"OK  audit list ({len(rows)} rows)")

        if WEB_URL:
            for path in ("/cognitive-dashboard", "/audit", f"/result/{rid}"):
                r = client.get(f"{WEB_URL}{path}", timeout=15.0)
                if r.status_code != 200:
                    raise SystemExit(f"Web {path} returned {r.status_code}")
                print(f"OK  web {path}")

    print("E2E smoke passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
