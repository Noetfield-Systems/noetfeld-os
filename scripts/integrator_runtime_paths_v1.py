"""Resolve runtime paths for the NOOS integrator coordination layer."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "data/noos-integrator-role-v1.json"
DEFAULT_RUNTIME_DIR = ROOT / ".noos-runtime" / "integrator"
DEFAULT_HOME_MIRROR = Path.home() / ".sina" / "noos-integrator-state-v1.json"


def integrator_runtime_dir() -> Path:
    override = os.environ.get("NOOS_INTEGRATOR_RUNTIME_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_RUNTIME_DIR


def integrator_state_path() -> Path:
    override = os.environ.get("NOOS_INTEGRATOR_STATE_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return integrator_runtime_dir() / "noos-integrator-state-v1.json"


def integrator_lock_path() -> Path:
    override = os.environ.get("NOOS_INTEGRATOR_LOCK_PATH", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return integrator_runtime_dir() / "noos-integrator-state-v1.lock"


def integrator_home_mirror_path() -> Path:
    override = os.environ.get("NOOS_INTEGRATOR_HOME_MIRROR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_HOME_MIRROR
