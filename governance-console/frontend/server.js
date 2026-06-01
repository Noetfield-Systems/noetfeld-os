#!/usr/bin/env node
/** Dev launcher: port 3010, bind all interfaces, open cognitive-dashboard. */
const { spawn } = require("child_process");
const http = require("http");

const port = process.env.PORT || process.env.COGNITIVE_DASHBOARD_PORT || "3010";
const host = "0.0.0.0";
const url = `http://localhost:${port}/cognitive-dashboard`;

const child = spawn(
  process.platform === "win32" ? "npx.cmd" : "npx",
  ["next", "dev", "--port", port, "--hostname", host],
  { stdio: "inherit", env: process.env, shell: process.platform === "win32" },
);

function waitReady(tries = 60) {
  if (tries <= 0) return;
  const req = http.get(url, (res) => {
    if (res.statusCode && res.statusCode < 500) {
      const open =
        process.platform === "darwin"
          ? spawn("open", [url], { stdio: "ignore", detached: true })
          : process.platform === "win32"
            ? spawn("cmd", ["/c", "start", "", url], { stdio: "ignore", detached: true })
            : null;
      open?.unref();
    } else {
      setTimeout(() => waitReady(tries - 1), 1000);
    }
  });
  req.on("error", () => setTimeout(() => waitReady(tries - 1), 1000));
  req.end();
}

setTimeout(() => waitReady(), 2000);

child.on("exit", (code) => process.exit(code ?? 0));
process.on("SIGINT", () => child.kill("SIGINT"));
process.on("SIGTERM", () => child.kill("SIGTERM"));
