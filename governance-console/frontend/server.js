#!/usr/bin/env node
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const port =
  process.env.PORT ||
  process.env.COGNITIVE_DASHBOARD_PORT ||
  process.env.NF_DEV_WEB_PORT ||
  "13000";

const mode = (process.env.NF_DASHBOARD_MODE || "production").toLowerCase();
const hasBuild = fs.existsSync(path.join(__dirname, ".next", "BUILD_ID"));
const standaloneCandidates = [
  path.join(__dirname, ".next", "standalone", "server.js"),
  path.join(__dirname, ".next", "standalone", "governance-console", "frontend", "server.js"),
];
const standaloneServer = standaloneCandidates.find((p) => fs.existsSync(p));
const useProduction = mode === "production" && hasBuild;

function runNode(script, args, label) {
  console.log(`>>> Governance UI: ${label} on :${port}`);
  const child = spawn(process.execPath, [script, ...args], {
    stdio: "inherit",
    env: {
      ...process.env,
      PORT: String(port),
      HOSTNAME: "0.0.0.0",
      NEXT_PUBLIC_WEB_PORT: String(port),
    },
    cwd: path.dirname(script) === __dirname ? __dirname : path.dirname(script),
  });
  child.on("exit", (code) => process.exit(code ?? 0));
  process.on("SIGINT", () => child.kill("SIGINT"));
  process.on("SIGTERM", () => child.kill("SIGTERM"));
}

if (useProduction && standaloneServer) {
  runNode(standaloneServer, [], "production (standalone)");
} else if (useProduction) {
  const bin = process.platform === "win32" ? "npx.cmd" : "npx";
  console.log(`>>> Governance UI: production (next start) on :${port}`);
  const child = spawn(bin, ["next", "start", "-p", String(port), "-H", "0.0.0.0"], {
    stdio: "inherit",
    env: { ...process.env, PORT: String(port), NEXT_PUBLIC_WEB_PORT: String(port) },
    shell: process.platform === "win32",
  });
  child.on("exit", (code) => process.exit(code ?? 0));
  process.on("SIGINT", () => child.kill("SIGINT"));
  process.on("SIGTERM", () => child.kill("SIGTERM"));
} else {
  if (mode === "production" && !hasBuild) {
    console.warn(">>> WARN: NF_DASHBOARD_MODE=production but no .next build — using next dev");
    console.warn(">>> Run: cd governance-console/frontend && npm run build");
  }
  const bin = process.platform === "win32" ? "npx.cmd" : "npx";
  console.log(`>>> Governance UI: dev (next dev) on :${port} — set NF_DASHBOARD_MODE=production for pro mode`);
  const child = spawn(bin, ["next", "dev", "--port", String(port), "--hostname", "0.0.0.0"], {
    stdio: "inherit",
    env: { ...process.env, PORT: String(port), NEXT_PUBLIC_WEB_PORT: String(port) },
    shell: process.platform === "win32",
  });
  child.on("exit", (code) => process.exit(code ?? 0));
  process.on("SIGINT", () => child.kill("SIGINT"));
  process.on("SIGTERM", () => child.kill("SIGTERM"));
}
