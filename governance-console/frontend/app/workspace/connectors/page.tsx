"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { LoadingBlock } from "@/components/LoadingBlock";
import { PageHero } from "@/components/PageHero";
import { listConnectors, registerConnector, ConnectorSummary } from "@/lib/api";

export default function ConnectorsPage() {
  const [rows, setRows] = useState<ConnectorSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [registering, setRegistering] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setRows(await listConnectors());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load connectors.");
    } finally {
      setLoading(false);
    }
  }

  async function registerM365() {
    setRegistering(true);
    setError(null);
    try {
      const id = `m365-purview-${Date.now()}`;
      await registerConnector({
        connector_id: id,
        connector_type: "m365_purview",
        required_scopes: ["Purview.Read", "AuditLog.Read"],
      });
      window.location.href = `/connectors/${encodeURIComponent(id)}/oauth/start`;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Registration failed.");
      setRegistering(false);
    }
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const connected = params.get("connected");
    if (connected) setSuccess(connected);
    load();
  }, []);

  return (
    <Shell active="workspace">
      <p className="mb-4">
        <Link href="/workspace" className="text-sm text-accent hover:underline">
          ← Trust Ledger
        </Link>
      </p>
      <PageHero
        eyebrow="Connectors"
        title="M365 evidence connectors"
        lead="Local dev uses mock OAuth (no production secrets). Set NF_M365_MOCK_TOKEN in the API environment."
      />
      {success && (
        <p
          className="mb-4 rounded-lg border border-emerald-900/80 bg-emerald-950/40 px-4 py-3 text-sm text-emerald-200"
          role="status"
        >
          Mock OAuth connected — <code>{success}</code>. M365 evidence ingested.
        </p>
      )}
      {error && (
        <p className="mb-4 rounded-lg border border-red-900/80 bg-red-950/40 px-4 py-3 text-sm text-red-200" role="alert">
          {error}
        </p>
      )}
      <div className="mb-6">
        <button type="button" className="nf-btn-primary" disabled={registering} onClick={() => registerM365()}>
          Register + mock connect (M365)
        </button>
      </div>
      {loading && <LoadingBlock label="Loading connectors…" />}
      {!loading && (
        <ul className="space-y-3">
          {rows.map((c) => (
            <li key={c.connector_id} className="nf-card p-4 text-sm">
              <p className="font-medium text-white">{c.connector_id}</p>
              <p className="text-muted-2">
                {c.connector_type} · {c.status}
                {c.oauth_connected ? " · OAuth connected" : ""}
              </p>
            </li>
          ))}
          {rows.length === 0 && <p className="text-muted">No connectors registered yet.</p>}
        </ul>
      )}
    </Shell>
  );
}
