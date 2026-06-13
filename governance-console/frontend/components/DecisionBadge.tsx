const styles: Record<string, string> = {
  allow: "border-emerald-200 bg-emerald-50 text-emerald-800",
  review: "border-amber-200 bg-amber-50 text-amber-900",
  deny: "border-red-200 bg-red-50 text-red-800",
};

export function DecisionBadge({ decision }: { decision: string }) {
  const key = decision.toLowerCase();
  const cls = styles[key] ?? "border-border bg-panel-solid text-muted";
  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${cls}`}
    >
      {decision}
    </span>
  );
}
