"""Noetfield L8 embedding provider — Voyage AI wire (SourceA pattern, repo-local).

Law: ~/.sina/secrets.env · SourceA SECRETS_VAULT.md · INCIDENT-036 fake-green guard.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"
_VOYAGE_MODEL = os.getenv("VOYAGE_MODEL", "voyage-4-lite")
_HASH_DIMS = 64

_VAULT_KEYS = (
    "VOYAGE_API_KEY",
    "OPENAI_API_KEY",
    "EMBEDDING_PROVIDER",
    "VOYAGE_MODEL",
    "OPENAI_MODEL",
)


def _vault_paths() -> list[Path]:
    return [
        Path.home() / ".sina" / "secrets.env",
        Path.home() / ".noetfield-platform-secrets" / "noetfield.env",
        Path.home() / ".sourcea-secrets" / "noetfield.env",
    ]


def hydrate_vault() -> None:
    """Load embedding keys from vault when not already in os.environ."""
    for vault in _vault_paths():
        if not vault.is_file():
            continue
        for line in vault.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            if key in _VAULT_KEYS and key not in os.environ:
                cleaned = val.strip().strip('"').strip("'")
                if cleaned:
                    os.environ[key] = cleaned
        break


def voyage_key_on_disk() -> bool:
    for vault in _vault_paths():
        if not vault.is_file():
            continue
        text = vault.read_text(encoding="utf-8", errors="replace")
        if "VOYAGE_API_KEY=" in text and not re.search(r"VOYAGE_API_KEY=\s*$", text, re.M):
            return True
    return bool(os.getenv("VOYAGE_API_KEY", "").strip())


def _active_provider() -> str:
    hydrate_vault()
    provider = os.getenv("EMBEDDING_PROVIDER", "").lower().strip()
    voyage_key = os.getenv("VOYAGE_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if provider == "voyage" and voyage_key:
        return "voyage"
    if provider == "openai" and openai_key:
        return "openai"
    if voyage_key:
        return "voyage"
    if openai_key:
        return "openai"
    return "hash_local"


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]{3,}", (text or "").lower())


def _hash_embed(text: str, dims: int = _HASH_DIMS) -> list[float]:
    vec = [0.0] * dims
    for tok in _tokenize(text):
        h = hashlib.sha256(tok.encode()).digest()
        for i in range(dims):
            vec[i] += (h[i % len(h)] / 255.0) - 0.5
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [round(v / norm, 6) for v in vec]


def _post(url: str, payload: dict, headers: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Embedding API error {exc.code}: {body}") from exc


def embed_text(text: str, *, is_query: bool = False) -> list[float]:
    mode = _active_provider()
    if mode == "voyage":
        key = os.getenv("VOYAGE_API_KEY", "").strip()
        model = os.getenv("VOYAGE_MODEL", _VOYAGE_MODEL)
        payload = {
            "input": [text],
            "model": model,
            "input_type": "query" if is_query else "document",
        }
        body = _post(
            _VOYAGE_URL,
            payload,
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        data = body.get("data") or []
        if not data:
            raise RuntimeError("Voyage API returned no embeddings")
        return [float(x) for x in data[0]["embedding"]]
    return _hash_embed(text)


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return round(dot / (na * nb), 6)


def hybrid_score(*, token_score: float, query: str, chunk_text: str) -> float:
    qe = embed_text(query, is_query=True)
    ce = embed_text(chunk_text, is_query=False)
    sem = cosine(qe, ce)
    return round(0.55 * token_score + 0.45 * sem, 6)


def provider_payload() -> dict[str, Any]:
    hydrate_vault()
    mode = _active_provider()
    semantic = mode in ("voyage", "openai")
    model = os.getenv("VOYAGE_MODEL", _VOYAGE_MODEL) if mode == "voyage" else (
        os.getenv("OPENAI_MODEL", "text-embedding-3-small") if mode == "openai" else "hash_local"
    )
    return {
        "mode": mode,
        "model": model,
        "semantic": semantic,
        "hybrid": True,
        "producer": "nf-embedding-provider-v1",
        "voyage_key_on_disk": voyage_key_on_disk(),
    }
