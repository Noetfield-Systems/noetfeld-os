"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Shell } from "@/components/Shell";
import { LoadingBlock } from "@/components/LoadingBlock";
import { PageHero } from "@/components/PageHero";
import { approveTle, canApproveInWorkspace, getTle, getWorkspaceRole, TleDetail } from "@/lib/api";
import { wwwHref } from "@/lib/www-links";

type ApprovalStep = {
  approver?: { id?: string; name?: string; role?: string };
  status?: string;
  signed_at?: string;
  conditions?: string;
};

export default function TleViewerPage() {
  const params = useParams();
  const tleId = String(params.tle_id ?? "");
  const [tle, setTle] = useState<TleDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setTle(await getTle(tleId));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load TLE.");
    } finally {
      setLoading(false);
    }
  }

  async function sign(approverId: string, decision: string) {
    setApproving(approverId);
    setError(null);
    try {
      setTle(await approveTle(tleId, { approver_id: approverId, decision }));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Approval failed.");
    } finally {
      setApproving(null);
    }
  }

  useEffect(() => {
    if (tleId === "connectors") {
      window.location.replace("/workspace/connectors");
      return;
    }
    if (tleId) load();
  }, [tleId]);

  const doc = (tle?.document ?? {}) as Record<string, unknown>;
  const chain = (doc.approval_chain as ApprovalStep[]) ?? [];
  const evidence = (doc.evidence as Array<{ title?: string; source?: string }>) ?? [];

  return (
    <Shell active="workspace">
      <p className="mb-4">
        <Link href="/workspace" className="text-sm text-accent hover:underline">
          ← Trust Ledger
        </Link>
      </p>

      {loading && <LoadingBlock label="Loading TLE…" />}

      {tle && (
        <>
          <PageHero
            eyebrow={tle.tle_id}
            title={String(doc.decision ?? "Trust Ledger Entry")}
            lead={`Status ${tle.status} · ${String(doc.date ?? "")} · Role ${getWorkspaceRole()}`}
          />

          <div
            className="nf-card mb-8 flex flex-wrap items-center justify-between gap-4 border border-accent/30 bg-accent/5 p-6"
            role="status"
            aria-label="TLE confidence score"
          >
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-muted">Confidence score</p>
              <p className="font-serif text-4xl font-semibold text-accent">
                {(tle.confidence_score * 100).toFixed(0)}%
              </p>
              <p className="mt-1 text-sm text-muted-2">Board/legal visibility — shown on PDF cover</p>
            </div>
            <div className="flex flex-wrap gap-2 text-sm">
              <Link href={wwwHref("/copilot/demo/")} className="nf-btn-secondary">
                Demo script
              </Link>
              <a href="/audit/export" className="nf-btn-secondary" download>
                Audit export
              </a>
            </div>
          </div>

          {error && (
            <p
              className="mb-4 rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200"
              role="alert"
            >
              {error}
            </p>
          )}

          <div className="mb-8 grid gap-4 sm:grid-cols-2">
            <div className="nf-card p-5">
              <h3 className="text-sm font-medium text-muted">Audit digest</h3>
              <p className="mt-2 break-all font-mono text-xs text-white/80">
                {tle.audit_digest ?? "Pending final approval"}
              </p>
            </div>
            <div className="nf-card p-5">
              <h3 className="text-sm font-medium text-muted">Export</h3>
              <div className="mt-3 flex flex-wrap gap-2">
                <a className="nf-btn-secondary text-sm" href={`/tle/${encodeURIComponent(tleId)}/export`}>
                  Board pack (JSON)
                </a>
                <a
                  className="nf-btn-secondary text-sm"
                  href={`/tle/${encodeURIComponent(tleId)}/export?format=html`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Board pack (HTML)
                </a>
                <a
                  className="nf-btn-secondary text-sm"
                  href={`/tle/${encodeURIComponent(tleId)}/export?format=pdf`}
                  download
                >
                  Board pack (PDF)
                </a>
                <a
                  className="nf-btn-secondary text-sm"
                  href={`/tle/${encodeURIComponent(tleId)}/export?format=zip`}
                  download
                >
                  Procurement pack (ZIP)
                </a>
              </div>
            </div>
          </div>

          <section className="mb-8">
            <h3 className="mb-3 font-serif text-xl text-white">Evidence ({evidence.length})</h3>
            <ul className="space-y-2">
              {evidence.map((e, i) => (
                <li key={i} className="nf-card p-4 text-sm">
                  <span className="text-accent">{e.source}</span>
                  <span className="text-muted-2"> · </span>
                  {e.title}
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h3 className="mb-3 font-serif text-xl text-white">Approval chain</h3>
            <ul className="space-y-3">
              {chain.map((step, i) => {
                const approver = step.approver ?? {};
                const pending = step.status === "Pending";
                return (
                  <li key={i} className="nf-card flex flex-wrap items-center justify-between gap-4 p-4">
                    <div>
                      <p className="font-medium text-white">{approver.name}</p>
                      <p className="text-xs text-muted-2">
                        {approver.role} · {approver.id} · {step.status}
                        {step.signed_at ? ` · ${new Date(step.signed_at).toLocaleString()}` : ""}
                      </p>
                    </div>
                    {pending && tle.status !== "Approved" && tle.status !== "Rejected" && canApproveInWorkspace() && (
                      <div className="flex gap-2">
                        <button
                          type="button"
                          className="nf-btn-primary text-sm"
                          disabled={approving === approver.id}
                          onClick={() => sign(String(approver.id), "Approved")}
                        >
                          Approve
                        </button>
                        <button
                          type="button"
                          className="nf-btn-secondary text-sm"
                          disabled={approving === approver.id}
                          onClick={() => sign(String(approver.id), "Rejected")}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          </section>
        </>
      )}
    </Shell>
  );
}
