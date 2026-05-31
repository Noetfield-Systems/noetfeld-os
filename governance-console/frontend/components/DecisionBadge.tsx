const styles: Record<string, string> = {
  allow: "bg-emerald-950 text-emerald-300 border-emerald-800",
  review: "bg-amber-950 text-amber-200 border-amber-800",
  deny: "bg-red-950 text-red-300 border-red-800",
};

export function DecisionBadge({ decision }: { decision: string }) {
  const key = decision.toLowerCase();
  const cls = styles[key] ?? "bg-gray-800 text-gray-200 border-gray-700";
  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium uppercase ${cls}`}>
      {decision}
    </span>
  );
}
