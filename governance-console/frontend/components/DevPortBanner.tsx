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

  return (
    <div
      className="mb-6 rounded-lg border border-accent/30 bg-accent/10 px-4 py-3 font-mono text-xs text-white/90"
      role="status"
      aria-live="polite"
    >
      <p className="text-[10px] uppercase tracking-widest text-accent">Local dev</p>
      <p className="mt-1">
        <span className="text-muted">Page: </span>
        {web ?? `http://localhost:${portEnv ?? "3000"}/cognitive-dashboard`}
      </p>
      <p className="mt-1">
        <span className="text-muted">Port: </span>
        {portEnv ?? (typeof window !== "undefined" ? window.location.port || "3000" : "3000")}
      </p>
      <p className="mt-1">
        <span className="text-muted">API: </span>
        {apiEnv}
      </p>
    </div>
  );
}
