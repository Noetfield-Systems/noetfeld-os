"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { createTleDraft, EvidenceObject, listEvidence } from "@/lib/trustLedger";

const TEMPLATES = [
  { id: "copilot-go-no-go-v1", label: "Copilot Go/No-Go v1" },
  { id: "custom-v0", label: "Custom draft v0" },
];

export default function TrustLedgerNewPage() {
  const router = useRouter();
  const [evidence, setEvidence] = useState<EvidenceObject[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [templateId, setTemplateId] = useState(TEMPLATES[0].id);
  const [decision, setDecision] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    listEvidence()
      .then((res) => setEvidence(res.items))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load evidence."))
      .finally(() => setLoading(false));
  }, []);

  function toggleEvidence(id: string) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (selected.length === 0) {
      setError("Select at least one evidence item.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const draft = await createTleDraft({
        template_id: templateId,
        evidence_ids: selected,
        decision: decision.trim() || undefined,
      });
      router.push(`/trust-ledger/${encodeURIComponent(draft.tle_id)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create draft.");
      setSubmitting(false);
    }
  }

  return (
    <Shell active="trust-ledger">
      <p className="mb-4 text-sm">
        <Link href="/trust-ledger" className="text-accent hover:underline">
          ← Trust Ledger
        </Link>
      </p>

      <section className="mb-6">
        <h2 className="text-2xl font-semibold text-white">TLE Generator</h2>
        <p className="mt-2 text-sm text-muted">
          Template + evidence refs → draft TLE with deterministic confidence score.
        </p>
      </section>

      {error && (
        <p className="mb-4 rounded-lg border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-300">
          {error}
        </p>
      )}

      <form onSubmit={onSubmit} className="space-y-6">
        <div>
          <label htmlFor="template" className="block text-sm font-medium text-white">
            Template
          </label>
          <select
            id="template"
            value={templateId}
            onChange={(e) => setTemplateId(e.target.value)}
            className="mt-2 w-full max-w-md rounded-lg border border-border bg-panel px-3 py-2 text-sm"
          >
            {TEMPLATES.map((t) => (
              <option key={t.id} value={t.id}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="decision" className="block text-sm font-medium text-white">
            Decision (optional)
          </label>
          <input
            id="decision"
            type="text"
            value={decision}
            onChange={(e) => setDecision(e.target.value)}
            placeholder="e.g. Approve Copilot pilot for Finance"
            className="mt-2 w-full max-w-xl rounded-lg border border-border bg-panel px-3 py-2 text-sm"
          />
        </div>

        <div>
          <p className="text-sm font-medium text-white">Evidence</p>
          {loading && <p className="mt-2 text-sm text-muted">Loading evidence…</p>}
          {!loading && evidence.length === 0 && (
            <p className="mt-2 text-sm text-muted">
              No evidence indexed. Run <code className="text-accent">./scripts/tle-smoke.sh --api</code> first.
            </p>
          )}
          {!loading && evidence.length > 0 && (
            <ul className="mt-3 space-y-2">
              {evidence.map((ev) => (
                <li key={ev.evidence_id}>
                  <label className="flex cursor-pointer items-start gap-3 rounded-lg border border-border bg-panel/60 px-3 py-2 hover:border-accent/40">
                    <input
                      type="checkbox"
                      checked={selected.includes(ev.evidence_id)}
                      onChange={() => toggleEvidence(ev.evidence_id)}
                      className="mt-1"
                    />
                    <span className="text-sm">
                      <span className="font-mono text-accent">{ev.evidence_id}</span>
                      <span className="text-muted"> — {ev.title}</span>
                      <span className="block text-xs text-muted">{ev.source}</span>
                    </span>
                  </label>
                </li>
              ))}
            </ul>
          )}
        </div>

        <button
          type="submit"
          disabled={submitting || selected.length === 0}
          className="rounded-lg border border-accent px-4 py-2 text-sm text-accent hover:bg-accent/10 disabled:opacity-50"
        >
          {submitting ? "Creating…" : "Create draft TLE"}
        </button>
      </form>
    </Shell>
  );
}
