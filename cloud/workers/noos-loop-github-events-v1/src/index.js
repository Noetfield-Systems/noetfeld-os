// Event Phase 1b — GitHub App webhook receiver: real events -> existing /loop
// contract. Fetch-only, no cron. Static table lookup only — no reasoning, no
// synthesis, no cross-event correlation (that's the BRAIN node's future job,
// explicitly out of scope here). Reuses the exact same executor contract the
// CF cron fleet worker (noos-loop-fleet-tick-v1) already uses, so Railway
// needs zero changes to accept dispatches from this worker.
import eventMap from "./event-map.json";

const RULES = eventMap.rules || [];

function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: { "Cache-Control": "no-store" },
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

function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

async function verifySignature(secret, rawBody, signatureHeader) {
  if (!secret || !signatureHeader || !signatureHeader.startsWith("sha256=")) {
    return false;
  }
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(rawBody));
  const macHex = [...new Uint8Array(mac)].map((b) => b.toString(16).padStart(2, "0")).join("");
  return timingSafeEqual(`sha256=${macHex}`, signatureHeader);
}

function matchRule(githubEvent, payload) {
  for (const rule of RULES) {
    if (rule.github_event !== githubEvent) continue;
    if (rule.repo && rule.repo !== "*" && payload?.repository?.full_name !== rule.repo) continue;
    if (rule.ref && payload?.ref !== rule.ref) continue;
    if (rule.action && payload?.action !== rule.action) continue;
    if (rule.conclusion && payload?.workflow_run?.conclusion !== rule.conclusion) continue;
    return rule;
  }
  return null;
}

async function forwardToExecutor(env, rule, meta) {
  const { url: base, secret } = executorConfig(env);
  if (!base || !secret) {
    console.error(
      JSON.stringify({
        schema: "noos-loop-github-events-dispatch-v1",
        ok: false,
        error: !base ? "executor_url_missing" : "loop_secret_missing",
        event_type: rule.event_type,
      }),
    );
    return;
  }
  try {
    const resp = await fetch(`${base}/loop`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "User-Agent": "noos-loop-github-events-v1",
        "X-NOOS-Loop-Secret": secret,
      },
      body: JSON.stringify({
        event_type: rule.event_type,
        dispatch_id: rule.dispatch_id,
        handler: rule.handler,
        source: "github_app_webhook",
        at: new Date().toISOString(),
        ...meta,
      }),
    });
    const raw = await resp.text();
    console.log(
      JSON.stringify({
        schema: "noos-loop-github-events-dispatch-v1",
        ok: resp.ok,
        status: resp.status,
        event_type: rule.event_type,
        dispatch_id: rule.dispatch_id,
        body_preview: raw.slice(0, 200),
      }),
    );
  } catch (err) {
    console.error(
      JSON.stringify({
        schema: "noos-loop-github-events-dispatch-v1",
        ok: false,
        event_type: rule.event_type,
        error: String(err && err.stack ? err.stack : err),
      }),
    );
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      const { url: execUrl, secret } = executorConfig(env);
      return json({
        ok: true,
        schema: "noos-loop-github-events-health-v1",
        service: "noos-loop-github-events-v1",
        executor_url_ready: Boolean(execUrl),
        loop_secret_ready: Boolean(secret),
        webhook_secret_ready: Boolean((env.MOTOR_APP_WEBHOOK_SECRET || "").trim()),
        rule_count: RULES.length,
      });
    }

    if (url.pathname === "/webhook/github" && request.method === "POST") {
      const rawBody = await request.text();
      const signature = request.headers.get("X-Hub-Signature-256") || "";
      const webhookSecret = (env.MOTOR_APP_WEBHOOK_SECRET || "").trim();
      const verified = await verifySignature(webhookSecret, rawBody, signature);
      if (!verified) {
        // This IS the security boundary for this worker — no other auth exists
        // on this route (GitHub webhooks carry no bearer token).
        return json({ ok: false, error: "invalid_signature" }, 401);
      }

      const githubEvent = request.headers.get("X-GitHub-Event") || "";
      let payload = null;
      try {
        payload = rawBody ? JSON.parse(rawBody) : null;
      } catch {
        return json({ ok: false, error: "invalid_json" }, 400);
      }

      const rule = matchRule(githubEvent, payload);
      if (!rule) {
        // Always 200 on no-match — GitHub disables a webhook after repeated
        // non-2xx responses, and "no rule configured for this event" is not
        // a delivery failure.
        return json({ ok: true, action: "no_rule_matched", github_event: githubEvent });
      }

      const meta = {
        github_event: githubEvent,
        repo: payload?.repository?.full_name,
        sha: payload?.after || payload?.workflow_run?.head_sha,
      };
      // GitHub expects an ack within ~10s; do the executor POST in the
      // background so this response returns immediately.
      ctx.waitUntil(forwardToExecutor(env, rule, meta));
      return json({ ok: true, action: "dispatched", event_type: rule.event_type });
    }

    return json({ ok: false, error: "not_found" }, 404);
  },
};
