import type { AuthRoutePath } from "./types.js";

/** Canonical auth routes — SG auth_core_interface_spec_v1. */
export const REQUIRED_AUTH_ROUTES: readonly AuthRoutePath[] = [
  "/auth/sign-in",
  "/auth/sign-up",
  "/auth/callback",
  "/auth/sign-out",
] as const;

export const AUTH_SESSION_CACHE_CONTROL = "private, no-store";

export const REDIRECT_CALLBACKS = [
  "https://sourcea.app/auth/callback",
  "https://www.noetfield.com/auth/callback",
  "https://www.trustfield.ca/auth/callback",
  "http://localhost:3000/auth/callback",
] as const;
