#!/usr/bin/env python3
"""Upsert noos-loop-runner env via Railway GraphQL (workspace API token).

Workspace API tokens work for project GraphQL but break `railway whoami`.
Use this for GHA/automation instead of railway CLI link/whoami.
"""
from __future__ import annotations
import json, os, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "94ade24c-9b24-4d8d-a443-9ddc5bf6ef54"
ENV = "54692a27-7882-4210-a012-d1260f8340a2"
SERVICE = "0ecc1f70-9582-4a7e-b6dd-0eb93accefa8"

def load_env_files() -> dict[str, str]:
    out = {}
    for p in (
        Path.home() / ".noetfield-platform-secrets" / "noos-local.env",
        Path.home() / ".noetfield-platform-secrets" / "noetfield.env",
    ):
        if not p.is_file():
            continue
        for line in p.read_text().splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"')
    out.update({k: v for k, v in os.environ.items() if v})
    return out

def gql(token: str, query: str, variables: dict | None = None) -> dict:
    body = {"query": query}
    if variables is not None:
        body["variables"] = variables
    req = urllib.request.Request(
        "https://backboard.railway.com/graphql/v2",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "RailwayCLI/5.27.2",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        row = json.loads(resp.read().decode())
    if row.get("errors"):
        raise RuntimeError(json.dumps(row["errors"])[:500])
    return row

def main() -> int:
    env = load_env_files()
    token = (
        env.get("RAILWAY_GHA_TOKEN")
        or env.get("RAILWAY_GRAPHQL_TOKEN")
        or env.get("RAILWAY_API_TOKEN")
        or env.get("RAILWAY_TOKEN")
        or ""
    ).strip()
    if not token:
        # OAuth session fallback (Mac)
        cfg = Path.home() / ".railway" / "config.json"
        if cfg.is_file():
            token = (json.loads(cfg.read_text()).get("user") or {}).get("accessToken") or ""
    if not token:
        print(json.dumps({"ok": False, "error": "no_railway_token"}))
        return 1
    variables = {
        "NOETFIELD_RUNWAY_API_URL": env.get("NOETFIELD_RUNWAY_API_URL")
        or "https://noetfield-runway-runtime-api-staging.sina-kazemnezhad-ca.workers.dev",
        "NOETFIELD_RUNWAY_API_SECRET": env["NOETFIELD_RUNWAY_API_SECRET"],
        "NOETFIELD_RUNWAY_API_KEY_ID": env.get("NOETFIELD_RUNWAY_API_KEY_ID") or "staging-proof",
        "NOOS_PLAN_COMPLETION_LIVE_INTAKE": env.get("NOOS_PLAN_COMPLETION_LIVE_INTAKE") or "1",
        "NOOS_PLAN_COMPLETION_TELEGRAM": env.get("NOOS_PLAN_COMPLETION_TELEGRAM") or "1",
        "NOOS_LOOP_SECRET": env.get("NOOS_LOOP_SECRET") or env.get("LOOP_RUNNER_SECRET") or "",
        "LOOP_RUNNER_SECRET": env.get("NOOS_LOOP_SECRET") or env.get("LOOP_RUNNER_SECRET") or "",
        "NOETFIELD_SUPABASE_URL": env.get("NOETFIELD_SUPABASE_URL") or env.get("SUPABASE_URL") or "",
        "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY": env.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or env.get("SUPABASE_SERVICE_ROLE_KEY")
        or "",
    }
    variables["SUPABASE_URL"] = variables["NOETFIELD_SUPABASE_URL"]
    variables["SUPABASE_SERVICE_ROLE_KEY"] = variables["NOETFIELD_SUPABASE_SERVICE_ROLE_KEY"]
    missing = [k for k, v in variables.items() if not v and k.endswith(("SECRET", "KEY", "URL"))]
    if missing:
        print(json.dumps({"ok": False, "error": "missing_vars", "missing": missing}))
        return 1
    gql(
        token,
        """
        mutation($input: VariableCollectionUpsertInput!) {
          variableCollectionUpsert(input: $input)
        }
        """,
        {
            "input": {
                "projectId": PROJECT,
                "environmentId": ENV,
                "serviceId": SERVICE,
                "skipDeploys": False,
                "variables": variables,
            }
        },
    )
    print(json.dumps({"ok": True, "service": "noos-loop-runner", "keys": sorted(variables.keys())}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
