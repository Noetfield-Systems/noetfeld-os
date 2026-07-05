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

// api/_lib/ai-factory-core.js
var require_ai_factory_core = __commonJS({
  "api/_lib/ai-factory-core.js"(exports, module) {
    function hash(value) {
      const s = JSON.stringify(value);
      let h = 2166136261;
      for (let i = 0; i < s.length; i++) {
        h ^= s.charCodeAt(i);
        h = Math.imul(h, 16777619);
      }
      return (h >>> 0).toString(16).padStart(8, "0");
    }
    function randomId() {
      if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") {
        return globalThis.crypto.randomUUID();
      }
      return "req-" + hash({ t: Date.now(), r: Math.random() });
    }
    function validateGateRequest(payload) {
      const errors = [];
      for (const field of ["factory_type", "target_user", "output_format", "payload"]) {
        if (payload[field] === void 0 || payload[field] === null || payload[field] === "") {
          errors.push({ field, code: "required", message: `${field} is required` });
        }
      }
      if (payload.payload !== void 0 && (typeof payload.payload !== "object" || Array.isArray(payload.payload))) {
        errors.push({ field: "payload", code: "invalid_type", message: "payload must be a JSON object" });
      }
      return errors;
    }
    function policyDecision(payload) {
      const serialized = JSON.stringify(payload).toLowerCase();
      if (serialized.includes("prohibited") || serialized.includes("bypass")) return "BLOCK";
      if (serialized.includes("regulated") || serialized.includes("msb") || serialized.includes("compliance")) return "ESCALATE";
      return "ALLOW";
    }
    function buildFactoryReceipt(payload) {
      const requestId = payload.request_id || randomId();
      const normalized = {
        request_id: requestId,
        user_id: payload.user_id || "anonymous",
        factory_type: payload.factory_type,
        target_user: payload.target_user,
        output_format: payload.output_format,
        payload: payload.payload || {},
        policy_mode: payload.policy_mode || "ALLOW / BLOCK / ESCALATE"
      };
      const decision = policyDecision(normalized);
      const statusRecord = {
        request_id: requestId,
        request_type: "AI Factory",
        lane: decision === "BLOCK" ? "validation" : "intake",
        next_action: decision === "BLOCK" ? "Revise request scope before design" : "Review generated Factory Spec",
        policy_decision: decision,
        current_node: "receive_request",
        audit_state: "minimal_receipt_created",
        terminal_state: null
      };
      const receipt = {
        request_id: requestId,
        gate_lane: "AI Factory Design",
        status: decision === "BLOCK" ? "partial" : "accepted",
        status_record: statusRecord,
        factory_spec_ref: "/ai-factories/spec/",
        audit: {
          request_id: requestId,
          input_hash: hash(normalized),
          policy_decision: decision,
          execution_trace: ["receive_request", "validate_input", "assign_gate_lane", "create_status_record", "write_minimal_audit_receipt"],
          stateless: true,
          storage: "none_in_runtime",
          created_at: (/* @__PURE__ */ new Date()).toISOString()
        },
        adapters: {
          status: { configured: false },
          trust_ledger: { configured: false }
        }
      };
      receipt.audit.final_output_hash = hash(receipt);
      return receipt;
    }
    function buildStatusPreview(requestId) {
      const lanes = ["intake", "design", "spec_review", "validation", "deployment", "ledger_complete"];
      const digest = hash(requestId);
      const lane = lanes[digest.charCodeAt(0) % lanes.length];
      return {
        request_id: requestId,
        request_type: "AI Factory",
        lane,
        policy_decision: digest.charCodeAt(1) % 5 === 0 ? "ESCALATE" : "ALLOW",
        current_node: lane === "ledger_complete" ? "write_audit_record" : "create_execution_plan",
        audit_state: lane === "ledger_complete" ? "ledger_ready" : "in_progress",
        next_action: lane === "ledger_complete" ? "Review Trust Ledger receipt" : "Continue factory design review",
        stateless_preview: true
      };
    }
    module.exports = { buildFactoryReceipt, buildStatusPreview, validateGateRequest };
  }
});

// api/status/ai-factory.js
var require_ai_factory = __commonJS({
  "api/status/ai-factory.js"(exports, module) {
    var { buildStatusPreview } = require_ai_factory_core();
    module.exports = async function handler2(req, res) {
      res.setHeader("Access-Control-Allow-Origin", "*");
      if (req.method !== "GET") return res.status(405).json({ detail: "Method not allowed" });
      const requestId = req.query && req.query.request_id;
      if (!requestId) {
        return res.status(400).json({ status: "failed", errors: [{ field: "request_id", code: "required", message: "request_id is required" }] });
      }
      return res.status(200).json(buildStatusPreview(requestId));
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

// tmp/pages-function-entries/api__status__ai-factory.js
var handlerModule = __toESM(require_ai_factory());
var handler = handlerModule.default || handlerModule;
var onRequest = (context) => runVercelHandler(handler, context);
export {
  onRequest
};
