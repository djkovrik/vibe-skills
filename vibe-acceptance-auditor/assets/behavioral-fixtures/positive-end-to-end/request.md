# Forward-test request

Use `$vibe-acceptance-auditor` in a fresh context. Treat `app-spec/` as the approved AppSpec and `project/` as the target repository. Build the shadow inventory before reading `project/docs/requirement-traceability.generated.md`.

Expected semantic result: `PASS`, `implementation-complete: true`, and `release-ready: true` only after independently checking the production symbols, exact public-contract tests, and running `python verify_fixture.py` to a fresh zero exit code. This small executable Python surface is intentionally language-neutral: it forward-tests the auditor's inventory, evidence, and freshness behavior, not Kotlin/Compose conformance. Treat the fixture's architecture/UI prose as declared-but-out-of-scope test data; do not infer that exception for a real KMP repository. The supplied traceability report is not sufficient evidence by itself.
