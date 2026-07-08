/** @typedef {{ ok: boolean, probe: string, status: string, reason?: string, receipt: Record<string, unknown> }} ProbeResult */

const PROBE_NAMES = ["uptime", "greeting", "drift", "intake_e2e"];
const TELEGRAM_PASS_ON_SUCCESS = (env) => (env.PROBE_TELEGRAM_PASS || "0").trim() === "1";
const RUN_SUMMARY_PROBE = "_run_summary";
const _notifiedProbeIntakeIds = new Map();

/**
 * @param {string} url
 * @param {RequestInit} [init]
 */
async function fetchJson(url, init = {}) {
  const res = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      "User-Agent": "noetfield-probe-cron/1.0",
      ...(init.headers || {}),
    },
  });
  const text = await res.text();
  let body = {};
  try {
    body = text ? JSON.parse(text) : {};
  } catch {
    body = { detail: text.slice(0, 500) };
  }
  return { status: res.status, body };
}

/**
 * @param {Record<string, string>} env
 * @param {string} table
 * @param {Record<string, unknown>} row
 */
async function supabaseSelect(env, table, query) {
  const base = (env.SUPABASE_URL || "").replace(/\/$/, "");
  const key = env.SUPABASE_SERVICE_ROLE_KEY || "";
  if (!base || !key) {
    return { ok: false, error: "supabase_not_configured", rows: [] };
  }
  const res = await fetch(`${base}/rest/v1/${table}?${query}`, {
    headers: {
      apikey: key,
      Authorization: `Bearer ${key}`,
      Accept: "application/json",
    },
  });
  if (!res.ok) {
    const detail = await res.text();
    return { ok: false, error: `supabase_${res.status}:${detail.slice(0, 200)}`, rows: [] };
  }
  const rows = await res.json().catch(() => []);
  return { ok: true, rows: Array.isArray(rows) ? rows : [] };
}

async function fetchLastRunSummary(env) {
  const query = new URLSearchParams({
    probe_name: `eq.${RUN_SUMMARY_PROBE}`,
    order: "checked_at.desc",
    limit: "1",
    select: "status,receipt,checked_at",
  });
  const result = await supabaseSelect(env, "probe_cron_receipts", query.toString());
  if (!result.ok || !result.rows.length) {
    return { ok: false, lastOk: null, failedProbes: [] };
  }
  const row = result.rows[0];
  const receipt = row.receipt && typeof row.receipt === "object" ? row.receipt : {};
  return {
    ok: true,
    lastOk: row.status === "pass",
    failedProbes: Array.isArray(receipt.failed_probes) ? receipt.failed_probes : [],
    checkedAt: row.checked_at || null,
  };
}

async function saveRunSummary(env, { runId, ok, failedProbes, checkedAt }) {
  return supabaseInsert(env, "probe_cron_receipts", {
    run_id: runId,
    probe_name: RUN_SUMMARY_PROBE,
    status: ok ? "pass" : "fail",
    receipt: {
      ok,
      failed_probes: failedProbes,
      checked_at: checkedAt,
    },
    checked_at: checkedAt,
  });
}

async function supabaseInsert(env, table, row) {
  const base = (env.SUPABASE_URL || "").replace(/\/$/, "");
  const key = env.SUPABASE_SERVICE_ROLE_KEY || "";
  if (!base || !key) {
    return { ok: false, error: "supabase_not_configured" };
  }
  const res = await fetch(`${base}/rest/v1/${table}`, {
    method: "POST",
    headers: {
      apikey: key,
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify(row),
  });
  if (!res.ok) {
    const detail = await res.text();
    return { ok: false, error: `supabase_${res.status}:${detail.slice(0, 200)}` };
  }
  return { ok: true };
}

/**
 * @param {Record<string, string>} env
 * @param {string} text
 */
async function sendTelegram(env, text) {
  const token = env.TELEGRAM_NOETFIELD_OPS_BOT_TOKEN || "";
  const chatId = env.TELEGRAM_OPS_CHAT_ID || "";
  if (!token || !chatId) {
    return { ok: false, error: "telegram_not_configured" };
  }
  const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: text.slice(0, 4096),
      disable_web_page_preview: true,
    }),
  });
  const body = await res.json().catch(() => ({}));
  return { ok: Boolean(body.ok), error: body.description };
}

