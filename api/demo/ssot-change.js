/** POST /api/demo/ssot-change — SSOT_CHANGED → invalidate stale evaluations + re-brief queue. */

const { applySsotChange } = require("../_lib/governance-evaluate");

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
  const result = applySsotChange({
    fromVersion: body.from_version || body.fromVersion || "3.1",
    toVersion: body.to_version || body.toVersion || "3.2",
    pending: body.pending,
  });

  return res.status(200).json(result);
};
