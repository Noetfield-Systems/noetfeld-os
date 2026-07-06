// Phase B — independent dead-man switch (*/30 cron). Watches noos_loop_registry in Supabase.
import config from "./deadman-config.json";
import intervals from "./loop-intervals.json";

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
  });
}

function supabaseHeaders(env) {
  const key = (env.NOETFIELD_SUPABASE_SERVICE_ROLE_KEY || env.SUPABASE_SERVICE_ROLE_KEY || "").trim();
  return {
    apikey: key,
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/json",
    Prefer: "return=minimal",
  };
}

function supabaseBase(env) {
  return (env.NOETFIELD_SUPABASE_URL || env.SUPABASE_URL || "").trim().replace(/\/$/, "");
}

function parseTs(value) {
  if (!value) return null;
  const t = Date.parse(String(value));
  return Number.isFinite(t) ? t : null;
}

function isStale(lastFiredAt, intervalMinutes, multiplier = 2) {
  const ts = parseTs(lastFiredAt);
  if (ts === null) return true;
  const ageMin = (Date.now() - ts) / 60000;
  return ageMin > intervalMinutes * multiplier;
}

function evaluateStale(registryRows, multiplier) {
  const stale = [];
  const seen = new Set();
  for (const row of registryRows) {
    const lid = String(row.loop_id);
    seen.add(lid);
    const spec = intervals[lid] || {};
    const interval = Number(row.interval_minutes || spec.interval_minutes || 5);
    if (isStale(row.last_fired_at, interval, multiplier)) {
      stale.push({
        loop_id: lid,
        event_type: row.event_type || spec.event_type,
        interval_minutes: interval,
        last_fired_at: row.last_fired_at || null,
      });
    }
  }
  for (const [lid, spec] of Object.entries(intervals)) {
    if (seen.has(lid)) continue;
    stale.push({
      loop_id: lid,
      event_type: spec.event_type,
      interval_minutes: spec.interval_minutes,
      last_fired_at: null,
      reason: "never_fired",
    });
  }
  return stale;
}

async function fetchRegistry(env) {
  const base = supabaseBase(env);
  if (!base) return { ok: false, error: "supabase_url_missing", rows: [] };
  const resp = await fetch(`${base}/rest/v1/noos_loop_registry?select=*`, {
    headers: supabaseHeaders(env),
  });
  if (!resp.ok) return { ok: false, error: `registry_http_${resp.status}`, rows: [] };
  return { ok: true, rows: await resp.json() };
}

async function probeMotorHealth(url) {
  if (!url) return { ok: false, error: "health_url_missing" };
  try {
    const resp = await fetch(url, { headers: { "User-Agent": "noos-deadman-v1" } });
    let body = null;
    try {
      body = await resp.json();
    } catch {
      body = null;
    }
    return { ok: resp.ok && (body?.ok !== false), status: resp.status, body };
  } catch (err) {
    return { ok: false, error: String(err) };
  }
}

