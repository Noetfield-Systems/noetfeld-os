#!/usr/bin/env python3
"""Mirror noetfield-1000 library index to ~/.cursor/plans/noetfield-os/README.md."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = Path.home() / ".cursor/plans/noetfield-os/README.md"
REG = ROOT / "os/plan-library/noetfield-1000/REGISTRY.json"


def main() -> None:
    import json

    data = json.loads(REG.read_text(encoding="utf-8"))
    plans = data.get("plans", [])
    done = sum(1 for p in plans if p.get("status") == "done")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    t0 = [p for p in plans if p.get("tier") == "T0" and p.get("status") == "backlog"]
    next_id = t0[0]["id"] if t0 else "none"

    body = f"""# Noetfield 1000 — global lane mirror

**Updated:** {ts}
**Library:** `{ROOT / 'os/plan-library/noetfield-1000'}`
**Done:** {done} / {len(plans)}
**Next T0 pick:** {next_id}

```bash
cd {ROOT}
make pick-no-asf-plan
```

Trigger: **PLAN WITH NO ASF**
"""
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(body, encoding="utf-8")
    print(f"OK mirror → {DEST}")


if __name__ == "__main__":
    main()
