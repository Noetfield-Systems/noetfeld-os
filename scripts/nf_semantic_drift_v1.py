#!/usr/bin/env python3
"""NF semantic drift — Voyage embeddings align chatbot knowledge to PRODUCT_TRUTH anchors.

SourceA pattern: governance_drift_engine GD-L8 · INCIDENT-036 fake-green guard.
Receipt: reports/agent-auto/events/nf-semantic-drift-v1.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

EVENTS = ROOT / "reports" / "agent-auto" / "events"
ANCHORS = ROOT / "data" / "chatbot" / "semantic_anchors_v1.json"
KNOWLEDGE = ROOT / "data" / "chatbot" / "knowledge"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _best_excerpt(*, knowledge_text: str, hint: str, ssot: str, embed_text, cosine) -> tuple[str, float]:
    if not knowledge_text.strip():
        return "", 0.0
    ssot_vec = embed_text(ssot, is_query=True)
    sections = knowledge_text.split("\n## ")
    best_text = knowledge_text[:800]
    best_score = cosine(ssot_vec, embed_text(best_text, is_query=False))
    for i, section in enumerate(sections):
        text = section if i == 0 else "## " + section
        if hint.lower() not in text.lower() and i > 0:
            continue
        score = cosine(ssot_vec, embed_text(text[:1200], is_query=False))
        if score > best_score:
            best_score = score
            best_text = text[:800]
    return best_text, best_score


def run_semantic_drift(*, min_similarity: float | None = None) -> dict:
    from nf_embedding_provider_v1 import cosine, embed_text, provider_payload, voyage_key_on_disk

    prov = provider_payload()
    doc = json.loads(ANCHORS.read_text(encoding="utf-8"))
    threshold = min_similarity if min_similarity is not None else float(doc.get("min_similarity", 0.72))

    fake_green = voyage_key_on_disk() and not prov.get("semantic")
    checks: list[dict] = []
    ok = not fake_green

    if not prov.get("semantic"):
        for anchor in doc.get("anchors") or []:
            checks.append(
                {
                    "id": anchor.get("id"),
                    "ok": True,
                    "reason": "skipped_no_voyage",
                    "similarity": None,
                    "semantic": False,
                }
            )
    else:
        for anchor in doc.get("anchors") or []:
            ssot = str(anchor.get("ssot_excerpt") or "").strip()
            kfile = str(anchor.get("knowledge_file") or "")
            hint = str(anchor.get("knowledge_hint") or "")
            knowledge = (KNOWLEDGE / kfile).read_text(encoding="utf-8", errors="replace") if kfile else ""
            if not ssot or not knowledge:
                checks.append({"id": anchor.get("id"), "ok": False, "reason": "missing_ssot_or_knowledge", "similarity": 0.0})
                ok = False
                continue
            _, similarity = _best_excerpt(
                knowledge_text=knowledge, hint=hint, ssot=ssot, embed_text=embed_text, cosine=cosine
            )
            check_ok = similarity >= threshold
            if not check_ok:
                ok = False
            checks.append(
                {
                    "id": anchor.get("id"),
                    "ok": check_ok,
                    "similarity": round(similarity, 4),
                    "threshold": threshold,
                    "knowledge_file": kfile,
                    "semantic": True,
                }
            )

    receipt = {
        "schema": "nf-semantic-drift-v1",
        "ok": ok,
        "generated_at": _now(),
        "provider": prov,
        "fake_green": fake_green,
        "min_similarity": threshold,
        "checks": checks,
        "law": "SourceA GD-L8 · voyage key in vault must not run hash_local",
    }
    EVENTS.mkdir(parents=True, exist_ok=True)
    (EVENTS / "nf-semantic-drift-v1.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="NF semantic drift — SSOT anchor alignment")
    parser.add_argument("--min-similarity", type=float, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    row = run_semantic_drift(min_similarity=args.min_similarity)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        failed = [c["id"] for c in row.get("checks", []) if not c.get("ok")]
        print(f"nf_semantic_drift: {'PASS' if row['ok'] else 'FAIL'} failed={failed}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
