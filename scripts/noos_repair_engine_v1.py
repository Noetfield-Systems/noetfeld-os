#!/usr/bin/env python3
"""NOOS deterministic repair engine v1 (NF-NOOS-SOFTWARE-REPAIR-RUNWAY-V1 §8).

A REAL, bounded, test-verified automated-program-repair engine — NOT a hard-coded
patch. It is the ``provider=deterministic-local`` strategy: honest, offline, and
distinct from a hosted model (which the router calls when a provider key exists).

Method (fault-localized mutation search, the GenProg family):
  1. run the test command; capture the failure;
  2. localize the fault to file:line from the traceback / lint output;
  3. generate a BOUNDED set of candidate single-edits at the localized sites
     (off-by-one, operator/comparison/boolean swaps, unused-import removal);
  4. apply each candidate in an isolated copy and RE-RUN the tests;
  5. keep the first candidate that turns the failing tests green.

Only a candidate that makes real tests pass is proposed. If none does, the engine
returns no patch (truthful failure) — it never fabricates a green.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable


def run_tests(repo_dir: Path, test_cmd: list[str], *, timeout: int = 120) -> dict[str, Any]:
    """Run the test command; return {passed, exit_code, output}."""
    try:
        p = subprocess.run(test_cmd, cwd=str(repo_dir), capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or "") + (p.stderr or "")
        return {"passed": p.returncode == 0, "exit_code": p.returncode, "output": out[-8000:]}
    except subprocess.TimeoutExpired:
        return {"passed": False, "exit_code": 124, "output": "TIMEOUT"}
    except FileNotFoundError as e:
        return {"passed": False, "exit_code": 127, "output": f"command not found: {e}"}


_TRACE_RE = re.compile(r"([\w./\\-]+\.(?:py|js|ts)):(\d+)")


def localize(output: str, repo_dir: Path, allowed_files: list[str]) -> list[tuple[Path, int]]:
    """Extract candidate (file, line) fault sites from test/lint output, filtered
    to allowed source files that exist under repo_dir."""
    sites: list[tuple[Path, int]] = []
    seen = set()
    allowed_abs = {str((repo_dir / f).resolve()) for f in allowed_files}
    for m in _TRACE_RE.finditer(output):
        rel, line = m.group(1), int(m.group(2))
        p = (repo_dir / rel).resolve() if not Path(rel).is_absolute() else Path(rel)
        if not p.is_file():
            continue
        # restrict to allowed source files (never tests/fixtures we shouldn't edit)
        if allowed_abs and str(p) not in allowed_abs:
            continue
        key = (str(p), line)
        if key not in seen:
            seen.add(key)
            sites.append((p, line))
    return sites


# ---- mutation operators (each yields replacement lines for a source line) ---
def _candidate_lines(line: str) -> Iterable[str]:
    """Bounded single-line mutations. Order = most-likely-first."""
    seen = set()

    def emit(s: str):
        if s != line and s not in seen:
            seen.add(s)
            return s
        return None

    # off-by-one on integer literals inside range(...) and bare ints
    for m in re.finditer(r"\b(\d+)\b", line):
        n = int(m.group(1))
        for delta in (1, -1):
            cand = line[: m.start(1)] + str(n + delta) + line[m.end(1):]
            r = emit(cand)
            if r:
                yield r
    # binary operator swaps
    for a, b in [("+", "-"), ("-", "+"), ("*", "/"), ("//", "*"),
                 ("<=", "<"), ("<", "<="), (">=", ">"), (">", ">="),
                 ("==", "!="), ("!=", "=="), (" and ", " or "), (" or ", " and ")]:
        if a in line:
            r = emit(line.replace(a, b, 1))
            if r:
                yield r
    # boolean literal flip
    for a, b in [("True", "False"), ("False", "True")]:
        if a in line:
            r = emit(re.sub(rf"\b{a}\b", b, line, count=1))
            if r:
                yield r
    # off-by-one on a VARIABLE bound: range(1, n) -> range(1, n + 1) (and -1).
    # Handles the classic loop/range regression the literal operators miss.
    # Insert the delta right after the identifier, preserving the closing token.
    for m in re.finditer(r"([A-Za-z_]\w*)(\s*)(\)|:|\])", line):
        for delta in (" + 1", " - 1"):
            cand = line[: m.end(1)] + delta + line[m.end(1):]
            r = emit(cand)
            if r:
                yield r


def _line_removal_candidate(lines: list[str], idx: int) -> list[str]:
    return lines[:idx] + lines[idx + 1:]


def _unused_import_sites(output: str, repo_dir: Path) -> list[tuple[Path, int]]:
    """Ruff/pyflakes F401 'X imported but unused' -> (file, line) to delete."""
    out = []
    for m in re.finditer(r"([\w./\\-]+\.py):(\d+):\d+:\s*F401", output):
        p = (repo_dir / m.group(1)).resolve()
        if p.is_file():
            out.append((p, int(m.group(2))))
    return out


def propose_and_verify_repair(
    *,
    repo_dir: Path,
    test_cmd: list[str],
    allowed_files: list[str],
    max_candidates: int = 60,
    timeout: int = 120,
) -> dict[str, Any]:
    """Return a verified repair (or a truthful no-repair). The returned patch is a
    unified diff that, applied to repo_dir, makes the failing tests pass."""
    before = run_tests(repo_dir, test_cmd, timeout=timeout)
    if before["passed"]:
        return {"repaired": False, "reason": "already_passing", "tests_before": before}

    # An assertion-failure traceback usually names only the TEST file, but the
    # bug lives in the allowed SOURCE files. So the candidate sites are: every
    # line of each allowed source file, with any traceback-referenced lines
    # tried FIRST (fault-localization priority).
    priority: dict[str, set[int]] = {}
    for (p, ln) in localize(before["output"], repo_dir, allowed_files) + _unused_import_sites(before["output"], repo_dir):
        priority.setdefault(str(p), set()).add(ln)

    attempts: list[dict[str, Any]] = []
    tried = 0

    for rel in allowed_files:
        path = (repo_dir / rel).resolve()
        if not path.is_file():
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except OSError:
            continue
        src_lines = original.splitlines(keepends=True)
        n = len(src_lines)
        pset = priority.get(str(path), set())
        # priority lines first, then the rest
        order = sorted(range(1, n + 1), key=lambda ln: (0 if ln in pset else 1, ln))
        for probe in order:
            if tried >= max_candidates:
                break
            idx = probe - 1
            raw = src_lines[idx]
            stripped = raw.rstrip("\n")
            candidates: list[list[str]] = []
            for repl in _candidate_lines(stripped):
                new_lines = src_lines[:idx] + [repl + ("\n" if raw.endswith("\n") else "")] + src_lines[idx + 1:]
                candidates.append(new_lines)
            # line-removal (for unused import lines)
            if "import" in stripped:
                candidates.append(_line_removal_candidate(src_lines, idx))

            for new_lines in candidates:
                if tried >= max_candidates:
                    break
                tried += 1
                ok, after = _try_candidate(repo_dir, path, "".join(new_lines), test_cmd, timeout)
                attempts.append({"file": _rel(path, repo_dir), "line": probe, "passed": ok})
                if ok:
                    new_content = "".join(new_lines)
                    patch = _unified_diff(repo_dir, path, original, new_content)
                    return {
                        "repaired": True,
                        "strategy": "fault_localized_mutation_search",
                        "file": _rel(path, repo_dir),
                        "line": probe,
                        "tests_before": before,
                        "tests_after": after,
                        "patch": patch,
                        "new_content": new_content,  # verified full file — apply directly
                        "candidates_tried": tried,
                        "attempts": attempts[-10:],
                    }
    return {
        "repaired": False,
        "reason": "no_verified_candidate_within_budget",
        "tests_before": before,
        "candidates_tried": tried,
        "attempts": attempts[-10:],
    }


def _try_candidate(repo_dir: Path, path: Path, new_content: str, test_cmd: list[str], timeout: int) -> tuple[bool, dict[str, Any]]:
    """Apply new_content to a temp COPY of repo_dir and run the tests there."""
    with tempfile.TemporaryDirectory(prefix="noos-repair-cand-") as td:
        dst = Path(td) / "repo"
        shutil.copytree(repo_dir, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", "node_modules"))
        rel = path.resolve().relative_to(repo_dir.resolve())
        (dst / rel).write_text(new_content, encoding="utf-8")
        res = run_tests(dst, test_cmd, timeout=timeout)
        return res["passed"], res


def apply_patch_to_repo(repo_dir: Path, path_rel: str, new_content: str) -> None:
    (repo_dir / path_rel).write_text(new_content, encoding="utf-8")


def _rel(path: Path, repo_dir: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_dir.resolve()))
    except ValueError:
        return str(path)


def _unified_diff(repo_dir: Path, path: Path, old: str, new: str) -> str:
    import difflib
    rel = _rel(path, repo_dir)
    diff = difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{rel}", tofile=f"b/{rel}",
    )
    return "".join(diff)
