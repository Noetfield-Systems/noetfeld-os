# Execution Truth — agent reply ingest (LOCKED)

**Law (external):** `SourceA/SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md`, `SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md`

## iPhone / RUN SYSTEM “red log” (Noetfield)

| What you see | Meaning |
|--------------|---------|
| **Result: PASS** (green) | Overall run succeeded; proof saved |
| **Red “Run started” / red log line** | Often **one repo ingest** failed inside a **multi-repo** run — not total failure |
| **smoke: complete** | Smoke phase finished |

**Do not treat PASS + red partial log as a false PASS** unless the run summary says FAIL.

### Common Noetfield ingest failure

**Missing `reported_at`** in the trailing YAML block → Prompt OS / `ingest-inbox.sh noetfield` may reject that **reply**.

**Fix:** Add `reported_at` to the YAML footer and re-ingest.  
**Do NOT:** stop shipping product work, wait for the next order, or treat ingest as the blocker — **ingest sends your answer to the system**; shipping continues in parallel.

---

## Required footer (copy every time)

```yaml
schema_version: 1
repo: noetfield
task: "<exact task string from Prompt OS>"
status: done | blocked | partial
verify_passed: true | false
verify_command: "<command you ran>"
verify_output_summary: "<one line>"
blocked_reason: ""
next_action: ""
evidence_paths: []
reported_at: "<ISO8601 UTC — REQUIRED>"
reporter: cursor
```

### `reported_at` rules

- Format: `YYYY-MM-DDTHH:MM:SSZ` (UTC, no offset ambiguity)
- Must be present even when `status: partial` or `blocked`
- Generate at **end of reply**, not copied from examples

---

## Inbox path (Mac)

Write full reply to:

`/Users/sinakazemnezhad/Desktop/SinaPromptOS/outputs/inbox/noetfield-latest.txt`

Then:

```bash
cd ~/Desktop/SinaPromptOS
./scripts/ingest-inbox.sh noetfield
```

---

## Verify before ingest (repo)

```bash
python3 scripts/verify_agent_reply_yaml.py path/to/reply.txt
# or
pbpaste | python3 scripts/verify_agent_reply_yaml.py
```

Exit `0` = safe to ingest; exit `1` = fix YAML (usually `reported_at`).
