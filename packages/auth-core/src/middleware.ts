import { AUTH_SESSION_CACHE_CONTROL } from "./constants.js";

export type MiddlewareGuardOptions = {
  pathname: string;
  search: string;
  hasSession: boolean;
  isGatedRoute: (pathname: string, searchParams?: URLSearchParams) => boolean;
  signInPath?: string;
  defaultNext?: string;
};

export type MiddlewareGuardResult =
  | { action: "continue"; cacheControl?: string }
  | { action: "redirect"; location: string };

/**
 * SG server law: callers must pass hasSession from getClaims(), not getSession() alone.
 */
export function evaluateAuthGuard(opts: MiddlewareGuardOptions): MiddlewareGuardResult {
  const signIn = opts.signInPath ?? "/auth/sign-in";
  const params = new URLSearchParams(opts.search);

  if (
    !opts.hasSession &&
    opts.isGatedRoute(opts.pathname, params)
  ) {
    const next = `${opts.pathname}${opts.search}`;
    return {
      action: "redirect",
      location: `${signIn}?next=${encodeURIComponent(next)}`,
    };
  }

  if (opts.hasSession && opts.pathname === signIn) {
    const next = params.get("next") || opts.defaultNext || "/";
    return { action: "redirect", location: next };
  }

  return { action: "continue", cacheControl: AUTH_SESSION_CACHE_CONTROL };
}
