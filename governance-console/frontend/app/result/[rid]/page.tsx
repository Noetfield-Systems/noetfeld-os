"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { DecisionBadge } from "@/components/DecisionBadge";
import { RidCopy } from "@/components/RidCopy";
import { RiskMeter } from "@/components/RiskMeter";
import { AuditRecord, getAudit } from "@/lib/api";

export default function ResultPage() {
  const params = useParams();
  const rid = decodeURIComponent(String(params.rid ?? ""));
  const [record, setRecord] = useState<AuditRecord | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAudit(rid)
      .then(setRecord)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load record."));
  }, [rid]);

  return (
    <Shell>
      <div className="mb-6 flex items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold text-white">Governance decision</h2>
        <Link href="/evaluate" className="text-sm text-accent hover:underline">
          New evaluation
        </Link>
      </div>

      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-300">
          {error}
        </p>
      )}

      {!record && !error && <p className="text-sm text-muted">Loading audit record…</p>}

      {record && (
        <div className="space-y-6">
          <RidCopy rid={record.rid} />
          <div className="flex flex-wrap items-center gap-4">
            <DecisionBadge decision={record.decision} />
            <div className="min-w-[200px] flex-1">
              <RiskMeter score={record.risk_score} />
            </div>
          </div>
          <section className="rounded-xl border border-border bg-panel p-5">
            <h3 className="mb-2 text-sm font-medium uppercase text-muted">Reason</h3>
            <ul className="list-disc space-y-1 pl-5 text-sm text-gray-200">
              {record.reason.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          </section>
          <section className="rounded-xl border border-border bg-panel p-5">
            <h3 className="mb-2 text-sm font-medium uppercase text-muted">Conditions</h3>
            <ul className="list-disc space-y-1 pl-5 text-sm text-gray-200">
              {record.conditions.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          </section>
          <section className="rounded-xl border border-border bg-panel p-5 text-sm">
            <p>
              <span className="text-muted">Actor:</span> {record.actor}
            </p>
            <p className="mt-1">
              <span className="text-muted">Action:</span> {record.action}
            </p>
            <p className="mt-1">
              <span className="text-muted">Context:</span> {record.context}
            </p>
          </section>
          <Link href="/audit" className="inline-block text-sm text-accent hover:underline">
            View full audit log →
          </Link>
        </div>
      )}
    </Shell>
  );
}
