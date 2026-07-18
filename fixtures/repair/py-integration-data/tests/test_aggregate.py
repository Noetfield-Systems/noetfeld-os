import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aggregate import totals_by_key  # noqa: E402


def test_totals():
    rows = [
        {"key": "a", "amount": 10},
        {"key": "b", "amount": 5},
        {"key": "a", "amount": 3},
    ]
    assert totals_by_key(rows) == {"a": 13, "b": 5}


def test_single():
    assert totals_by_key([{"key": "x", "amount": 7}]) == {"x": 7}
