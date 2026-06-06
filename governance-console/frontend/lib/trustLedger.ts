/** Trust Ledger v1 — platform API via same-origin proxy (/api/v1 → :8001). */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

function pilotAuthHeaders(): Record<string, string> {
  const key = process.env.NEXT_PUBLIC_PILOT_API_KEY?.trim();
  if (!key) return {};
  return { Authorization: `Bearer ${key}` };
}

export type ConfidenceFactor = {
  factor: string;
  contribution: number;
  detail: string;
};

export type TrustLedgerEntry = {
  tle_id: string;
  status: string;
  decision?: string;
  date?: string;
  template_id?: string;
  confidence_score?: number;
  confidence_factors?: ConfidenceFactor[];
  confidence_method?: string;
  evidence?: Array<Record<string, unknown>>;
  approval_chain?: Array<Record<string, unknown>>;
};

export type EvidenceObject = {
  evidence_id: string;
  source: string;
  title: string;
  hash: string;
};

export type TleListResponse = {
  items: TrustLedgerEntry[];
  count: number;
};

export type EvidenceListResponse = {
  items: EvidenceObject[];
  count: number;
};

export type TleDraftRequest = {
  template_id: string;
  evidence_ids: string[];
  owner_id?: string;
  decision?: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...pilotAuthHeaders(),
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function listTles(status?: string, limit = 50): Promise<TleListResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (status?.trim()) params.set("status", status.trim());
  return request<TleListResponse>(`/api/v1/tle?${params}`);
}

export function getTle(tleId: string): Promise<TrustLedgerEntry> {
  return request<TrustLedgerEntry>(`/api/v1/tle/${encodeURIComponent(tleId)}`);
}

export function listEvidence(limit = 50): Promise<EvidenceListResponse> {
  return request<EvidenceListResponse>(`/api/v1/evidence?limit=${limit}`);
}

export function createTleDraft(payload: TleDraftRequest): Promise<TrustLedgerEntry> {
  return request<TrustLedgerEntry>("/api/v1/tle/draft", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function exportTlePdfUrl(tleId: string): string {
  return `${API_BASE}/api/v1/tle/${encodeURIComponent(tleId)}/export`;
}

export function formatConfidence(score?: number): string {
  if (score === undefined || Number.isNaN(score)) return "—";
  return `${Math.round(score * 100)}%`;
}
