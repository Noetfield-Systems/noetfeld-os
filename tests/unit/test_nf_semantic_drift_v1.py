"""Semantic drift + hybrid score helpers."""

from __future__ import annotations

import math
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from nf_embedding_provider_v1 import cosine, embed_text, hybrid_score, provider_payload  # noqa: E402


def test_hybrid_score_bounded() -> None:
    score = hybrid_score(token_score=0.5, query="gel runtime", chunk_text="GEL governance execution layer")
    assert 0.0 <= score <= 1.5


def test_semantic_drift_skips_without_voyage(monkeypatch) -> None:
    monkeypatch.chdir(Path(__file__).resolve().parents[2])
    from scripts.nf_semantic_drift_v1 import run_semantic_drift

    row = run_semantic_drift()
    assert row["schema"] == "nf-semantic-drift-v1"
    if not row["provider"].get("semantic"):
        assert all(c.get("reason") == "skipped_no_voyage" for c in row["checks"])
