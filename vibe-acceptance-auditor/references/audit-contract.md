# Closure audit Protocol 2.0

The orchestrator creates immutable .vibe/audits/<request-id>/request.json before launching the auditor. It contains protocol/request IDs, creation time, pre-audit ledger digest, exact AppSpec and workspace fingerprints, required auditor context ID, invocation kind, and implementationContextAvailable false. Validate this request before reading the ledger.

The closure audit is also immutable for that request and records:

- schemaVersion 2.0 and a unique audit ID;
- auditRequest.path, requestId, and SHA-256 of exact request bytes;
- auditorContext.contextId, invocationKind, and implementationContextAvailable false;
- startedAt and completedAt;
- exact current AppSpec/workspace fingerprints;
- canonical shadow inventory built with the shared AppSpec module;
- one record per AC, required managed operation, and quality gate;
- evidence per declared verification surface;
- audit-time checks with structured argv, ordered UTC timestamps inside the audit window, executionStatus, real exit code, matching start/end fingerprints, and exact obligation/surface coverage;
- findings, verdict, and both completion booleans.

The audit validator independently loads AppSpec 2.0 and rebuilds canonical inventory. A copied ledger inventory cannot substitute. Each verified surface requires both an evidence path and a zero-exit audit-time check covering the same obligation and surface. A command that covers only another surface is unrelated. Missing files, stale fingerprints or request hash, wrong context, fabricated waiver path/anchor, any failed check under PASS, and shadow-inventory drift are errors.

Waived obligations carry decisionReference to accepted scoped decision JSON with a captured exact user approval source and hash; source files and arbitrary anchors are not authorization. blocked-external is restricted to platform, external, and release gates.

PASS requires all implementation obligations verified or waived. GAPS requires an explicit gap obligation/finding. BLOCKED represents inability to inspect or run required proof, not a known implementation defect. releaseReady additionally requires every applicable gate verified or waived.

Render docs/closure-audit.generated.md from the JSON. validate-delivery-ledger.py later recomputes the audit result and both report projections, so a remembered standalone command cannot bless drift.

The fresh-process launcher writes `launch.json` next to request/audit, containing host thread.started evidence, exact exec argv, hashes and process outcome. Self-reported isolation is insufficient. Every normative-document section must appear in sourceCoverage with obligation links or an explained contextual classification. Audit and launch timestamps must agree. See [recovery-contract.md](../../vibe-developer/references/recovery-contract.md) for attempt recovery and decisions.
