"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { DecisionBadge } from "@/components/DecisionBadge";
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
    <Shell>
      <section className="mb-6">
        <h2 className="text-2xl font-semibold text-white">Audit log</h2>
        <p className="mt-2 text-sm text-muted">Every evaluation is stored with a unique RID for compliance traceability.</p>
      </section>

      <form
        className="mb-6 flex flex-wrap gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          load(q);
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by RID…"
          className="min-w-[240px] flex-1 rounded-lg border border-border bg-panel px-3 py-2 text-sm"
        />
        <button
          type="submit"
          className="rounded-lg border border-border px-4 py-2 text-sm hover:bg-white/5"
        >
          Search
        </button>
        <button
          type="button"
          onClick={() => {
            setQ("");
            load();
          }}
          className="rounded-lg border border-border px-4 py-2 text-sm hover:bg-white/5"
        >
          Reset
        </button>
      </form>

      {error && (
        <p className="mb-4 rounded-lg border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-300">
          {error}
        </p>
      )}

      {loading && <p className="text-sm text-muted">Loading…</p>}

      {!loading && rows.length === 0 && (
        <p className="text-sm text-muted">No evaluations yet. Submit intent from the Evaluate screen.</p>
      )}

      <ul className="space-y-3">
        {rows.map((row) => (
          <li key={row.rid}>
            <Link
              href={`/result/${encodeURIComponent(row.rid)}`}
              className="block rounded-xl border border-border bg-panel p-4 transition hover:border-accent/40"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <code className="font-mono text-sm text-accent">{row.rid}</code>
                <DecisionBadge decision={row.decision} />
              </div>
              <p className="mt-2 text-sm text-gray-300">
                {row.actor} · {row.action}
              </p>
              <p className="mt-1 text-xs text-muted">
                Risk {row.risk_score} · {new Date(row.timestamp).toLocaleString()}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </Shell>
  );
}
