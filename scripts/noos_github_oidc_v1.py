"""Verify GitHub Actions OIDC for keyless cloud coding queue access.

Only the fixed first-party workflow on the default branch is authorized.
An issue event can queue a packet only when the authenticated actor is the
Founder; scheduled runs may claim and report, not create arbitrary work.
"""
from __future__ import annotations

import os
from functools import lru_cache

ISSUER = "https://token.actions.githubusercontent.com"
AUDIENCE = "noetfield-coding-workforce"
JWK_URL = ISSUER + "/.well-known/jwks"
REPOSITORY = "Noetfield-Systems/noetfeld-os"
WORKFLOW = REPOSITORY + "/.github/workflows/noos-cloud-coder.yml@refs/heads/main"


@lru_cache(maxsize=1)
def _keys():
    import jwt
    return jwt.PyJWKClient(JWK_URL, cache_keys=True, lifespan=600)


def authorize(credential: str, operation: str) -> dict:
    if operation not in {"queue", "claim", "report", "status"}:
        raise ValueError("GITHUB_OIDC_OPERATION_DENIED")
    if not credential.startswith("Bearer ") or len(credential) < 250:
        raise ValueError("GITHUB_OIDC_MISSING")
    try:
        import jwt
        token = credential.removeprefix("Bearer ").strip()
        signing_key = _keys().get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token, signing_key, algorithms=["RS256"],
            audience=AUDIENCE, issuer=ISSUER, leeway=30,
            options={"require":["iss","aud","exp","iat","repository","workflow_ref","event_name"]},
        )
    except Exception as exc:
        raise ValueError("GITHUB_OIDC_UNTRUSTED") from exc
    if (claims.get("repository") != REPOSITORY
        or claims.get("ref") != "refs/heads/main"
        or claims.get("workflow_ref") != WORKFLOW):
        raise ValueError("GITHUB_WORKFLOW_IDENTITY_DENIED")
    event = claims.get("event_name")
    if operation=="queue":
        if event != "issues" or claims.get("actor") != os.environ.get(
                "NOOS_FOUNDER_GITHUB_LOGIN", "kazemnezhadsina144-dot"):
            raise ValueError("GITHUB_ISSUE_ENQUEUE_DENIED")
    elif event not in {"schedule","workflow_dispatch","issues","repository_dispatch"}:
        raise ValueError("GITHUB_CODING_EXECUTOR_EVENT_DENIED")
    return {"source":"signed_github_oidc","workflow_ref":WORKFLOW,
            "actor":claims.get("actor"),"event":event,"run_id":claims.get("run_id")}
