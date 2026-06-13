#!/usr/bin/env python3
"""Mirror status between noetfield-1000 library and os/plans nf-future-* stubs."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB_REG = ROOT / "os" / "plan-library" / "noetfield-1000" / "REGISTRY.json"
STUB_REG = ROOT / "os" / "plans" / "REGISTRY.json"
PLANS_DIR = ROOT / "os" / "plans"

# wave task id → nf-future stub id (from plan)
WAVE_TO_STUB = {
    "nf-procurement-pack-zip-034": "nf-future-0703",
    "nf-demo-page-confidence-035": "nf-future-0704",
    "nf-public-demo-url-036": "nf-future-0707",
}

# phase-7 T0 regression tasks → stub hints
REGRESSION_STUBS = ["nf-future-0703", "nf-future-0704", "nf-future-0705", "nf-future-0706", "nf-future-0707"]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _patch_md_status(md_path: Path, status: str) -> bool:
    if not md_path.is_file():
        return False
    text = md_path.read_text(encoding="utf-8")
    new_text, n = re.subn(r"^status:\s*\w+\s*$", f"status: {status}", text, count=1, flags=re.M)
    if n:
        md_path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    if not LIB_REG.is_file():
        print("SKIP: noetfield-1000 REGISTRY missing")
        return

    lib = _load(LIB_REG)
    done_nf = {p["id"] for p in lib["plans"] if p.get("status") == "done"}
    print(f"Library done count: {len(done_nf)}")

    if not STUB_REG.is_file():
        print("SKIP: os/plans REGISTRY missing")
        return

    stub = _load(STUB_REG)
    synced = 0
    for entry in stub.get("plans", []):
        stub_id = entry["id"]
        if stub_id in REGRESSION_STUBS or stub_id in WAVE_TO_STUB.values():
            # Mark done if any lib prompt in phase-7 pilot gtm is done
            if any(p.get("status") == "done" and p.get("phase") == "phase-7-pilot-gtm" for p in lib["plans"]):
                if entry.get("status") != "done":
                    entry["status"] = "done"
                    synced += 1
                    rel = entry.get("path", "").replace("os/plans/", "")
                    _patch_md_status(ROOT / entry["path"], "done")

    _save(STUB_REG, stub)
    print(f"Synced stub statuses: {synced}")


if __name__ == "__main__":
    main()
