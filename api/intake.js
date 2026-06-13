/** POST /api/intake — forward to platform + deliver to operations inbox (Resend). */

const { emailConfigured, sendIntakeEmails } = require("./_lib/intake-email");

function randomIntakeId() {
  const hex = Array.from({ length: 12 }, function () {
    return Math.floor(Math.random() * 16).toString(16);
  }).join("");
  return "INT-" + hex.toUpperCase();
}

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

  const body = req.body || {};
  const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
  let platformData = null;
  let platformOk = false;

  try {
    const forward = await fetch(platformBase + "/api/intake", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    });
    platformData = await forward.json().catch(function () {
      return {};
    });
    platformOk = forward.ok;
  } catch (err) {
    console.error("platform_intake_forward_failed", err && err.message ? err.message : err);
  }

  const intakeId = (platformData && platformData.intake_id) || randomIntakeId();
  let emailResult = { ops: false, ack: false, configured: emailConfigured() };

  try {
    emailResult = await sendIntakeEmails(body, { intakeId: intakeId, rid: body.request_id || null });
  } catch (err) {
    console.error("intake_email_failed", err && err.message ? err.message : err);
  }

  if (platformOk && platformData) {
    return res.status(200).json(platformData);
  }
  if (emailResult.ops) {
    return res.status(200).json({
      intake_id: intakeId,
      request_id: body.request_id || null,
      message: "Intake recorded — operations notified by email",
    });
  }

  return res.status(502).json({
    detail:
      "Intake unavailable. Use /contact/ or email operations@noetfield.com with your Request ID.",
  });
};
