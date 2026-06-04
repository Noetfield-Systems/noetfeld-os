"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { listTles, TrustLedgerEntry } from "@/lib/trustLedger";

export default function TrustLedgerListPage() {
  const [status, setStatus] = useState("");
  const [rows, setRows] = useState<TrustLedgerEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load(filter?: string) {
    setLoading(true);
    setError(null);
    try {
      const res = await listTles(filter || undefined);
      setRows(res.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load Trust Ledger entries.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <Shell active="trust-ledger">
      <section className="mb-6">
        <h2 className="text-2xl font-semibold text-white">Trust Ledger</h2>
        <p className="mt-2 text-sm text-muted">
          Read-only view of Trust Ledger Entries (TLE v1). Copilot audit trail for procurement sign-off.
        </p>
      </section>

      <form
        className="mb-6 flex flex-wrap gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          load(status);
        }}
      >
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-lg border border-border bg-panel px-3 py-2 text-sm"
        >
          <option value="">All statuses</option>
          <option value="PendingApproval">Pending approval</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
          <option value="Draft">Draft</option>
        </select>
        <button
          type="submit"
          className="rounded-lg border border-border px-4 py-2 text-sm hover:bg-white/5"
        >
          Filter
        </button>
        <button
          type="button"
          onClick={() => {
            setStatus("");
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
        <p className="text-sm text-muted">
          No TLEs yet. Run <code className="text-accent">./scripts/tle-smoke.sh --api</code> or create via API.
        </p>
      )}

      {!loading && rows.length > 0 && (
        <ul className="space-y-3">
          {rows.map((row) => (
            <li
              key={row.tle_id}
              className="rounded-lg border border-border bg-panel/60 px-4 py-3 hover:border-accent/40"
            >
              <Link href={`/trust-ledger/${encodeURIComponent(row.tle_id)}`} className="block">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-mono text-sm text-accent">{row.tle_id}</span>
                  <span className="rounded bg-white/10 px-2 py-0.5 text-xs uppercase">{row.status}</span>
                </div>
                <p className="mt-2 text-sm text-muted line-clamp-2">{row.decision ?? "—"}</p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Shell>
  );
}
