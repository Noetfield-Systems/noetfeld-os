// NOOS loop motor: CF cron/HTTP → Railway Python executor (one bounded tick per POST /loop).
import dispatchDoc from "./dispatch-table.json";

const TARGETS = dispatchDoc.targets || [];

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
  });
}

function executorConfig(env) {
  const url = (
    env.FLY_LOOP_EXECUTOR_URL ||
    env.RAILWAY_LOOP_EXECUTOR_URL ||
    env.LOOP_EXECUTOR_URL ||
    ""
  )
    .trim()
    .replace(/\/$/, "");
  const secret = (env.NOOS_LOOP_SECRET || "").trim();
  return { url, secret };
}

async function dispatchTarget(env, target, meta = {}) {
  const { url: base, secret } = executorConfig(env);
  const eventType = target.event_type;
  if (!base) {
    return { ok: false, error: "FLY_LOOP_EXECUTOR_URL missing", event_type: eventType };
  }
  if (!secret) {
    return { ok: false, error: "NOOS_LOOP_SECRET missing", event_type: eventType };
  }
  const headers = {
    "Content-Type": "application/json",
    "User-Agent": "noos-loop-fleet-tick-v1",
    "X-NOOS-Loop-Secret": secret,
  };
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
  const raw = await resp.text();
  let body = null;
  try {
    body = raw ? JSON.parse(raw) : null;
  } catch {
    body = { raw: raw.slice(0, 200) };
  }
  return {
    ok: resp.ok && body?.ok !== false,
    status: resp.status,
    event_type: eventType,
    dispatch_id: target.dispatch_id,
    execution_plane: dispatchDoc.execution_plane || "railway:noos-loop-runner",
    body,
  };
}

function dueTargets(utcMinute) {
  return TARGETS.filter((t) => {
    if (t.enabled === false || t.schedule_status === "quarantined") return false;
    return utcMinute % Number(t.interval_minutes || 5) === 0;
  });
}

async function dispatchAll(env, targets, meta) {
  // Repair fix 4: dispatchTarget() had no try/catch here — one thrown fetch()
  // silently dropped every remaining target in this tick, with zero logging
  // anywhere in the worker (compounding gap that let staleness go unnoticed).
  const results = [];
  for (const target of targets) {
    let result;
    try {
      result = await dispatchTarget(env, target, meta);
    } catch (err) {
      result = {
        ok: false,
        error: String(err && err.stack ? err.stack : err),
        event_type: target.event_type,
        dispatch_id: target.dispatch_id,
      };
    }
    const logLine = {
      schema: "noos-loop-motor-dispatch-v1",
      ok: result.ok,
      event_type: result.event_type,
      dispatch_id: result.dispatch_id,
      status: result.status,
      source: meta.source,
    };
    if (result.ok) {
      console.log(JSON.stringify(logLine));
    } else {
      console.error(JSON.stringify({ ...logLine, error: result.error }));
    }
    results.push(result);
  }
  return results;
}

export default {
  async scheduled(event, env, ctx) {
    const minute = new Date().getUTCMinutes();
    const due = dueTargets(minute);
    ctx.waitUntil(
      dispatchAll(env, due, {
        source: "cf-cron",
        cron: event?.cron || dispatchDoc.motor_cron || "*/5 * * * *",
        utc_minute: minute,
      }),
    );
  },

  async fetch(request, env, ctx) {
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
        executor_url_ready: Boolean(executorConfig(env).url),
        loop_secret_ready: Boolean(executorConfig(env).secret),
        target_count: TARGETS.length,
        targets: TARGETS,
        due_now: dueTargets(minute).map((t) => t.event_type),
        utc_minute: minute,
      });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const minute = new Date().getUTCMinutes();
      const force = url.searchParams.get("all") === "1";
      const wait = url.searchParams.get("wait") === "1";
      const eventFilter = url.searchParams.get("event_type");
      let targets = force ? TARGETS : dueTargets(minute);
      if (eventFilter) {
        targets = TARGETS.filter((t) => t.event_type === eventFilter);
      }
      const meta = { source: force ? "http_tick_all" : "http_tick", utc_minute: minute };
      if (force && !wait) {
        ctx.waitUntil(dispatchAll(env, targets, meta));
        return json(
          {
            ok: true,
            schema: "noos-loop-motor-tick-v1",
            status: "dispatched_async",
            target_count: targets.length,
            targets: targets.map((t) => t.event_type),
          },
          202,
        );
      }
      const results = await dispatchAll(env, targets, meta);
      const ok = results.length > 0 && results.every((r) => r.ok);
      return json({ ok, schema: "noos-loop-motor-tick-v1", results }, ok ? 200 : 502);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
