/** POST /api/public/chat — www-local FAQ assistant until platform spine is live. */

const CANONICAL_INTAKE = "operations@noetfield.com";

const RULES = [
  {
    match: /\b(trust brief|10k|10000|\$10)\b/i,
    reply:
      "Trust Brief is a six-week engagement ($10,000): governance audit, AI policy mapping, and risk exposure analysis. " +
      "Request at /trust-brief/intake/ or email " +
      CANONICAL_INTAKE +
      " with your site Request ID (RID in the footer).",
    citations: ["/trust-brief/intake/"],
  },
  {
    match: /\b(pilot|copilot|governance pack|board pdf|\$2k|\$10k)\b/i,
    reply:
      "Copilot Governance Pack is $2k–10k over 90 days with a board PDF as the success signal. " +
      "Apply at /trust-brief/intake/?interest=pilot&vector=copilot-governance or /copilot/pilot/. " +
      "Operational intake: " +
      CANONICAL_INTAKE +
      ".",
    citations: ["/copilot/pilot/", "/trust-brief/intake/"],
  },
  {
    match: /\b(bank pilot|shadow|simulation)\b/i,
    reply:
      "Bank Pilot is read-only governance simulation (shadow mode) — no execution rights. " +
      "See /copilot/ and apply via /trust-brief/intake/ or " +
      CANONICAL_INTAKE +
      ".",
    citations: ["/copilot/"],
  },
  {
    match: /\b(pric(e|ing)|cost|fee)\b/i,
    reply:
      "Published lanes: Diagnostic Sprint from $2,500 · Copilot Governance Pack $2k–10k · Trust Brief $10,000. " +
      "See /pricing/ and /start/ for paths. Intake: /trust-brief/intake/ · " +
      CANONICAL_INTAKE +
      ".",
    citations: ["/pricing/", "/start/"],
  },
  {
    match: /\b(engage|contact|how do|get started|intake)\b/i,
    reply:
      "Start at /start/ or submit /trust-brief/intake/. All operational intake routes to " +
      CANONICAL_INTAKE +
      " — include your Request ID (RID) from the site footer.",
    citations: ["/start/", "/trust-brief/intake/"],
  },
  {
    match: /\b(what is|who is|noetfield)\b/i,
    reply:
      "Noetfield is governance execution infrastructure for regulated organizations. " +
      "We evaluate AI-driven operational intent before execution, record tamper-evident decision records, and return allow/deny. " +
      "We do not move money, hold custody, or execute transactions on your behalf.",
    citations: ["/", "/governance/"],
  },
];

function pickReply(message) {
  const text = String(message || "").trim();
  if (!text) {
    return {
      reply:
        "Ask about Trust Brief, Copilot Governance Pack, Bank Pilot, pricing, or how to engage. " +
        "Or use /trust-brief/intake/ · " +
        CANONICAL_INTAKE +
        ".",
      citations: ["/trust-brief/intake/"],
    };
  }
  for (const rule of RULES) {
    if (rule.match.test(text)) {
      return { reply: rule.reply, citations: rule.citations || [] };
    }
  }
  return {
    reply:
      "I can help with offerings, pricing, and intake paths on www.noetfield.com. " +
      "For a detailed answer, use /trust-brief/intake/ or email " +
      CANONICAL_INTAKE +
      " with your Request ID.",
    citations: ["/trust-brief/intake/"],
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

  const picked = pickReply(message);
  return res.status(200).json({
    reply: picked.reply,
    provider: "www-local",
    citations: picked.citations,
    intake_email: CANONICAL_INTAKE,
  });
};
