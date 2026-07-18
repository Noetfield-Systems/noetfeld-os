#!/usr/bin/env python3
"""NOOS recipe registry v1 (NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §6).

Versioned recipe registry. Loads recipe definitions from data/recipes/ and
REJECTS unknown or unversioned recipes. A recipe pins the entire policy surface
(providers, authz, inputs, stacks, limits, path allow/deny, commands, network,
branch/PR policy, approval boundary, output contract) so the runner cannot
exceed it.
"""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECIPE_DIR = ROOT / "data" / "recipes"


class UnknownRecipe(Exception):
    """Raised for an unknown or unversioned recipe."""


def _recipe_path(recipe_id: str) -> Path:
    return RECIPE_DIR / f"{recipe_id}.json"


def load_recipe(recipe_id: str, *, version: str | None = None) -> dict[str, Any]:
    """Load and validate a recipe. Rejects unknown recipe_id and, if ``version``
    is given, a version mismatch. A recipe without a recipe_version is rejected."""
    if not recipe_id or "/" in recipe_id or ".." in recipe_id:
        raise UnknownRecipe(f"invalid recipe_id {recipe_id!r}")
    path = _recipe_path(recipe_id)
    if not path.is_file():
        raise UnknownRecipe(f"unknown recipe {recipe_id!r} (no {path.name})")
    recipe = json.loads(path.read_text(encoding="utf-8"))
    if recipe.get("recipe_id") != recipe_id:
        raise UnknownRecipe(f"recipe_id mismatch in {path.name}")
    rv = recipe.get("recipe_version")
    if not rv:
        raise UnknownRecipe(f"recipe {recipe_id!r} is unversioned (rejected)")
    if version is not None and version != rv:
        raise UnknownRecipe(f"recipe {recipe_id!r} version {version!r} != registered {rv!r}")
    return recipe


def list_recipes() -> list[dict[str, str]]:
    out = []
    if RECIPE_DIR.is_dir():
        for p in sorted(RECIPE_DIR.glob("*.json")):
            try:
                r = json.loads(p.read_text(encoding="utf-8"))
                out.append({"recipe_id": r.get("recipe_id", p.stem), "recipe_version": r.get("recipe_version", "?"), "status": r.get("status", "?")})
            except (json.JSONDecodeError, OSError):
                continue
    return out


def path_allowed(recipe: dict[str, Any], rel_path: str) -> tuple[bool, str | None]:
    """True iff rel_path matches an allowed glob AND no forbidden glob. Forbidden
    always wins (defense in depth)."""
    rel = rel_path.lstrip("./")
    for pat in recipe.get("forbidden_file_paths", []):
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, pat.replace("**", "*")):
            return False, f"forbidden:{pat}"
    for pat in recipe.get("allowed_file_paths", []):
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, pat.replace("**/", "")):
            return True, None
    return False, "not_in_allowlist"


def within_limits(recipe: dict[str, Any], *, changed_files: int, patch_bytes: int,
                  model_calls: int, attempts: int) -> tuple[bool, list[str]]:
    lim = recipe.get("limits", {})
    viol = []
    if changed_files > lim.get("max_changed_files", 3):
        viol.append("max_changed_files")
    if patch_bytes > lim.get("max_patch_bytes", 20000):
        viol.append("max_patch_bytes")
    if model_calls > lim.get("max_model_calls", 4):
        viol.append("max_model_calls")
    if attempts > lim.get("max_repair_attempts", 3):
        viol.append("max_repair_attempts")
    return (not viol), viol


def requires_human_approval(recipe: dict[str, Any], action: str) -> bool:
    """True if ``action`` touches a human-approval-boundary concern."""
    boundary = " ".join(recipe.get("human_approval_boundary", [])).lower()
    a = action.lower()
    triggers = ["merge", "deploy", "secret", "credential", "branch-protection",
                "ownership", "billing", "forbidden"]
    return any(t in a and t in boundary for t in triggers)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        try:
            r = load_recipe(sys.argv[1], version=sys.argv[2] if len(sys.argv) > 2 else None)
            print(json.dumps({"recipe_id": r["recipe_id"], "version": r["recipe_version"], "status": r["status"]}, indent=2))
        except UnknownRecipe as e:
            print(f"REJECTED: {e}")
            raise SystemExit(1)
    else:
        print(json.dumps(list_recipes(), indent=2))
