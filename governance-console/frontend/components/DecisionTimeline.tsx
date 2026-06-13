"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { AuditRecord } from "@/lib/api";
import { ReceiptMock } from "@/components/ReceiptMock";

type TimelineNode = {
  id: string;
  rid: string;
  type: "Evaluate" | "Decision" | "Connector ingest" | "TLE draft" | "Approval" | "Export";
  label: string;
  timestamp: string;
};

type DecisionTimelineProps = {
  records: AuditRecord[];
};

function inferNodes(records: AuditRecord[]): TimelineNode[] {
  const nodes: TimelineNode[] = [];
  for (const row of records) {
    nodes.push({
      id: `${row.rid}-eval`,
      rid: row.rid,
      type: "Evaluate",
      label: `${row.actor} · ${row.action}`,
      timestamp: row.timestamp,
    });
    nodes.push({
      id: `${row.rid}-dec`,
      rid: row.rid,
      type: "Decision",
      label: `${row.decision} · risk ${row.risk_score}`,
      timestamp: row.timestamp,
    });
    nodes.push({
      id: `${row.rid}-conn`,
      rid: row.rid,
      type: "Connector ingest",
      label: "M365 metadata ingested (Purview · Entra · audit)",
      timestamp: row.timestamp,
    });
    nodes.push({
      id: `${row.rid}-tle`,
      rid: row.rid,
      type: "TLE draft",
      label: "Trust Ledger Entry draft linked",
      timestamp: row.timestamp,
    });
    nodes.push({
      id: `${row.rid}-exp`,
      rid: row.rid,
      type: "Export",
      label: "Board PDF · procurement ZIP orientation",
      timestamp: row.timestamp,
    });
  }
  return nodes;
}

export function DecisionTimeline({ records }: DecisionTimelineProps) {
  const [filterRid, setFilterRid] = useState("");
  const [env, setEnv] = useState<"all" | "sandbox">("all");
  const [density, setDensity] = useState<"comfortable" | "compact">("comfortable");
  const [selected, setSelected] = useState<TimelineNode | null>(null);

  const nodes = useMemo(() => inferNodes(records), [records]);
  const filtered = nodes.filter((n) => {
    if (filterRid && !n.rid.toLowerCase().includes(filterRid.toLowerCase())) return false;
    if (env === "sandbox" && !n.rid.toLowerCase().includes("sandbox")) return false;
    return true;
  });

  const gap = density === "compact" ? "gap-2" : "gap-4";
  const pad = density === "compact" ? "p-2" : "p-4";

  if (!records.length) {
    return (
      <div className="nf-card p-8 text-center">
        <p className="text-muted">No decision threads yet.</p>
        <Link href="/evaluate" className="mt-3 inline-block text-sm text-accent hover:underline">
          Submit your first evaluate →
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
      <div>
        <div className="nf-card mb-4 flex flex-wrap gap-3 p-4">
          <input
            value={filterRid}
            onChange={(e) => setFilterRid(e.target.value)}
            placeholder="Filter by RID…"
            className="nf-input min-w-[200px] flex-1"
            aria-label="Filter timeline by RID"
          />
          <select
            value={env}
            onChange={(e) => setEnv(e.target.value as "all" | "sandbox")}
            className="nf-input w-auto"
            aria-label="Environment filter"
          >
            <option value="all">All environments</option>
            <option value="sandbox">Sandbox only</option>
          </select>
          <div className="flex gap-2">
            <button
              type="button"
              className={`nf-btn-secondary text-sm ${density === "comfortable" ? "border-accent/40" : ""}`}
              onClick={() => setDensity("comfortable")}
            >
              Comfortable
            </button>
            <button
              type="button"
              className={`nf-btn-secondary text-sm ${density === "compact" ? "border-accent/40" : ""}`}
              onClick={() => setDensity("compact")}
            >
              Compact
            </button>
          </div>
        </div>

        <ul className={`flex flex-col ${gap}`}>
          {filtered.map((node) => (
            <li key={node.id}>
              <button
                type="button"
                className={`nf-card-hover w-full text-left ${pad}`}
                onClick={() => setSelected(node)}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="rounded bg-accent/10 px-2 py-0.5 text-xs font-semibold text-accent">
                    {node.type}
                  </span>
                  <code className="font-mono text-xs text-muted-2">{node.rid}</code>
                </div>
                <p className="mt-2 text-sm text-text">{node.label}</p>
                <p className="mt-1 text-xs text-muted-2">{new Date(node.timestamp).toLocaleString()}</p>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <aside className="nf-card p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">Node detail</p>
        {selected ? (
          <>
            <p className="mt-2 font-mono text-sm text-accent">{selected.rid}</p>
            <p className="mt-1 text-sm text-muted">
              {selected.type} · {selected.label}
            </p>
            <div className="mt-4">
              <ReceiptMock
                rid={selected.rid}
                footer={
                  <Link href={`/result/${encodeURIComponent(selected.rid)}`} className="text-accent hover:underline">
                    Open full record →
                  </Link>
                }
              />
            </div>
          </>
        ) : (
          <p className="mt-2 text-sm text-muted-2">Select a node to preview receipt snippet.</p>
        )}
      </aside>
    </div>
  );
}
