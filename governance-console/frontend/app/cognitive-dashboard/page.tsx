"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { EvaluateForm } from "@/components/EvaluateForm";
import { DevPortBanner } from "@/components/DevPortBanner";
import { PageHero } from "@/components/PageHero";
import { StatCard } from "@/components/StatCard";
import { ApiHealth, apiBaseLabel, fetchApiHealth } from "@/lib/health";
import { platformConsoleHref } from "@/lib/platform-console";

function HealthStatus({ health }: { health: ApiHealth | null }) {
  if (health === null) {
    return <span className="text-sm text-muted">Checking…</span>;
  }
  if (health.ok) {
    return (
      <span className="inline-flex items-center gap-2 text-sm text-ok">
        <span className="h-2 w-2 animate-pulse rounded-full bg-ok" aria-hidden />
        Operational · {health.detail}
      </span>
    );
  }
  return <span className="text-sm text-red-300">Offline · {health.detail}</span>;
}

export default function CognitiveDashboardPage() {
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [consoleHref, setConsoleHref] = useState("/console");

  useEffect(() => {
    setConsoleHref(platformConsoleHref());
    fetchApiHealth().then(setHealth);
    const id = setInterval(() => fetchApiHealth().then(setHealth), 15000);
    return () => clearInterval(id);
  }, []);

  return (
    <Shell active="dashboard">
      <DevPortBanner />
      <PageHero
        eyebrow="Cognitive governance"
        title="Cognitive dashboard"
        lead="Dev sandbox for pre-execution intent evaluation. Production pilots use the platform console for regulated workflows."
      />

      <div className="mb-10 grid gap-4 sm:grid-cols-3">
        <StatCard label="Governance API" title="Policy engine" description={apiBaseLabel()}>
          <HealthStatus health={health} />
          {!health?.ok && health !== null && (
            <p className="mt-3 text-xs text-muted-2">
              Run <code className="rounded bg-black/40 px-1">make dev-local</code> from the Noetfield
              repo root.
            </p>
          )}
        </StatCard>
        <StatCard
          label="Compliance"
          title="Audit log"
          description="Search evaluations by RID"
          href="/audit"
        />
        <StatCard
          label="Platform"
          title="Governance console"
          description="Institutional console · same-origin /console on :13080"
          href={consoleHref}
          external={consoleHref.startsWith("http")}
        />
      </div>

      <section>
        <h3 className="mb-4 font-serif text-xl font-semibold text-white">Submit operational intent</h3>
        <EvaluateForm />
      </section>
    </Shell>
  );
}
