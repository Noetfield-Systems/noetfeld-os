"""Tests for Phase-3 ecosystem observe witnesses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_sourcea_spine_witness_v1 as spine  # noqa: E402
import noos_trustfield_observe_witness_v1 as tf  # noqa: E402


def test_trustfield_witness_schema(monkeypatch):
    monkeypatch.setattr(
        tf,
        "run_observe",
        lambda script, **_: {
            "overall_status": "yellow",
            "summary": {"green": 9, "yellow": 2, "red": 0},
            "closure_token": "NOOS_TF_11_LAYERS: yellow",
            "registry_read_ok": True,
        }
        if "registry" in script
        else {
            "overall_status": "green",
            "summary": {"red": 0, "deadman_status": "green", "deadman_watched_red": []},
            "closure_token": "NOOS_TF_LOOP_REGISTRY_OBSERVE: green",
            "registry_read_ok": True,
        },
    )
    row = tf.witness(write_receipt=False)
    assert row["schema"] == "noos-trustfield-observe-witness-v1"
    assert row["checks"]["ICL-D06"]["ok"] is True
    assert row["closure_token"].startswith("NOOS_TF_OBSERVE_WITNESS:")


def test_sourcea_spine_witness_readonly(monkeypatch):
    wf_doc = json.loads((ROOT / "data/autorun-workflows-v1.json").read_text(encoding="utf-8"))

    def fake_probe(wf_doc_in, wf_id, stale):
        return {
            "id": wf_id,
            "status": "IDLE_NO_WORK",
            "data_freshness": "FRESH",
            "age_minutes": 5,
            "evidence": {"observed_at": "2026-07-08T00:00:00Z"},
        }

    monkeypatch.setattr(spine, "load_wf_doc", lambda: wf_doc)
    monkeypatch.setattr(spine, "probe_workflow", fake_probe)
    row = spine.witness(write_receipt=False)
    assert row["schema"] == "noos-sourcea-spine-witness-v1"
    assert row["mutates_spine"] is False
    assert row["sourcea_cloud_queue"]["fresh"] is True
