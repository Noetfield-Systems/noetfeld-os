import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { evaluateAuthGuard } from "../dist/middleware.js";

function isGated(pathname: string): boolean {
  return pathname === "/partner-access" || pathname.startsWith("/partner-access/platform");
}

describe("evaluateAuthGuard", () => {
  it("redirects unauthenticated users on gated routes", () => {
    const result = evaluateAuthGuard({
      pathname: "/partner-access",
      search: "",
      hasSession: false,
      isGatedRoute: isGated,
    });
    assert.equal(result.action, "redirect");
    if (result.action === "redirect") {
      assert.ok(result.location.includes("/auth/sign-in"));
      assert.ok(result.location.includes("next=%2Fpartner-access"));
    }
  });

  it("allows public routes without session", () => {
    const result = evaluateAuthGuard({
      pathname: "/",
      search: "",
      hasSession: false,
      isGatedRoute: isGated,
    });
    assert.equal(result.action, "continue");
  });

  it("redirects signed-in users away from sign-in", () => {
    const result = evaluateAuthGuard({
      pathname: "/auth/sign-in",
      search: "?next=/partner-access/platform",
      hasSession: true,
      isGatedRoute: isGated,
      defaultNext: "/partner-access/platform",
    });
    assert.equal(result.action, "redirect");
    if (result.action === "redirect") {
      assert.equal(result.location, "/partner-access/platform");
    }
  });
});