/**
 * @param {{
 *   pass: boolean,
 *   pipeline: string,
 *   intakeId?: string | null,
 *   timestamp: string,
 *   founderActionRequired: boolean,
 *   receiptPath?: string | null,
 *   supabaseReceiptId?: string | null,
 *   reason?: string | null,
 *   runId?: string | null,
 * }} fields
 */
function formatHealthReceiptTelegram(fields) {
  const lines = [
    `NF ${fields.pass ? "PASS" : "FAIL"} · TEST`,
    `pipeline: ${fields.pipeline}`,
    `intake_id: ${fields.intakeId || "—"}`,
    `at: ${fields.timestamp}`,
    `founder_action: ${fields.founderActionRequired ? "yes" : "no"}`,
  ];
  if (fields.receiptPath) lines.push(`receipt: ${fields.receiptPath}`);
  if (fields.supabaseReceiptId) lines.push(`supabase_receipt: ${fields.supabaseReceiptId}`);
  if (fields.runId) lines.push(`run_id: ${fields.runId}`);
  if (fields.reason) lines.push(`reason: ${fields.reason}`);
  return lines.join("\n");
}

function formatRecoveryTelegram(fields) {
  const lines = [
    "NF RECOVERED · TEST",
    `pipeline: ${fields.pipeline}`,
    `at: ${fields.timestamp}`,
    `previously_failed: ${(fields.previouslyFailed || []).join(", ") || "—"}`,
    `run_id: ${fields.runId}`,
    `receipt: probe_cron_receipts/${fields.runId}`,
  ];
  return lines.join("\n");
}

function wasProbeIntakeNotified(intakeId) {
  if (!intakeId) return false;
  return _notifiedProbeIntakeIds.has(intakeId);
}

function markProbeIntakeNotified(intakeId) {
  if (!intakeId) return;
  _notifiedProbeIntakeIds.set(intakeId, Date.now());
}

function intakeTelegramPathOk(body) {
  if (!body || typeof body !== "object") return false;
  if (body.telegram_delivered) return true;
  return body.intake_kind === "test" && body.telegram_mode === "receipt_only";
}

/**
 * @param {Record<string, string>} env
 * @returns {Promise<ProbeResult>}
 */
