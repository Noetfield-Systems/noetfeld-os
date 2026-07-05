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

// assets/noetfield-ecosystem.json
var require_noetfield_ecosystem = __commonJS({
  "assets/noetfield-ecosystem.json"(exports, module) {
    module.exports = {
      version: "1",
      intake_email: "operations@noetfield.com",
      intake_url: "https://www.noetfield.com/trust-brief/intake/",
      chat_api_base: "https://platform.noetfield.com",
      telegram_bot_username: "",
      channels: {
        website_chat: true,
        telegram: false,
        email: true
      }
    };
  }
});

// api/ecosystem/public.js
var require_public = __commonJS({
  "api/ecosystem/public.js"(exports, module) {
    var ecosystem = require_noetfield_ecosystem();
    module.exports = async function handler2(req, res) {
      res.setHeader("Access-Control-Allow-Origin", "*");
      if (req.method !== "GET") {
        return res.status(405).json({ detail: "Method not allowed" });
      }
      try {
        const data = { ...ecosystem };
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
          channels: { website_chat: true, telegram: false, email: true }
        });
      }
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

// tmp/pages-function-entries/api__ecosystem__public.js
var handlerModule = __toESM(require_public());
var handler = handlerModule.default || handlerModule;
var onRequest = (context) => runVercelHandler(handler, context);
export {
  onRequest
};
