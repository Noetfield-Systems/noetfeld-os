#!/usr/bin/env python3
"""Generate docs/ops/plans registry — delegates to generate-prompt-pack-v2.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    v2 = ROOT / "scripts" / "generate-prompt-pack-v2.py"
    rc = subprocess.call([sys.executable, str(v2)])
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
