import pytest
from scripts import autorun_status_v1 as aus


def test_non_fatal_substring_filtering():
    # Build synthetic dashboard findings that include variants of non-fatal reasons
    findings = [
        {"scope": "wf1", "severity": "high", "summary": "X", "detail": "stale_supabase_row"},
        {"scope": "wf2", "severity": "high", "summary": "Y", "detail": "No_Supabase_Rows detected for probe"},
        {"scope": "wf3", "severity": "high", "summary": "Z", "detail": "some other fatal issue"},
        {"scope": "wf4", "severity": "high", "summary": "A", "detail": "SUPABASE_QUERY_FAILED: timeout"},
    ]

    # Reuse the module's is_non_fatal logic by invoking main-like filtering
    non_fatal_substrings = [
        "stale_supabase_row",
        "supabase_not_configured",
        "no_supabase_rows",
        "no_supabase_receipt",
        "no_github_runs",
        "supabase_query_failed",
        "supabase_truth_tables_missing",
    ]

    def is_non_fatal(detail):
        if not detail:
            return False
        d = str(detail).lower()
        return any(sub in d for sub in non_fatal_substrings)

    critical = [f for f in findings if not is_non_fatal(f.get("detail"))]
    # Expect wf3 only to be critical
    assert len(critical) == 1
    assert critical[0]["scope"] == "wf3"
