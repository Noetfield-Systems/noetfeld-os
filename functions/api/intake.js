var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __commonJS = (cb, mod) => function __require() {
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

// api/_lib/intake-email.js
var require_intake_email = __commonJS({
  "api/_lib/intake-email.js"(exports, module) {
    var CANONICAL = "operations@noetfield.com";
    function meta(body) {
      return body && typeof body.metadata === "object" && body.metadata ? body.metadata : {};
    }
    function intakeLabel(body) {
      const m = meta(body);
      const vector = String(body.vector || "").toLowerCase();
      const topic = String(m.topic || m.role || m.program_lane || "").toLowerCase();
      const sku = String(body.sku || "").toLowerCase();
      const formId = String(m.form_id || "").toLowerCase();
      if (vector.indexOf("sandbox") >= 0 || formId === "nfsandboxform" || formId === "nftrialaccountform") {
        return "Sandbox signup";
      }
      if (vector === "investor-diligence" || topic === "investor-diligence") {
        return "Investor diligence vault";
      }
      if (topic === "investor" || vector === "work-with-us" && topic === "investor") {
        return "Investor brief";
      }
      if (vector === "work-with-us" || ["connector", "facilitator", "co-partner", "partner"].indexOf(topic) >= 0) {
        return "Work with Noetfield application";
      }
      if (vector.indexOf("copilot") >= 0 || sku === "copilot" || topic === "pilot") {
        return "Governance Pack apply";
      }
      if (vector.indexOf("trust") >= 0 || sku === "trust_brief" || topic === "trust-brief") {
        return "Trust Brief Intake";
      }
      if (vector.indexOf("bank") >= 0 || sku === "bank_pilot" || topic === "bank-pilot") {
        return "Bank Pilot inquiry";
      }
      if (topic === "federal") return "Federal Brief";
      if (topic === "feedback") return "Site feedback";
      if (topic === "partner") return "Partner program";
      if (vector === "contact" && topic) return "Contact \u2014 " + topic;
      if (vector === "contact") return "Contact";
      return "Intake";
    }
    function metaLine(body) {
      const m = meta(body);
      const parts = [];
      const lane = m.program_lane || m.buyer_role || m.role || "";
      const topic = m.topic || "";
      if (lane) parts.push("lane/role: " + lane);
      if (topic && topic !== lane) parts.push("topic: " + topic);
      if (m.pilot_band) parts.push("pilot_band: " + m.pilot_band);
      if (m.engagement) parts.push("engagement: " + m.engagement);
      if (m.page) parts.push("page: " + m.page);
      if (m.form_id) parts.push("form: " + m.form_id);
      if (m.async) parts.push("async web submit");
      return parts.join(" \xB7 ");
    }
    function intakeSubject(body, intakeId) {
      const rid = body.request_id || intakeId;
      const label = intakeLabel(body);
      const vector = String(body.vector || "").trim();
      if (vector && label.indexOf("[vector:") < 0) {
        return "[vector:" + vector + "] Noetfield \u2014 " + label + " (" + rid + ")";
      }
      return "Noetfield \u2014 " + label + " (" + rid + ")";
    }
    function opsBodyText(body, intakeId) {
      const m = meta(body);
      const ctx = metaLine(body);
      const lines = [
        "New Noetfield intake \u2014 REPLY to this email to reach the submitter.",
        "",
        "Intake ID: " + intakeId,
        "RID: " + (body.request_id || "\u2014"),
        "Organization: " + (body.organization || "\u2014"),
        "Contact: " + (body.contact_name || "\u2014") + " <" + (body.contact_email || "\u2014") + ">",
        "SKU: " + (body.sku || "\u2014"),
        "Vector: " + (body.vector || "\u2014"),
        "Source: " + (body.source || "web")
      ];
      if (ctx) lines.push("Context: " + ctx);
      lines.push("", "Message:", String(body.message || "").trim(), "");
      return lines.join("\n");
    }
    function ackBody(body, intakeId) {
      const name = body.contact_name ? " " + body.contact_name : "";
      const rid = body.request_id || intakeId;
      return "Hi" + name + ",\n\nYour message was saved instantly. Operations at Noetfield will follow up within one business day.\n\nReference: " + rid + "\nIntake ID: " + intakeId + "\n\nReply to this email or write " + CANONICAL + " \u2014 include your Request ID in any follow-up.\n\n\u2014 Noetfield Operations\n" + CANONICAL + "\n";
    }
    async function sendResend({ from, to, subject, text, replyTo }) {
      const key = (process.env.RESEND_API_KEY || "").trim();
      if (!key) return { ok: false, error: "missing_api_key" };
      const payload = { from, to, subject, text };
      if (replyTo) payload.reply_to = replyTo;
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + key
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) return { ok: true };
      const errBody = await res.text().catch(function() {
        return "";
      });
      console.error("resend_send_failed", res.status, errBody.slice(0, 500));
      return { ok: false, error: errBody.slice(0, 200) };
    }
    function emailConfigured() {
      return Boolean((process.env.RESEND_API_KEY || "").trim());
    }
    async function sendIntakeEmails(body, ids) {
      const intakeId = ids.intakeId;
      const from = (process.env.INTAKE_EMAIL_FROM || "").trim() || "Noetfield Intake <notifications@noetfield.com>";
      const inbox = (process.env.INTAKE_EMAIL_TO || CANONICAL).trim();
      const autoAck = (process.env.INTAKE_AUTO_ACK_ENABLED || "true").toLowerCase() !== "false";
      if (!emailConfigured()) {
        return { ops: false, ack: false, configured: false };
      }
      if (!body.contact_email || String(body.contact_email).indexOf("@") < 1) {
        return { ops: false, ack: false, configured: true };
      }
      const opsResult = await sendResend({
        from,
        to: [inbox],
        subject: intakeSubject(body, intakeId),
        text: opsBodyText(body, intakeId),
        replyTo: body.contact_email
      });
      const ops = opsResult.ok;
      let ack = false;
      if (autoAck && ops) {
        const ackResult = await sendResend({
          from,
          to: [body.contact_email],
          subject: "Noetfield \u2014 message received (" + (body.request_id || intakeId) + ")",
          text: ackBody(body, intakeId),
          replyTo: CANONICAL
        });
        ack = ackResult.ok;
      }
      return { ops, ack, configured: true, resend_error: ops ? null : opsResult.error || null };
    }
    module.exports = {
      CANONICAL,
      emailConfigured,
      intakeLabel,
      intakeSubject,
      opsBodyText,
      sendIntakeEmails
    };
  }
});

