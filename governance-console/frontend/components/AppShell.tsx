"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";
import { Footer } from "@/components/Footer";
import { CommandPalette, CommandPaletteHint } from "@/components/CommandPalette";
import { ProofRail } from "@/components/ProofRail";
import { UsageMeter } from "@/components/UsageMeter";

export type ShellActive =
  | "dashboard"
  | "evaluate"
  | "audit"
  | "trust-ledger"
  | "workspace"
  | "onboarding";

type AppShellProps = {
  children: ReactNode;
  active?: ShellActive;
  title?: string;
  proofRid?: string;
};

const NAV: { href: string; label: string; key: ShellActive }[] = [
  { href: "/cognitive-dashboard", label: "Dashboard", key: "dashboard" },
  { href: "/evaluate", label: "Evaluate", key: "evaluate" },
  { href: "/workspace", label: "Workspace", key: "workspace" },
  { href: "/audit", label: "Audit", key: "audit" },
  { href: "/audit/timeline", label: "Timeline", key: "audit" },
  { href: "/trust-ledger", label: "Trust Ledger", key: "trust-ledger" },
];

const MOBILE_TABS = [
  { href: "/cognitive-dashboard", label: "Dashboard", key: "dashboard" as const },
  { href: "/evaluate", label: "Evaluate", key: "evaluate" as const },
  { href: "/workspace", label: "Workspace", key: "workspace" as const },
  { href: "/audit", label: "More", key: "audit" as const },
];

function navClass(active: boolean): string {
  return `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition ${
    active
      ? "bg-accent/10 text-text before:block before:h-4 before:w-0.5 before:rounded-full before:bg-accent"
      : "text-muted hover:bg-panel-solid hover:text-text"
  }`;
}

export function AppShell({ children, active, title, proofRid }: AppShellProps) {
  const pathname = usePathname();
  const [railOpen, setRailOpen] = useState(true);
  const [proofMode, setProofMode] = useState(false);
  const [tenant, setTenant] = useState("sandbox");

  useEffect(() => {
    try {
      const raw = localStorage.getItem("nf_sandbox_v1");
      if (raw) {
        const s = JSON.parse(raw) as { tenant_id?: string };
        if (s.tenant_id) setTenant(s.tenant_id);
      }
    } catch {
      /* ignore */
    }
  }, []);

  return (
    <div className={`min-h-screen flex flex-col bg-surface ${proofMode ? "nf-proof-mode" : ""}`}>
      <CommandPalette />
      <header className="sticky top-0 z-50 border-b border-border bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-3 px-4 py-2.5 sm:px-6">
          <Link href="/cognitive-dashboard" className="flex shrink-0 items-center gap-2 hover:opacity-90">
            <div>
              <p className="text-base font-bold tracking-tight text-text">Noetfield</p>
              <p className="text-xs text-muted-2">Governance Console</p>
            </div>
          </Link>
          <div className="hidden flex-wrap items-center gap-2 md:flex">
            <code className="rounded bg-panel-solid px-2 py-1 text-xs text-muted">{tenant}</code>
            <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-900">
              Sandbox
            </span>
            <UsageMeter />
            <Link
              href="/pricing/"
              className="rounded-lg border border-accent/30 px-3 py-1.5 text-xs font-semibold text-accent hover:bg-accent/5"
            >
              Upgrade
            </Link>
            <CommandPaletteHint />
            <button
              type="button"
              className="rounded-lg border border-border px-2.5 py-1.5 text-xs text-muted-2"
              onClick={() => setProofMode((v) => !v)}
              aria-pressed={proofMode}
            >
              Proof mode
            </button>
          </div>
          <Link href="/start/" className="nf-btn-secondary hidden text-sm sm:inline-flex">
            Start free
          </Link>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-[1600px] flex-1">
        <nav
          className="hidden w-52 shrink-0 border-r border-border bg-white/80 p-4 lg:block"
          aria-label="Primary"
        >
          <ul className="space-y-1">
            {NAV.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={navClass(active === item.key || pathname === item.href)}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
          <Link href="/onboarding" className="mt-6 block text-xs text-accent hover:underline">
            Trial OS onboarding →
          </Link>
        </nav>

        <div className="flex min-w-0 flex-1 flex-col">
          {title && (
            <div className="border-b border-border px-4 py-4 sm:px-6">
              <h1 className="font-serif text-2xl font-semibold text-text">{title}</h1>
            </div>
          )}
          <main className="flex-1 px-4 py-8 sm:px-6 lg:pr-[380px]">{children}</main>
        </div>

        <ProofRail open={railOpen} onToggle={() => setRailOpen((v) => !v)} rid={proofRid} />
      </div>

      <nav
        className="fixed bottom-0 left-0 right-0 z-50 flex border-t border-border bg-white/95 backdrop-blur lg:hidden"
        aria-label="Mobile navigation"
      >
        {MOBILE_TABS.map((tab) => (
          <Link
            key={tab.href}
            href={tab.href}
            className={`flex flex-1 flex-col items-center py-2.5 text-xs ${
              active === tab.key ? "font-semibold text-accent" : "text-muted"
            }`}
          >
            {tab.label}
          </Link>
        ))}
      </nav>

      <div className="hidden lg:block">
        <Footer />
      </div>
    </div>
  );
}
