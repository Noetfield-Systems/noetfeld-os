import { defineConfig } from "@playwright/test";

/** Headless only — founder law: no visible Chrome windows. */
export default defineConfig({
  testDir: "../playwright",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  use: {
    headless: true,
    launchOptions: {
      args: ["--headless=new"],
    },
  },
});
