import Link from "next/link";
import { Footer } from "@/components/Footer";

type ShellProps = {
  children: React.ReactNode;
  active?: "dashboard" | "evaluate" | "audit" | "trust-ledger" | "workspace";
};

function navClass(active: boolean): string {
  return `rounded-md px-3 py-2 hover:bg-white/5${active ? " bg-white/10 text-white" : ""}`;
}

export function Shell({ children, active }: ShellProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-border bg-panel/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4">
          <Link href="/cognitive-dashboard" className="flex items-center gap-3 hover:opacity-90">
            <img
              src="/noetfield-favicon-512.png"
              alt=""
              width={36}
              height={36}
              className="rounded-md"
            />
            <div>
              <p className="text-xs uppercase tracking-widest text-accent">Noetfield</p>
              <h1 className="text-lg font-semibold text-white">Governance Console</h1>
              <p className="text-xs text-muted">Pre-execution intent evaluation · no custody or payments</p>
            </div>
          </Link>
          <nav className="flex flex-wrap gap-1 text-sm">
            <Link href="/cognitive-dashboard" className={navClass(active === "dashboard")}>
              Dashboard
            </Link>
            <Link href="/evaluate" className={navClass(active === "evaluate")}>
              Evaluate
            </Link>
            <Link href="/audit" className={navClass(active === "audit")}>
              Audit log
            </Link>
            <Link href="/trust-ledger" className={navClass(active === "trust-ledger")}>
              Trust Ledger
            </Link>
            <Link href="/workspace" className={navClass(active === "workspace")}>
              Workspace
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">{children}</main>
      <Footer />
    </div>
  );
}
