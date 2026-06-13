"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { EvaluateForm } from "@/components/EvaluateForm";
import { StatCard } from "@/components/StatCard";
import { ReceiptMock } from "@/components/ReceiptMock";
import { PageHero } from "@/components/PageHero";
import { AgentCommandDeck } from "@/components/AgentCommandDeck";
import { apiBaseLabel } from "@/lib/health";
import { useApiHealth } from "@/lib/useApiHealth";

export default function CognitiveDashboardPage() {
  const health = useApiHealth();
  const [sandboxLabel, setSandboxLabel] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const inSandbox =
      params.get("sandbox") === "1" ||
      window.localStorage.getItem("nf_sandbox_v1") !== null;
    if (!inSandbox) return;
    try {
      const raw = window.localStorage.getItem("nf_sandbox_v1");
      if (!raw) {
        setSandboxLabel("Sandbox mode · mock M365 · 50 evaluate calls");
        return;
      }
      const session = JSON.parse(raw) as {
        tenant_id?: string;
        evaluates_used?: number;
        evaluates_limit?: number;
      };
      setSandboxLabel(
        `Sandbox · tenant ${session.tenant_id ?? "active"} · ${session.evaluates_used ?? 0}/${session.evaluates_limit ?? 50} evaluates`,
      );
    } catch {
      setSandboxLabel("Sandbox mode · mock M365");
    }
  }, []);

  return (
    <Shell active="dashboard">
      {sandboxLabel && (
        <p
          className="mb-6 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
          role="status"
        >
          {sandboxLabel} ·{" "}
          <Link href="/pricing/" className="font-semibold text-accent hover:underline">
            Upgrade to production
          </Link>
        </p>
      )}

      <AgentCommandDeck />

      <div className="mb-10 grid gap-8 lg:grid-cols-[minmax(0,1.1fr)_minmax(280px,360px)] lg:items-start">
        <PageHero
          className="mb-0"
          eyebrow="Pre-execution governance"
          title="Cognitive dashboard"
          lead="Govern Copilot execution before production scope opens — submit operational intent, review confidence score, and continue to Trust Ledger workspace for signed TLE export."
        />
        <ReceiptMock
          footer={
            <>
              Live evaluate path ·{" "}
              <Link href="/trust-ledger/sample-report/" className="text-accent hover:underline">
                TLE samples
              </Link>
            </>
          }
        />
      </div>

      <section
        className="mb-8 rounded-xl border border-accent/25 bg-accent/5 p-6"
        aria-label="5-minute demo"
      >
        <p className="nf-eyebrow">5-minute demo</p>
        <h3 className="mt-1 text-lg font-semibold text-text">
          Evaluate → confidence score → Trust Ledger
        </h3>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Submit intent below, open the result RID, and show the{" "}
          <strong className="text-text">confidence score</strong> badge. Continue in{" "}
          <Link href="/workspace" className="text-accent hover:underline">
            Workspace
          </Link>{" "}
          for board PDF and procurement ZIP export.
        </p>
        <p className="mt-3 text-sm">
          <Link href="/copilot/demo/" className="text-accent hover:underline">
            Locked demo script →
          </Link>
        </p>
      </section>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Governance API" title={apiBaseLabel()}>
          <p className="text-sm">
            {health === null ? (
              <span className="text-muted">Checking…</span>
            ) : health.ok ? (
              <span className="text-ok">Operational · {health.detail}</span>
            ) : (
              <span className="text-red-600">Offline · {health.detail}</span>
            )}
          </p>
        </StatCard>
        <StatCard
          label="Drift contract"
          title="Governance drift v0"
          description="Evaluate → diff → TLE draft against last signed baseline (metadata-only)."
        />
        <Link
          href="/audit"
          className="rounded-xl border border-border bg-panel p-4 transition hover:border-accent/40"
        >
          <p className="text-xs uppercase tracking-wide text-muted">Compliance</p>
          <p className="mt-2 text-lg font-medium text-text">Audit log</p>
          <p className="mt-1 text-sm text-muted">Search evaluations by RID</p>
        </Link>
        <Link
          href="/workspace"
          className="rounded-xl border border-border bg-panel p-4 transition hover:border-accent/40"
        >
          <p className="text-xs uppercase tracking-wide text-muted">Trust Ledger</p>
          <p className="mt-2 text-lg font-medium text-text">TLE workspace</p>
          <p className="mt-1 text-sm text-muted">Create, sign, export PDF and ZIP</p>
        </Link>
      </div>

      <section className="nf-card p-6">
        <h3 className="mb-4 text-lg font-semibold text-text">Submit operational intent</h3>
        <EvaluateForm />
      </section>
    </Shell>
  );
}
