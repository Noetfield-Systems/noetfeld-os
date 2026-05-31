#!/usr/bin/env python3
"""Emit docs/api/openapi.yaml from the filtered public OpenAPI schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "types"))
sys.path.insert(0, str(ROOT / "packages" / "config"))
sys.path.insert(0, str(ROOT / "services" / "governance"))
sys.path.insert(0, str(ROOT / "services" / "events"))
sys.path.insert(0, str(ROOT / "services" / "ledger"))
sys.path.insert(0, str(ROOT / "services" / "graph"))
sys.path.insert(0, str(ROOT / "services" / "signals"))
sys.path.insert(0, str(ROOT / "services" / "workflow"))
sys.path.insert(0, str(ROOT / "services" / "ai-runtime"))
sys.path.insert(0, str(ROOT / "services" / "inspectors"))
sys.path.insert(0, str(ROOT / "services" / "identity"))
sys.path.insert(0, str(ROOT / "services" / "copilot-governance"))


def main() -> int:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        yaml = None

    from noetfield_governance.api import app

    schema = app.openapi()
    out_dir = ROOT / "docs" / "api"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "openapi.json"
    json_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    yaml_path = out_dir / "openapi.yaml"
    if yaml is not None:
        yaml_path.write_text(yaml.dump(schema, sort_keys=False, allow_unicode=True), encoding="utf-8")
    else:
        yaml_path.write_text(
            "# Install PyYAML to regenerate openapi.yaml from openapi.json\n",
            encoding="utf-8",
        )
    print(f"Wrote {json_path} and {yaml_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
