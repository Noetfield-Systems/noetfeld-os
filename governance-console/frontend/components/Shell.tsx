import Link from "next/link";
import { Footer } from "@/components/Footer";

type ShellProps = {
  children: React.ReactNode;
  active?: "dashboard" | "evaluate" | "audit" | "workspace";
};

function navClass(active: boolean): string {
  return [
    "rounded-lg px-3 py-2 text-sm font-medium transition",
    active
      ? "bg-accent/15 text-accent ring-1 ring-accent/30"
      : "text-muted hover:bg-white/5 hover:text-white",
  ].join(" ");
}

export function Shell({ children, active }: ShellProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 border-b border-border bg-surface/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <Link href="/cognitive-dashboard" className="group flex items-center gap-3">
            <span
              className="flex h-10 w-10 items-center justify-center rounded-lg border border-accent/40 bg-accent/10 font-serif text-lg font-semibold text-accent shadow-glow transition group-hover:border-accent/60"
              aria-hidden
            >
              N
            </span>
            <div>
              <p className="nf-eyebrow">Noetfield</p>
              <h1 className="font-serif text-lg font-semibold leading-tight text-white">
                Governance Console
              </h1>
              <p className="hidden text-xs text-muted-2 sm:block">
                Pre-execution intent · no custody or payments
              </p>
            </div>
          </Link>
          <nav className="flex flex-wrap items-center gap-1" aria-label="Main">
            <Link href="/cognitive-dashboard" className={navClass(active === "dashboard")}>
              Dashboard
            </Link>
            <Link href="/evaluate" className={navClass(active === "evaluate")}>
              Evaluate
            </Link>
            <Link href="/audit" className={navClass(active === "audit")}>
              Audit log
            </Link>
            <Link href="/workspace" className={navClass(active === "workspace")}>
              Trust Ledger
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6 sm:py-10">{children}</main>
      <Footer />
    </div>
  );
}
