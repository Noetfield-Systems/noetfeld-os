/** Signed Unified Motor Event API client (Workers / Node). Mirrors scripts/unified_motor_event_client_v1.py */

export const EVENT_SCHEMA_VERSION = "motor.event.v1";
export const MAX_TIMESTAMP_SKEW_SEC = 300;

export async function sha256HexHmac(secret, message) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return [...new Uint8Array(mac)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function signMotorEventBody(secret, timestamp, rawBody) {
  const digest = await sha256HexHmac(secret, `${timestamp}.${rawBody}`);
  return `sha256=${digest}`;
}

export function buildIdempotencyKey({ loopId, cycleNumber, opKey, noosSourceId = "noos.portfolio" }) {
  if (opKey) return `${noosSourceId}:${opKey}`;
  return `${noosSourceId}:${loopId}:cycle:${cycleNumber}`;
}

export async function postSignedEvent({
  gatewayUrl,
  secret,
  event,
  idempotencyKey,
  fetchImpl = fetch,
}) {
  const rawBody = JSON.stringify(event);
  const timestamp = String(Math.floor(Date.now() / 1000));
  const signature = await signMotorEventBody(secret, timestamp, rawBody);
  const loopId = event?.payload?.loop_id || "unknown";
  const cycleNumber = event?.payload?.cycle_number || 0;
  const idem =
    idempotencyKey ||
    buildIdempotencyKey({ loopId, cycleNumber, opKey: event?.payload?.op_key });
  const resp = await fetchImpl(`${gatewayUrl.replace(/\/$/, "")}/v1/events`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "User-Agent": "noos-unified-motor-event-client-v1",
      "x-motor-timestamp": timestamp,
      "x-motor-signature": signature,
      "Idempotency-Key": idem,
    },
    body: rawBody,
  });
  let body = {};
  try {
    body = await resp.json();
  } catch {
    body = {};
  }
  return { ok: resp.ok, status: resp.status, idempotency_key: idem, body };
}
