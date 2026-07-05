// NOOS loop motor: single CF cron → Railway HTTP (no GitHub Actions dispatch).
import dispatchDoc from "./dispatch-table.json";

const TARGETS = dispatchDoc.targets || [];

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
  });
}

async function dispatchTarget(env, target, meta = {}) {
  const base = (env.LOOP_RUNNER_URL || "").trim().replace(/\/$/, "");
  const secret = (env.LOOP_RUNNER_SECRET || "").trim();
  const eventType = target.event_type;
  if (!base) {
    return { ok: false, error: "LOOP_RUNNER_URL missing", event_type: eventType };
  }
  const headers = { "Content-Type": "application/json", "User-Agent": "noos-loop-fleet-tick-v1" };
  if (secret) headers.Authorization = `Bearer ${secret}`;
  const resp = await fetch(`${base}/loop`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      event_type: eventType,
      dispatch_id: target.dispatch_id,
      handler: target.handler,
      source: meta.source || "cf-cron",
      at: new Date().toISOString(),
      ...meta,
    }),
  });
  let body = null;
  try {
    body = await resp.json();
  } catch {
    body = { raw: (await resp.text()).slice(0, 200) };
  }
  return {
    ok: resp.ok && body?.ok !== false,
    status: resp.status,
    event_type: eventType,
    dispatch_id: target.dispatch_id,
    body,
  };
}

function dueTargets(utcMinute) {
  return TARGETS.filter((t) => utcMinute % Number(t.interval_minutes || 5) === 0);
}

export default {
  async scheduled(event, env, ctx) {
    const minute = new Date().getUTCMinutes();
    const due = dueTargets(minute);
    ctx.waitUntil(
      (async () => {
        const results = [];
        for (const target of due) {
          results.push(
            await dispatchTarget(env, target, {
              source: "cf-cron",
              cron: event?.cron || dispatchDoc.motor_cron || "*/5 * * * *",
              utc_minute: minute,
            }),
          );
        }
        return results;
      })(),
    );
  },

  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      });
    }
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      const minute = new Date().getUTCMinutes();
      return json({
        ok: true,
        schema: "noos-loop-motor-health-v1",
        service: "noos-loop-fleet-tick-v1",
        cron: dispatchDoc.motor_cron || "*/5 * * * *",
        execution_plane: dispatchDoc.execution_plane || "railway:noos-loop-runner",
        loop_runner_url_ready: Boolean(env.LOOP_RUNNER_URL),
        target_count: TARGETS.length,
        targets: TARGETS,
        due_now: dueTargets(minute).map((t) => t.event_type),
        utc_minute: minute,
      });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const minute = new Date().getUTCMinutes();
      const force = url.searchParams.get("all") === "1";
      const eventFilter = url.searchParams.get("event_type");
      let targets = force ? TARGETS : dueTargets(minute);
      if (eventFilter) {
        targets = TARGETS.filter((t) => t.event_type === eventFilter);
      }
      const results = [];
      for (const target of targets) {
        results.push(await dispatchTarget(env, target, { source: "http_tick", utc_minute: minute }));
      }
      const ok = results.length > 0 && results.every((r) => r.ok);
      return json({ ok, schema: "noos-loop-motor-tick-v1", results }, ok ? 200 : 502);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
