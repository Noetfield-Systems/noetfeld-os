/** POST /api/analytics/event — first-party www proxy to platform analytics. */

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
}

module.exports = async function handler(req, res) {
  cors(res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }
  if (req.method !== "POST") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const body = req.body || {};

  try {
    const forwarded = await fetch(platformBase + "/api/analytics/event", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "User-Agent": req.headers["user-agent"] || "noetfield-www-analytics-proxy",
      },
      body: JSON.stringify(body),
    });
    const data = await forwarded.json().catch(function () {
      return {};
    });
    return res.status(forwarded.status).json(data);
  } catch (err) {
    console.error("platform_analytics_forward_failed", err && err.message ? err.message : err);
    return res.status(202).json({ ok: false, queued: false, detail: "Analytics accepted locally" });
  }
};
