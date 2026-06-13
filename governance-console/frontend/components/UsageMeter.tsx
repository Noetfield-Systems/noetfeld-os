"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "nf_sandbox_v1";

type SandboxSession = {
  tenant_id?: string;
  evaluates_used?: number;
  evaluates_limit?: number;
  expires_at?: string;
  mode?: string;
};

function daysRemaining(expiresAt: string): number {
  const ms = new Date(expiresAt).getTime() - Date.now();
  return Math.max(0, Math.ceil(ms / 86400000));
}

export function UsageMeter({ className = "" }: { className?: string }) {
  const [label, setLabel] = useState<string | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        setLabel("Sandbox · 0/50 evaluates · 14d trial");
        return;
      }
      const session = JSON.parse(raw) as SandboxSession;
      const used = session.evaluates_used ?? 0;
      const limit = session.evaluates_limit ?? 50;
      const days = session.expires_at ? daysRemaining(session.expires_at) : 14;
      setLabel(
        `${used}/${limit} evaluates · ${days} days left · ${session.mode ?? "sandbox"}`,
      );
    } catch {
      setLabel(null);
    }
  }, []);

  if (!label) return null;

  return (
    <span
      className={`inline-flex items-center rounded-full border border-accent/25 bg-accent/5 px-3 py-1 text-xs font-semibold text-text ${className}`}
      data-nf-usage-chip
      role="status"
    >
      {label}
    </span>
  );
}
