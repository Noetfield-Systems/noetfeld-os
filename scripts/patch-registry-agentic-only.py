#!/usr/bin/env python3
"""Set agentic_only on customer-outreach NF-PLAN rows (R-011)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "ops" / "plans" / "registry.json"

AGENTIC_PROMPT_PREFIX = (
    "As NF-CLOUD-AGENT (Noetfield only), agentic layer only — maintain pipeline copy on disk "
    "(not send/call): "
)


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    n = 0
    for pl in data.get("plans", []):
        if pl.get("pattern") != "customer-outreach":
            continue
        pl["agentic_only"] = True
        title = pl.get("title", "outreach task")
        pl["prompt"] = (
            f"{AGENTIC_PROMPT_PREFIX}{title}. "
            "Read R-011 + AGENTIC_COMMERCIAL_HANDOFF. Hub executes send; NF-CLOUD wires www/docs only."
        )
        n += 1
    REGISTRY.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"patch-registry-agentic-only: updated {n} customer-outreach plans")

    gtm_path = ROOT / "docs" / "ops" / "plans" / "PROMPT_PACK_LOCKED" / "GTM_PRIORITY_100.md"
    if gtm_path.exists():
        lines = gtm_path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        for line in lines:
            if "Design-partner outreach" in line and "AGENTIC ONLY" not in line and line.startswith("- **NF-PLAN"):
                line = line.replace("- **", "- **AGENTIC ONLY — skip NF-CLOUD** · **", 1)
            out.append(line)
        gtm_path.write_text("\n".join(out) + "\n", encoding="utf-8")
        print("patch-registry-agentic-only: updated GTM_PRIORITY_100 outreach markers")


if __name__ == "__main__":
    main()
