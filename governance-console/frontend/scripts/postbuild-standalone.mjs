#!/usr/bin/env node
/** Copy static assets into Next standalone output (required for next start / standalone). */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.dirname(fileURLToPath(import.meta.url));
const frontend = path.join(root, "..");
const standaloneRoot = path.join(frontend, ".next", "standalone", "governance-console", "frontend");

function copyDir(src, dest) {
  if (!fs.existsSync(src)) return;
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const from = path.join(src, entry.name);
    const to = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(from, to);
    else fs.copyFileSync(from, to);
  }
}

if (!fs.existsSync(standaloneRoot)) {
  console.warn("postbuild-standalone: no standalone output — skip");
  process.exit(0);
}

copyDir(path.join(frontend, ".next", "static"), path.join(standaloneRoot, ".next", "static"));
copyDir(path.join(frontend, "public"), path.join(standaloneRoot, "public"));
console.log("postbuild-standalone: copied .next/static and public into standalone bundle");
