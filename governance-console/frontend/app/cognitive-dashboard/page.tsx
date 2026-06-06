"use client";

import Link from "next/link";
import { Shell } from "@/components/Shell";
import { EvaluateForm } from "@/components/EvaluateForm";
import { DevPortBanner } from "@/components/DevPortBanner";
import { apiBaseLabel } from "@/lib/health";
import { platformConsoleHref } from "@/lib/platform-console";
import { useApiHealth } from "@/lib/useApiHealth";

export default function CognitiveDashboardPage() {
  const health = useApiHealth();

  return (
    <Shell active="dashboard">
      <DevPortBanner />
      <section className="mb-8">
        <p className="text-xs uppercase tracking-widest text-accent">Cognitive governance</p>
        <h2 className="mt-1 text-2xl font-semibold text-white">Cognitive dashboard</h2>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Dev sandbox for pre-execution intent evaluation. Production pilots use{" "}
          <a
            className="text-accent underline"
            href="https://platform.noetfield.com/console"
            target="_blank"
            rel="noopener noreferrer"
          >
            platform console
          </a>
          .
        </p>
      </section>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-border bg-panel p-4">
          <p className="text-xs uppercase tracking-wide text-muted">Governance API</p>
          <p className="mt-2 font-mono text-xs text-white/90">{apiBaseLabel()}</p>
          <p className="mt-2 text-sm">
            {health === null ? (
              <span className="text-muted">Checking…</span>
            ) : health.ok ? (
              <span className="text-emerald-400">Operational · {health.detail}</span>
            ) : (
              <span className="text-red-300">Offline · {health.detail}</span>
            )}
          </p>
          {!health?.ok && health !== null && (
            <p className="mt-2 text-xs text-muted">
              Start stack:{" "}
              <code className="rounded bg-black/40 px-1">make dev-local</code>
            </p>
          )}
        </div>
        <Link
          href="/audit"
          className="rounded-xl border border-border bg-panel p-4 transition hover:border-accent/40"
        >
          <p className="text-xs uppercase tracking-wide text-muted">Compliance</p>
          <p className="mt-2 text-lg font-medium text-white">Audit log</p>
          <p className="mt-1 text-sm text-muted">Search evaluations by RID</p>
        </Link>
        <Link
          href="/trust-ledger"
          className="rounded-xl border border-border bg-panel p-4 transition hover:border-accent/40"
        >
          <p className="text-xs uppercase tracking-wide text-muted">Trust Ledger</p>
          <p className="mt-2 text-lg font-medium text-white">TLE workspace</p>
          <p className="mt-1 text-sm text-muted">Read-only list, detail, PDF export</p>
        </Link>
        <a
          href={platformConsoleHref()}
          className="rounded-xl border border-border bg-panel p-4 transition hover:border-accent/40"
        >
          <p className="text-xs uppercase tracking-wide text-muted">Platform console</p>
          <p className="mt-2 text-lg font-medium text-white">Governance console</p>
          <p className="mt-1 text-sm text-muted">Local port 8001 or 13080/console (make dev-local)</p>
        </a>
      </div>

      <section>
        <h3 className="mb-3 text-lg font-semibold text-white">Submit operational intent</h3>
        <EvaluateForm />
      </section>
    </Shell>
  );
}
