"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useCallback, useEffect, useState } from "react";

type PaletteItem = {
  id: string;
  label: string;
  href: string;
  hint?: string;
};

const ITEMS: PaletteItem[] = [
  { id: "dash", label: "Dashboard", href: "/cognitive-dashboard" },
  { id: "eval", label: "Evaluate", href: "/evaluate" },
  { id: "audit", label: "Audit log", href: "/audit" },
  { id: "timeline", label: "Decision timeline", href: "/audit/timeline" },
  { id: "workspace", label: "Workspace", href: "/workspace" },
  { id: "tle", label: "TLE TLE-015DCFB8B953", href: "/workspace/TLE-015DCFB8B953", hint: "Receipt Studio" },
  { id: "onboard", label: "Onboarding wizard", href: "/onboarding" },
  { id: "docs", label: "API docs", href: "/docs/api/" },
  { id: "start", label: "Start free sandbox", href: "/start/" },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const router = useRouter();

  const filtered = ITEMS.filter(
    (item) =>
      !q.trim() ||
      item.label.toLowerCase().includes(q.toLowerCase()) ||
      item.id.includes(q.toLowerCase()),
  );

  const onKey = useCallback((e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      setOpen((v) => !v);
    }
    if (e.key === "Escape") setOpen(false);
  }, []);

  useEffect(() => {
    const openPalette = () => setOpen(true);
    window.addEventListener("nf-open-palette", openPalette);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("nf-open-palette", openPalette);
      window.removeEventListener("keydown", onKey);
    };
  }, [onKey]);

  function go(href: string) {
    setOpen(false);
    setQ("");
    if (href.startsWith("/docs") || href.startsWith("/start")) {
      window.location.href = href;
    } else {
      router.push(href);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const ridMatch = q.match(/RID-[A-Z0-9-]+/i);
    if (ridMatch) {
      go(`/result/${encodeURIComponent(ridMatch[0])}`);
      return;
    }
    if (filtered[0]) go(filtered[0].href);
  }

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center bg-black/40 p-4 pt-[12vh]"
      role="dialog"
      aria-modal="true"
      aria-label="Command palette"
      onClick={() => setOpen(false)}
    >
      <div
        className="w-full max-w-lg overflow-hidden rounded-xl border border-border bg-white shadow-panel"
        onClick={(e) => e.stopPropagation()}
      >
        <form onSubmit={onSubmit} className="border-b border-border p-3">
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Jump to route, RID, or TLE id…"
            className="w-full border-0 bg-transparent text-sm text-text outline-none placeholder:text-muted-2"
            aria-label="Command search"
          />
        </form>
        <ul className="max-h-72 overflow-y-auto py-2">
          {filtered.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                className="flex w-full items-center justify-between px-4 py-2.5 text-left text-sm hover:bg-panel-solid"
                onClick={() => go(item.href)}
              >
                <span className="font-medium text-text">{item.label}</span>
                {item.hint && <span className="text-xs text-muted-2">{item.hint}</span>}
              </button>
            </li>
          ))}
        </ul>
        <p className="border-t border-border px-4 py-2 text-xs text-muted-2">
          ⌘K · try <code className="text-accent">RID-…</code> or{" "}
          <code className="text-accent">TLE-015DCFB8B953</code>
        </p>
      </div>
    </div>
  );
}

export function CommandPaletteHint() {
  return (
    <button
      type="button"
      className="hidden rounded-lg border border-border px-2.5 py-1.5 text-xs text-muted-2 hover:border-accent/30 sm:inline-flex"
      onClick={() => window.dispatchEvent(new Event("nf-open-palette"))}
    >
      ⌘K
    </button>
  );
}
