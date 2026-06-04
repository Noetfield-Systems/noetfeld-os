import Link from "next/link";
import { Shell } from "@/components/Shell";

export default function NotFound() {
  return (
    <Shell>
      <div className="nf-card mx-auto max-w-lg p-10 text-center">
        <p className="nf-eyebrow">404</p>
        <h1 className="mt-2 font-serif text-2xl font-semibold text-white">Page not found</h1>
        <p className="mt-3 text-sm text-muted">
          This route is not part of the governance console dev surface.
        </p>
        <Link href="/cognitive-dashboard" className="nf-btn-primary mt-6 inline-flex">
          Back to dashboard
        </Link>
      </div>
    </Shell>
  );
}
