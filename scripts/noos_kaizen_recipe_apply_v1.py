#!/usr/bin/env python3
"""Phase D — apply locked kaizen recipes with external verify."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "data/noos-kaizen-recipes-v1.json"
PROOF = ROOT / "receipts/proof/noos-kaizen-recipe-apply-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_recipes() -> list[dict[str, Any]]:
    doc = json.loads(RECIPES.read_text(encoding="utf-8"))
    return list(doc.get("recipes") or [])


def match_recipe(text: str, recipes: list[dict[str, Any]]) -> dict[str, Any] | None:
    hay = text.lower()
    for recipe in recipes:
        if str(recipe.get("class") or "").lower() != "machine_safe":
            continue
        pattern = str(recipe.get("match_pattern") or "")
        if pattern and re.search(pattern, hay, re.IGNORECASE):
            return recipe
    return None


def run_cmd(command: str, *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"ok": True, "command": command, "dry_run": True}
    proc = subprocess.run(command, shell=True, cwd=ROOT, capture_output=True, text=True, check=False, timeout=1800)
    return {
        "ok": proc.returncode == 0,
        "command": command,
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-400:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def apply_recipe(recipe: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    fix = run_cmd(str(recipe.get("fix_command") or ""), dry_run=dry_run)
    verify = run_cmd(str(recipe.get("external_verify_command") or ""), dry_run=dry_run)
    ok = fix.get("ok") and verify.get("ok")
    return {
        "schema": "noos-kaizen-recipe-apply-v1",
        "applied_at": utc_now(),
        "recipe_id": recipe.get("id"),
        "class": recipe.get("class"),
        "title": recipe.get("title"),
        "dry_run": dry_run,
        "fix": fix,
        "external_verify": verify,
        "rollback_command": recipe.get("rollback_command"),
        "ok": ok,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--match-text", default="", help="Error/symptom text to match recipe")
    ap.add_argument("--recipe-id", help="Apply specific recipe id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    recipes = load_recipes()
    recipe: dict[str, Any] | None = None
    if args.recipe_id:
        recipe = next((r for r in recipes if r.get("id") == args.recipe_id), None)
    elif args.match_text:
        recipe = match_recipe(args.match_text, recipes)

    if not recipe:
        row = {"ok": False, "error": "no_matching_recipe", "match_text": args.match_text[:200]}
        if args.json:
            print(json.dumps(row, indent=2))
        return 1

    row = apply_recipe(recipe, dry_run=args.dry_run)
    if args.write_receipt and not args.dry_run:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"kaizen_recipe · id={recipe.get('id')} ok={row.get('ok')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
