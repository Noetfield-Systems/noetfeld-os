"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { DecisionBadge } from "@/components/DecisionBadge";
import { LoadingBlock } from "@/components/LoadingBlock";
import { RidCopy } from "@/components/RidCopy";
import { RiskMeter } from "@/components/RiskMeter";
import { AuditRecord, getAudit } from "@/lib/api";

export default function ResultPage() {
  const params = useParams();
  const rid = decodeURIComponent(String(params?.rid ?? ""));
  const [record, setRecord] = useState<AuditRecord | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!rid) return;
    getAudit(rid)
      .then(setRecord)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load record."));
  }, [rid]);

  return (
    <Shell>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="nf-eyebrow">Decision record</p>
          <h2 className="mt-1 font-serif text-3xl font-semibold text-white">Governance decision</h2>
        </div>
        <Link href="/evaluate" className="nf-btn-secondary text-sm">
          New evaluation
        </Link>
      </div>

      {error && (
        <p
          className="mb-6 rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200"
          role="alert"
        >
          {error}
        </p>
      )}

      {!record && !error && <LoadingBlock label="Loading audit record…" />}

      {record && (
        <div className="space-y-6">
          <RidCopy rid={record.rid} />
          <div className="nf-card flex flex-col gap-6 p-6 sm:flex-row sm:items-center">
            <DecisionBadge decision={record.decision} />
            <div className="min-w-0 flex-1">
              <RiskMeter score={record.risk_score} />
            </div>
          </div>
          <section className="nf-card p-6">
            <h3 className="nf-eyebrow mb-3">Reason</h3>
            <ul className="list-disc space-y-2 pl-5 text-sm leading-relaxed text-white/90">
              {record.reason.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          </section>
          <section className="nf-card p-6">
            <h3 className="nf-eyebrow mb-3">Conditions</h3>
            <ul className="list-disc space-y-2 pl-5 text-sm leading-relaxed text-white/90">
              {record.conditions.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          </section>
          <section className="nf-card space-y-2 p-6 text-sm">
            <p>
              <span className="text-muted-2">Actor</span>
              <span className="mt-0.5 block text-white">{record.actor}</span>
            </p>
            <p>
              <span className="text-muted-2">Action</span>
              <span className="mt-0.5 block text-white">{record.action}</span>
            </p>
            <p>
              <span className="text-muted-2">Context</span>
              <span className="mt-0.5 block text-white/90">{record.context}</span>
            </p>
          </section>
          <Link href="/audit" className="inline-flex text-sm font-medium text-accent hover:underline">
            View full audit log →
          </Link>
        </div>
      )}
    </Shell>
  );
}
