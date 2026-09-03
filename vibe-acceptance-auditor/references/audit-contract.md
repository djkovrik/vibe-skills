# Closure audit contract

Read this contract when creating or validating `.vibe/closure-audit.json`.

## Authority and freshness

The audit JSON is an independent observation, not a copy of `.vibe/delivery-ledger.json`. Its `appSpecFingerprint` and `workspaceFingerprint` are the complete objects computed at audit time with `vibe-developer/scripts/compute-workspace-fingerprint.py`, not digest strings. They cover the same inputs as the delivery ledger. A mismatch against current values invalidates the audit immediately.

`completedAt` is an ISO 8601 UTC timestamp. `auditorContext` records `fresh: true`; absence of a fresh context permits only `BLOCKED`.

## Inventory and obligation records

`shadowInventory` contains the stable IDs independently extracted before consulting implementation claims:

- `requirementIds`;
- `acceptanceScenarioIds`;
- `managedOperationIds`, using `<entity-id>:<operation>`;
- `qualityGateIds`.

Create one `obligations` item for every acceptance scenario, required managed operation, and quality gate. A managed operation covered by an acceptance scenario remains visible as its own record and points to that AC. Never collapse multiple open obligations into one status.

Each obligation records `scope` as `repository`, `platform`, `external`, or `release`. Acceptance scenarios and managed operations remain completion-blocking unless verified or waived, even when their implementation touches a platform. Allowed obligation results are:

- `verified`: independently traced through all applicable layers and required test surfaces;
- `gap`: missing, stale, contradicted, or insufficient evidence;
- `blocked-external`: implementation exists, but an external/platform/release gate cannot be closed locally;
- `waived`: an explicit user decision applies and its durable reference is recorded.

Each record names its declared verification surfaces and supplies concrete production/test evidence where applicable. Evidence must use repository-relative paths. `testName` is the exact runnable test name, not a class or file approximation.

## Checks

Each executed audit check records the exact command, real exit code, UTC completion time, result, covered obligation IDs, and the workspace fingerprint observed for that command. Never write a successful check before the process completes. An unavailable or timed-out check uses `exitCode: null` and result `blocked`.

## Findings and completion

Allowed finding kinds are `gap`, `audit-blocker`, `external-blocker`, `waiver`, and `observation`. Every `gap` identifies at least one obligation. `audit-blocker` explains why the auditor cannot reach a reliable verdict; do not use it for a known implementation defect. Findings cite evidence; they do not prescribe unapproved product changes.

Completion is derived:

- `implementationComplete` requires top-level `PASS`, current fingerprints, and every required acceptance/repository obligation `verified` or `waived`.
- `releaseReady` additionally requires every platform/external/release obligation `verified` or `waived`; no `blocked-external` remains.
- `GAPS` and `BLOCKED` require both booleans to be false.

`PASS` may therefore be implementation-complete but not release-ready when its only remaining records are truthful external blockers. Such blockers must be findings and obligation records, not hidden in prose.

## Deterministic Markdown

Generate `docs/closure-audit.generated.md` from the JSON. It must include verdict, both completion booleans, fingerprints, inventory counts, every obligation, every finding, and every check. Do not hand-edit it. Use `render-closure-audit.py --check` to detect drift.
