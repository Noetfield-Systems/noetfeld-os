"use client";

import Link from "next/link";
import { Shell } from "@/components/Shell";
import { PageHero } from "@/components/PageHero";
import { UsageMeter } from "@/components/UsageMeter";

export default function OnboardingPage() {
  return (
    <Shell active="onboarding" title="Trial OS onboarding">
      <PageHero
        className="mb-6"
        eyebrow="Self-serve sandbox"
        title="Trial OS — product mirror"
        lead="Complete sandbox signup on www, then continue evaluate → TLE → export in the Governance Console."
      />
      <UsageMeter className="mb-6" />
      <ol className="nf-card list-decimal space-y-4 p-6 pl-10 text-sm text-muted">
        <li>Account — work email and org (local sandbox tenant).</li>
        <li>Environment — Sandbox active · Production locked until design partner.</li>
        <li>Connect mock M365 — OAuth success UI in workspace connectors.</li>
        <li>First evaluate — POST /evaluate with confidence score and RID.</li>
        <li>Receipt + export — board PDF and procurement ZIP from workspace.</li>
      </ol>
      <div className="mt-6 flex flex-wrap gap-3">
        <Link href="/start/" className="nf-btn-primary">
          Open www Trial OS
        </Link>
        <Link href="/evaluate" className="nf-btn-secondary">
          Evaluate in console
        </Link>
        <Link href="/workspace/TLE-015DCFB8B953" className="nf-btn-secondary">
          Receipt Studio sample
        </Link>
      </div>
    </Shell>
  );
}
