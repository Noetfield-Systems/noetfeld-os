/** Empty = same-origin (required when using unified dev proxy on :13080). */
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export type WorkspaceRole = "viewer" | "approver" | "compliance_owner" | "governance_admin";

export function getWorkspaceRole(): WorkspaceRole {
  const r = (process.env.NEXT_PUBLIC_NF_DEV_ROLE ?? "approver").trim().toLowerCase();
  if (r === "viewer" || r === "approver" || r === "compliance_owner" || r === "governance_admin") {
    return r;
  }
  return "approver";
}

export function canApproveInWorkspace(): boolean {
  const role = getWorkspaceRole();
  return role === "approver" || role === "compliance_owner" || role === "governance_admin";
}

function apiHeaders(extra?: HeadersInit): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Role": getWorkspaceRole(),
    ...(extra ?? {}),
  };
}

export type EvaluatePayload = {
  actor: string;
  action: string;
  context: string;
  metadata?: Record<string, unknown>;
};

export type EvaluateResult = {
  decision: "allow" | "deny" | "review" | string;
  risk_score: number;
  reason: string[];
  conditions: string[];
  rid: string;
};

export type AuditRecord = {
  id: string;
  rid: string;
  actor: string;
  action: string;
  context: string;
  metadata: Record<string, unknown>;
  decision: string;
  risk_score: number;
  reason: string[];
  conditions: string[];
  timestamp: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: apiHeaders(init?.headers),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function evaluateIntent(payload: EvaluatePayload): Promise<EvaluateResult> {
  return request<EvaluateResult>("/evaluate", {
    method: "POST",
    body: JSON.stringify({
      actor: payload.actor,
      action: payload.action,
      context: payload.context,
      metadata: payload.metadata ?? {},
    }),
  });
}

export function listAudit(q?: string): Promise<AuditRecord[]> {
  const params = new URLSearchParams();
  if (q?.trim()) params.set("q", q.trim());
  const qs = params.toString();
  return request<AuditRecord[]>(`/audit${qs ? `?${qs}` : ""}`);
}

export function getAudit(rid: string): Promise<AuditRecord> {
  return request<AuditRecord>(`/audit/${encodeURIComponent(rid)}`);
}

export type TleSummary = {
  tle_id: string;
  status: string;
  decision: string;
  confidence_score: number;
  date: string;
  source_rid: string | null;
  created_at: string;
};

export type TleDetail = {
  tle_id: string;
  tenant_id: string;
  status: string;
  confidence_score: number;
  audit_digest: string | null;
  created_at: string;
  finalized_at: string | null;
  document: Record<string, unknown>;
};

export function listTles(params?: { q?: string; status?: string }): Promise<TleSummary[]> {
  const search = new URLSearchParams();
  if (params?.q?.trim()) search.set("q", params.q.trim());
  if (params?.status?.trim()) search.set("status", params.status.trim());
  const qs = search.toString();
  return request<TleSummary[]>(`/tle${qs ? `?${qs}` : ""}`);
}

export function getTle(tleId: string): Promise<TleDetail> {
  return request<TleDetail>(`/tle/${encodeURIComponent(tleId)}`);
}

export function draftTle(payload: {
  source_rid?: string;
  evidence_ids: string[];
}): Promise<TleDetail> {
  return request<TleDetail>("/tle/draft", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function approveTle(
  tleId: string,
  payload: { approver_id: string; decision: string; conditions?: string },
): Promise<TleDetail> {
  return request<TleDetail>(`/tle/${encodeURIComponent(tleId)}/approve`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export type ConnectorSummary = {
  connector_id: string;
  connector_type: string;
  status: string;
  oauth_connected: boolean;
  required_scopes: string[];
};

export function listConnectors(): Promise<ConnectorSummary[]> {
  return request<ConnectorSummary[]>("/connectors");
}

export function registerConnector(payload: {
  connector_id: string;
  connector_type: string;
  required_scopes?: string[];
}): Promise<ConnectorSummary> {
  return request<ConnectorSummary>("/connectors", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
