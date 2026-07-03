// NOOS 24/7 loop fleet: Cloudflare five-minute cron dispatches due domain loops.
const DEFAULT_REPO = "Noetfield-Systems/noetfeld-os";

const LOOPS = [
  { event_type: "noos_inbox_loop_tick", interval: 5, domain: "factory-inbox" },
  { event_type: "noos_runtime_loop_tick", interval: 15, domain: "gel-runtime" },
  { event_type: "noos_surface_loop_tick", interval: 20, domain: "public-nerve" },
  { event_type: "noos_chain_loop_tick", interval: 30, domain: "chain-tools" },
  { event_type: "noos_self_heal_loop_tick", interval: 10, domain: "self-improvement" },
  { event_type: "noos_sourcea_observe_loop_tick", interval: 30, domain: "sourcea-observe" },
  { event_type: "noos_agent_nerve_loop_tick", interval: 60, domain: "agent-docs" },
];

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Access-Control-Allow-Origin": "*", "Cache-Control": "no-store" },
  });
}

async function dispatchLoop(env, eventType, meta = {}) {
  const token = (env.GITHUB_TOKEN || "").trim();
  const repo = (env.GITHUB_REPO || DEFAULT_REPO).trim();
  if (!token) {
    return { ok: false, error: "GITHUB_TOKEN missing", event_type: eventType };
  }
  const resp = await fetch(`https://api.github.com/repos/${repo}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "noos-loop-fleet-tick-v1",
    },
    body: JSON.stringify({
      event_type: eventType,
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
    event_type: eventType,
    body: text ? text.slice(0, 120) : null,
  };
}

function dueLoops(utcMinute) {
  return LOOPS.filter((loop) => utcMinute % loop.interval === 0);
}

export default {
  async scheduled(event, env, ctx) {
    const minute = new Date().getUTCMinutes();
    const due = dueLoops(minute);
    ctx.waitUntil(
      (async () => {
        const results = [];
        for (const loop of due) {
          results.push(
            await dispatchLoop(env, loop.event_type, {
              source: "cf-cron",
              cron: event?.cron || "*/5 * * * *",
              domain: loop.domain,
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
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      const minute = new Date().getUTCMinutes();
      return json({
        ok: true,
        schema: "noos-loop-fleet-tick-health-v1",
        service: "noos-loop-fleet-tick-v1",
        cron: "*/5 * * * *",
        github_token_ready: Boolean(env.GITHUB_TOKEN),
        github_repo: env.GITHUB_REPO || DEFAULT_REPO,
        loops: LOOPS,
        due_now: dueLoops(minute).map((l) => l.event_type),
        utc_minute: minute,
      });
    }
    if (url.pathname === "/tick" && request.method === "POST") {
      const minute = new Date().getUTCMinutes();
      const force = url.searchParams.get("all") === "1";
      const targets = force ? LOOPS : dueLoops(minute);
      const results = [];
      for (const loop of targets) {
        results.push(
          await dispatchLoop(env, loop.event_type, { source: "http_tick", utc_minute: minute }),
        );
      }
      const ok = results.every((r) => r.ok);
      return json({ ok, schema: "noos-loop-fleet-tick-v1", results }, ok ? 200 : 502);
    }
    return json({ ok: false, error: "not_found" }, 404);
  },
};
