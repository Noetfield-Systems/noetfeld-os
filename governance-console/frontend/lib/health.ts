const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ApiHealth = {
  ok: boolean;
  detail: string;
};

export async function fetchApiHealth(): Promise<ApiHealth> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    if (!res.ok) {
      return { ok: false, detail: `API returned HTTP ${res.status}` };
    }
    const body = (await res.json()) as { status?: string; database?: string };
    const db = body.database ?? body.status ?? "unknown";
    return { ok: true, detail: String(db) };
  } catch (e) {
    const msg = e instanceof Error ? e.message : "unreachable";
    return { ok: false, detail: msg };
  }
}

export function apiBaseLabel(): string {
  return API_BASE;
}
