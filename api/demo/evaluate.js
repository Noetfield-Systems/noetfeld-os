/** POST /api/demo/evaluate — pre-execution evaluate for Copilot governance demo. */

const { evaluateIntent } = require("../_lib/governance-evaluate");

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, X-Tenant-ID");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ detail: "Method not allowed" });
  }

  const body = req.body && typeof req.body === "object" ? req.body : {};
  const result = evaluateIntent({
    actor: body.actor,
    action: body.action,
    context: body.context,
    metadata: {
      ...(body.metadata || {}),
      tenant_id: req.headers["x-tenant-id"] || (body.metadata && body.metadata.tenant_id),
    },
  });

  if (result.error === "re_brief_required") {
    return res.status(409).json(result);
  }

  return res.status(200).json(result);
};
