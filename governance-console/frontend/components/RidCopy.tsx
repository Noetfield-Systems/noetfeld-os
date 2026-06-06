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
    <div className="nf-card flex flex-wrap items-center gap-3 px-4 py-4">
      <span className="nf-eyebrow">Record ID</span>
      <code className="min-w-0 flex-1 break-all font-mono text-sm text-accent">{rid}</code>
      <button type="button" onClick={copy} className="nf-btn-secondary shrink-0 text-xs">
        {copied ? "Copied" : "Copy RID"}
      </button>
    </div>
  );
}
