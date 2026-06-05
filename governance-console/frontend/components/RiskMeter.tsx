export function RiskMeter({ score }: { score: number }) {
  const level = score >= 70 ? "high" : score >= 40 ? "medium" : "low";
  const barClass =
    level === "high"
      ? "bg-gradient-to-r from-amber-600 to-red-500"
      : level === "medium"
        ? "bg-gradient-to-r from-emerald-600 to-amber-500"
        : "bg-gradient-to-r from-emerald-700 to-emerald-400";

  return (
    <div className="w-full">
      <div className="mb-2 flex justify-between text-sm">
        <span className="font-medium text-muted">Risk score</span>
        <span className="font-mono font-semibold text-white">{score}</span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-border">
        <div
          className={`h-full rounded-full transition-all duration-500 ${barClass}`}
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>
    </div>
  );
}
