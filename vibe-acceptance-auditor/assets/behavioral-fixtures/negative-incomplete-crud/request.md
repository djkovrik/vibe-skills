# Forward-test request

Use `$vibe-acceptance-auditor` in a fresh context. Treat `app-spec/` as the approved AppSpec and `project/` as the target repository. The generated traceability report claims completion; do not trust it.

Expected semantic result: `GAPS`. The audit must separately identify missing or unproved preset rename/update, history reuse, history deletion, draft resume, draft discard, direct quantity change, direct removal, and granular draft deletion. It must not collapse these into a generic CRUD or `partial` finding.
