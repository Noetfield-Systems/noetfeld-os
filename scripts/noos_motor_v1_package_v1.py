#!/usr/bin/env python3
"""NOOS Motor v1 — release packager.

NF-NOOS-MOTOR-V1-FULL-RUNWAY, Phase 6. Builds a versioned, self-describing
release bundle for the sellable vertical slice and a manifest with checksums,
git commit, build time, schema/workflow versions, migration version and rollback
instructions. Deterministic components; build time + commit are injected/read at
build (not baked into importable code).

The bundle is a tarball of the motor components + docs + sample IO. It is a
deployable archive appropriate for this Python stack (no container toolchain
assumed present). Nothing here claims the release is deployed — only built.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

PRODUCT_VERSION = "1.0.0"
SCHEMA_VERSION = "noos-motor-execution-v1"
WORKFLOW_VERSION = "noos-motor-v1"
MIGRATION_VERSION = "0020_motor_provenance_fields"

# Components that constitute the shippable motor.
COMPONENTS = [
    "scripts/noos_motor_state_machine_v1.py",
    "scripts/noos_motor_local_executor_v1.py",
    "scripts/noos_observability_semantics_v1.py",
    "scripts/noos_motor_v1_verify_v1.py",
    "scripts/noos_motor_v1_package_v1.py",
    "infrastructure/supabase/migrations/0020_motor_provenance_fields.sql",
    "docs/product/NOOS-MOTOR-V1.md",
    "docs/product/NOOS-MOTOR-V1-ARCHITECTURE.md",
    "docs/product/NOOS-MOTOR-V1-QUICKSTART.md",
    "docs/product/NOOS-MOTOR-V1-RUNBOOK.md",
    "docs/product/samples/sample-input.json",
    "bin/noos",
    ".env.example",
]
TESTS = [
    "tests/test_noos_motor_state_machine_v1.py",
    "tests/test_noos_motor_local_executor_v1.py",
    "tests/test_noos_motor_provenance_v1.py",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return "unknown"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(*, build_time: str | None = None) -> dict[str, Any]:
    build_time = build_time or utc_now()
    present, missing, checksums = [], [], {}
    for rel in COMPONENTS + TESTS:
        p = ROOT / rel
        if p.is_file():
            present.append(rel)
            checksums[rel] = _sha256(p)
        else:
            missing.append(rel)
    return {
        "schema": "noos-motor-v1-release-manifest-v1",
        "not_a_verdict": "Release manifest. Describes a BUILT artifact only — not a deployment claim. SUBMITTED for independent verification.",
        "canon_version": "FOUNDER_CANON_v1+MACHINE_LOOPS_v1",
        "product": "NOOS Motor v1",
        "product_version": PRODUCT_VERSION,
        "git_commit": _git_commit(),
        "build_time": build_time,
        "schema_version": SCHEMA_VERSION,
        "workflow_version": WORKFLOW_VERSION,
        "migration_version": MIGRATION_VERSION,
        "components_present": present,
        "components_missing": missing,
        "checksums_sha256": checksums,
        "external_activation_required": [
            "Restart cloud http_loop producer (Railway noos-loop-runner) — needs cloud deploy creds",
            "Apply Supabase migration 0020 (make supabase-migrate) — founder-gated, needs DB creds",
            "Run 3 consecutive real cloud organic http_loop cycles — depends on producer restart",
        ],
        "rollback": {
            "code": "git revert the motor commits on this branch (no merge to main was performed)",
            "migration": "0020 is additive/nullable; DROP COLUMN IF EXISTS block at the foot of the .sql reverses it",
        },
    }


def build_bundle(*, out_dir: Path | None = None) -> dict[str, Any]:
    out_dir = out_dir or DIST
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest()
    manifest_path = out_dir / "noos-motor-v1-release-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    bundle_path = out_dir / f"noos-motor-v1-{PRODUCT_VERSION}.tar.gz"
    with tarfile.open(bundle_path, "w:gz") as tar:
        for rel in manifest["components_present"]:
            tar.add(ROOT / rel, arcname=f"noos-motor-v1/{rel}")
        tar.add(manifest_path, arcname="noos-motor-v1/release-manifest.json")
    manifest["bundle_path"] = str(bundle_path)
    manifest["bundle_sha256"] = _sha256(bundle_path)
    manifest["manifest_path"] = str(manifest_path)
    # rewrite manifest with the bundle checksum included
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--manifest-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.manifest_only:
        m = build_manifest()
    else:
        m = build_bundle(out_dir=args.out_dir)
    if args.json:
        print(json.dumps(m, indent=2))
    else:
        print(f"product={m['product']} v{m['product_version']} commit={m['git_commit'][:8]}")
        print(f"components: {len(m['components_present'])} present, {len(m['components_missing'])} missing")
        if not args.manifest_only:
            print(f"bundle={m.get('bundle_path')} sha256={m.get('bundle_sha256', '')[:16]}")
        if m["components_missing"]:
            print(f"MISSING: {m['components_missing']}")
    return 0 if not m["components_missing"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
