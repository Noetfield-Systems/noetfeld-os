/** Trust Ledger v1 — platform API via same-origin proxy (/api/v1 → :8001). */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export type TrustLedgerEntry = {
  tle_id: string;
  status: string;
  decision?: string;
  date?: string;
  template_id?: string;
  evidence?: Array<Record<string, unknown>>;
  approval_chain?: Array<Record<string, unknown>>;
};

export type TleListResponse = {
  items: TrustLedgerEntry[];
  count: number;
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

export function listTles(status?: string, limit = 50): Promise<TleListResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (status?.trim()) params.set("status", status.trim());
  return request<TleListResponse>(`/api/v1/tle?${params}`);
}

export function getTle(tleId: string): Promise<TrustLedgerEntry> {
  return request<TrustLedgerEntry>(`/api/v1/tle/${encodeURIComponent(tleId)}`);
}

export function exportTlePdfUrl(tleId: string): string {
  return `${API_BASE}/api/v1/tle/${encodeURIComponent(tleId)}/export`;
}
