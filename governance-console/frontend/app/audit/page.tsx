"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { DecisionBadge } from "@/components/DecisionBadge";
import { LoadingBlock } from "@/components/LoadingBlock";
import { PageHero } from "@/components/PageHero";
import { AuditRecord, listAudit } from "@/lib/api";

export default function AuditPage() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<AuditRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load(search?: string) {
    setLoading(true);
    setError(null);
    try {
      setRows(await listAudit(search));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load audit log.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <Shell active="audit">
      <PageHero
        eyebrow="Compliance"
        title="Audit log"
        lead="Every evaluation is stored with a unique RID for immutable compliance traceability."
      />

      <form
        className="nf-card mb-8 flex flex-wrap gap-3 p-4"
        onSubmit={(e) => {
          e.preventDefault();
          load(q);
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by RID, actor, or action…"
          className="nf-input min-w-[240px] flex-1"
          aria-label="Search audit log"
        />
        <button type="submit" className="nf-btn-primary">
          Search
        </button>
        <button
          type="button"
          onClick={() => {
            setQ("");
            load();
          }}
          className="nf-btn-secondary"
        >
          Reset
        </button>
      </form>

      {error && (
        <p
          className="mb-4 rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200"
          role="alert"
        >
          {error}
        </p>
      )}

      {loading && <LoadingBlock label="Loading audit records…" />}

      {!loading && rows.length === 0 && (
        <div className="nf-card p-8 text-center">
          <p className="text-muted">No evaluations yet.</p>
          <Link href="/evaluate" className="mt-3 inline-block text-sm text-accent hover:underline">
            Submit your first intent →
          </Link>
        </div>
      )}

      <ul className="space-y-3">
        {rows.map((row) => (
          <li key={row.rid}>
            <Link href={`/result/${encodeURIComponent(row.rid)}`} className="nf-card-hover block p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <code className="font-mono text-sm text-accent">{row.rid}</code>
                <DecisionBadge decision={row.decision} />
              </div>
              <p className="mt-3 text-sm text-white/90">
                {row.actor}
                <span className="text-muted-2"> · </span>
                {row.action}
              </p>
              <p className="mt-1 text-xs text-muted-2">
                Risk {row.risk_score} · {new Date(row.timestamp).toLocaleString()}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </Shell>
  );
}
