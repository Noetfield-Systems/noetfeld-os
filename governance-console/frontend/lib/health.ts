const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export type ApiHealth = {
  ok: boolean;
  detail: string;
};

let cache: { at: number; value: ApiHealth } | null = null;
let inflight: Promise<ApiHealth> | null = null;
const CACHE_MS = 5_000;

export async function fetchApiHealth(): Promise<ApiHealth> {
  const now = Date.now();
  if (cache && now - cache.at < CACHE_MS) {
    return cache.value;
  }
  if (inflight) {
    return inflight;
  }
  inflight = (async () => {
    try {
      const res = await fetch(`${API_BASE}/health`, {
        cache: "no-store",
        signal: AbortSignal.timeout(4_000),
      });
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
  })();
  try {
    const value = await inflight;
    cache = { at: Date.now(), value };
    return value;
  } finally {
    inflight = null;
  }
}

export function apiBaseLabel(): string {
  return API_BASE || "(same-origin)";
}
