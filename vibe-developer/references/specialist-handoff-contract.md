# Specialist hand-off Protocol 2.0

A specialist assigned by `$vibe-developer` writes exactly one immutable JSON artifact directly under `<repo>/.vibe/handoffs/<handoffId>.json`. Conversation summaries are not delivery evidence. The specialist never edits `.vibe/delivery-ledger.json`, never runs Gradle on Windows, and never declares an AC, gate, implementation, or release complete.

## Required shape

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
  "baseWorkspaceFingerprint": {},
  "resultWorkspaceFingerprint": {},
  "allowedFiles": ["feature/**", "tests/feature/**"],
  "changedFiles": ["feature/Example.kt"],
  "productionEvidence": [{"path": "feature/Example.kt", "symbol": "Example", "surface": "public-contract"}],
  "testEvidence": [{"path": "tests/feature/ExampleTest.kt", "testName": "exampleWorks", "surface": "component-test"}],
  "nonGradleChecks": [{"argv": ["tool", "check"], "exitCode": 0, "startedAt": "...", "completedAt": "..."}],
  "requestedCommands": [{"argv": ["gradlew.bat", ":feature:test"], "tasks": [":feature:test"], "coveredObligations": [{"obligationId": "AC-001", "surfaces": ["component-test"]}]}],
  "blockers": []
}
```

Fingerprints use `compute-workspace-fingerprint.py`. Paths and boundaries are repository-relative POSIX paths; glob boundaries are permitted. Every changed file must be inside `allowedFiles`. Evidence names exact production symbols and tests and identifies the AppSpec verification surface it proves. Record only checks actually completed; requested Gradle commands are requests, not receipts.

Write the final bytes once. If a correction is needed, create a new hand-off ID and file. The orchestrator checkpoints, inspects the diff and boundary match, then imports the SHA-256 with `ingest-handoff.py --expected-ledger-digest ...`. A hand-off whose result fingerprint is stale or whose files escape either assignment or ledger boundaries is rejected.
