"use client";

import { useState } from "react";

export function RidCopy({ rid }: { rid: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(rid);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-lg border border-border bg-panel px-4 py-3">
      <span className="text-xs uppercase text-muted">RID</span>
      <code className="flex-1 font-mono text-sm text-accent">{rid}</code>
      <button
        type="button"
        onClick={copy}
        className="rounded-md border border-border px-3 py-1 text-xs hover:bg-white/5"
      >
        {copied ? "Copied" : "Copy"}
      </button>
    </div>
  );
}
