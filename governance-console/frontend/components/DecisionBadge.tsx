const styles: Record<string, string> = {
  allow: "border-emerald-700/60 bg-emerald-950/80 text-emerald-300 shadow-[0_0_20px_rgba(45,227,138,0.15)]",
  review: "border-amber-700/60 bg-amber-950/80 text-amber-200 shadow-[0_0_20px_rgba(245,158,11,0.12)]",
  deny: "border-red-800/60 bg-red-950/80 text-red-300 shadow-[0_0_20px_rgba(239,68,68,0.12)]",
};

export function DecisionBadge({ decision }: { decision: string }) {
  const key = decision.toLowerCase();
  const cls = styles[key] ?? "border-gray-700 bg-gray-900 text-gray-200";
  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${cls}`}
    >
      {decision}
    </span>
  );
}
