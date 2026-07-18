"""Fixture: a real off-by-one regression (upper bound excludes n)."""


def sum_to(n):
    """Sum of integers 1..n inclusive."""
    total = 0
    for i in range(1, n):  # BUG: excludes n; should be range(1, n + 1)
        total += i
    return total
