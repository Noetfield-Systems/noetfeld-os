import Link from "next/link";

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-panel/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4">
          <div>
            <p className="text-xs uppercase tracking-widest text-accent">Noetfield</p>
            <h1 className="text-lg font-semibold text-white">Governance Console</h1>
            <p className="text-xs text-muted">Pre-execution intent evaluation · no custody or payments</p>
          </div>
          <nav className="flex gap-3 text-sm">
            <Link href="/" className="rounded-md px-3 py-2 hover:bg-white/5">
              Evaluate
            </Link>
            <Link href="/audit" className="rounded-md px-3 py-2 hover:bg-white/5">
              Audit log
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
    </div>
  );
}
