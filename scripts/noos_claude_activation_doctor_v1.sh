#!/usr/bin/env bash
# noos_claude_activation_doctor_v1.sh
#
# Instruction-load + authority doctor for the NOOS Claude Code activation surface.
# Verifies the surface is actually wired, not just present:
#   1. surface files exist (CLAUDE.md, .claude/noos/*, .claude/agents/*)
#   2. CLAUDE.md is concise and carries the required anchors + canon strings
#   3. agent definitions have valid frontmatter (name matches filename)
#   4. every repo-relative path the surface cites exists
#   5. in-repo authority pins resolve (commit exists AND file exists at pin)
#   6. AUTHORITY.md records every pin the doctor enforces
#   7. Master SSOT / SG Library pins resolve in the sibling SG repo
#      (DEGRADED, not FAIL, when the sibling repo is not on this machine)
#   8. founder-canon binding intact: dispatch line verbatim in all dispatch
#      templates, canon_version string in machine-loops config
#   9. forbidden legacy slug absent from the Claude surface
#  10. AGENTS.md cross-links the Claude surface
#  11. custody chain (noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json): pins file
#      agrees with this doctor's pins (mismatch = FAIL), every artifact blob
#      SHA verifies at its pinned commit, SSOT §0.7 / P2 matrix / P7 §11-§12 /
#      P8 continuation+commissioning / P10 cost doctrine / custody receipts +
#      verifier exist at the SG pin, NOOS custody pin is an ancestor of HEAD
#  12. staleness: a pin that is no longer its repo's current main is reported
#      [STALE] and forces DEGRADED — stale authority pins cannot pass silently
#
# Writes a receipt to receipts/ and exits 0 (PASS or DEGRADED) or 1 (FAIL).
# DEGRADED means: local surface verified but either sibling-repo checks were
# skipped offline or a pin is stale — do not report "fully green".
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SG_REPO="${NOOS_SG_REPO:-$HOME/Desktop/Noetfield-Systems/sina-governance-SSOT}"

SG_PIN="b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0"  # Re-pin after SG PR #18: NF-COMMAND-GATEWAY-V2-ARCHITECTURE-V1 + SinaGPT founder-brain land on SG main (merge_commit b72f5a3, ancestor of SG main; dc6080d8 motor authority remains ancestor); must equal custody pins-file sg_repo.commit
NOOS_CUSTODY_PIN="a4bdf1f338a5ecf9de58fb5eda8ef974eee715ca"
CANON_COMMIT="6c13aa2765dbb129bc4981da4f25ef1a8a96b84d"
SG_LIB_VERSION="v0.9-SG-RATIFIED"
SG_LIB_ZIP_SHA256="929d449364c6b4d88931e71f44352953ee243e4cd6e2b6b7e7495ff2d0662cc1"
CUSTODY_PINS_FILE="noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json"

# in-repo pins: "<sha> <path>"
LOCAL_PINS=(
  "146e8fe1acee1748cd6b51352e062432e081aa6d docs/_NOOS_AGENT/NOETFIELD_UNIFIED_MASTER_v1_LOCKED.md"
  "146e8fe1acee1748cd6b51352e062432e081aa6d docs/_NOOS_AGENT/NOETFIELD_OS_SSOT_v1_LOCKED.md"
  "404e4c7193af79b555cdababe8ab668b30e81441 docs/_NOOS_AGENT/PRODUCT_TRUTH.md"
  "c36aaf142719ece6e82dc1490cdac34e53e0885c docs/_NOOS_AGENT/[NOOS-AGENT-20260703-005]_FOUNDER_CANON_INTERFACE_v1.md"
)

# Rendered dispatch line = "LAWS: " + the laws payload carried by every template
LAWS_PAYLOAD='FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.'
DISPATCH_LINE="LAWS: $LAWS_PAYLOAD"
CANON_VERSION='FOUNDER_CANON_v1+MACHINE_LOOPS_v1'

ALL_PASS=1
DEGRADED=0
STALE_PINS=0
CHECKS_JSON="[]"
TS=$(date -u +%Y%m%dT%H%M%SZ)

