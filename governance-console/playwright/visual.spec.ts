import { test, expect } from "@playwright/test";

const BASE = process.env.NF_VISUAL_BASE ?? "http://127.0.0.1:13080";

test.describe("v18 visual smoke", () => {
  test("homepage live proof hero layout", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.goto(`${BASE}/`);
    await expect(page.locator("[data-live-proof-hero]")).toBeVisible();
    await expect(page.getByRole("button", { name: "Evaluate intent" })).toBeVisible();
  });

  test("start trial OS wizard", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 900 });
    await page.goto(`${BASE}/start/`);
    await expect(page.locator("[data-trial-os-flow]")).toBeVisible();
    await expect(page.getByText("Trial OS")).toBeVisible();
  });

  test("receipt studio page", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(`${BASE}/workspace/TLE-015DCFB8B953`);
    await expect(page.getByText("Receipt Studio")).toBeVisible({ timeout: 15000 });
  });
});
