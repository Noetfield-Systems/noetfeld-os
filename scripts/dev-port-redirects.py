#!/usr/bin/env python3
"""Legacy port redirects so old bookmarks (8001, 3000) reach the unified dev server."""

from __future__ import annotations

import http.server
import os
import sys
import threading

PUBLIC = os.environ.get("NF_DEV_PUBLIC_PORT", "13080")
PUBLIC_BASE = f"http://127.0.0.1:{PUBLIC}"

REDIRECTS: dict[int, str] = {
    8001: f"{PUBLIC_BASE}/console",
    3000: f"{PUBLIC_BASE}/cognitive-dashboard",
}


class RedirectHandler(http.server.BaseHTTPRequestHandler):
    target: str = PUBLIC_BASE

    def do_GET(self) -> None:
        loc = self.target + self.path
        self.send_response(302)
        self.send_header("Location", loc)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_HEAD(self) -> None:
        self.do_GET()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[redirect:{self.server.server_port}] {fmt % args}\n")


def serve(port: int, target: str) -> None:
    handler = type("H", (RedirectHandler,), {"target": target})
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"redirect :{port} -> {target}", flush=True)
    httpd.serve_forever()


def main() -> None:
    threads = []
    for port, target in REDIRECTS.items():
        t = threading.Thread(target=serve, args=(port, target), daemon=True)
        t.start()
        threads.append(t)
    print(f"Legacy redirects active (public site: {PUBLIC_BASE}/)", flush=True)
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
