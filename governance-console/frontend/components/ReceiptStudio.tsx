"use client";

import { useState } from "react";
import { ReceiptMock } from "@/components/ReceiptMock";
import { ApprovalTimeline } from "@/components/ApprovalTimeline";
import { ExportDock } from "@/components/ExportDock";
import { TleDetail } from "@/lib/api";

type ApprovalStep = {
  approver?: { id?: string; name?: string; role?: string };
  status?: string;
  signed_at?: string;
};

type ReceiptStudioProps = {
  tle: TleDetail;
  chain: ApprovalStep[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  canAct: boolean;
  approving: string | null;
};

export function ReceiptStudio({
  tle,
  chain,
  onApprove,
  onReject,
  canAct,
  approving,
}: ReceiptStudioProps) {
  const [tab, setTab] = useState<"yaml" | "json">("yaml");
  const [tamper, setTamper] = useState(false);
  const doc = tle.document as Record<string, unknown>;
  const yaml = JSON.stringify(doc, null, 2);

  return (
    <div className="grid gap-6 xl:grid-cols-2 xl:items-start">
      <div className="space-y-4">
        <div className="flex gap-2">
          <button
            type="button"
            className={`rounded-lg px-3 py-1.5 text-sm ${tab === "yaml" ? "bg-accent/10 font-semibold text-text" : "text-muted"}`}
            onClick={() => setTab("yaml")}
          >
            YAML
          </button>
          <button
            type="button"
            className={`rounded-lg px-3 py-1.5 text-sm ${tab === "json" ? "bg-accent/10 font-semibold text-text" : "text-muted"}`}
            onClick={() => setTab("json")}
          >
            JSON
          </button>
        </div>
        <pre className="max-h-[420px] overflow-auto rounded-xl border border-border bg-[#141820] p-4 font-mono text-xs text-[#e8eaef]">
          {yaml}
        </pre>
        <div className="flex flex-wrap gap-2">
          {["Purview", "Entra", "audit"].map((chip) => (
            <span
              key={chip}
              className="rounded-full border border-border bg-panel-solid px-3 py-1 text-xs text-muted"
            >
              {chip} · connector OK
            </span>
          ))}
        </div>
        <section>
          <h3 className="mb-3 font-sans text-lg font-semibold text-text">Approval timeline</h3>
          <ApprovalTimeline
            chain={chain}
            onApprove={onApprove}
            onReject={onReject}
            canAct={canAct}
            approving={approving}
          />
        </section>
      </div>

      <div className="space-y-4">
        <ReceiptMock
          tleId={tle.tle_id}
          decision={String(doc.decision ?? "allow")}
          confidenceScore={tle.confidence_score}
          exportIntegrity={
            tamper ? "FAIL · fail closed on tamper" : "PASS · fail closed on tamper"
          }
          verified={!tamper}
          footer="Receipt Studio · board demo from one URL"
        />
        <ExportDock tleId={tle.tle_id} onTamperDemo={() => setTamper(true)} />
      </div>
    </div>
  );
}
