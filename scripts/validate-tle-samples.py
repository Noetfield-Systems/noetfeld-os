#!/usr/bin/env python3
"""Validate TLE v1 YAML samples against packages/schemas/tle-v1.schema.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "packages/schemas/tle-v1.schema.json"
SAMPLES = ROOT / "docs/spec/samples"


def main() -> int:
    try:
        import jsonschema
        import yaml
    except ImportError:
        print("FAIL: pip install jsonschema pyyaml", file=sys.stderr)
        return 1

    schema = json.loads(SCHEMA.read_text())
    fail = 0
    for path in sorted(SAMPLES.glob("tle-*.yaml")):
        data = yaml.safe_load(path.read_text())
        try:
            jsonschema.validate(data, schema)
            print(f"OK   {path.name}")
        except jsonschema.ValidationError as e:
            print(f"FAIL {path.name}: {e.message}", file=sys.stderr)
            fail = 1
    if fail:
        return 1
    print("All TLE samples valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
