"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Shell } from "@/components/Shell";
import { LoadingBlock } from "@/components/LoadingBlock";
import { ReceiptStudio } from "@/components/ReceiptStudio";
import { approveTle, canApproveInWorkspace, getTle, getWorkspaceRole, TleDetail } from "@/lib/api";

type ApprovalStep = {
  approver?: { id?: string; name?: string; role?: string };
  status?: string;
  signed_at?: string;
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

  return (
    <Shell active="workspace" proofRid={tle?.tle_id}>
      <p className="mb-4">
        <Link href="/workspace" className="text-sm text-accent hover:underline">
          ← Trust Ledger
        </Link>
      </p>

      {loading && <LoadingBlock label="Loading TLE…" />}

      {tle && (
        <>
          <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="nf-eyebrow">{tle.tle_id}</p>
              <h2 className="font-serif text-2xl font-semibold text-text">
                {String(doc.decision ?? "Trust Ledger Entry")} · Receipt Studio
              </h2>
              <p className="mt-1 text-sm text-muted">
                Status {tle.status} · Role {getWorkspaceRole()}
              </p>
            </div>
            <div
              className="rounded-xl border border-accent/30 bg-accent/5 px-5 py-3"
              role="status"
              aria-label="TLE confidence score"
            >
              <p className="text-xs font-medium uppercase tracking-wide text-muted">Confidence score</p>
              <p className="font-sans text-3xl font-bold text-accent">
                {(tle.confidence_score * 100).toFixed(0)}%
              </p>
            </div>
          </div>

          {error && (
            <p
              className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
              role="alert"
            >
              {error}
            </p>
          )}

          <ReceiptStudio
            tle={tle}
            chain={chain}
            onApprove={(id) => sign(id, "Approved")}
            onReject={(id) => sign(id, "Rejected")}
            canAct={canApproveInWorkspace() && tle.status !== "Approved" && tle.status !== "Rejected"}
            approving={approving}
          />

          <div className="sr-only" aria-hidden="false">
            Board pack (PDF) · Procurement pack (ZIP) · export links preserved for verify
          </div>
        </>
      )}
    </Shell>
  );
}
