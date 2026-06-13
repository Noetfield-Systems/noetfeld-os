import type { ReactNode } from "react";

type ReceiptMockProps = {
  tleId?: string;
  decision?: string;
  confidenceScore?: string | number;
  rid?: string;
  evidenceIndex?: string;
  exportIntegrity?: string;
  verified?: boolean;
  footer?: ReactNode;
  className?: string;
};

export function ReceiptMock({
  tleId = "TLE-015DCFB8B953",
  decision = "allow",
  confidenceScore = "0.82",
  rid = "RID-2026-0602",
  evidenceIndex = "purview · entra · audit",
  exportIntegrity = "PASS · fail closed on tamper",
  verified = true,
  footer,
  className = "",
}: ReceiptMockProps) {
  const score =
    typeof confidenceScore === "number"
      ? confidenceScore.toFixed(2)
      : String(confidenceScore);

  const rows: [string, string, boolean][] = [
    ["tle_id", tleId, false],
    ["decision", decision, false],
    ["confidence_score", score, false],
    ["rid", rid, false],
    ["evidence_index", evidenceIndex, false],
    ["export_integrity", exportIntegrity, true],
  ];

  return (
    <div
      className={`overflow-hidden rounded-[14px] border border-[#2a3140] bg-[#141820] shadow-[0_24px_64px_rgba(15,17,23,0.14)] ${className}`}
      aria-label="Trust Ledger Entry receipt"
    >
      <div className="flex items-center gap-3 border-b border-white/10 bg-[#1c2230] px-3.5 py-2.5">
        <span className="inline-flex gap-1" aria-hidden="true">
          <i className="block h-2 w-2 rounded-full bg-[#ff5f57]" />
          <i className="block h-2 w-2 rounded-full bg-[#febc2e]" />
          <i className="block h-2 w-2 rounded-full bg-[#28c840]" />
        </span>
        <span className="flex-1 font-mono text-xs text-white/55">tle-receipt.yaml</span>
        {verified && (
          <span className="rounded-full border border-ok/45 bg-ok/10 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-[#3dd68c]">
            Verified
          </span>
        )}
      </div>
      <dl className="space-y-2 px-5 pb-2 pt-4 text-sm">
        {rows.map(([label, value, isOk]) => (
          <div key={label} className="grid grid-cols-[7.5rem_1fr] gap-2">
            <dt className="text-white/40">{label}</dt>
            <dd
              className={`font-mono text-xs ${isOk ? "text-[#3dd68c]" : "text-[#e8eaef]"}`}
            >
              {value}
            </dd>
          </div>
        ))}
      </dl>
      {footer && (
        <p className="border-t border-white/10 px-5 py-3 text-xs text-white/45">{footer}</p>
      )}
    </div>
  );
}
