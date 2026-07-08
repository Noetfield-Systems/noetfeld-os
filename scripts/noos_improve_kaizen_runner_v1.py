#!/usr/bin/env python3
"""UPG-0211 — daily Kaizen runner: top machine_safe item → repair loop route."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data/noos-machine-loops-config-v1.json"
PROOF = ROOT / "receipts/proof/noos-improve-kaizen-daily-v1.json"
KAIZEN_GLOB = "noos-kaizen-*.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def roi_score(row: dict[str, Any]) -> float:
    roi = row.get("expected_roi") or {}
    if isinstance(roi, dict):
        cost = float(roi.get("cost_saved_usd") or 0)
        risk = 1.0 if roi.get("risk_reduced") else 0.0
        revenue = 1.0 if roi.get("revenue_unblocked") else 0.0
        return cost + (risk * 10) + (revenue * 20)
    if isinstance(roi, str) and roi:
        return 5.0
    score = row.get("score") or {}
    if isinstance(score, dict) and score.get("score") is not None:
        return max(0.0, 100.0 - float(score["score"]))
    return 1.0


def load_kaizen_candidates() -> list[dict[str, Any]]:
    proof_dir = ROOT / "receipts/proof"
    rows: list[dict[str, Any]] = []
    for path in sorted(proof_dir.glob(KAIZEN_GLOB), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if str(row.get("class") or "").lower() != "machine_safe":
            continue
        row["_source_path"] = str(path.relative_to(ROOT))
        rows.append(row)
    rows.sort(key=roi_score, reverse=True)
    return rows


def already_ran_today() -> bool:
    if not PROOF.is_file():
        return False
    try:
        row = json.loads(PROOF.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    ran = str(row.get("ran_at") or row.get("evaluated_at") or "")[:10]
    return ran == utc_now()[:10]


def run(*, force: bool = False) -> dict[str, Any]:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.is_file() else {}
    kaizen_recipes = ROOT / "data/noos-kaizen-recipes-v1.json"
    recipe_hint = None
    if kaizen_recipes.is_file():
        recipe_hint = {"path": str(kaizen_recipes.relative_to(ROOT)), "count": len(json.loads(kaizen_recipes.read_text()).get("recipes") or [])}
    candidates = load_kaizen_candidates()
    picked = candidates[0] if candidates else None
    skipped = already_ran_today() and not force
    repair_route = {
        "worker": (cfg.get("workers") or {}).get("reconciler", "noos-machine-reconciler"),
        "action": "route_to_repair_loop",
        "founder_required": False,
    }
    row: dict[str, Any] = {
        "schema": "noos-improve-kaizen-daily-v1",
        "ran_at": utc_now(),
        "authority": "UPG-0211",
        "sandbox_id": "improve",
        "roi_class": "THROTTLED_ROI",
        "skipped_today": skipped,
        "candidate_count": len(candidates),
        "recipe_registry": recipe_hint,
        "prefer_recipes": bool(recipe_hint),
        "picked": None,
        "repair_route": repair_route if picked and not skipped else None,
        "ok": True,
        "report_line": "improve_kaizen_daily · no_candidates",
    }
    if skipped:
        row["report_line"] = "improve_kaizen_daily · skipped_already_ran_today"
        return row
    if not picked:
        return row
    row["picked"] = {
        "source_path": picked.get("_source_path"),
        "diff_summary": picked.get("diff_summary") or picked.get("title"),
        "loop_id": picked.get("loop_id"),
        "roi_score": roi_score(picked),
        "class": picked.get("class"),
    }
    row["report_line"] = (
        f"improve_kaizen_daily · picked={picked.get('loop_id') or picked.get('source_ref')} "
        f"roi={row['picked']['roi_score']:.1f}"
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="Run even if already ran today")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = run(force=args.force)
    if args.write_receipt:
        PROOF.parent.mkdir(parents=True, exist_ok=True)
        PROOF.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(PROOF.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
