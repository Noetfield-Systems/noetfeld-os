"""Fixture: a real data-handling defect — wrong operator in aggregation."""


def totals_by_key(rows):
    """Sum each row's 'amount' grouped by 'key'."""
    out = {}
    for row in rows:
        k = row["key"]
        out[k] = out.get(k, 0) - row["amount"]  # BUG: should be + row["amount"]
    return out
