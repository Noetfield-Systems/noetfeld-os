/** Same-origin console URL when on unified proxy (:13080). */
export function platformConsoleHref(): string {
  if (typeof window !== "undefined") {
    const port = window.location.port;
    if (port === "13080" || port === "") {
      return `${window.location.origin}/console`;
    }
  }
  const env = process.env.NEXT_PUBLIC_PLATFORM_CONSOLE_URL;
  if (env) return env;
  const p = process.env.NEXT_PUBLIC_PLATFORM_CONSOLE_PORT ?? "8001";
  return `http://127.0.0.1:${p}/console`;
}
