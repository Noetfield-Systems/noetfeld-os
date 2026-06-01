"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { EvaluateForm } from "@/components/EvaluateForm";
import { ApiHealth, apiBaseLabel, fetchApiHealth } from "@/lib/health";

export default function CognitiveDashboardPage() {
  const [health, setHealth] = useState<ApiHealth | null>(null);

  useEffect(() => {
    fetchApiHealth().then(setHealth);
    const id = setInterval(() => {
      fetchApiHealth().then(setHealth);
    }, 15000);
    return () => clearInterval(id);
  }, []);

  return (
    <Shell active="dashboard">
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

      <div className="mb-8 grid gap-4 sm:grid-cols-3">
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
              Start API:{" "}
              <code className="rounded bg-black/40 px-1">
                cd governance-console/backend && uvicorn main:app --reload --port 8000
              </code>
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
        <a
          href="http://127.0.0.1:8001/console"
          className="rounded-xl border border-border bg-panel p-4 transition hover:border-accent/40"
        >
          <p className="text-xs uppercase tracking-wide text-muted">Production path</p>
          <p className="mt-2 text-lg font-medium text-white">Platform console</p>
          <p className="mt-1 text-sm text-muted">Local:8001 when api-v3 is running</p>
        </a>
      </div>

      <section>
        <h3 className="mb-3 text-lg font-semibold text-white">Submit operational intent</h3>
        <EvaluateForm />
      </section>
    </Shell>
  );
}
