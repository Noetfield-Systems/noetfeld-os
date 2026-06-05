/** Copilot/www paths — same-origin on unified proxy (:13080), else public www origin. */
export function wwwHref(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  if (typeof window !== "undefined") {
    const port = window.location.port;
    if (port === "13080" || port === "") {
      return p;
    }
  }
  const origin = process.env.NEXT_PUBLIC_WWW_ORIGIN ?? "http://127.0.0.1:13080";
  return `${origin.replace(/\/$/, "")}${p}`;
}
