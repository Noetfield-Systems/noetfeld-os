"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { PageHero } from "@/components/PageHero";
import { DecisionTimeline } from "@/components/DecisionTimeline";
import { LoadingBlock } from "@/components/LoadingBlock";
import { AuditRecord, listAudit } from "@/lib/api";

export default function AuditTimelinePage() {
  const [rows, setRows] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listAudit()
      .then(setRows)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load timeline."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Shell active="audit" title="Decision timeline">
      <PageHero
        className="mb-8"
        eyebrow="Governance graph"
        title="Decision timeline"
        lead="RID-threaded evaluate → decision → TLE → export — institutional density for GRC power users."
      />

      {error && (
        <p className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
          {error}
        </p>
      )}

      {loading ? <LoadingBlock label="Loading decision threads…" /> : <DecisionTimeline records={rows} />}
    </Shell>
  );
}
