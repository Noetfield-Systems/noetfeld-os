"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { evaluateIntent } from "@/lib/api";

export function EvaluateForm() {
  const router = useRouter();
  const [actor, setActor] = useState("");
  const [action, setAction] = useState("");
  const [context, setContext] = useState("");
  const [metadataRaw, setMetadataRaw] = useState("{}");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    let metadata: Record<string, unknown> = {};
    try {
      metadata = metadataRaw.trim() ? JSON.parse(metadataRaw) : {};
    } catch {
      setError("Metadata must be valid JSON.");
      setLoading(false);
      return;
    }
    try {
      const result = await evaluateIntent({ actor, action, context, metadata });
      router.push(`/result/${encodeURIComponent(result.rid)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="nf-card space-y-6 p-6 sm:p-8" noValidate>
      <div className="grid gap-5 sm:grid-cols-2">
        <label className="block sm:col-span-1">
          <span className="text-sm font-medium text-muted">Actor</span>
          <input
            required
            value={actor}
            onChange={(e) => setActor(e.target.value)}
            placeholder="e.g. service:copilot-agent-01"
            className="nf-input"
            autoComplete="off"
            aria-required="true"
          />
        </label>
        <label className="block sm:col-span-1">
          <span className="text-sm font-medium text-muted">Action</span>
          <input
            required
            value={action}
            onChange={(e) => setAction(e.target.value)}
            placeholder="e.g. export_customer_summary"
            className="nf-input"
            autoComplete="off"
            aria-required="true"
          />
        </label>
      </div>
      <label className="block">
        <span className="text-sm font-medium text-muted">Context</span>
        <textarea
          required
          rows={4}
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="Business justification, data scope, policy references…"
          className="nf-input"
          aria-required="true"
        />
      </label>
      <label className="block">
        <span className="text-sm font-medium text-muted">Metadata (JSON, optional)</span>
        <textarea
          rows={3}
          value={metadataRaw}
          onChange={(e) => setMetadataRaw(e.target.value)}
          className="nf-input font-mono text-xs"
          spellCheck={false}
          aria-describedby="metadata-hint"
        />
        <p id="metadata-hint" className="mt-1 text-xs text-muted-2">
          Optional structured fields for policy engines.
        </p>
      </label>
      {error && (
        <p
          className="rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200"
          role="alert"
        >
          {error}
        </p>
      )}
      <button type="submit" disabled={loading} className="nf-btn-primary w-full sm:w-auto">
        {loading && <span className="nf-spinner" aria-hidden />}
        {loading ? "Evaluating…" : "Evaluate intent"}
      </button>
    </form>
  );
}
