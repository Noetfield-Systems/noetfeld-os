"use client";

import Link from "next/link";
import { ReceiptMock } from "@/components/ReceiptMock";

type ProofRailProps = {
  open: boolean;
  onToggle: () => void;
  rid?: string;
};

export function ProofRail({ open, onToggle, rid }: ProofRailProps) {
  return (
    <>
      <button
        type="button"
        className="fixed bottom-20 right-4 z-40 rounded-full border border-border bg-white px-4 py-2 text-sm font-semibold shadow-panel lg:hidden"
        onClick={onToggle}
        aria-expanded={open}
      >
        Receipt
      </button>
      <aside
        className={`fixed right-0 top-[7.5rem] z-30 hidden h-[calc(100vh-7.5rem)] w-[min(360px,92vw)] overflow-y-auto border-l border-border bg-surface p-4 transition-transform lg:block ${
          open ? "translate-x-0" : "translate-x-full lg:translate-x-0"
        }`}
        aria-label="Proof rail"
      >
        <div className="mb-3 flex items-center justify-between">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted">Proof rail</p>
          <button type="button" className="text-xs text-muted-2 lg:hidden" onClick={onToggle}>
            Close
          </button>
        </div>
        <ReceiptMock
          rid={rid ?? "RID-live"}
          footer={
            <>
              Live evaluate path ·{" "}
              <Link href="/trust-ledger/sample-report/" className="text-accent hover:underline">
                TLE samples
              </Link>
            </>
          }
        />
      </aside>
    </>
  );
}
