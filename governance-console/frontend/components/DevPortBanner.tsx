"use client";

import { useEffect, useState } from "react";

export function DevPortBanner() {
  const [web, setWeb] = useState<string | null>(null);
  const apiEnv = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  const portEnv = process.env.NEXT_PUBLIC_WEB_PORT;

  useEffect(() => {
    if (typeof window !== "undefined") {
      setWeb(`${window.location.origin}/cognitive-dashboard`);
    }
  }, []);

  if (process.env.NODE_ENV === "production") {
    return null;
  }

  const port =
    portEnv ?? (typeof window !== "undefined" ? window.location.port || "3000" : "3000");
  const pageUrl =
    web ?? `http://localhost:${port}/cognitive-dashboard`;

  return (
    <div
      className="mb-6 rounded-lg border border-accent/30 bg-accent/10 px-4 py-3 font-mono text-xs text-white/90"
      role="status"
      aria-live="polite"
    >
      <p className="text-[10px] uppercase tracking-widest text-accent">Local dev</p>
      <p className="mt-1">
        <span className="text-muted">Page: </span>
        <a className="text-accent underline" href={pageUrl}>
          {pageUrl}
        </a>
      </p>
      <p className="mt-1">
        <span className="text-muted">Port: </span>
        {port}
      </p>
      <p className="mt-1">
        <span className="text-muted">API: </span>
        {apiEnv}
      </p>
      <p className="mt-2 text-[11px] leading-relaxed text-muted">
        Cursor Cloud: open the <strong className="text-white/80">Ports</strong> tab and forward port{" "}
        {port} — your Mac browser only sees localhost after forwarding.
      </p>
      <p className="mt-1 text-[11px] text-muted">
        Platform console:{" "}
        <a className="text-accent underline" href="http://127.0.0.1:8001/console">
          http://127.0.0.1:8001/console
        </a>{" "}
        (forward port 8001)
      </p>
    </div>
  );
}
