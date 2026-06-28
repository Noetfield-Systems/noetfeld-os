#!/usr/bin/env python3
"""Summarize public chatbot telemetry JSONL for operator review."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_events(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    events = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                events.append({"status": "invalid_json", "message": line[:120]})
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description="Report public chatbot telemetry.")
    parser.add_argument(
        "--path",
        default="var/public_chat_telemetry.jsonl",
        help="Telemetry JSONL path. Defaults to var/public_chat_telemetry.jsonl.",
    )
    parser.add_argument("--recent", type=int, default=10, help="Recent turns to include.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    path = Path(args.path).expanduser()
    if not path.is_absolute():
        path = root / path
    events = load_events(path)

    status_counts = Counter(str(e.get("status", "unknown")) for e in events)
    provider_counts = Counter(str(e.get("provider") or "none") for e in events)
    citation_counts = Counter(c for e in events for c in e.get("citations", []))
    error_counts = Counter(str(e.get("error_type") or "none") for e in events if e.get("status") != "ok")
    intent_counts = Counter(str((e.get("intent") or {}).get("primary_intent") or "unknown") for e in events)
    alignment_counts = Counter(
        "aligned" if (e.get("alignment") or {}).get("aligned") is True else "misaligned"
        for e in events
        if e.get("status") == "ok"
    )

    report = {
        "path": str(path),
        "events": len(events),
        "status_counts": dict(status_counts),
        "provider_counts": dict(provider_counts),
        "intent_counts": dict(intent_counts),
        "alignment_counts": dict(alignment_counts),
        "error_counts": dict(error_counts),
        "top_citations": dict(citation_counts.most_common(10)),
        "recent": [
            {
                "created_at": e.get("created_at"),
                "status": e.get("status"),
                "provider": e.get("provider"),
                "intent": (e.get("intent") or {}).get("primary_intent"),
                "aligned": (e.get("alignment") or {}).get("aligned"),
                "turn_index": (e.get("conversation_state") or {}).get("turn_index"),
                "message": e.get("message"),
                "reply_preview": (e.get("reply") or "")[:240],
                "error_type": e.get("error_type"),
            }
            for e in events[-args.recent :]
        ],
    }
    print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
