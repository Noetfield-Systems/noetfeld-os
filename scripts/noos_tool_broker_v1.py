#!/usr/bin/env python3
"""NOOS Tool Broker (minimal M1 implementation).
Provides a ToolBroker class to execute allowed tool commands only via a controlled interface,
record receipts into .noos-runtime/tool-broker/receipts, and enforce a simple cost cap.

This is intentionally small and non-invasive for Phase 1: it does not replace existing
call sites yet — it provides a canonical place for Layer-2 and P1 agents to call tools via
an allow-listed wrapper in subsequent steps (M2..M5).
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIR = ROOT / ".noos-runtime" / "tool-broker" / "receipts"
RECEIPT_DIR.mkdir(parents=True, exist_ok=True)

# Minimal allowlist: commands that may be executed through the broker (no shell strings).
DEFAULT_ALLOWLIST = [
    "git",
    "python3",
    "echo",
]


class ToolBroker:
    def __init__(self, allowlist: Optional[List[str]] = None, cost_cap_usd: float = 1.0):
        self.allowlist = allowlist or DEFAULT_ALLOWLIST
        # simple cost cap: total_usd for the call (no metering implemented yet)
        self.cost_cap_usd = float(os.environ.get("NOOS_BROKER_COST_CAP_USD", cost_cap_usd))

    def _allowed(self, cmd: List[str]) -> bool:
        if not cmd:
            return False
        # Only allow direct commands whose executable is in allowlist and no shell metacharacters
        exe = cmd[0]
        if exe not in self.allowlist:
            return False
        joined = " ".join(cmd)
        forbidden = [";", "|", "&&", "$", "`", ">", "<"]
        if any(ch in joined for ch in forbidden):
            return False
        return True

    def execute(self, cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
        """Execute a command if allowed. Returns a receipt dict and writes it to receipts dir.
        The broker never runs via shell=True and captures stdout/stderr. Exit codes are surfaced.
        """
        start = time.time()
        receipt: Dict[str, Any] = {
            "cmd": cmd,
            "allowed": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "duration_seconds": None,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cost_estimate_usd": 0.0,
        }
        if not self._allowed(cmd):
            receipt["reason"] = "not_allowed"
            self._write_receipt(receipt)
            return receipt

        # Placeholder cost estimation: small fixed cost per call; future versions will meter
        receipt["allowed"] = True
        receipt["cost_estimate_usd"] = 0.01
        if receipt["cost_estimate_usd"] > self.cost_cap_usd:
            receipt["reason"] = "cost_cap_exceeded"
            self._write_receipt(receipt)
            return receipt

        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout, check=False)
            receipt["exit_code"] = proc.returncode
            receipt["stdout"] = (proc.stdout or "").strip()[:2000]
            receipt["stderr"] = (proc.stderr or "").strip()[:2000]
        except subprocess.TimeoutExpired:
            receipt["exit_code"] = -1
            receipt["stderr"] = "timeout"
        except Exception as exc:
            receipt["exit_code"] = -1
            receipt["stderr"] = str(exc)
        finally:
            receipt["duration_seconds"] = round(time.time() - start, 3)
            self._write_receipt(receipt)
        return receipt

    def _write_receipt(self, receipt: Dict[str, Any]) -> None:
        # Write a unique file per timestamp+pid
        ts = int(time.time() * 1000)
        fname = RECEIPT_DIR / f"receipt-{ts}-{os.getpid()}.json"
        try:
            fname.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        except OSError:
            pass


# Simple CLI for manual testing (not used by automated agents in this change)
if __name__ == "__main__":
    import sys

    broker = ToolBroker()
    if len(sys.argv) <= 1:
        print("usage: noos_tool_broker_v1.py <cmd> [args...]", flush=True)
        raise SystemExit(2)
    cmd = sys.argv[1:]
    r = broker.execute(cmd)
    print(json.dumps(r, indent=2))
    raise SystemExit(0)
