"""Paperclip v2026.1023 company-scoped Company OS integration.

Paperclip owns its native company, agent, issue, project, approval and budget
records. Business OS owns only the idempotent reference to a *backlog* intake.
This is not an authority/permit service or a substitute for Noetfield verification.

Explicitly disable ALL live writes until the founder claims Paperclip and binds
a separate board API key to exactly one Paperclip company and intake project.
No customer contact details, secret, model output or unverified tool actions
ever cross this boundary.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

CANONICAL_BASE = "https://paperclip-agent-workforce-staging.up.railway.app"
INTAKE_RE = re.compile(r"^[A-Za-z0-9._:-]{12,100}$")
RESOURCE_RE = re.compile(r"^[a-zA-Z0-9_-]{4,100}$")
EMAIL_RE = re.compile(r"(?i)\b[\w.+-]+@[\w.-]+\.[A-Z]{2,}\b")
CREDENTIAL_RE = re.compile(r"(?i)(?:bearer\s+\S+|(?:sk|ghp|pcp)_[a-zA-Z0-9_-]{15,})")
MAX_RESPONSE_BYTES = 160_000
MAX_LIST_ITEMS = 100


class PaperclipError(Exception):
    def __init__(self, code, http_status=503):
        super().__init__(code)
        self.code = code
        self.http_status = http_status


@dataclass(frozen=True)
class Config:
    enabled: bool
    board_key: str
    company_id: str
    project_id: str
    base_url: str

    @property
    def ready(self):
        return (
            self.enabled
            and self.base_url == CANONICAL_BASE
            and self.board_key.startswith("pcp_board_")
            and len(self.board_key) >= 30
            and bool(RESOURCE_RE.fullmatch(self.company_id))
            and bool(RESOURCE_RE.fullmatch(self.project_id))
        )


def config():
    return Config(
        enabled=os.environ.get("PAPERCLIP_COMPANY_OS_ENABLED", "false").lower() == "true",
        board_key=os.environ.get("PAPERCLIP_COMPANY_OS_BOARD_API_KEY", ""),
        company_id=os.environ.get("PAPERCLIP_COMPANY_OS_COMPANY_ID", "").strip(),
        project_id=os.environ.get("PAPERCLIP_COMPANY_OS_INTAKE_PROJECT_ID", "").strip(),
        base_url=os.environ.get("PAPERCLIP_COMPANY_OS_BASE_URL", CANONICAL_BASE).rstrip("/"),
    )


def status(cfg=None):
    cfg = cfg or config()
    requirements = {
        "founder_claimed_company_id": bool(RESOURCE_RE.fullmatch(cfg.company_id)),
        "intake_project_id": bool(RESOURCE_RE.fullmatch(cfg.project_id)),
        "dedicated_board_api_key": cfg.board_key.startswith("pcp_board_") and len(cfg.board_key) >= 30,
        "explicit_integration_enabled": cfg.enabled,
        "canonical_https_origin": cfg.base_url == CANONICAL_BASE,
    }
    return {
        "schema": "noetfield.company-os.paperclip-status.v1",
        "paperclip": "v2026.1023.0",
        "base_url": CANONICAL_BASE,
        "configured": cfg.ready,
        "requirements": requirements,
        "mode": "scoped_board_backlog_only" if cfg.ready else "NOT_COMMISSIONED",
        "company_id": cfg.company_id if RESOURCE_RE.fullmatch(cfg.company_id) else None,
        "project_id": cfg.project_id if RESOURCE_RE.fullmatch(cfg.project_id) else None,
        "workspace_authenticated": False if not cfg.ready else None,
        "max_authority": "A2_BACKLOG_ONLY",
        "agent_wakeup_authorized": False,
        "production_mutations_authorized": False,
        "credentials_exposed": False,
    }


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def api_call(method, path, *, body=None, cfg=None):
    cfg = cfg or config()
    if not cfg.ready:
        raise PaperclipError("PAPERCLIP_NOT_COMMISSIONED", 503)
    if (not path.startswith("/api/") or "//" in path[1:] or "?" in path
        or not re.fullmatch(r"/api/[A-Za-z0-9_/-]+", path)):
        raise PaperclipError("PAPERCLIP_PATH_NOT_ALLOWED", 400)
    allowed_get = {
        f"/api/companies/{cfg.company_id}",
        f"/api/companies/{cfg.company_id}/agents",
        f"/api/companies/{cfg.company_id}/projects",
        f"/api/companies/{cfg.company_id}/issues",
        f"/api/companies/{cfg.company_id}/approvals",
    }
    create_path = f"/api/companies/{cfg.company_id}/issues"
    if (method == "GET" and path not in allowed_get) or (
        method == "POST" and path != create_path
    ) or method not in ("GET", "POST"):
        raise PaperclipError("PAPERCLIP_ACTION_NOT_ALLOWED", 403)
    payload = None if body is None else json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()
    if payload is not None and len(payload) > 4500:
        raise PaperclipError("PAPERCLIP_PAYLOAD_TOO_LARGE", 413)
    req = urllib.request.Request(
        cfg.base_url + path,
        data=payload, method=method,
        headers={"Authorization": "Bearer " + cfg.board_key,
                 "Accept": "application/json",
                 "Content-Type": "application/json",
                 "User-Agent": "Noetfield-Company-OS/1.0"},
    )
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=8) as response:
            if response.status not in (200, 201):
                raise PaperclipError("PAPERCLIP_RESPONSE_NOT_ACCEPTED", 502)
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise PaperclipError("PAPERCLIP_RESPONSE_TOO_LARGE", 502)
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise PaperclipError("PAPERCLIP_BOARD_CREDENTIAL_REJECTED", 503) from None
        if exc.code == 404:
            raise PaperclipError("PAPERCLIP_COMPANY_OR_PROJECT_NOT_FOUND", 409) from None
        if exc.code in (409, 422):
            raise PaperclipError("PAPERCLIP_REMOTE_CONFLICT", 409) from None
        raise PaperclipError("PAPERCLIP_UPSTREAM_HTTP_ERROR", 502) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise PaperclipError("PAPERCLIP_NETWORK_OR_TIMEOUT", 502) from None
    except (ValueError, UnicodeError, TypeError):
        raise PaperclipError("PAPERCLIP_INVALID_RESPONSE", 502) from None


def _items(v):
    if isinstance(v, list):
        return v[:MAX_LIST_ITEMS]
    if isinstance(v, dict):
        for key in ("items", "issues", "agents", "projects", "approvals", "data"):
            if isinstance(v.get(key), list):
                return v[key][:MAX_LIST_ITEMS]
    raise PaperclipError("PAPERCLIP_RESPONSE_SHAPE_INVALID", 502)


def _metadata(item, keys):
    if not isinstance(item, dict):
        return {}
    return {k: item[k] for k in keys if isinstance(item.get(k), (str, int, float, bool))}


def snapshot(cfg=None, fetch=None):
    cfg = cfg or config()
    fetch = fetch or api_call
    if not cfg.ready:
        raise PaperclipError("PAPERCLIP_NOT_COMMISSIONED")
    company = fetch("GET", f"/api/companies/{cfg.company_id}", cfg=cfg)
    if not isinstance(company, dict) or company.get("id") != cfg.company_id:
        raise PaperclipError("PAPERCLIP_COMPANY_SCOPE_MISMATCH", 403)
    data = {}
    collections = {
        "agents": ("id", "name", "role", "title", "status", "lifecycleState"),
        "projects": ("id", "name", "status"),
        "issues": ("id", "title", "status", "priority", "projectId", "assigneeAgentId"),
        "approvals": ("id", "type", "status"),
    }
    for key, columns in collections.items():
        value = fetch("GET", f"/api/companies/{cfg.company_id}/{key}", cfg=cfg)
        rows = _items(value)
        data[key] = [
            _metadata(x, columns)
            for x in rows
            if isinstance(x, dict) and (
                x.get("companyId") in (None, cfg.company_id)
                and (key != "issues" or not x.get("projectId") or x.get("projectId") == cfg.project_id)
            )
        ]
    if not any(p.get("id") == cfg.project_id for p in data["projects"]):
        raise PaperclipError("PAPERCLIP_INTAKE_PROJECT_SCOPE_MISMATCH", 409)
    return {
        "schema": "noetfield.company-os.paperclip-snapshot.v1",
        "company": _metadata(company, ("id", "name", "status", "budgetMonthlyCents", "spentMonthlyCents")),
        "intake_project_id": cfg.project_id,
        "counts": {k: len(v) for k, v in data.items()},
        "records": data,
        "limited_to_first_100_per_collection": True,
        "source": "live_paperclip_api",
        "read_only": True,
        "independent_verification": False,
        "execution_permit": False,
    }


def create_binding_table(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS paperclip_backlog_bindings (
            company_id TEXT NOT NULL,
            idempotency_key TEXT NOT NULL,
            payload_sha256 TEXT NOT NULL,
            paperclip_issue_id TEXT,
            state TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (company_id,idempotency_key)
        )
    """)


