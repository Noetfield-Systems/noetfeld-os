const ORIGIN = (typeof ORIGIN_HOST !== "undefined" ? ORIGIN_HOST : null) || "https://project-gc7lm.vercel.app";

export default {
  async fetch(request, env) {
    const origin = env.ORIGIN || ORIGIN;
    const url = new URL(request.url);
    const target = new URL(url.pathname + url.search, origin);
    const headers = new Headers(request.headers);
    headers.set("Host", new URL(origin).host);
    headers.set("X-Forwarded-Host", url.host);
    headers.set("X-Forwarded-Proto", url.protocol.replace(":", ""));
    const init = {
      method: request.method,
      headers,
      redirect: "manual",
    };
    if (request.method !== "GET" && request.method !== "HEAD") {
      init.body = request.body;
    }
    const res = await fetch(target, init);
    const out = new Response(res.body, res);
    out.headers.set("X-Noetfield-Proxy", "cf-www-proxy");
    return out;
  },
};
