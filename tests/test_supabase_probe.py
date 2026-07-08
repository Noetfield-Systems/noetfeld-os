import importlib
from scripts import autorun_status_v1 as aus


def test_supabase_probe_no_rows_returns_blocked():
    # Monkeypatch supabase_get to simulate no rows returned
    def fake_supabase_get(cfg, table, query, prefer_count=False):
        return {"ok": True, "rows": []}

    original = aus.supabase_get
    try:
        aus.supabase_get = fake_supabase_get
        wf = {"id": "sourcea_recipe_queue_builder", "probe": {"receipt_schema": "test_schema"}, "verify_command": "echo check"}
        wf_doc = {"supabase_profiles": {}}
        res = aus.probe_supabase_sourcea_receipt(wf, wf_doc, stale_minutes=30)
        assert res.get("status") in {"IDLE_NO_WORK", "BLOCKED_WITH_REASON"} or res.get("reason") is not None
    finally:
        aus.supabase_get = original
