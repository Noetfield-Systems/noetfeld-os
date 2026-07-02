"""Resolve factory runtime output paths (tracked vs local ephemeral)."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKED_EXECUTION_DIR = ROOT / "docs/run_patches/execution"
DEFAULT_RUNTIME_DIR = ROOT / ".noos-runtime/factory"
TRACKED_INBOX_BUNDLE = ROOT / "data/noos-cloud-worker-inbox-v1.json"
MANIFEST_PATH = ROOT / "docs/run_patches/noetfield_run_patch_manifest_10100_v1.json"


def receipt_commit_enabled(explicit: bool = False) -> bool:
    if explicit:
        return True
    return os.environ.get("NOOS_FACTORY_RECEIPT_COMMIT", "").strip() in {"1", "true", "yes", "on"}


def execution_dir(*, receipt_commit: bool = False) -> Path:
    if receipt_commit_enabled(receipt_commit):
        return TRACKED_EXECUTION_DIR
    override = os.environ.get("NOOS_FACTORY_RUNTIME_DIR", "").strip()
    if override:
        return Path(override)
    return DEFAULT_RUNTIME_DIR / "execution"


def inbox_bundle_path(*, receipt_commit: bool = False) -> Path:
    if receipt_commit_enabled(receipt_commit):
        return TRACKED_INBOX_BUNDLE
    override = os.environ.get("NOOS_FACTORY_RUNTIME_DIR", "").strip()
    if override:
        return Path(override) / "noos-cloud-worker-inbox-v1.json"
    return DEFAULT_RUNTIME_DIR / "noos-cloud-worker-inbox-v1.json"
