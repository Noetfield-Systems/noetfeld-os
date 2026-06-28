/** POST /api/public/chat — proxies platform chat; local fallback only routes intake. */

const CANONICAL_INTAKE = "operations@noetfield.com";

function routeOnlyFallback() {
  return {
    reply:
      "I’m having trouble reaching the live assistant right now. " +
      "If you’re exploring, start with /start/ or /pricing/. If you want to share context, use /trust-brief/intake/ or email " +
      CANONICAL_INTAKE +
      ".",
    citations: ["/start/", "/pricing/", "/trust-brief/intake/"],
  };
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const body = req.body && typeof req.body === "object" ? req.body : {};
  const message = String(body.message || "").trim();
  if (!message) {
    return res.status(400).json({ detail: "message is required" });
  }
  if (message.length > 2000) {
    return res.status(400).json({ detail: "message too long" });
  }

  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  try {
    const r = await fetch(platformBase + "/api/public/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ message: message, session_id: body.session_id || null }),
    });
    if (r.ok) {
      const data = await r.json().catch(function () {
        return null;
      });
      if (data && data.reply) {
        return res.status(200).json(data);
      }
    }
  } catch (_) {
    /* fall through to www-local */
  }

  const picked = routeOnlyFallback();
  return res.status(200).json({
    reply: picked.reply,
    provider: "www-routing-fallback",
    citations: picked.citations,
    intake_email: CANONICAL_INTAKE,
  });
};
