import { createBrowserClient as ssrBrowserClient } from "@supabase/ssr";
import { createServerClient as ssrServerClient } from "@supabase/ssr";

export type CookieStore = {
  getAll(): { name: string; value: string }[];
  set(name: string, value: string, options?: Record<string, unknown>): void;
};

export type BrowserClientOptions = {
  url: string;
  anonKey: string;
};

export type ServerClientOptions = BrowserClientOptions & {
  cookies: CookieStore;
};

type CookieToSet = { name: string; value: string; options?: Record<string, unknown> };

/** Browser Supabase client — PKCE flow, persist session. */
export function createBrowserClient(opts: BrowserClientOptions) {
  return ssrBrowserClient(opts.url, opts.anonKey);
}

/** Server Supabase client with cookie adapter for Next.js / SSR frameworks. */
export function createServerClient(opts: ServerClientOptions) {
  return ssrServerClient(opts.url, opts.anonKey, {
    cookies: {
      getAll() {
        return opts.cookies.getAll();
      },
      setAll(cookiesToSet: CookieToSet[]) {
        cookiesToSet.forEach(({ name, value, options }) => {
          opts.cookies.set(name, value, options);
        });
      },
    },
  });
}
