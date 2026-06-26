/** GET /api/ecosystem/public — safe www config (mirrors assets/noetfield-ecosystem.json). */

const fs = require("fs");
const path = require("path");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "GET") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const jsonPath = path.join(process.cwd(), "assets", "noetfield-ecosystem.json");
  try {
    const raw = fs.readFileSync(jsonPath, "utf8");
    const data = JSON.parse(raw);
    if (!data.chat_api_base || data.chat_api_base.indexOf("platform.noetfield.com") >= 0) {
      data.chat_api_base = "";
    }
    return res.status(200).json(data);
  } catch (_) {
    return res.status(200).json({
      version: "1",
      intake_email: "operations@noetfield.com",
      intake_url: "https://www.noetfield.com/trust-brief/intake/",
      chat_api_base: "",
      channels: { website_chat: true, telegram: false, email: true },
    });
  }
};
