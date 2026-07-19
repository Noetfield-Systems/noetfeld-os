#!/usr/bin/env python3
"""NOOS durable health incident supervision (Missions 2 + 4).

Turns every stack-health ``fix_queue`` entry into a DURABLE, ROUTABLE incident,
so a failure survives the reconciler's ephemeral checkout (the defect in run
29664358570, which reported ``pending=0`` while scanning only committed receipts
and invoked no worker).

Durable authority = the Supabase control table ``noos_health_incident``
(migration 0020). ``.noos-runtime/**`` and GHA artifacts are NOT the durable
queue (Mission 2 rule 4). For deterministic offline proof and replay, a
file-backed transport double implements the same contract; the Supabase
transport is the production authority.

Lifecycle: OPEN → DISPATCHED → (RESOLVED | BLOCKED_EXTERNAL | RETRY_EXHAUSTED).

An incident is only ``DISPATCHED`` when a callable handler or owner endpoint
accepted it and returned a concrete run/job id. Ordinary machine-safe failures
never escalate to the founder; escalation is reserved for exhausted machine
remedies with no external owner endpoint.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

ROOT = Path(__file__).resolve().parents[1]
ROUTING_MAP = ROOT / "data/noos-health-incident-routing-v1.json"

STATE_OPEN = "OPEN"
STATE_DISPATCHED = "DISPATCHED"
STATE_RESOLVED = "RESOLVED"
STATE_BLOCKED_EXTERNAL = "BLOCKED_EXTERNAL"
STATE_RETRY_EXHAUSTED = "RETRY_EXHAUSTED"

OPEN_STATES = (STATE_OPEN,)
TERMINAL_STATES = (STATE_RESOLVED, STATE_BLOCKED_EXTERNAL, STATE_RETRY_EXHAUSTED)

SUPABASE_TABLE = "noos_health_incident"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_routing() -> dict[str, Any]:
    if not ROUTING_MAP.is_file():
        return {"routes": {}, "default_route": {}}
    return json.loads(ROUTING_MAP.read_text(encoding="utf-8"))


def route_for(fix_queue_key: str) -> dict[str, Any]:
    doc = load_routing()
    routes = doc.get("routes") or {}
    return dict(routes.get(fix_queue_key) or doc.get("default_route") or {})


def build_idempotency_key(*, fix_queue_key: str, source_sha: str | None, source_run_url: str | None) -> str:
    """Deterministic key so a repeated fix_queue entry from the same source SHA/run
    does not double-file. Distinct source → distinct incident."""
    basis = f"{fix_queue_key}|{source_sha or ''}|{source_run_url or ''}"
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    return f"noos.health:{fix_queue_key}:{digest}"


def build_incident_id(*, fix_queue_key: str, idempotency_key: str) -> str:
    suffix = idempotency_key.rsplit(":", 1)[-1]
    return f"NOOS-HEALTH-{fix_queue_key.upper()}-{suffix}"


@dataclass
class Incident:
    incident_id: str
    idempotency_key: str
    fix_queue_key: str
    failure_type: str
    target_owner: str
    target_repository: str | None
    handler_id: str
    authority_class: str
    source_receipt: str | None = None
    source_run_url: str | None = None
    source_sha: str | None = None
    attempt: int = 0
    retry_ceiling: int = 3
    state: str = STATE_OPEN
    worker_run_id: str | None = None
    terminal_receipt: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


def make_incident(
    *,
    fix_queue_key: str,
    source_receipt: str | None = None,
    source_run_url: str | None = None,
    source_sha: str | None = None,
    retry_ceiling: int = 3,
    detail: dict[str, Any] | None = None,
) -> Incident:
    r = route_for(fix_queue_key)
    idem = build_idempotency_key(
        fix_queue_key=fix_queue_key, source_sha=source_sha, source_run_url=source_run_url
    )
    return Incident(
        incident_id=build_incident_id(fix_queue_key=fix_queue_key, idempotency_key=idem),
        idempotency_key=idem,
        fix_queue_key=fix_queue_key,
        failure_type=str(r.get("failure_type") or "unclassified"),
        target_owner=str(r.get("owner") or "noos"),
        target_repository=r.get("target_repository"),
        handler_id=str(r.get("handler_id") or "noos.unknown_failure_triage"),
        authority_class=str(r.get("authority_class") or "machine_safe"),
        source_receipt=source_receipt,
        source_run_url=source_run_url,
        source_sha=source_sha,
        retry_ceiling=retry_ceiling,
        detail=detail or {},
    )


# --------------------------------------------------------------------------- #
# Durable transport contract                                                   #
# --------------------------------------------------------------------------- #
class Transport(Protocol):
    def available(self) -> bool: ...
    def insert(self, row: dict[str, Any]) -> dict[str, Any]: ...
    def list_open(self) -> list[dict[str, Any]]: ...
    def update(self, incident_id: str, patch: dict[str, Any]) -> dict[str, Any]: ...


class FileDurableTransport:
    """Durable proof/replay double: one JSON file, unique on idempotency_key.

    Real restart survival is provable — a fresh instance over the same path reads
    prior rows. This is the TEST/REPLAY backend; Supabase is the production
    authority (Mission 2 rule 3/4)."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def available(self) -> bool:
        return True

    def _load(self) -> dict[str, dict[str, Any]]:
        if not self.path.is_file():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _save(self, store: dict[str, dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")

    def insert(self, row: dict[str, Any]) -> dict[str, Any]:
        store = self._load()
        key = str(row["idempotency_key"])
        if key in store:
            return {"ok": True, "duplicate": True, "incident_id": store[key]["incident_id"]}
        store[key] = dict(row)
        self._save(store)
        return {"ok": True, "duplicate": False, "incident_id": row["incident_id"]}

    def list_open(self) -> list[dict[str, Any]]:
        return [r for r in self._load().values() if r.get("state") in OPEN_STATES]

    def update(self, incident_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        store = self._load()
        for key, row in store.items():
            if row.get("incident_id") == incident_id:
                row.update(patch)
                row["updated_at"] = utc_now()
                self._save(store)
                return {"ok": True}
        return {"ok": False, "reason": "incident_not_found"}


class SupabaseTransport:
    """Production authority transport → Supabase control table via PostgREST."""

    def __init__(self) -> None:
        url = (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or "").strip()
        key = (
            os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or ""
        ).strip()
        self._base = url.rstrip("/") if url else ""
        self._key = key

    def available(self) -> bool:
        return bool(self._base and self._key)

    def _headers(self, prefer: str) -> dict[str, str]:
        return {
            "apikey": self._key,
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
            "Prefer": prefer,
        }

    def insert(self, row: dict[str, Any]) -> dict[str, Any]:  # pragma: no cover - network
        try:
            req = urllib.request.Request(
                f"{self._base}/rest/v1/{SUPABASE_TABLE}",
                data=json.dumps(row).encode("utf-8"),
                headers=self._headers("resolution=ignore-duplicates,return=representation"),
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
                return {"ok": True, "status": resp.status, "body": body[:400]}
        except urllib.error.HTTPError as exc:
            return {"ok": False, "status": exc.code, "error": exc.read().decode("utf-8", "replace")[:300]}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)[:300]}

    def list_open(self) -> list[dict[str, Any]]:  # pragma: no cover - network
        try:
            url = f"{self._base}/rest/v1/{SUPABASE_TABLE}?state=eq.{STATE_OPEN}&select=*"
            req = urllib.request.Request(url, headers=self._headers("count=none"))
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:  # noqa: BLE001
            return []

    def update(self, incident_id: str, patch: dict[str, Any]) -> dict[str, Any]:  # pragma: no cover - network
        try:
            url = f"{self._base}/rest/v1/{SUPABASE_TABLE}?incident_id=eq.{incident_id}"
            req = urllib.request.Request(
                url,
                data=json.dumps(patch).encode("utf-8"),
                headers=self._headers("return=minimal"),
                method="PATCH",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return {"ok": 200 <= resp.status < 300, "status": resp.status}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)[:300]}


def default_transport() -> Transport | None:
    t = SupabaseTransport()
    return t if t.available() else None


def supabase_blocker() -> dict[str, Any]:
    return {
        "ok": False,
        "verdict": "BLOCKED_DURABLE_STORE_NOT_CONFIGURED",
        "missing": ["NOETFIELD_SUPABASE_URL", "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY"],
        "target_environment": "Noetfield Systems Supabase (project tkgpapowwplupyekpivy)",
        "unblock_action": (
            "Provide NOETFIELD_SUPABASE_URL + NOETFIELD_SUPABASE_SERVICE_ROLE_KEY and apply "
            "migration 0020_noos_health_incident.sql, then re-run reconciliation."
        ),
    }


# --------------------------------------------------------------------------- #
# Persist / read / dispatch                                                    #
# --------------------------------------------------------------------------- #
def persist_incident(incident: Incident, *, transport: Transport | None = None) -> dict[str, Any]:
    """Persist ONE durable incident before reconciliation (idempotent)."""
    t = transport or default_transport()
    if t is None:
        return supabase_blocker()
    return t.insert(incident.to_row())


def read_open_incidents(*, transport: Transport | None = None) -> dict[str, Any]:
    """Reconciler reads durable OPEN incidents (not committed-receipt scan)."""
    t = transport or default_transport()
    if t is None:
        return {**supabase_blocker(), "open": []}
    rows = t.list_open()
    return {"ok": True, "open": rows, "actionable": len(rows)}


# Handler contract: returns {"ok": bool, "run_id": str|None, "receipt": str|None, "reason": str|None}
HandlerFn = Callable[[dict[str, Any]], dict[str, Any]]


def _noos_integrator_mirror_repair(incident: dict[str, Any]) -> dict[str, Any]:
    """Real NOOS-owned machine-safe handler: refresh the integrator mirror/liveness.

    Returns a concrete run id only if the underlying repair command executed.
    """
    import subprocess

    run_id = f"noos-run-{int(time.time())}-{incident['incident_id'][-6:]}"
    try:
        proc = subprocess.run(
            ["python3", str(ROOT / "scripts/noos_integrator_repair_autorun_v1.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        ok = proc.returncode == 0
        return {
            "ok": ok,
            "run_id": run_id if ok else None,
            "receipt": None,
            "reason": None if ok else (proc.stderr or "repair_nonzero")[-200:],
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "run_id": None, "receipt": None, "reason": str(exc)[:200]}


DEFAULT_HANDLERS: dict[str, HandlerFn] = {
    "noos.integrator_mirror_repair": _noos_integrator_mirror_repair,
}


def dispatch_incident(
    incident: dict[str, Any],
    *,
    transport: Transport | None = None,
    handlers: dict[str, HandlerFn] | None = None,
    owner_endpoints: dict[str, HandlerFn] | None = None,
) -> dict[str, Any]:
    """Dispatch ONE open incident to a registered handler or external owner.

    Only marks DISPATCHED/RESOLVED if the callable returned a concrete run/job id.
    Ordinary machine-safe failures never escalate to the founder.
    """
    t = transport or default_transport()
    if t is None:
        return supabase_blocker()
    handlers = handlers if handlers is not None else DEFAULT_HANDLERS
    owner_endpoints = owner_endpoints or {}

    owner = str(incident.get("target_owner") or "noos")
    handler_id = str(incident.get("handler_id") or "")
    incident_id = str(incident.get("incident_id"))
    attempt = int(incident.get("attempt") or 0) + 1
    ceiling = int(incident.get("retry_ceiling") or 3)

    # External owner (SourceA / TrustField / Railway): needs a registered endpoint.
    if owner != "noos":
        endpoint = owner_endpoints.get(handler_id) or owner_endpoints.get(owner)
        if endpoint is None:
            patch = {"state": STATE_BLOCKED_EXTERNAL, "attempt": attempt}
            t.update(incident_id, patch)
            return {
                "ok": False,
                "state": STATE_BLOCKED_EXTERNAL,
                "verdict": "BLOCKED_EXTERNAL_OWNER_ENDPOINT",
                "owner": owner,
                "handler_id": handler_id,
                "founder_escalation": False,
            }
        result = endpoint(incident)
    else:
        handler = handlers.get(handler_id)
        if handler is None:
            # handler unavailable → retry accounting; exhaustion is a bounded
            # terminal blocker, still NOT a founder escalation for ordinary work.
            if attempt >= ceiling:
                t.update(incident_id, {"state": STATE_RETRY_EXHAUSTED, "attempt": attempt})
                return {
                    "ok": False,
                    "state": STATE_RETRY_EXHAUSTED,
                    "reason": "handler_unavailable",
                    "founder_escalation": False,
                }
            t.update(incident_id, {"attempt": attempt})
            return {"ok": False, "state": STATE_OPEN, "reason": "handler_unavailable", "attempt": attempt}
        result = handler(incident)

    run_id = result.get("run_id")
    if result.get("ok") and run_id:
        patch = {
            "state": STATE_RESOLVED,
            "attempt": attempt,
            "worker_run_id": run_id,
            "terminal_receipt": result.get("receipt"),
        }
        t.update(incident_id, patch)
        return {"ok": True, "state": STATE_RESOLVED, "worker_run_id": run_id, "founder_escalation": False}

    # Failed attempt with no run id.
    if attempt >= ceiling:
        t.update(incident_id, {"state": STATE_RETRY_EXHAUSTED, "attempt": attempt})
        return {
            "ok": False,
            "state": STATE_RETRY_EXHAUSTED,
            "reason": result.get("reason") or "no_run_id",
            "founder_escalation": False,
        }
    t.update(incident_id, {"attempt": attempt})
    return {"ok": False, "state": STATE_OPEN, "reason": result.get("reason") or "no_run_id", "attempt": attempt}


def file_from_fix_queue(
    fix_queue: list[str],
    *,
    source_receipt: str | None,
    source_run_url: str | None,
    source_sha: str | None,
    transport: Transport | None = None,
) -> dict[str, Any]:
    """Persist one durable incident per fix_queue entry (idempotent)."""
    t = transport or default_transport()
    if t is None:
        return supabase_blocker()
    created: list[dict[str, Any]] = []
    duplicates = 0
    for key in fix_queue:
        inc = make_incident(
            fix_queue_key=key,
            source_receipt=source_receipt,
            source_run_url=source_run_url,
            source_sha=source_sha,
        )
        res = t.insert(inc.to_row())
        if res.get("duplicate"):
            duplicates += 1
        else:
            created.append({"incident_id": inc.incident_id, "owner": inc.target_owner, "handler_id": inc.handler_id})
    return {"ok": True, "created": created, "duplicates": duplicates, "count": len(created)}
