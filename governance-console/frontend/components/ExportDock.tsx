"use client";

type ExportDockProps = {
  tleId: string;
  onTamperDemo?: () => void;
};

export function ExportDock({ tleId, onTamperDemo }: ExportDockProps) {
  const base = `/tle/${encodeURIComponent(tleId)}/export`;

  return (
    <div
      className="sticky bottom-4 z-10 rounded-xl border border-accent/30 bg-white/95 p-4 shadow-panel backdrop-blur"
      role="region"
      aria-label="Export dock"
    >
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Export dock</p>
      <div className="flex flex-wrap gap-2">
        <a className="nf-btn-primary text-sm" href={`${base}?format=pdf`} download>
          Board pack (PDF)
        </a>
        <a className="nf-btn-secondary text-sm" href={`${base}?format=zip`} download>
          Procurement pack (ZIP)
        </a>
        <a className="nf-btn-secondary text-sm" href="/trust-ledger/verify/">
          Verify integrity
        </a>
        <button type="button" className="nf-btn-secondary text-sm" onClick={() => navigator.clipboard?.writeText(tleId)}>
          Copy manifest
        </button>
        {onTamperDemo && (
          <button type="button" className="nf-btn-secondary text-sm" onClick={onTamperDemo}>
            Tamper demo (sandbox)
          </button>
        )}
      </div>
      <iframe
        title="Board PDF preview"
        src={`${base}?format=html`}
        className="mt-4 h-48 w-full rounded-lg border border-border bg-panel-solid"
      />
    </div>
  );
}
