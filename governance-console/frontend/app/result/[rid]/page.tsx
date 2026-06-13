"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { DecisionBadge } from "@/components/DecisionBadge";
import { ReceiptMock } from "@/components/ReceiptMock";
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

  const confidencePct = record
    ? Math.max(0, Math.min(100, 100 - record.risk_score))
    : 0;

  return (
    <Shell active="evaluate">
      <div className="mb-6 flex items-center justify-between gap-4">
        <h1 className="font-serif text-2xl font-semibold text-text">Governance decision</h1>
        <Link href="/evaluate" className="text-sm text-accent hover:underline">
          New evaluation
        </Link>
      </div>

      {error && (
        <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </p>
      )}

      {!record && !error && <p className="text-sm text-muted">Loading audit record…</p>}

      {record && (
        <div className="grid gap-6 lg:grid-cols-[1fr_minmax(280px,360px)]">
          <div className="space-y-6">
            <RidCopy rid={record.rid} />
            <div
              className="nf-card flex flex-wrap items-center justify-between gap-4 border border-accent/25 bg-accent/5 p-6"
              role="status"
              aria-label="Governance confidence score"
            >
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted">
                  Confidence score
                </p>
                <p className="text-4xl font-bold text-accent">{confidencePct.toFixed(0)}%</p>
                <p className="mt-1 text-sm text-muted-2">
                  Derived from governance risk — shown in board demos
                </p>
              </div>
              <DecisionBadge decision={record.decision} />
            </div>
            <RiskMeter score={record.risk_score} />
            <section className="nf-card p-5">
              <h3 className="mb-2 text-sm font-medium uppercase text-muted">Reason</h3>
              <ul className="list-disc space-y-1 pl-5 text-sm text-muted">
                {record.reason.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            </section>
            <section className="nf-card p-5">
              <h3 className="mb-2 text-sm font-medium uppercase text-muted">Conditions</h3>
              <ul className="list-disc space-y-1 pl-5 text-sm text-muted">
                {record.conditions.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </section>
            <section className="nf-card p-5 text-sm">
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
          <ReceiptMock
            rid={record.rid}
            decision={record.decision}
            confidenceScore={(confidencePct / 100).toFixed(2)}
            exportIntegrity="PASS · fail closed on tamper"
          />
        </div>
      )}
    </Shell>
  );
}
