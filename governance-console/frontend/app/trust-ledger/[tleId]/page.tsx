"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { exportTlePdfUrl, getTle, TrustLedgerEntry } from "@/lib/trustLedger";

export default function TrustLedgerDetailPage() {
  const params = useParams();
  const tleId = typeof params.tleId === "string" ? params.tleId : "";
  const [entry, setEntry] = useState<TrustLedgerEntry | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tleId) return;
    setLoading(true);
    setError(null);
    getTle(tleId)
      .then(setEntry)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load TLE."))
      .finally(() => setLoading(false));
  }, [tleId]);

  return (
    <Shell active="trust-ledger">
      <p className="mb-4 text-sm">
        <Link href="/trust-ledger" className="text-accent hover:underline">
          ← Trust Ledger
        </Link>
      </p>

      {loading && <p className="text-sm text-muted">Loading…</p>}
      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-300">{error}</p>
      )}

      {entry && (
        <section className="space-y-6">
          <header>
            <h2 className="font-mono text-xl text-white">{entry.tle_id}</h2>
            <p className="mt-1 text-sm text-muted">
              Status: <strong className="text-white">{entry.status}</strong>
              {entry.date ? ` · ${entry.date}` : ""}
            </p>
          </header>

          <div className="rounded-lg border border-border bg-panel/60 p-4">
            <h3 className="text-sm font-semibold text-white">Decision</h3>
            <p className="mt-2 text-sm text-muted">{entry.decision ?? "—"}</p>
          </div>

          {entry.evidence && entry.evidence.length > 0 && (
            <div className="rounded-lg border border-border bg-panel/60 p-4">
              <h3 className="text-sm font-semibold text-white">Evidence</h3>
              <ul className="mt-2 list-inside list-disc text-sm text-muted">
                {entry.evidence.map((ev, i) => (
                  <li key={i}>
                    {(ev as { evidence_id?: string }).evidence_id ?? "ev"} —{" "}
                    {(ev as { title?: string }).title ?? ""}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {entry.approval_chain && entry.approval_chain.length > 0 && (
            <div className="rounded-lg border border-border bg-panel/60 p-4">
              <h3 className="text-sm font-semibold text-white">Approval chain</h3>
              <ul className="mt-2 space-y-2 text-sm text-muted">
                {entry.approval_chain.map((step, i) => (
                  <li key={i}>
                    {(step as { approver?: { id?: string } }).approver?.id ?? "approver"} —{" "}
                    {(step as { status?: string }).status}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {entry.status === "Approved" && (
            <a
              href={exportTlePdfUrl(tleId)}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block rounded-lg border border-accent px-4 py-2 text-sm text-accent hover:bg-accent/10"
            >
              Download board pack (PDF)
            </a>
          )}
        </section>
      )}
    </Shell>
  );
}
