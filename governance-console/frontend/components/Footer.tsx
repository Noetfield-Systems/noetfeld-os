import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-16 border-t border-border py-8">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 text-xs text-muted-2 sm:px-6">
        <p>
          Noetfield — AI Governance &amp; Evidence for M365 Copilot · blocked · receipted · fail-closed export ·{" "}
          <a
            href="https://www.noetfield.com"
            className="text-accent hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            www.noetfield.com
          </a>
        </p>
        <nav className="flex flex-wrap gap-4" aria-label="Footer">
          <Link href="/cognitive-dashboard" className="hover:text-accent">
            Dashboard
          </Link>
          <Link href="/evaluate" className="hover:text-accent">
            Evaluate
          </Link>
          <Link href="/audit" className="hover:text-accent">
            Audit
          </Link>
          <Link href="/workspace" className="hover:text-accent">
            Workspace
          </Link>
          <Link href="/trust-ledger" className="hover:text-accent">
            Trust Ledger
          </Link>
        </nav>
      </div>
    </footer>
  );
}
