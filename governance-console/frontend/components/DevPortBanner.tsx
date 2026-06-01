"use client";

import { useEffect, useState } from "react";

const DEFAULT_WEB_PORT = process.env.NEXT_PUBLIC_WEB_PORT ?? "13000";
const DEFAULT_PLATFORM_PORT = process.env.NEXT_PUBLIC_PLATFORM_CONSOLE_PORT ?? "18001";
const apiEnv = process.env.NEXT_PUBLIC_API_URL ?? `http://127.0.0.1:18002`;

export function DevPortBanner() {
  const [web, setWeb] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setWeb(`${window.location.origin}/cognitive-dashboard`);
    }
  }, []);

  if (process.env.NODE_ENV === "production") {
    return null;
  }

  const port =
    DEFAULT_WEB_PORT || (typeof window !== "undefined" ? window.location.port : "13000");
  const pageUrl = web ?? `http://localhost:${port}/cognitive-dashboard`;
  const consoleUrl = `http://localhost:${DEFAULT_PLATFORM_PORT}/console`;

  return (
    <div
      className="mb-6 rounded-lg border border-accent/30 bg-accent/10 px-4 py-3 font-mono text-xs text-white/90"
      role="status"
      aria-live="polite"
    >
      <p className="text-[10px] uppercase tracking-widest text-accent">Local dev</p>
      <p className="mt-1">
        <span className="text-muted">Dashboard: </span>
        <a className="text-accent underline" href={pageUrl}>
          {pageUrl}
        </a>
      </p>
      <p className="mt-1">
        <span className="text-muted">Console: </span>
        <a className="text-accent underline" href={consoleUrl}>
          {consoleUrl}
        </a>
      </p>
      <p className="mt-1">
        <span className="text-muted">Gov API: </span>
        {apiEnv}
      </p>
    </div>
  );
}
