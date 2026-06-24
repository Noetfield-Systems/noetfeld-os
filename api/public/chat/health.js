/** GET /api/public/chat/health — www stub until platform spine is fully live. */

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
    const body = await r.json().catch(function () {
      return { ok: false, detail: "invalid_json" };
    });
    return res.status(r.status).json(body);
  } catch (_) {
    return res.status(200).json({
      ok: false,
      mode: "www-stub",
      detail: "platform spine unreachable — chat disabled on institutional www",
      platform_base: platformBase,
    });
  }
};
