"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { LoadingBlock } from "@/components/LoadingBlock";
import { PageHero } from "@/components/PageHero";
import { draftTle, listTles, TleSummary } from "@/lib/api";

function statusClass(status: string): string {
  if (status === "Approved") return "text-emerald-300";
  if (status === "Rejected") return "text-red-300";
  if (status === "Conditional") return "text-amber-300";
  return "text-muted";
}

export default function WorkspacePage() {
  const [q, setQ] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [rows, setRows] = useState<TleSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [drafting, setDrafting] = useState(false);

  async function load(search?: string, status?: string) {
    setLoading(true);
    setError(null);
    try {
      setRows(
        await listTles({
          q: search,
          status: status || undefined,
        }),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load Trust Ledger.");
    } finally {
      setLoading(false);
    }
  }

  async function createDraft() {
    setDrafting(true);
    setError(null);
    try {
      const tle = await draftTle({
        evidence_ids: ["EV-PURVIEW-001", "EV-ENTRA-001", "EV-AUDIT-001"],
      });
      window.location.href = `/workspace/${encodeURIComponent(tle.tle_id)}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create TLE draft.");
      setDrafting(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <Shell active="workspace">
      <PageHero
        eyebrow="Trust Ledger v1"
        title="Trust Ledger Workspace"
        lead="Procurement-grade authorization records for Copilot adoption — evidence, confidence score, and approval chain."
      />
      <p className="mb-6 flex flex-wrap gap-x-4 gap-y-1 text-sm">
        <Link href="/workspace/connectors" className="text-accent hover:underline">
          M365 connectors (dev OAuth)
        </Link>
        <Link href="/copilot/demo/" className="text-accent hover:underline">
          5-minute demo script
        </Link>
        <a href="/audit/export" className="text-accent hover:underline" download>
          Audit export (JSON)
        </a>
        <Link href="/copilot/procurement/" className="text-accent hover:underline">
          Procurement buyer pack
        </Link>
      </p>

      <form
        className="nf-card mb-8 flex flex-wrap gap-3 p-4"
        onSubmit={(e) => {
          e.preventDefault();
          load(q, statusFilter);
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search TLE id, RID, decision…"
          className="nf-input min-w-[200px] flex-1"
          aria-label="Search Trust Ledger"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="nf-input"
          aria-label="Filter by status"
        >
          <option value="">All statuses</option>
          <option value="Draft">Draft</option>
          <option value="Approved">Approved</option>
          <option value="Conditional">Conditional</option>
          <option value="Rejected">Rejected</option>
        </select>
        <button type="submit" className="nf-btn-primary">
          Search
        </button>
        <button
          type="button"
          className="nf-btn-secondary"
          onClick={() => {
            setQ("");
            setStatusFilter("");
            load();
          }}
        >
          Reset
        </button>
      </form>

      <div className="mb-8 flex flex-wrap gap-3">
        <button type="button" className="nf-btn-primary" disabled={drafting} onClick={createDraft}>
          {drafting ? "Creating draft…" : "Create TLE draft from pilot evidence"}
        </button>
        <Link href="/trust-ledger/sample-report/" className="nf-btn-secondary">
          TLE v1 samples (YAML)
        </Link>
      </div>

      {error && (
        <p
          className="mb-4 rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200"
          role="alert"
        >
          {error}
        </p>
      )}

      {loading && <LoadingBlock label="Loading Trust Ledger entries…" />}

      {!loading && rows.length === 0 && (
        <div className="nf-card p-8 text-center">
          <p className="text-muted">No Trust Ledger entries yet.</p>
          <p className="mt-2 text-sm text-muted-2">
            Create a draft from seeded pilot evidence or link from a governance evaluation.
          </p>
        </div>
      )}

      <ul className="space-y-3">
        {rows.map((row) => (
          <li key={row.tle_id}>
            <Link href={`/workspace/${encodeURIComponent(row.tle_id)}`} className="nf-card-hover block p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <code className="font-mono text-sm text-accent">{row.tle_id}</code>
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className="rounded-full border border-accent/40 bg-accent/10 px-3 py-1 text-sm font-semibold text-accent"
                    aria-label={`Confidence ${(row.confidence_score * 100).toFixed(0)} percent`}
                  >
                    {(row.confidence_score * 100).toFixed(0)}% confidence
                  </span>
                  <span className={`text-sm font-medium ${statusClass(row.status)}`}>{row.status}</span>
                </div>
              </div>
              <p className="mt-3 text-sm text-white/90">{row.decision}</p>
              <p className="mt-1 text-xs text-muted-2">
                {row.date}
                {row.source_rid ? ` · RID ${row.source_rid}` : ""}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </Shell>
  );
}
