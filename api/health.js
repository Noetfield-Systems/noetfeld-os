/** GET /api/health — lightweight www liveness (production E2E). */

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }
  return res.status(200).json({
    status: "ok",
    service: "noetfield-www",
    surface: "institutional",
  });
};
