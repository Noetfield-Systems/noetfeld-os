"use client";

import { Shell } from "@/components/Shell";
import { EvaluateForm } from "@/components/EvaluateForm";

export default function EvaluatePage() {
  return (
    <Shell active="evaluate">
      <section className="mb-8">
        <h2 className="text-2xl font-semibold text-white">Submit operational intent</h2>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Describe who is acting, what they propose, and the operational context. Noetfield returns a
          governance decision before any external system executes.
        </p>
      </section>
      <EvaluateForm />
    </Shell>
  );
}
