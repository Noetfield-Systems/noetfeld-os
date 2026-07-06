## Step 5 — NOOS Copilot Sync Mode Patch (discovery/registration)

- Completed discovery and registration of NOOS Copilot dispatcher machine record (data/noos-copilot-dispatcher-mode-v1.json).
- Added dispatcher authority documentation (docs/NOOS_COPILOT_DISPATCHER_AUTHORITY.md).
- Added non-enforcing CI discovery test to validate registration via data/package_map.json.
- Runtime enforcement is deferred to a later bounded PR; this change is registration-only.
- External attestations and blocked items remain listed in audits/BLOCKED_WITH_REASON.md (unchanged).
