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
    <form onSubmit={onSubmit} className="space-y-5 rounded-xl border border-border bg-panel p-6">
      <label className="block">
        <span className="text-sm text-muted">Actor</span>
        <input
          required
          value={actor}
          onChange={(e) => setActor(e.target.value)}
          placeholder="e.g. service:copilot-agent-01"
          className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        />
      </label>
      <label className="block">
        <span className="text-sm text-muted">Action</span>
        <input
          required
          value={action}
          onChange={(e) => setAction(e.target.value)}
          placeholder="e.g. export_customer_summary"
          className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        />
      </label>
      <label className="block">
        <span className="text-sm text-muted">Context</span>
        <textarea
          required
          rows={4}
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="Business justification, data scope, policy references…"
          className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm"
        />
      </label>
      <label className="block">
        <span className="text-sm text-muted">Metadata (JSON, optional)</span>
        <textarea
          rows={3}
          value={metadataRaw}
          onChange={(e) => setMetadataRaw(e.target.value)}
          className="mt-1 w-full font-mono text-xs rounded-lg border border-border bg-surface px-3 py-2"
        />
      </label>
      {error && (
        <p className="rounded-lg border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-300">
          {error}
        </p>
      )}
      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-black hover:opacity-90 disabled:opacity-50"
      >
        {loading ? "Evaluating…" : "Evaluate Intent"}
      </button>
    </form>
  );
}
