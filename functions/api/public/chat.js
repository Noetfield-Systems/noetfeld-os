var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __require = /* @__PURE__ */ ((x) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(x, {
  get: (a, b) => (typeof require !== "undefined" ? require : a)[b]
}) : x)(function(x) {
  if (typeof require !== "undefined") return require.apply(this, arguments);
  throw Error('Dynamic require of "' + x + '" is not supported');
});
var __commonJS = (cb, mod) => function __require2() {
  return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// api/public/chat/index.js
var require_chat = __commonJS({
  "api/public/chat/index.js"(exports, module) {
    var CANONICAL_INTAKE = "operations@noetfield.com";
    var EXECUTIVE_OVERVIEW_REPLY = "Noetfield produces the audit trail a regulated Copilot rollout will be asked for later. For CCO, CRO, CISO, CTO, procurement, and board teams, Noetfield turns each high-risk Microsoft 365 Copilot or AI go/no-go into signed evidence: policy check, confidence score, named approvers, metadata-only M365 evidence index, Trust Ledger Entry, board PDF, and procurement ZIP. The lead paid path is the Copilot Governance Pack ($2k-10k, 90 days): live TLE records, board PDF for a governance meeting, and procurement ZIP for diligence. Trust Brief is the $10k diagnostic when policy mapping comes first. Bank Pilot is read-only shadow governance for regulated institutions. Plain English: we make AI execution impossible to bypass governance.";
    var EXECUTIVE_OVERVIEW_CITATIONS = [
      "/enterprise/",
      "/copilot/pilot/",
      "/copilot/demo/",
      "/trust-brief/intake/?interest=pilot&vector=copilot-governance"
    ];
    function executiveOverviewReply(provider) {
      return {
        reply: EXECUTIVE_OVERVIEW_REPLY,
        provider,
        citations: EXECUTIVE_OVERVIEW_CITATIONS,
        intake_email: CANONICAL_INTAKE
      };
    }
    function isExecutiveOverview(message) {
      const text = String(message || "").toLowerCase();
      return text === "executive overview" || text.includes("help me understand noetfield") || text.includes("what is noetfield") || text.includes("what does noetfield do");
    }
    function isStaleInfrastructureReply(reply) {
      const text = String(reply || "").toLowerCase();
      return text.includes("noetfield provides governance execution infrastructure") || text.includes("record a compliance log") && text.includes("allow or deny decisions") || text.includes("our offerings include the trust brief") && text.includes("support compliance and risk management");
    }
    function isInternalSourceLeakReply(reply) {
      const text = String(reply || "").toLowerCase();
      return text.includes("offerings_locked") || text.includes("product_brief") || text.includes("positioning.md") || text.includes("faq.md") || text.includes("gel-runtime.md") || text.includes("knowledge/") || text.includes("docs/") || text.includes("source:");
    }
    function publicGuidanceReply(provider) {
      return {
        reply: "Before applying, read the public pilot and pricing pages, then choose the intake path that matches your stage. For most teams, start with the Copilot Governance Pack if you need a board-ready governance receipt, or Trust Brief if you need policy mapping first. Next step: use /copilot/pilot/ or /trust-brief/intake/ and include your Request ID if you already have one.",
        provider,
        citations: ["/copilot/pilot/", "/pricing/", "/trust-brief/intake/"],
        intake_email: CANONICAL_INTAKE
      };
    }
    function routeOnlyFallback() {
      return {
        reply: "I\u2019m having trouble reaching the live assistant right now. If you\u2019re exploring, start with /start/ or /pricing/. If you want to share context, use /trust-brief/intake/ or email " + CANONICAL_INTAKE + ".",
        citations: ["/start/", "/pricing/", "/trust-brief/intake/"]
      };
    }
    function localGreetingPayload() {
      try {
        const data = __require("../_lib/greeting-ssot.json");
        const greeting = String(data.greeting || "").trim();
        const citations = Array.isArray(data.citations) ? data.citations : [];
        return {
          greeting,
          citations,
          content_hash: String(data.content_hash || ""),
          source: "www-disk-ssot"
        };
      } catch (_) {
        return {
          greeting: "Hi \u2014 what are you working on?",
          citations: ["/pricing/"],
          source: "www-minimal-fallback"
        };
      }
    }
    async function serveGreeting(res, platformBase) {
      try {
        const r = await fetch(platformBase + "/api/public/chat/greeting", {
          headers: { Accept: "application/json" }
        });
        if (r.ok) {
          const body = await r.json().catch(function() {
            return {};
          });
          if (body && body.greeting) {
            return res.status(200).json({
              ok: true,
              mode: "platform-proxy",
              platform_base: platformBase,
              ...body
            });
          }
        }
      } catch (_) {
      }
      return res.status(200).json({
        ok: true,
        mode: "www-disk-ssot",
        ...localGreetingPayload()
      });
    }
    module.exports = async function handler2(req, res) {
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
      res.setHeader("Access-Control-Allow-Headers", "Content-Type");
      if (req.method === "OPTIONS") {
        return res.status(204).end();
      }
      const platformBase = (process.env.PLATFORM_API_BASE || "https://platform.noetfield.com").replace(/\/$/, "");
      if (req.method === "GET") {
        return serveGreeting(res, platformBase);
      }
      if (req.method !== "POST") {
        return res.status(405).json({ detail: "Method not allowed" });
      }
      const body = req.body && typeof req.body === "object" ? req.body : {};
      const message = String(body.message || "").trim();
      if (!message) {
        return res.status(400).json({ detail: "message is required" });
      }
      if (message.length > 2e3) {
        return res.status(400).json({ detail: "message too long" });
      }
      if (isExecutiveOverview(message)) {
        return res.status(200).json(executiveOverviewReply("www-controlled-executive-overview"));
      }
      try {
        const r = await fetch(platformBase + "/api/public/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ message, session_id: body.session_id || null })
        });
        if (r.ok) {
          const data = await r.json().catch(function() {
            return null;
          });
          if (data && data.reply) {
            if (isStaleInfrastructureReply(data.reply)) {
              return res.status(200).json(executiveOverviewReply("www-stale-platform-guard"));
            }
            if (isInternalSourceLeakReply(data.reply)) {
              return res.status(200).json(publicGuidanceReply("www-source-leak-guard"));
            }
            return res.status(200).json(data);
          }
        }
      } catch (_) {
      }
      const picked = routeOnlyFallback();
      return res.status(200).json({
        reply: picked.reply,
        provider: "www-routing-fallback",
        citations: picked.citations,
        intake_email: CANONICAL_INTAKE
      });
    };
  }
});

