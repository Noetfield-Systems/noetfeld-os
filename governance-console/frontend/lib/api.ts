const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
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
