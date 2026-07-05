#!/usr/bin/env node
/** Bundle Pages Functions (handler + adapter) for Cloudflare deploy. */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const API_ROOT = path.join(ROOT, "api");
const FUNCTIONS_ROOT = path.join(ROOT, "functions");
const DIST_FUNCTIONS = path.join(ROOT, "functions");

function walkApiRoutes(dir, base = "") {
  const routes = [];
  for (const name of fs.readdirSync(dir)) {
    if (name === "_lib") continue;
    const full = path.join(dir, name);
    const rel = base ? `${base}/${name}` : name;
    if (fs.statSync(full).isDirectory()) {
      routes.push(...walkApiRoutes(full, rel));
      continue;
    }
    if (!name.endsWith(".js")) continue;
    routes.push(rel.replace(/\\/g, "/"));
  }
  return routes;
}

function functionOutPath(apiRel) {
  const parts = apiRel.split("/");
  if (parts[parts.length - 1] === "index.js") {
    parts.pop();
    const suffix = parts.length ? parts.join("/") : "index";
    return path.join("api", `${suffix}.js`);
  }
  const file = parts.pop().replace(/\.js$/, "");
  return path.join("api", ...parts, `${file}.js`);
}

function entrySource(apiRel) {
  const importPath = `../../api/${apiRel}`.replace(/\\/g, "/");
  return `import { runVercelHandler } from "../../functions/_lib/vercel-adapter.js";
import * as handlerModule from "${importPath}";
const handler = handlerModule.default || handlerModule;
export const onRequest = (context) => runVercelHandler(handler, context);
`;
}

async function bundleEntry({ entryFile, outFile, source }) {
  fs.mkdirSync(path.dirname(entryFile), { recursive: true });
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  fs.writeFileSync(entryFile, source, "utf8");
  await build({
    entryPoints: [entryFile],
    outfile: outFile,
    bundle: true,
    format: "esm",
    platform: "node",
    target: "node18",
    loader: { ".json": "json" },
    logLevel: "silent",
  });
}

function aliasEntrySource(importPath) {
  return `export { onRequest } from "${importPath}";
`;
}

async function main() {
  const routes = walkApiRoutes(API_ROOT);
  const tmpDir = path.join(ROOT, "tmp", "pages-function-entries");
  fs.rmSync(tmpDir, { recursive: true, force: true });
  fs.mkdirSync(tmpDir, { recursive: true });
  fs.rmSync(path.join(DIST_FUNCTIONS, "api"), { recursive: true, force: true });

  const vercel = JSON.parse(fs.readFileSync(path.join(ROOT, "vercel.json"), "utf8"));
  const aliasRoutes = [];
  for (const rule of vercel.rewrites || []) {
    const source = String(rule.source || "").trim().replace(/^\//, "");
    const dest = String(rule.destination || "").trim();
    if (!source || !dest.startsWith("/api/")) continue;
    const apiPath = dest.replace(/^\/api\//, "");
    aliasRoutes.push({ source, apiPath });
  }

  for (const apiRel of routes) {
    const relOut = functionOutPath(apiRel);
    const outFile = path.join(DIST_FUNCTIONS, relOut);
    const entryFile = path.join(tmpDir, relOut.replace(/\//g, "__"));
    await bundleEntry({
      entryFile,
      outFile,
      source: entrySource(apiRel),
    });
  }

  for (const alias of aliasRoutes) {
    const importTarget =
      alias.apiPath === "health"
        ? "./api/health.js"
        : alias.apiPath === "demo/evaluate"
          ? "./api/demo/evaluate.js"
          : `./api/${alias.apiPath}.js`;
    const outFile = path.join(DIST_FUNCTIONS, `${alias.source}.js`);
    fs.writeFileSync(outFile, `export { onRequest } from "${importTarget}";\n`, "utf8");
  }

  console.log(`bundle-pages-functions: wrote ${routes.length} api functions + ${aliasRoutes.length} aliases`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