export async function probeUptime(env) {
  const wwwBase = (env.WWW_BASE || "https://www.noetfield.com").replace(/\/$/, "");
  const platformBase = (env.PLATFORM_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const receipt = { www: {}, platform: {} };

  const www = await fetchJson(`${wwwBase}/health`);
  receipt.www = { status: www.status, body: www.body };
  const platform = await fetchJson(`${platformBase}/api/public/chat/health`);
  receipt.platform = { status: platform.status, body: platform.body };

  const wwwOk = www.status === 200 && www.body && www.body.status === "ok";
  const platformOk = platform.status === 200;
  const ok = wwwOk && platformOk;
  return {
    ok,
    probe: "uptime",
    status: ok ? "pass" : "fail",
    reason: ok
      ? undefined
      : !wwwOk
        ? "www_health_failed"
        : "platform_health_failed",
    receipt,
  };
}

/**
 * @param {Record<string, string>} env
 * @returns {Promise<ProbeResult>}
 */
export async function probeGreeting(env) {
  const wwwBase = (env.WWW_BASE || "https://www.noetfield.com").replace(/\/$/, "");
  const platformBase = (env.PLATFORM_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const expected = (env.GREETING_SSOT_HASH || "").trim();
  const receipt = { expected_hash: expected || null, platform_hash: null, www_hash: null };

  if (!expected) {
    return {
      ok: false,
      probe: "greeting",
      status: "error",
      reason: "greeting_ssot_hash_missing",
      receipt,
    };
  }

  const platform = await fetchJson(`${platformBase}/api/public/chat/health`);
  const greeting = platform.body && platform.body.greeting_ssot;
  if (greeting && typeof greeting === "object") {
    receipt.platform_hash = greeting.content_hash || null;
  }

  const asset = await fetch(`${wwwBase}/assets/nf-chat-greeting-ssot.js`, {
    headers: { "User-Agent": "noetfield-probe-cron/1.0" },
  });
  const assetText = await asset.text();
  const match = assetText.match(/sha256=([a-f0-9]{64})/);
  receipt.www_hash = match ? match[1] : null;

  const platformOk = receipt.platform_hash === expected;
  const wwwOk = receipt.www_hash === expected;
  const ok = platformOk && wwwOk && asset.status === 200;
  return {
    ok,
    probe: "greeting",
    status: ok ? "pass" : "fail",
    reason: ok
      ? undefined
      : !wwwOk
        ? "www_greeting_hash_mismatch"
        : "platform_greeting_hash_mismatch",
    receipt,
  };
}

/**
 * @param {Record<string, string>} env
 * @returns {Promise<ProbeResult>}
 */
export async function probeDrift(env) {
  const platformBase = (env.PLATFORM_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const expectedSha = (env.EXPECTED_GIT_SHA || "").trim();
  const receipt = { expected_git_sha: expectedSha || null, live_git_sha: null };

  const platform = await fetchJson(`${platformBase}/api/public/chat/health`);
  receipt.live_git_sha = platform.body && platform.body.git_sha ? String(platform.body.git_sha) : null;

  if (!expectedSha) {
    return {
      ok: true,
      probe: "drift",
      status: "pass",
      reason: "expected_git_sha_not_configured",
      receipt,
    };
  }

  const live = receipt.live_git_sha || "";
  const ok = platform.status === 200 && (live === expectedSha || live.startsWith(expectedSha.slice(0, 12)));
  return {
    ok,
    probe: "drift",
    status: ok ? "pass" : "fail",
    reason: ok ? undefined : "platform_git_sha_drift",
    receipt,
  };
}

/**
 * @param {Record<string, string>} env
 * @returns {Promise<ProbeResult>}
 */
export async function probeIntakeE2e(env) {
  const wwwBase = (env.WWW_BASE || "https://www.noetfield.com").replace(/\/$/, "");
  const platformBase = (env.PLATFORM_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const intakeUrl = `${wwwBase}/api/intake`;
  const requestId = `RID-PROBE-${Math.floor(Date.now() / 1000)}`;
  const body = {
    organization: "NF Probe Cron",
    contact_name: "NF Probe Bot",
    contact_email: "probe@noetfield.com",
    message: `Automated intake health probe — ${new Date().toISOString()}`,
    request_id: requestId,
    sku: "general",
    vector: "contact",
    source: "api",
    metadata: {
      form_id: "nf_probe_cron",
      topic: "probe",
      intake_kind: "test",
      pipeline: "probe_cron:intake_e2e",
    },
  };
  const receipt = { request_id: requestId, submit: null, dedupe: null };

  const health = await fetchJson(`${platformBase}/api/intake/health`);
  if (health.status !== 200 || health.body.storage !== "postgres") {
    return {
      ok: false,
      probe: "intake_e2e",
      status: "fail",
      reason: "platform_storage_not_postgres",
      receipt: { ...receipt, health },
    };
  }

  const submit = await fetchJson(intakeUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  receipt.submit = { status: submit.status, body: submit.body };

  const intakeId = submit.body && submit.body.intake_id ? String(submit.body.intake_id) : "";
  receipt.intake_id = intakeId || null;
  const telegramOk = intakeTelegramPathOk(submit.body);
  if (submit.status < 200 || submit.status >= 300 || !intakeId) {
    return {
      ok: false,
      probe: "intake_e2e",
      status: "fail",
      reason: "intake_submit_failed",
      receipt,
    };
  }
  if (!telegramOk) {
    return {
      ok: false,
      probe: "intake_e2e",
      status: "fail",
      reason: "telegram_not_delivered",
      receipt,
    };
  }

  const dedupe = await fetchJson(intakeUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  receipt.dedupe = { status: dedupe.status, intake_id: dedupe.body && dedupe.body.intake_id };
  const dedupeOk =
    dedupe.status >= 200 &&
    dedupe.status < 300 &&
    String((dedupe.body && dedupe.body.intake_id) || "") === intakeId;

  return {
    ok: dedupeOk,
    probe: "intake_e2e",
    status: dedupeOk ? "pass" : "fail",
    reason: dedupeOk ? undefined : "db_dedupe_failed",
    receipt,
  };
}

/** @type {Record<string, (env: Record<string, string>) => Promise<ProbeResult>>} */
export const PROBES = {
  uptime: probeUptime,
  greeting: probeGreeting,
  drift: probeDrift,
  intake_e2e: probeIntakeE2e,
};

export { PROBE_NAMES };

/**
 * @param {Record<string, string>} env
 */
export async function runAllProbes(env) {
  const runId = crypto.randomUUID();
  const checkedAt = new Date().toISOString();
  const results = [];
  const previousSummary = await fetchLastRunSummary(env);

  for (const name of PROBE_NAMES) {
    const fn = PROBES[name];
    let result;
    try {
      result = await fn(env);
    } catch (err) {
      result = {
        ok: false,
        probe: name,
        status: "error",
        reason: err && err.message ? err.message : "probe_error",
        receipt: {},
      };
    }

    await supabaseInsert(env, "probe_cron_receipts", {
      run_id: runId,
      probe_name: name,
      status: result.status,
      receipt: {
        ...result.receipt,
        ok: result.ok,
        reason: result.reason || null,
        pass_definition: name === "intake_e2e" ? "test_intake_path_and_db_dedupe" : null,
        checked_at: checkedAt,
      },
      checked_at: checkedAt,
    });

    if (!result.ok && result.status !== "pass") {
      await supabaseInsert(env, "improvement_queue", {
        finding: result.reason || `${name}_failed`,
        source: `probe_cron:${name}`,
        expected_roi: name === "intake_e2e" ? "ops_intake_reliability" : "www_uptime_visibility",
        machine_safe: name === "drift" || name === "greeting",
        status: "open",
        metadata: { run_id: runId, receipt: result.receipt },
      });
    }

    results.push(result);
  }

  const failures = results.filter((r) => !r.ok);
  const failedProbeNames = failures.map((f) => f.probe);
  const intakeProbe = results.find((r) => r.probe === "intake_e2e");
  const intakeId =
    intakeProbe && intakeProbe.receipt && intakeProbe.receipt.intake_id
      ? String(intakeProbe.receipt.intake_id)
      : "";
  const allOk = failures.length === 0;

  if (failures.length) {
    for (const failure of failures) {
      const pipeline =
        failure.probe === "intake_e2e"
          ? "probe_cron:intake_e2e"
          : `probe_cron:${failure.probe}`;
      const notifyIntakeId = failure.probe === "intake_e2e" ? intakeId : null;
      if (notifyIntakeId && wasProbeIntakeNotified(notifyIntakeId)) {
        continue;
      }
      const text = formatHealthReceiptTelegram({
        pass: false,
        pipeline,
        intakeId: notifyIntakeId,
        timestamp: checkedAt,
        founderActionRequired: true,
        receiptPath: `probe_cron_receipts/${runId}`,
        supabaseReceiptId: runId,
        reason: failure.reason || failure.status,
        runId,
      });
      await sendTelegram(env, text);
      if (notifyIntakeId) markProbeIntakeNotified(notifyIntakeId);
    }
  } else if (previousSummary.ok && previousSummary.lastOk === false) {
    const text = formatRecoveryTelegram({
      pipeline: "probe_cron:all",
      timestamp: checkedAt,
      previouslyFailed: previousSummary.failedProbes,
      runId,
    });
    await sendTelegram(env, text);
  } else if (
    allOk &&
    (env.PROBE_BOOTSTRAP_RECOVERY || "0").trim() === "1"
  ) {
    const text = formatRecoveryTelegram({
      pipeline: "probe_cron:all",
      timestamp: checkedAt,
      previouslyFailed: ["bootstrap_after_pin_fix"],
      runId,
    });
    await sendTelegram(env, text);
  } else if (TELEGRAM_PASS_ON_SUCCESS(env)) {
    const text = formatHealthReceiptTelegram({
      pass: true,
      pipeline: "probe_cron:all",
      intakeId: intakeId || null,
      timestamp: checkedAt,
      founderActionRequired: false,
      receiptPath: `probe_cron_receipts/${runId}`,
      supabaseReceiptId: runId,
      runId,
    });
    await sendTelegram(env, text);
  }

  await saveRunSummary(env, {
    runId,
    ok: allOk,
    failedProbes: failedProbeNames,
    checkedAt,
  });

  return { runId, checkedAt, results, ok: allOk };
}