// functions/_lib/vercel-adapter.js
function headersToObject(request) {
  const out = {};
  request.headers.forEach((value, key) => {
    out[key] = value;
  });
  return out;
}
function createRes() {
  let statusCode = 200;
  const headers = {};
  let settled = null;
  const res = {
    status(code) {
      statusCode = code;
      return res;
    },
    setHeader(key, value) {
      headers[key] = value;
      return res;
    },
    json(data) {
      headers["content-type"] = headers["content-type"] || "application/json;charset=UTF-8";
      settled = new Response(JSON.stringify(data), { status: statusCode, headers });
      return settled;
    },
    end(body) {
      settled = new Response(body == null ? null : String(body), { status: statusCode, headers });
      return settled;
    },
    _response() {
      return settled;
    }
  };
  return res;
}
async function readBody(request) {
  if (request.method === "GET" || request.method === "HEAD" || request.method === "OPTIONS") {
    return {};
  }
  const contentType = request.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      return await request.json();
    } catch (_) {
      return {};
    }
  }
  const text = await request.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch (_) {
    return { raw: text };
  }
}
function bindEnv(env) {
  const base = typeof process !== "undefined" && process.env ? { ...process.env } : {};
  for (const [key, value] of Object.entries(env || {})) {
    if (value != null) base[key] = String(value);
  }
  if (typeof process !== "undefined") {
    process.env = base;
  }
  return base;
}
async function runVercelHandler(handler2, context) {
  const { request, env } = context;
  bindEnv(env);
  const url = new URL(request.url);
  const req = {
    method: request.method,
    url: url.pathname + url.search,
    headers: headersToObject(request),
    body: await readBody(request)
  };
  const res = createRes();
  const result = await handler2(req, res);
  if (result instanceof Response) return result;
  const fromRes = res._response();
  if (fromRes instanceof Response) return fromRes;
  return new Response(JSON.stringify({ detail: "handler did not send a response" }), {
    status: 500,
    headers: { "content-type": "application/json" }
  });
}

// tmp/pages-function-entries/api__public__chat.js
var handlerModule = __toESM(require_chat());
var handler = handlerModule.default || handlerModule;
var onRequest = (context) => runVercelHandler(handler, context);
export {
  onRequest
};
