export function LoadingBlock({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="nf-card flex items-center gap-3 p-6" role="status" aria-live="polite">
      <span className="nf-spinner border-white/20 border-t-accent" aria-hidden />
      <span className="text-sm text-muted">{label}</span>
    </div>
  );
}
