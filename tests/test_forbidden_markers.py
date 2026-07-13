from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_law_drift_check_v1 import load_forbidden_markers, run_check  # noqa: E402


def test_marker_file_lists_expected_tokens() -> None:
    markers = load_forbidden_markers()
    assert "kazemnezhadsina144-dot" in markers
    assert "vercel" in markers


def test_forbidden_tokens_only_in_marker_file() -> None:
    row = run_check()
    assert row["registry_ok"] is True
    assert row["violation_count"] == 0, row.get("violations")
    assert row["ok"] is True


def test_drift_scan_detects_leaked_token(tmp_path: Path, monkeypatch) -> None:
    import noos_law_drift_check_v1 as mod

    marker_file = tmp_path / "noetfield-org/FORBIDDEN_MARKERS.txt"
    marker_file.parent.mkdir(parents=True)
    marker_file.write_text("bad-token\n", encoding="utf-8")
    doc_root = tmp_path / "docs"
    doc_root.mkdir()
    leaked = doc_root / "note.md"
    leaked.write_text("Do not use bad-token in public copy.\n", encoding="utf-8")
    registry = tmp_path / "noetfield-org/system-laws/SYSTEM_LAW_REGISTRY_v1.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text('{"schema":"noos-system-law-v1","laws":[]}\n', encoding="utf-8")

    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "MARKER_PATH", marker_file)
    monkeypatch.setattr(mod, "REGISTRY_PATH", registry)
    monkeypatch.setattr(mod, "SCAN_ROOTS", (doc_root,))
    monkeypatch.setattr(mod, "SCAN_FILES", ())

    row = mod.run_check(markers=["bad-token"])
    assert row["violation_count"] == 1
    assert row["violations"][0]["path"] == "docs/note.md"
    assert row["ok"] is False
