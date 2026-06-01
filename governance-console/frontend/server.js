#!/usr/bin/env node
const { spawn } = require("child_process");

const port =
  process.env.PORT ||
  process.env.COGNITIVE_DASHBOARD_PORT ||
  process.env.NF_DEV_WEB_PORT ||
  "13000";

const child = spawn(
  process.platform === "win32" ? "npx.cmd" : "npx",
  ["next", "dev", "--port", String(port), "--hostname", "0.0.0.0"],
  {
    stdio: "inherit",
    env: { ...process.env, PORT: String(port), NEXT_PUBLIC_WEB_PORT: String(port) },
    shell: process.platform === "win32",
  },
);

child.on("exit", (code) => process.exit(code ?? 0));
process.on("SIGINT", () => child.kill("SIGINT"));
process.on("SIGTERM", () => child.kill("SIGTERM"));
