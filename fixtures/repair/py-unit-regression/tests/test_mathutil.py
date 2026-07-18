import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mathutil import sum_to  # noqa: E402


def test_sum_to_5():
    assert sum_to(5) == 15  # 1+2+3+4+5


def test_sum_to_10():
    assert sum_to(10) == 55


def test_sum_to_1():
    assert sum_to(1) == 1
