export function RiskMeter({ score }: { score: number }) {
  const color =
    score >= 70 ? "bg-red-500" : score >= 40 ? "bg-amber-500" : "bg-emerald-500";
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm text-muted">
        <span>Risk score</span>
        <span className="font-mono text-white">{score} / 100</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-border">
        <div className={`h-full transition-all ${color}`} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}
