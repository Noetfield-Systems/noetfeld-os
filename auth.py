"""
API key authentication — Phase 2 tenant stub.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from pathlib import Path

from fastapi import Header, HTTPException, status

from config import API_KEYS_PATH


@dataclass(frozen=True)
class AuthenticatedClient:
    key_id: str
    tenant_id: str
    org_id: str
    scopes: frozenset[str]


def _hash_key(raw_key: str, *, salt: str) -> str:
    material = f"{salt}:{raw_key}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


class ApiKeyStore:
    def __init__(self) -> None:
        self._by_hash: dict[str, AuthenticatedClient] = {}
        self._salt = "noetfeld-os-v1"

    def load(self, path: Path | None = None) -> None:
        path = path or API_KEYS_PATH
        if not path.is_file():
            self._by_hash = {}
            return
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._salt = str(raw.get("salt", "noetfeld-os-v1"))
        self._by_hash = {}
        for item in raw.get("keys", []):
            client = AuthenticatedClient(
                key_id=str(item["key_id"]),
                tenant_id=str(item["tenant_id"]),
                org_id=str(item["org_id"]),
                scopes=frozenset(str(s) for s in item.get("scopes", [])),
            )
            self._by_hash[str(item["key_hash"])] = client

    def authenticate(self, raw_key: str) -> AuthenticatedClient | None:
        key_hash = _hash_key(raw_key, salt=self._salt)
        return self._by_hash.get(key_hash)

    @staticmethod
    def generate_key() -> str:
        return secrets.token_urlsafe(32)


KEY_STORE = ApiKeyStore()


def require_scope(scope: str):
    async def dependency(
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ) -> AuthenticatedClient:
        if not x_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-API-Key header",
            )
        client = KEY_STORE.authenticate(x_api_key)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key",
            )
        if scope not in client.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key missing scope: {scope}",
            )
        return client

    return dependency


require_decision_write = require_scope("decision:write")
require_audit_read = require_scope("audit:read")


__all__ = [
    "AuthenticatedClient",
    "ApiKeyStore",
    "KEY_STORE",
    "_hash_key",
    "require_audit_read",
    "require_decision_write",
]
