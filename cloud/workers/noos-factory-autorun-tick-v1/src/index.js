/**
 * NOOS factory autorun tick — Cloudflare cron → GitHub repository_dispatch.
 * Native GitHub schedule is silent on this private repo; CF cron is the autonomous motor.
 */
const DEFAULT_REPO = "Noetfield-Systems/noetfeld-os";
const EVENT_TYPE = "noos_factory_autorun_tick";

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-store",
    },
  });
}

async function dispatchFactoryAutorun(env, meta = {}) {
  const token = (env.GITHUB_TOKEN || "").trim();
  const repo = (env.GITHUB_REPO || DEFAULT_REPO).trim();
  if (!token) {
    return { ok: false, error: "GITHUB_TOKEN missing", schema: "noos-factory-autorun-tick-v1" };
  }
  const resp = await fetch(`https://api.github.com/repos/${repo}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "noos-factory-autorun-tick-v1",
    },
    body: JSON.stringify({
      event_type: EVENT_TYPE,
      client_payload: {
        source: meta.source || "cf-cron",
        at: new Date().toISOString(),
        ...meta,
      },
    }),
  });
  const text = await resp.text();
  return {
    ok: resp.status === 204,
    status: resp.status,
    schema: "noos-factory-autorun-tick-v1",
    event_type: EVENT_TYPE,
    repo,
    at: new Date().toISOString(),
    body: text ? text.slice(0, 200) : null,
  };
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(
      dispatchFactoryAutorun(env, {
        source: "cf-cron",
        cron: event?.cron || "*/10 * * * *",
      }),
    );
  },

  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return json({
        ok: true,
        schema: "noos-factory-autorun-tick-health-v1",
        service: "noos-factory-autorun-tick-v1",
        cron: "*/10 * * * *",
        github_token_ready: Boolean(env.GITHUB_TOKEN),
        github_repo: env.GITHUB_REPO || DEFAULT_REPO,
        event_type: EVENT_TYPE,
      });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const result = await dispatchFactoryAutorun(env, { source: "http_tick" });
      return json(result, result.ok ? 200 : 502);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
