#!/usr/bin/env python3
"""Cross-repo health aggregation for the orchestrator loop (replaces echo stub).

L10: reads only shared sink / public health URLs / local registries — never another repo's disk.
Also emits a Runway role-dispatch artifact for durable valuable output.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_role_runway_dispatch_v1 as role_dispatch  # noqa: E402

LOOPS = ROOT / "data/noos-24-7-loops-v1.json"
PROOF = ROOT / "receipts/proof"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def probe(url: str, timeout: int = 10) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "noos-orchestrator-v1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")[:500]
            return {"url": url, "ok": resp.status < 300, "status": resp.status, "snippet": body[:160]}
    except urllib.error.HTTPError as exc:
        return {"url": url, "ok": False, "status": exc.code, "error": str(exc)[:160]}
    except OSError as exc:
        return {"url": url, "ok": False, "error": str(exc)[:160]}


def run(*, write: bool = True) -> dict[str, Any]:
    loops = json.loads(LOOPS.read_text(encoding="utf-8"))
    motor = loops.get("motor") or {}
    probes = [
        probe(str(motor.get("health_url") or "")),
        probe(str(motor.get("deadman_health_url") or "")),
        probe(str(motor.get("railway_health_url") or "")),
    ]
    probes = [p for p in probes if p.get("url")]
    healthy = sum(1 for p in probes if p.get("ok"))
    dispatch = role_dispatch.dispatch_role(
        "orchestrator",
        subject="cross-repo-health",
        context={"probes_ok": healthy, "probes_total": len(probes)},
    )
    row = {
        "schema": "noos-orchestrator-cross-repo-v1",
        "at": utc_now(),
        "probes": probes,
        "healthy_count": healthy,
        "probe_total": len(probes),
        "role_dispatch": {
            "ok": dispatch.get("ok"),
            "receipt_path": dispatch.get("receipt_path"),
            "job_id": (dispatch.get("ack") or {}).get("job_id"),
            "dry_run": (dispatch.get("ack") or {}).get("dry_run"),
        },
        "value_class": "risk_reduction",
        "ok": healthy == len(probes) and bool(dispatch.get("ok")),
        "report_line": f"orchestrator · probes={healthy}/{len(probes)} dispatch_ok={dispatch.get('ok')}",
    }
    if write:
        PROOF.mkdir(parents=True, exist_ok=True)
        out = PROOF / f"noos-orchestrator-cross-repo-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(out.relative_to(ROOT))
    return row


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    row = run(write=not args.dry_run)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