async function restartMotor(env, recipeId) {
  const base = (env.LOOP_RUNNER_URL || "").trim().replace(/\/$/, "");
  const secret = (env.LOOP_RUNNER_SECRET || "").trim();
  const path = (config.loop_runner || {}).motor_restart_path || "/motor-restart";
  if (!base || !recipeId) return { ok: false, error: "loop_runner_or_recipe_missing" };
  const headers = { "Content-Type": "application/json", "User-Agent": "noos-deadman-v1" };
  if (secret) headers.Authorization = `Bearer ${secret}`;
  const resp = await fetch(`${base}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify({ recipe_id: recipeId, source: "deadman-v1", dry_run: false }),
  });
  let body = null;
  try {
    body = await resp.json();
  } catch {
    body = { raw: (await resp.text()).slice(0, 200) };
  }
  return { ok: resp.ok && body?.ok !== false, status: resp.status, recipe_id: recipeId, body };
}

async function restartLoop(env, eventType) {
  const base = (env.LOOP_RUNNER_URL || "").trim().replace(/\/$/, "");
  const secret = (env.LOOP_RUNNER_SECRET || "").trim();
  if (!base || !eventType) return { ok: false, error: "loop_runner_or_event_missing" };
  const headers = { "Content-Type": "application/json", "User-Agent": "noos-deadman-v1" };
  if (secret) headers.Authorization = `Bearer ${secret}`;
  const resp = await fetch(`${base}/loop`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      event_type: eventType,
      source: "deadman-v1",
      at: new Date().toISOString(),
    }),
  });
  let body = null;
  try {
    body = await resp.json();
  } catch {
    body = { raw: (await resp.text()).slice(0, 200) };
  }
  return { ok: resp.ok, status: resp.status, event_type: eventType, body };
}

async function sendTelegram(env, text) {
  const token = (env.DEADMAN_TELEGRAM_BOT_TOKEN || "").trim();
  const chatId = (env.DEADMAN_TELEGRAM_CHAT_ID || "").trim();
  if (!token || !chatId) return { ok: false, skipped: true, reason: "telegram_not_configured" };
  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text }),
  });
  return { ok: resp.ok, status: resp.status };
}

async function sinkReceipt(env, receipt) {
  const base = supabaseBase(env);
  if (!base) return { ok: false, skipped: true, reason: "supabase_url_missing" };
  const runId = receipt.run_id || crypto.randomUUID();
  receipt.run_id = runId;
  const resp = await fetch(`${base}/rest/v1/noos_deadman_runs`, {
    method: "POST",
    headers: supabaseHeaders(env),
    body: JSON.stringify({ run_id: runId, receipt }),
  });
  return { ok: resp.ok, run_id: runId, status: resp.status };
}

async function maybeHeartbeatSummary(env, staleCount) {
  const hours = config.heartbeat_summary_hours_utc || [];
  const hour = new Date().getUTCHours();
  if (!hours.includes(hour)) return { ok: false, skipped: true, reason: "not_summary_hour" };
  const msg =
    staleCount === 0
      ? `NOOS deadman heartbeat (T+${hour}h UTC): all loops fresh, motors OK`
      : `NOOS deadman heartbeat (T+${hour}h UTC): stale_count=${staleCount}`;
  return sendTelegram(env, msg);
}

async function runCheck(env, meta = {}) {
  const multiplier = Number((config.interval_multipliers || {}).default || 2);
  const maxAttempts = Number(config.restart_attempts_max || 1);
  const loopRunnerBase = (env.LOOP_RUNNER_URL || "").trim().replace(/\/$/, "");
  const loopHealthPath = (config.loop_runner || {}).health_path || "/health";
  const loopRunnerHealth = loopRunnerBase
    ? await probeMotorHealth(`${loopRunnerBase}${loopHealthPath}`)
    : { ok: false, error: "loop_runner_url_missing" };
  const cfMotorHealth = await probeMotorHealth((config.cf_loop_motor || {}).health_url);
  const motorRestarts = [];
  if (!loopRunnerHealth.ok && maxAttempts > 0) {
    motorRestarts.push(await restartMotor(env, "railway-loop-runner"));
  } else if (!cfMotorHealth.ok && maxAttempts > 0) {
    motorRestarts.push(await restartMotor(env, (config.cf_loop_motor || {}).restart_recipe_id || "cf-loop-motor"));
  }
  const registry = await fetchRegistry(env);
  const stale = evaluateStale(registry.rows || [], multiplier);
  const restartAttempts = [];
  const loopBudget = Math.max(0, maxAttempts - motorRestarts.length);
  for (const row of stale.slice(0, loopBudget)) {
    if (row.event_type) {
      restartAttempts.push({ ...row, restart: await restartLoop(env, row.event_type) });
    }
  }
  let alertSent = false;
  let alertResult = { ok: false, skipped: true };
  if (stale.length > 0) {
    const msg = `NOOS deadman: ${stale.length} stale loop(s): ${stale.map((s) => s.loop_id).join(", ")}`;
    alertResult = await sendTelegram(env, msg);
    alertSent = alertResult.ok === true;
  }
  const heartbeat = await maybeHeartbeatSummary(env, stale.length);
  const receipt = {
    schema: "noos-deadman-run-v1",
    run_at: new Date().toISOString(),
    source: meta.source || "cf-cron",
    loop_runner_health: loopRunnerHealth,
    cf_motor_health: cfMotorHealth,
    motor_restarts: motorRestarts,
    stale_count: stale.length,
    stale_loops: stale,
    restart_attempts: restartAttempts,
    restart_attempt_count: restartAttempts.length,
    alert_sent: alertSent,
    alert: alertResult,
    heartbeat_summary: heartbeat,
    ok: registry.ok !== false,
  };
  receipt.supabase_sink = await sinkReceipt(env, receipt);
  return receipt;
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runCheck(env, { source: "cf-cron", cron: event?.cron || config.cron }));
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
      return json({
        ok: true,
        schema: "noos-deadman-health-v1",
        service: "noos-deadman-v1",
        cron: config.cron || "*/30 * * * *",
        supabase_ready: Boolean(supabaseBase(env)),
        loop_runner_ready: Boolean(env.LOOP_RUNNER_URL),
        telegram_ready: Boolean(env.DEADMAN_TELEGRAM_BOT_TOKEN && env.DEADMAN_TELEGRAM_CHAT_ID),
        interval_multiplier: (config.interval_multipliers || {}).default || 2,
        restart_attempts_max: config.restart_attempts_max || 1,
      });
    }
    if (url.pathname === "/check" && request.method === "POST") {
      const receipt = await runCheck(env, { source: "http_check" });
      return json(receipt, receipt.ok ? 200 : 502);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
