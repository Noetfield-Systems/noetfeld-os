"use client";

import { useEffect, useState } from "react";

const DEFAULT_PLATFORM_PORT = process.env.NEXT_PUBLIC_PLATFORM_CONSOLE_PORT ?? "8001";

export function DevPortBanner() {
  const [urls, setUrls] = useState<{
    dashboard: string;
    console: string;
    unified: string;
  } | null>(null);
  const [open, setOpen] = useState(true);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const port = window.location.port || "13080";
    const origin = window.location.origin;
    setUrls({
      dashboard: `${origin}/cognitive-dashboard`,
      console:
        port === "13080"
          ? `${origin}/console`
          : `http://localhost:${DEFAULT_PLATFORM_PORT}/console`,
      unified: port === "13080" ? origin : `http://localhost:13080`,
    });
  }, []);

  if (process.env.NODE_ENV === "production") {
    return null;
  }

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="mb-6 text-xs text-accent underline"
      >
        Show local dev URLs
      </button>
    );
  }

  return (
    <div
      className="nf-card mb-8 border-accent/25 bg-accent/5 px-4 py-3 font-mono text-xs text-white/90"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-start justify-between gap-2">
        <p className="nf-eyebrow">Local dev</p>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="text-muted-2 hover:text-white"
          aria-label="Dismiss"
        >
          ×
        </button>
      </div>
      {urls ? (
        <ul className="mt-2 space-y-1">
          <li>
            <span className="text-muted-2">Unified: </span>
            <a className="text-accent underline" href={urls.unified}>
              {urls.unified}
            </a>
          </li>
          <li>
            <span className="text-muted-2">Dashboard: </span>
            <a className="text-accent underline" href={urls.dashboard}>
              {urls.dashboard}
            </a>
          </li>
          <li>
            <span className="text-muted-2">Console: </span>
            <a className="text-accent underline" href={urls.console}>
              {urls.console}
            </a>
          </li>
        </ul>
      ) : (
        <p className="mt-2 text-muted">Loading URLs…</p>
      )}
    </div>
  );
}
