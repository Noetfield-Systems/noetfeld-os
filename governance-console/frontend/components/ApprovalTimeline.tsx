"use client";

type ApprovalStep = {
  approver?: { id?: string; name?: string; role?: string };
  status?: string;
  signed_at?: string;
};

type ApprovalTimelineProps = {
  chain: ApprovalStep[];
  onApprove?: (approverId: string) => void;
  onReject?: (approverId: string) => void;
  canAct?: boolean;
  approving?: string | null;
};

export function ApprovalTimeline({
  chain,
  onApprove,
  onReject,
  canAct,
  approving,
}: ApprovalTimelineProps) {
  if (!chain.length) {
    return <p className="text-sm text-muted">No approval steps yet.</p>;
  }

  return (
    <ol className="relative space-y-4 border-l-2 border-border pl-6">
      {chain.map((step, i) => {
        const approver = step.approver ?? {};
        const pending = step.status === "Pending";
        const done = step.status === "Approved" || step.status === "Signed";
        return (
          <li key={i} className="relative">
            <span
              className={`absolute -left-[1.6rem] top-1 flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold ${
                done ? "bg-ok/15 text-ok" : pending ? "bg-amber-100 text-amber-800" : "bg-panel-solid text-muted"
              }`}
              aria-hidden
            >
              {done ? "✓" : i + 1}
            </span>
            <div className="rounded-lg border border-border bg-white p-4">
              <p className="font-medium text-text">{approver.name ?? "Approver"}</p>
              <p className="text-xs text-muted-2">
                {approver.role} · {step.status}
                {step.signed_at ? ` · ${new Date(step.signed_at).toLocaleString()}` : ""}
              </p>
              {pending && canAct && onApprove && onReject && (
                <div className="mt-3 flex gap-2">
                  <button
                    type="button"
                    className="nf-btn-primary text-sm"
                    disabled={approving === approver.id}
                    onClick={() => onApprove(String(approver.id))}
                  >
                    Approve
                  </button>
                  <button
                    type="button"
                    className="nf-btn-secondary text-sm"
                    disabled={approving === approver.id}
                    onClick={() => onReject(String(approver.id))}
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
