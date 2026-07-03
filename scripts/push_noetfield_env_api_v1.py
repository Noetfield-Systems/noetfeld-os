#!/usr/bin/env python3
"""Push Noetfield intake env to main Vercel via API (no OAuth loop).

Reads: ~/.sina/noetfield-trial-env-clone-v1.env
Token: VERCEL_TOKEN env · ~/.sina/secrets.env · ~/.sina/sourcea-vercel-token-v1.json
Receipt: ~/.sina/noetfield-intake-env-push-receipt-v1.json
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "noetfield-intake-env-push-receipt-v1.json"
ENV_CLONE = SINA / "noetfield-trial-env-clone-v1.env"
SECRETS = SINA / "secrets.env"
TOKEN_JSON = SINA / "sourcea-vercel-token-v1.json"

SCOPE = os.environ.get("NF_VERCEL_SCOPE", "the-777-foundation")
PROJECT = os.environ.get("NF_VERCEL_PROJECT", "noetfield")
KEYS = ["RESEND_API_KEY", "INTAKE_EMAIL_FROM", "INTAKE_EMAIL_TO", "INTAKE_AUTO_ACK_ENABLED"]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_token() -> str | None:
    tok = os.environ.get("VERCEL_TOKEN", "").strip()
    if tok:
        return tok
    for path in (SECRETS, TOKEN_JSON):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".json":
            try:
                row = json.loads(text)
                tok = str(row.get("token") or row.get("vercel_token") or "").strip()
                if tok:
                    return tok
            except json.JSONDecodeError:
                pass
        else:
            matches = [ln for ln in text.splitlines() if ln.startswith("VERCEL_TOKEN=")]
            for line in reversed(matches):
                val = line.split("=", 1)[1].strip().strip('"')
                if val and "PASTE" not in val and len(val) >= 20:
                    return val
    return None


def _read_env_file() -> dict[str, str]:
    src = Path(os.environ.get("NF_SECRETS_VAULT", str(ENV_CLONE)))
    merged: dict[str, str] = {}
    for path in (ENV_CLONE, SECRETS):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            merged[k.strip()] = v.strip().strip('"')
    if not merged:
        raise SystemExit(f"FAIL: missing env clone {src}")
    # Vault may use RESEND_NOETFIELD_API_KEY — map to Vercel key name
    if not merged.get("RESEND_API_KEY"):
        for alt in ("RESEND_NOETFIELD_API_KEY", "RESEND_FULL_API_KEY", "RESEND_FROM"):
            if merged.get(alt) and alt.startswith("RESEND"):
                if alt == "RESEND_FROM":
                    continue
                merged["RESEND_API_KEY"] = merged[alt]
                break
    return merged


def _api(method: str, path: str, token: str, body: dict | None = None) -> dict:
    q = urllib.parse.urlencode({"slug": SCOPE})
    url = f"https://api.vercel.com{path}?{q}" if "?" not in path else f"https://api.vercel.com{path}&{q}"
    data = None
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:800]}") from exc


def _list_env(token: str) -> list[dict]:
    row = _api("GET", f"/v9/projects/{PROJECT}/env", token)
    return list(row.get("envs") or [])


def _upsert_env(token: str, key: str, value: str) -> dict:
    existing = [e for e in _list_env(token) if e.get("key") == key]
    body = {
        "key": key,
        "value": value,
        "type": "encrypted",
        "target": ["production"],
    }
    if existing:
        eid = existing[0]["id"]
        return _api("PATCH", f"/v9/projects/{PROJECT}/env/{eid}", token, body)
    return _api("POST", f"/v10/projects/{PROJECT}/env", token, body)


def _trigger_deploy(token: str) -> dict:
    return _api(
        "POST",
        f"/v13/deployments",
        token,
        {
            "name": PROJECT,
            "project": PROJECT,
            "target": "production",
            "gitSource": {
                "type": "github",
                "org": "Noetfield-Systems",
                "repo": "Noetfield",
                "ref": "ship/nf-gaos-w2-production",
            },
        },
    )


def _intake_health() -> dict:
    url = "https://www.noetfield.com/api/intake/health"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except OSError:
        return {}


def main() -> int:
    token = _load_token()
    if not token or "PASTE" in token or len(token) < 20:
        msg = {
            "ok": False,
            "error": "invalid_or_placeholder_vercel_token",
            "fix": "Replace VERCEL_TOKEN in ~/.sina/secrets.env with REAL token from https://vercel.com/account/settings/tokens (main Gmail kazemnezhadsina144@gmail.com)",
            "url": "https://vercel.com/account/settings/tokens",
        }
        RECEIPT.write_text(json.dumps(msg, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(msg, indent=2))
        return 1

    env = _read_env_file()
    steps: list[dict] = []
    for key in KEYS:
        val = env.get(key, "")
        if not val:
            steps.append({"key": key, "ok": False, "error": "missing_in_clone"})
            continue
        try:
            _upsert_env(token, key, val)
            steps.append({"key": key, "ok": True})
        except RuntimeError as exc:
            steps.append({"key": key, "ok": False, "error": str(exc)})

    deploy_row: dict = {"ok": False, "skipped": True}
    if all(s.get("ok") for s in steps):
        try:
            deploy_row = {"ok": True, **_trigger_deploy(token)}
        except RuntimeError as exc:
            deploy_row = {"ok": False, "error": str(exc)}

    health = _intake_health()
    ok = all(s.get("ok") for s in steps) and health.get("delivery_mode") == "resend"
    row = {
        "ok": ok,
        "schema": "noetfield-intake-env-push-v1",
        "at": _now(),
        "scope": SCOPE,
        "project": PROJECT,
        "steps": steps,
        "deploy": deploy_row,
        "intake_health": health,
        "founder_line": (
            "PASS: main intake green — delete trial www"
            if ok
            else "WAIT: redeploy propagating or health still unconfigured — re-check in 60s"
        ),
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
