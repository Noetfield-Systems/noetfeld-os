/** GET /api/admin/traction — same-origin proxy for protected platform traction summary. */

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Accept, X-Admin-Secret");
}

module.exports = async function handler(req, res) {
  cors(res);

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }
  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const adminSecret = req.headers["x-admin-secret"] || "";
  if (!adminSecret) {
    return res.status(401).json({ detail: "X-Admin-Secret required" });
  }

  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  const days = String(req.query.days || "30").replace(/[^0-9]/g, "") || "30";

  try {
    const forwarded = await fetch(platformBase + "/api/analytics/traction?days=" + encodeURIComponent(days), {
      method: "GET",
      headers: {
        Accept: "application/json",
        "X-Admin-Secret": String(adminSecret),
        "User-Agent": req.headers["user-agent"] || "noetfield-www-admin-traction",
      },
    });
    const data = await forwarded.json().catch(function () {
      return {};
    });
    return res.status(forwarded.status).json(data);
  } catch (err) {
    console.error("platform_traction_forward_failed", err && err.message ? err.message : err);
    return res.status(502).json({ detail: "Traction API unavailable" });
  }
};
