# Specialist hand-off Protocol 2.0

A specialist assigned by `$vibe-developer` writes exactly one immutable JSON artifact directly under `<repo>/.vibe/handoffs/<handoffId>.json`. Conversation summaries are not delivery evidence. The specialist never edits `.vibe/delivery-ledger.json`, never runs Gradle on Windows, and never declares an AC, gate, implementation, or release complete.

## Assignment-local evidence (required)

Follow [flow-delivery-contract.md](flow-delivery-contract.md). Register an assignment with `delivery-work.py` before edits; request compile/tests before final handoff. A `handoff` JSON request generates `evidenceMode: "assignment"`, `assignmentBaselineRef`, authored `changedFiles`, `resultScopeFingerprint` and optional registered-input fingerprint. Global base/resultWorkspaceFingerprint fields are unsupported. The ledger binds the immutable assignment and its own baseline; unrelated writers do not stale the result. Own-file or input-contract changes after capture are rejected. Never substitute the whole AC's cumulative drift for the assignment delta. Inspect then use `ingest` to atomically import and checkpoint.

## Generated artifact shape

```json
{
  "schemaVersion": "2.0",
  "handoffId": "HANDOFF-unique-id",
  "assignmentId": "ASSIGNMENT-unique-id",
  "owner": "vibe-specialist-name",
  "acceptanceScenarioIds": ["AC-001"],
  "qualityGateIds": [],
  "startedAt": "2026-09-04T10:00:00Z",
  "completedAt": "2026-09-04T10:15:00Z",
  "evidenceMode": "assignment",
  "assignmentBaselineRef": {"path": ".vibe/snapshots/<digest>.json", "sha256": "<computed>"},
  "resultScopeFingerprint": {"algorithm": "sha256", "patterns": ["feature/**", "tests/feature/**"], "files": [], "digest": "<computed>"},
  "allowedFiles": ["feature/**", "tests/feature/**"],
  "changedFiles": ["feature/Example.kt"],
  "productionEvidence": [{"path": "feature/Example.kt", "symbol": "Example", "surface": "public-contract"}],
  "testEvidence": [{"path": "tests/feature/ExampleTest.kt", "testName": "exampleWorks", "surface": "component-test"}],
  "nonGradleChecks": [{"argv": ["tool", "check"], "exitCode": 0, "startedAt": "...", "completedAt": "..."}],
  "requestedCommands": [{"argv": ["gradlew.bat", ":feature:test"], "tasks": [":feature:test"], "coveredObligations": [{"obligationId": "AC-001", "surfaces": ["component-test"]}]}],
  "blockers": []
}
```

Generate the actual baseline/result fingerprints with `delivery-work.py handoff`; the illustrative placeholders above must never be authored as evidence. Paths and boundaries are repository-relative POSIX paths; glob boundaries are permitted. Every changed file must be inside `allowedFiles`. Evidence names exact production symbols and tests and identifies the AppSpec verification surface it proves. Record only checks actually completed; requested Gradle commands are requests, not receipts.

Write the final bytes once. If a correction is needed, create a new hand-off ID and file. The orchestrator checkpoints, inspects the diff and boundary match, then imports the SHA-256 with `ingest-handoff.py --expected-ledger-digest ...`. Validation compares owned files and registered inputs and rejects files escaping assignment or ledger boundaries.

For unfinished work, use the shared [recovery contract](recovery-contract.md) at meaningful progress and before interruption, return or context loss. Gate-only assignments also require an owner, baseline and file boundaries in the ledger. Clear pending checks/blockers only after resolving them; a final hand-off does not erase a durable decision.