check() {
  local name="$1" rc="$2" detail="$3"
  if [ "$rc" = "0" ]; then
    echo "[PASS] $name — $detail"
  elif [ "$rc" = "2" ]; then
    echo "[SKIP] $name — $detail"
    DEGRADED=1
  elif [ "$rc" = "3" ]; then
    echo "[STALE] $name — $detail"
    DEGRADED=1
    STALE_PINS=1
  else
    echo "[FAIL] $name — $detail"
    ALL_PASS=0
  fi
  CHECKS_JSON=$(python3 -c "
import json, sys
checks = json.loads(sys.argv[1])
status = {'0': 'pass', '2': 'skipped_offline', '3': 'stale_pin'}.get(sys.argv[3], 'fail')
checks.append({'name': sys.argv[2], 'status': status, 'detail': sys.argv[4]})
print(json.dumps(checks))
" "$CHECKS_JSON" "$name" "$rc" "$detail")
}

# 1. surface files exist
SURFACE_FILES=(
  "CLAUDE.md"
  ".claude/noos/SYSTEM_IDENTITY.md"
  ".claude/noos/AUTHORITY.md"
  ".claude/noos/RUNTIME_MAP.md"
  ".claude/noos/PROJECT_RULES.md"
  ".claude/agents/noos-architect.md"
  ".claude/agents/noos-integrator.md"
)
for f in "${SURFACE_FILES[@]}"; do
  [ -f "$f" ]; check "surface_file:$f" "$?" "exists"
done

# 2. CLAUDE.md concise + anchors
if [ -f CLAUDE.md ]; then
  SIZE=$(wc -c < CLAUDE.md | tr -d ' ')
  [ "$SIZE" -le 10000 ]; check "claude_md_concise" "$?" "CLAUDE.md is ${SIZE} bytes (cap 10000)"
  for anchor in "execution and integration control plane" "graph-out/GRAPH_REPORT.md" ".claude/noos/AUTHORITY.md" "Hard rules"; do
    grep -qF "$anchor" CLAUDE.md; check "claude_md_anchor:${anchor}" "$?" "CLAUDE.md contains '${anchor}'"
  done
  grep -qF "$DISPATCH_LINE" CLAUDE.md; check "claude_md_dispatch_line" "$?" "dispatch line verbatim in CLAUDE.md"
  grep -qF "$CANON_VERSION" CLAUDE.md; check "claude_md_canon_version" "$?" "canon_version string in CLAUDE.md"
  grep -qF "${SG_PIN:0:8}" CLAUDE.md; check "claude_md_sg_pin_current" "$?" "CLAUDE.md authority table cites current SG pin ${SG_PIN:0:8}"
  grep -qF "${NOOS_CUSTODY_PIN:0:8}" CLAUDE.md; check "claude_md_custody_pin_current" "$?" "CLAUDE.md authority table cites current NOOS custody pin ${NOOS_CUSTODY_PIN:0:8}"
fi

# 3. agent frontmatter
for a in noos-architect noos-integrator; do
  if [ -f ".claude/agents/$a.md" ]; then
    head -5 ".claude/agents/$a.md" | grep -q "^name: $a$"
    check "agent_frontmatter:$a" "$?" "frontmatter name matches filename"
  else
    check "agent_frontmatter:$a" "1" "agent file missing"
  fi
done

# 4. every repo-relative path cited by the surface exists
PATHS_RC=0
PATHS_DETAIL=$(SG_REPO="$SG_REPO" python3 - <<'PYEOF'
import re, os, sys
sg = os.environ.get("SG_REPO", "")
sg_roots = [sg, os.path.join(sg, "SG-Canonical-Library", "noetfield-library")] if os.path.isdir(sg) else []
files = ["CLAUDE.md", ".claude/noos/SYSTEM_IDENTITY.md", ".claude/noos/AUTHORITY.md",
         ".claude/noos/RUNTIME_MAP.md", ".claude/noos/PROJECT_RULES.md",
         ".claude/agents/noos-architect.md", ".claude/agents/noos-integrator.md"]
missing, checked, sg_skipped = [], 0, 0
for fn in files:
    if not os.path.isfile(fn):
        continue
    text = open(fn, encoding="utf-8").read()
    for token in re.findall(r"\x60([^\x60\n]+)\x60", text):
        token = token.strip()
        if "/" not in token or " " in token or "<" in token or "*" in token:
            continue
        if token.startswith(("~", "/", "http", ".noos-runtime", "https")):
            continue
        if not re.match(r"^[A-Za-z0-9_.\-]", token):
            continue
        checked += 1
        if os.path.exists(token):
            continue
        # paths cited relative to the sibling SG repo (or its library root)
        if sg_roots:
            if any(os.path.exists(os.path.join(r, token)) for r in sg_roots):
                continue
        else:
            sg_skipped += 1
            continue
        missing.append(f"{fn} -> {token}")
if missing:
    print(f"{len(missing)}/{checked} cited paths missing: " + "; ".join(missing[:8]))
    sys.exit(1)
note = f" ({sg_skipped} SG-relative paths unverified offline)" if sg_skipped else ""
print(f"all {checked} cited paths exist locally or in the SG repo{note}")
PYEOF
) || PATHS_RC=1
check "cited_paths_exist" "$PATHS_RC" "$PATHS_DETAIL"

# 5. in-repo authority pins resolve
for pin in "${LOCAL_PINS[@]}"; do
  sha="${pin%% *}"; path="${pin#* }"
  if git cat-file -e "${sha}^{commit}" 2>/dev/null && git cat-file -e "${sha}:${path}" 2>/dev/null; then
    check "local_pin:${sha:0:8}:${path}" "0" "commit resolves and file exists at pin"
  else
    check "local_pin:${sha:0:8}:${path}" "1" "commit or file-at-pin missing"
  fi
done

# 6. AUTHORITY.md records every enforced pin
if [ -f .claude/noos/AUTHORITY.md ]; then
  for sha in "$SG_PIN" "$NOOS_CUSTODY_PIN" "$CANON_COMMIT" 146e8fe1acee1748cd6b51352e062432e081aa6d 404e4c7193af79b555cdababe8ab668b30e81441 c36aaf142719ece6e82dc1490cdac34e53e0885c; do
    grep -q "$sha" .claude/noos/AUTHORITY.md
    check "authority_records_pin:${sha:0:8}" "$?" "AUTHORITY.md cites the pin"
  done
  grep -qF "$SG_LIB_VERSION" .claude/noos/AUTHORITY.md && grep -qF "$SG_LIB_ZIP_SHA256" .claude/noos/AUTHORITY.md
  check "authority_records_library" "$?" "AUTHORITY.md cites SG Library version + zip sha256"
fi

# 7. sibling SG repo pins (DEGRADED when repo absent)
if [ -d "$SG_REPO/.git" ] || [ -f "$SG_REPO/.git" ]; then
  git -C "$SG_REPO" cat-file -e "${SG_PIN}^{commit}" 2>/dev/null
  check "sg_pin_commit" "$?" "Master SSOT pin ${SG_PIN:0:8} resolves in $SG_REPO"
  git -C "$SG_REPO" cat-file -e "${SG_PIN}:ssot/strategy-ssot-v6-split.md" 2>/dev/null
  check "sg_pin_strategy_ssot" "$?" "strategy-ssot-v6-split.md exists at pin"
  git -C "$SG_REPO" cat-file -e "${SG_PIN}:SG-Canonical-Library/noetfield-library/P1-CANON/FOUNDER_CANON_v1.md" 2>/dev/null
  check "sg_pin_founder_canon_file" "$?" "P1-CANON/FOUNDER_CANON_v1.md exists at pin"
  git -C "$SG_REPO" cat-file -e "${CANON_COMMIT}^{commit}" 2>/dev/null
  check "sg_canon_commit" "$?" "FOUNDER_CANON commit ${CANON_COMMIT:0:8} resolves"
  REG=$(git -C "$SG_REPO" show "${SG_PIN}:SG-Canonical-Library/LIBRARY_REGISTRY.json" 2>/dev/null)
  if echo "$REG" | grep -qF "$SG_LIB_VERSION" && echo "$REG" | grep -qF "$SG_LIB_ZIP_SHA256"; then
    check "sg_library_registry_at_pin" "0" "registry at pin carries $SG_LIB_VERSION + zip sha256"
  else
    check "sg_library_registry_at_pin" "1" "registry at pin missing version or zip sha256"
  fi
else
  check "sg_repo_reachable" "2" "sibling SG repo not present at $SG_REPO — authority pins not re-verified on this machine"
fi

# 8. founder-canon binding intact
TEMPLATES=(.agent-policy/dispatch-templates/*.json)
TPL_RC=0
for t in "${TEMPLATES[@]}"; do
  grep -qF "$LAWS_PAYLOAD" "$t" || TPL_RC=1
  grep -qF "\"canon_version\": \"$CANON_VERSION\"" "$t" || TPL_RC=1
done
check "laws_payload_in_templates" "$TPL_RC" "laws payload + canon_version in ${#TEMPLATES[@]} dispatch templates"
grep -qF "\"canon_version\": \"$CANON_VERSION\"" data/noos-machine-loops-config-v1.json
check "canon_version_in_config" "$?" "canon_version string in machine-loops config"

# 9. forbidden legacy slug absent from the Claude surface
LEGACY_SLUG="kazemnezhadsina144""-dot"
SLUG_RC=0
grep -rqF "$LEGACY_SLUG" CLAUDE.md .claude/noos .claude/agents 2>/dev/null && SLUG_RC=1
check "forbidden_slug_absent" "$SLUG_RC" "legacy slug not present in Claude surface"

# 10. AGENTS.md cross-links the Claude surface
grep -q "CLAUDE.md" AGENTS.md
check "agents_md_cross_link" "$?" "AGENTS.md references CLAUDE.md"

# 11. custody chain — pins file, cross-surface agreement, artifact blob SHAs,
#     custody docs/receipts at the SG pin, NOOS pin ancestry
if [ -f "$CUSTODY_PINS_FILE" ]; then
  python3 -c "import json; json.load(open('$CUSTODY_PINS_FILE'))" 2>/dev/null
  check "custody_pins_valid_json" "$?" "$CUSTODY_PINS_FILE parses"

  JSON_SG=$(python3 -c "import json; print(json.load(open('$CUSTODY_PINS_FILE'))['sg_repo']['commit'])" 2>/dev/null)
  JSON_NOOS=$(python3 -c "import json; print(json.load(open('$CUSTODY_PINS_FILE'))['noos_repo']['commit'])" 2>/dev/null)
  [ "$JSON_SG" = "$SG_PIN" ]
  check "custody_pins_sg_agree" "$?" "pins-file SG commit ${JSON_SG:0:8} == doctor SG pin ${SG_PIN:0:8} (mismatch = stale surface = FAIL)"
  [ "$JSON_NOOS" = "$NOOS_CUSTODY_PIN" ]
  check "custody_pins_noos_agree" "$?" "pins-file NOOS commit ${JSON_NOOS:0:8} == doctor NOOS pin ${NOOS_CUSTODY_PIN:0:8} (mismatch = stale surface = FAIL)"

  git cat-file -e "${NOOS_CUSTODY_PIN}^{commit}" 2>/dev/null && git merge-base --is-ancestor "$NOOS_CUSTODY_PIN" HEAD 2>/dev/null
  check "noos_custody_pin_ancestor" "$?" "NOOS custody pin ${NOOS_CUSTODY_PIN:0:8} resolves and is an ancestor of HEAD"

  if [ -d "$SG_REPO/.git" ] || [ -f "$SG_REPO/.git" ]; then
    BLOB_RC=0
    BLOB_DETAIL=$(SG_REPO="$SG_REPO" SG_PIN="$SG_PIN" NOOS_PIN="$NOOS_CUSTODY_PIN" PINS_FILE="$CUSTODY_PINS_FILE" python3 - <<'PYEOF'
import json, os, subprocess, sys
pins = json.load(open(os.environ["PINS_FILE"]))
sg, sgpin, npin = os.environ["SG_REPO"], os.environ["SG_PIN"], os.environ["NOOS_PIN"]
def blob(repo, commit, path):
    r = subprocess.run(["git", "-C", repo, "rev-parse", f"{commit}:{path}"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None
bad, n = [], 0
for a in pins["artifacts"]:
    repo, commit = (sg, sgpin) if a["layer"].startswith(("sg", "library")) else (".", npin)
    if "files" in a:
        n += 1
        if blob(repo, commit, a["index"]) != a["index_blob_sha"]:
            bad.append(a["index"])
        for f in a["files"]:
            n += 1
            if blob(repo, commit, "noetfield-org/schemas/" + f["name"]) != f["blob_sha"]:
                bad.append(f["name"])
    else:
        n += 1
        if blob(repo, commit, a["path"]) != a.get("blob_sha"):
            bad.append(a["role"])
if bad:
    print(f"{len(bad)}/{n} artifact blob SHAs drift from pins: " + ", ".join(bad[:6])); sys.exit(1)
print(f"all {n} custody artifact blob SHAs verify at their pinned commits")
PYEOF
) || BLOB_RC=1
    check "custody_artifact_blobs" "$BLOB_RC" "$BLOB_DETAIL"

    git -C "$SG_REPO" show "${SG_PIN}:ssot/strategy-ssot-v6-split.md" 2>/dev/null | grep -q "0\.7 — Motor escalation continuity"
    check "sg_pin_ssot_section_0_7" "$?" "Master SSOT §0.7 (motor escalation continuity) present at SG pin"
    git -C "$SG_REPO" show "${SG_PIN}:SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md" 2>/dev/null | grep -q "WAITING_FOR_FOUNDER_REASONING"
    check "sg_pin_p7_terminology_11_12" "$?" "P7 terminology §11-§12 motor terms present at SG pin"
    for p in \
      "SG-Canonical-Library/noetfield-library/P2-SSOT/LIBRARY_CUSTODY_MATRIX_LOCKED_v1.md" \
      "SG-Canonical-Library/noetfield-library/P2-SSOT/AUTHORITY_GRAPH_FOUNDER_REASONING_LOCKED_v1.md" \
      "SG-Canonical-Library/noetfield-library/P8-MACHINE-LOOPS/founder-reasoning-continuation-doctrine-LOCKED_v1.md" \
      "SG-Canonical-Library/noetfield-library/P8-MACHINE-LOOPS/MOTOR_COMMISSIONING_AND_ACCEPTANCE_STANDARD_LOCKED_v1.md" \
      "SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/COST_EXECUTION_DOCTRINE_LOCKED_v1.md" \
      "receipts/custody/CUSTODY_ABSORPTION_ADVISOR_PACKAGE_OPTION_C_v1.json" \
      "receipts/custody/CUSTODY_WIRING_FOUNDER_REASONING_v1.json" \
      "scripts/verify_founder_reasoning_custody_chain_v1.py"; do
      git -C "$SG_REPO" cat-file -e "${SG_PIN}:${p}" 2>/dev/null
      check "sg_pin_custody_file:$(basename "$p")" "$?" "exists at SG pin"
    done
  else
    check "custody_sg_checks" "2" "sibling SG repo absent — custody artifacts not re-verified on this machine"
  fi
else
  check "custody_pins_file" "1" "$CUSTODY_PINS_FILE missing"
fi

# 12. staleness — a pin that is no longer its repo's current main cannot pass silently
NOOS_MAIN=$(git rev-parse origin/main 2>/dev/null || true)
if [ -n "$NOOS_MAIN" ]; then
  if [ "$NOOS_MAIN" = "$NOOS_CUSTODY_PIN" ]; then
    check "noos_pin_freshness" "0" "NOOS custody pin == origin/main"
  else
    check "noos_pin_freshness" "3" "origin/main is ${NOOS_MAIN:0:8}, pin is ${NOOS_CUSTODY_PIN:0:8} — refresh pins + wiring receipt before claiming custody compliance"
  fi
else
  check "noos_pin_freshness" "2" "origin/main not resolvable locally — freshness unverified"
fi
if [ -d "$SG_REPO/.git" ] || [ -f "$SG_REPO/.git" ]; then
  SG_MAIN=$(git -C "$SG_REPO" rev-parse origin/main 2>/dev/null || git -C "$SG_REPO" rev-parse main 2>/dev/null || true)
  if [ -n "$SG_MAIN" ]; then
    if [ "$SG_MAIN" = "$SG_PIN" ]; then
      check "sg_pin_freshness" "0" "SG pin == SG main"
    else
      check "sg_pin_freshness" "3" "SG main is ${SG_MAIN:0:8}, pin is ${SG_PIN:0:8} — refresh pins + wiring receipt before claiming custody compliance"
    fi
  else
    check "sg_pin_freshness" "2" "SG main ref not resolvable — freshness unverified"
  fi
fi

RESULT="PASS"
[ "$DEGRADED" = "1" ] && RESULT="DEGRADED"
[ "$ALL_PASS" = "1" ] || RESULT="FAIL"

RECEIPT_PATH="receipts/noos-claude-activation-doctor-${TS}.json"
python3 -c "
import json, sys, subprocess
sha = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True).stdout.strip()
payload = {
    'schema': 'noos-claude-activation-doctor-v1',
    'action': 'claude_activation_instruction_load_and_authority_doctor',
    'repo': 'noetfeld-os',
    'canon_version': sys.argv[5],
    'timestamp_utc': sys.argv[1],
    'branch': branch,
    'repo_sha': sha,
    'custody_pins': {'sg': sys.argv[7], 'noos': sys.argv[8], 'registry': sys.argv[9]},
    'result': sys.argv[2],
    'stale_pins': sys.argv[6] == '1',
    'degraded_means': 'local surface verified; sibling-repo checks skipped offline or a custody pin is stale — not fully green',
    'checks': json.loads(sys.argv[3]),
}
open(sys.argv[4], 'w').write(json.dumps(payload, indent=2) + chr(10))
" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$RESULT" "$CHECKS_JSON" "$RECEIPT_PATH" "$CANON_VERSION" "$STALE_PINS" "$SG_PIN" "$NOOS_CUSTODY_PIN" "$CUSTODY_PINS_FILE"

echo
echo "NOOS Claude activation doctor: $RESULT"
echo "Receipt: $RECEIPT_PATH"

[ "$RESULT" != "FAIL" ]