// api/intake.js
var require_intake = __commonJS({
  "api/intake.js"(exports, module) {
    var { CANONICAL, emailConfigured, sendIntakeEmails, opsBodyText } = require_intake_email();
    function randomIntakeId() {
      const hex = Array.from({ length: 12 }, function() {
        return Math.floor(Math.random() * 16).toString(16);
      }).join("");
      return "INT-" + hex.toUpperCase();
    }
    function cors(res) {
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
      res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept");
    }
    module.exports = async function handler2(req, res) {
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
          body: JSON.stringify(body)
        });
        platformData = await forward.json().catch(function() {
          return {};
        });
        platformOk = forward.ok;
      } catch (err) {
        console.error("platform_intake_forward_failed", err && err.message ? err.message : err);
      }
      const intakeId = platformData && platformData.intake_id || randomIntakeId();
      let emailResult = { ops: false, ack: false, configured: emailConfigured() };
      try {
        emailResult = await sendIntakeEmails(body, { intakeId, rid: body.request_id || null });
      } catch (err) {
        console.error("intake_email_failed", err && err.message ? err.message : err);
      }
      if (platformOk && platformData) {
        return res.status(200).json({
          ...platformData,
          email_delivered: emailResult.ops,
          email_ack: emailResult.ack
        });
      }
      if (emailResult.ops) {
        return res.status(200).json({
          intake_id: intakeId,
          request_id: body.request_id || null,
          message: "Intake recorded \u2014 operations notified by email",
          email_delivered: true,
          email_ack: emailResult.ack
        });
      }
      const mailSubject = "[vector:" + (body.vector || "web-intake") + "] Noetfield \u2014 Intake fallback (" + intakeId + ")";
      const mailBody = opsBodyText(body, intakeId);
      return res.status(502).json({
        detail: "Intake unavailable \u2014 email not configured. Use /contact/ or email operations@noetfield.com with your Request ID.",
        intake_id: intakeId,
        mailto: "mailto:" + CANONICAL + "?subject=" + encodeURIComponent(mailSubject) + "&body=" + encodeURIComponent(mailBody),
        www_email_configured: emailResult.configured
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

// tmp/pages-function-entries/api__intake.js
var handlerModule = __toESM(require_intake());
var handler = handlerModule.default || handlerModule;
var onRequest = (context) => runVercelHandler(handler, context);
export {
  onRequest
};
