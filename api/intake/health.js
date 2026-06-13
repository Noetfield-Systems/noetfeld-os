/** GET /api/intake/health — platform status + www email delivery readiness. */

const { CANONICAL, emailConfigured } = require("../_lib/intake-email");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");

  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  let platform = {};
  try {
    const r = await fetch(platformBase + "/api/intake/health", {
      headers: { Accept: "application/json" },
    });
    platform = await r.json().catch(function () {
      return {};
    });
  } catch (_) {
    platform = { enabled: false, platform_reachable: false };
  }

  const wwwEmail = emailConfigured();
  return res.status(200).json({
    enabled: platform.enabled !== false,
    intake_email: CANONICAL,
    storage: platform.storage || "www-proxy",
    ops_webhook_configured: Boolean(platform.ops_webhook_configured),
    ops_email_configured: wwwEmail || Boolean(platform.ops_email_configured),
    www_email_configured: wwwEmail,
    auto_ack_enabled: (process.env.INTAKE_AUTO_ACK_ENABLED || "true").toLowerCase() !== "false",
    platform_reachable: platform.enabled !== undefined,
  });
};