def _validate_text(title, objective, source_ref):
    for label, value, max_len in (
        ("title", title, 140), ("objective", objective, 1100), ("source_ref", source_ref, 300),
    ):
        if not isinstance(value, str) or not 12 <= len(value.strip()) <= max_len:
            raise PaperclipError("INVALID_BACKLOG_" + label.upper(), 422)
        if EMAIL_RE.search(value) or CREDENTIAL_RE.search(value):
            raise PaperclipError("SENSITIVE_DATA_NOT_ALLOWED_IN_PAPERCLIP", 422)
        if any(ord(ch) < 32 and ch not in ("\n", "\t") for ch in value):
            raise PaperclipError("CONTROL_CHAR_NOT_ALLOWED", 422)


def _marker(key):
    return "noetfield-intake:" + hashlib.sha256(key.encode()).hexdigest()


def submit_backlog(db, *, title, objective, source_ref, idempotency_key, cfg=None, fetch=None):
    cfg = cfg or config()
    fetch = fetch or api_call
    if not cfg.ready:
        raise PaperclipError("PAPERCLIP_NOT_COMMISSIONED")
    if not INTAKE_RE.fullmatch(idempotency_key):
        raise PaperclipError("INVALID_BACKLOG_IDEMPOTENCY_KEY", 422)
    _validate_text(title, objective, source_ref)
    obj = {"company_id": cfg.company_id, "project_id": cfg.project_id,
           "title": title.strip(), "objective": objective.strip(),
           "source_ref": source_ref.strip()}
    fingerprint = hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()
    marker = _marker(idempotency_key)
    db.execute("BEGIN IMMEDIATE")
    try:
        create_binding_table(db)
        old = db.execute(
            "SELECT * FROM paperclip_backlog_bindings WHERE company_id=? AND idempotency_key=?",
            (cfg.company_id, idempotency_key),
        ).fetchone()
        if old and old["payload_sha256"] != fingerprint:
            raise PaperclipError("BACKLOG_IDEMPOTENCY_CONFLICT", 409)
        if old and old["state"] == "BACKLOG_CREATED":
            db.commit()
            return {"state": "BACKLOG_CREATED", "paperclip_issue_id": old["paperclip_issue_id"],
                    "idempotent": True, "model_execution": False}
        # Remote server may commit an issue then return a timeout/500. Search
        # by digest before ever retrying a write; fail closed on unknown state.
        issues = _items(fetch("GET", f"/api/companies/{cfg.company_id}/issues", cfg=cfg))
        matched = [x for x in issues if isinstance(x, dict) and marker in (x.get("description") or "")]
        if len(matched) > 1:
            raise PaperclipError("PAPERCLIP_REMOTE_DUPLICATES_REQUIRE_REVIEW", 409)
        if len(matched) == 1:
            target = matched[0]
            if target.get("projectId") != cfg.project_id:
                raise PaperclipError("PAPERCLIP_RECONCILIATION_SCOPE_CONFLICT", 409)
        elif old:
            raise PaperclipError("PAPERCLIP_UNCERTAIN_WRITE_REQUIRES_REVIEW", 409)
        else:
            body = {
                "title": title.strip(),
                "description": objective.strip() + "\n\nSource (not independently verified): " + source_ref.strip()
                  + "\nTracking key: " + marker
                  + "\nNoetfield authority: A2 backlog ONLY; not an execution permit. "
                    "No agent assigned, no heartbeat, no customer contact, no production authorization.",
                "status": "backlog",
                "priority": "medium",
                "projectId": cfg.project_id,
                "parentId": None,
            }
            # Write a durable uncertain state before network mutation, so a
            # restart cannot silently issue a duplicate POST.
            when = datetime.now(timezone.utc).isoformat()
            db.execute(
                "INSERT INTO paperclip_backlog_bindings VALUES (?,?,?,?,?,?,?)",
                (cfg.company_id, idempotency_key, fingerprint, None,
                 "UNCERTAIN_REMOTE_WRITE", when, when)
            )
            db.commit()
            target = fetch("POST", f"/api/companies/{cfg.company_id}/issues", cfg=cfg, body=body)
            db.execute("BEGIN IMMEDIATE")
            if (not isinstance(target, dict) or not isinstance(target.get("id"), str)
                or target.get("companyId") not in (None, cfg.company_id)
                or target.get("projectId") != cfg.project_id
                or target.get("status") not in ("backlog",)):
                raise PaperclipError("PAPERCLIP_CREATE_SCOPE_OR_STATE_UNVERIFIED", 409)
        if not isinstance(target.get("id"), str):
            raise PaperclipError("PAPERCLIP_ISSUE_ID_NOT_VERIFIED", 409)
        when = datetime.now(timezone.utc).isoformat()
        db.execute(
            "INSERT INTO paperclip_backlog_bindings VALUES (?,?,?,?,?,?,?) "
            "ON CONFLICT(company_id,idempotency_key) DO UPDATE SET "
            "paperclip_issue_id=excluded.paperclip_issue_id,state='BACKLOG_CREATED',"
            "updated_at=excluded.updated_at",
            (cfg.company_id,idempotency_key,fingerprint,target["id"],"BACKLOG_CREATED",when,when),
        )
        db.commit()
        return {"state":"BACKLOG_CREATED", "paperclip_issue_id":target["id"],
                "idempotent":False, "model_execution":False}
    except BaseException:
        db.rollback()
        raise
