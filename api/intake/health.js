/** GET /api/intake/health — platform status + www email delivery readiness. */

const { CANONICAL, emailConfigured } = require("../_lib/intake-email");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");

  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  let platform = {};
  let platformReachable = false;
  try {
    const r = await fetch(platformBase + "/api/intake/health", {
      headers: { Accept: "application/json" },
    });
    if (r.ok) {
      platform = await r.json().catch(function () {
        return {};
      });
      platformReachable = true;
    } else {
      platform = { enabled: false };
    }
  } catch (_) {
    platform = { enabled: false };
  }

  const wwwEmail = emailConfigured();
  const platformEnabled = platform.enabled === true;
  const intakeReady = wwwEmail || platformEnabled || Boolean(platform.ops_email_configured);

  return res.status(200).json({
    enabled: intakeReady,
    intake_email: CANONICAL,
    storage: platform.storage || (wwwEmail ? "www-email" : "www-proxy"),
    ops_webhook_configured: Boolean(platform.ops_webhook_configured),
    ops_email_configured: wwwEmail || Boolean(platform.ops_email_configured),
    www_email_configured: wwwEmail,
    platform_intake_enabled: platformEnabled,
    auto_ack_enabled: (process.env.INTAKE_AUTO_ACK_ENABLED || "true").toLowerCase() !== "false",
    platform_reachable: platformReachable,
    delivery_mode: wwwEmail ? "resend" : platformEnabled ? "platform" : "unconfigured",
  });
};
