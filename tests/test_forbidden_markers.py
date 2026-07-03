from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_forbidden_slug_only_lives_in_marker_file() -> None:
    legacy_slug = "kazemnezhadsina144" + "-dot"
    marker_path = ROOT / "noetfield-org/FORBIDDEN_MARKERS.txt"
    active_paths = [
        ROOT / ".github/copilot-instructions.md",
        ROOT / ".noetfield/agent_manifest.yml",
        ROOT / "noetfield-org/REPO_REGISTRY.md",
        ROOT / "noetfield-org/LOOP_STATE.json",
    ]

    assert marker_path.read_text(encoding="utf-8").strip() == legacy_slug
    for path in active_paths:
        assert legacy_slug not in path.read_text(encoding="utf-8")
