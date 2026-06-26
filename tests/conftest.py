"""Pytest path setup so `scripts.*` imports resolve in CI and local runs."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Offline verify bundles — force memory stores unless explicitly overridden.
if os.environ.get("NF_PYTEST_ALLOW_POSTGRES") != "1":
    os.environ["RUNTIME_EVENT_STORE"] = "memory"
    os.environ["INTAKE_PERSISTENCE"] = "memory"
    os.environ["REDIS_SESSIONS_ENABLED"] = "false"

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
