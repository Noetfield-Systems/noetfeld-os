"""
Policy metadata — hashes, versions, and startup registry (Phase 2).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from config import BASE_DIR, BASE_POLICY_PATH, CORRIDOR_POLICY_PATH
from policy_loader import BasePolicy, CorridorPolicy, load_base_policy, load_corridor_policy


class PolicyNotReadyError(RuntimeError):
    """Raised when policy files are missing or not active."""


@dataclass(frozen=True)
class PolicyMeta:
    rule_set_id: str
    rule_set_version: str
    base_policy_hash: str
    corridor_policy_hash: str
    base_policy: BasePolicy
    corridor_policy: CorridorPolicy
    base_status: str
    corridor_status: str

    @property
    def combined_hash(self) -> str:
        material = f"{self.base_policy_hash}:{self.corridor_policy_hash}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_raw(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_policy_meta(
    *,
    base_path: Path | None = None,
    corridor_path: Path | None = None,
) -> PolicyMeta:
    base_path = base_path or BASE_POLICY_PATH
    corridor_path = corridor_path or CORRIDOR_POLICY_PATH

    if not base_path.is_file() or not corridor_path.is_file():
        raise PolicyNotReadyError("Policy files missing — gate fail-closed")

    base_raw = _load_raw(base_path)
    corridor_raw = _load_raw(corridor_path)

    base_status = str(base_raw.get("status", "active"))
    corridor_status = str(corridor_raw.get("status", "active"))
    if base_status != "active" or corridor_status != "active":
        raise PolicyNotReadyError("Policy pack is not active — gate fail-closed")

    rule_set_id = str(base_raw.get("rule_set_id", "noetfeld-base"))
    rule_set_version = str(
        base_raw.get("policy_pack_version", base_raw.get("rule_set_version", "0.0.0"))
    )

    return PolicyMeta(
        rule_set_id=rule_set_id,
        rule_set_version=rule_set_version,
        base_policy_hash=_file_sha256(base_path),
        corridor_policy_hash=_file_sha256(corridor_path),
        base_policy=load_base_policy(base_path),
        corridor_policy=load_corridor_policy(corridor_path),
        base_status=base_status,
        corridor_status=corridor_status,
    )


class PolicyRegistry:
    """Loaded once at startup; required before /v1/decision."""

    _meta: PolicyMeta | None = None

    @classmethod
    def load(cls) -> PolicyMeta:
        cls._meta = build_policy_meta()
        return cls._meta

    @classmethod
    def meta(cls) -> PolicyMeta:
        if cls._meta is None:
            raise PolicyNotReadyError("Policy registry not initialized")
        return cls._meta

    @classmethod
    def ensure_ready(cls) -> PolicyMeta:
        return cls.meta()

    @classmethod
    def reset(cls) -> None:
        cls._meta = None


__all__ = [
    "PolicyMeta",
    "PolicyNotReadyError",
    "PolicyRegistry",
    "build_policy_meta",
]
