#!/usr/bin/env python3
"""Legacy port 3000 → unified dev server (8001 is served directly by the platform API)."""

from __future__ import annotations

import http.server
import os
import sys

PUBLIC = os.environ.get("NF_DEV_PUBLIC_PORT", "13080")
PUBLIC_BASE = f"http://127.0.0.1:{PUBLIC}"
LEGACY_PORT = int(os.environ.get("NF_DEV_LEGACY_NEXT_PORT", "3000"))


class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path if self.path.startswith("/") else f"/{self.path}"
        loc = PUBLIC_BASE + path
        self.send_response(302)
        self.send_header("Location", loc)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_HEAD(self) -> None:
        self.do_GET()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[redirect:3000] {fmt % args}\n")


def main() -> None:
    try:
        httpd = http.server.ThreadingHTTPServer(("0.0.0.0", LEGACY_PORT), RedirectHandler)
    except OSError as e:
        print(f"redirect :{LEGACY_PORT} skipped ({e})", flush=True)
        sys.exit(0)
    print(f"redirect :{LEGACY_PORT} -> {PUBLIC_BASE}/*", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
