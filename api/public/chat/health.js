/** GET /api/public/chat/health — platform proxy when live; www-local FAQ otherwise. */

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  try {
    const r = await fetch(platformBase + "/api/public/chat/health", {
      headers: { Accept: "application/json" },
    });
    if (r.ok) {
      const body = await r.json().catch(function () {
        return {};
      });
      return res.status(200).json({
        ok: true,
        mode: "platform-proxy",
        platform_base: platformBase,
        ...body,
      });
    }
  } catch (_) {
    /* www-local spine */
  }

  return res.status(200).json({
    ok: true,
    mode: "www-local",
    enabled: true,
    configured: true,
    provider: "rule-based",
    active_provider: "www-local",
    detail: "Institutional FAQ assistant on www (LLM proxy when platform spine is live)",
    platform_reachable: false,
  });
};
