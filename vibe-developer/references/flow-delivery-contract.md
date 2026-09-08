# Flow packages and scoped implementation evidence

This is the only supported delivery workflow. AppSpec remains 2.0 and requires the current complete contract, including assetRequirements. Handoffs require assignment-local evidence; targeted receipts require registered input scopes. Global handoffs and unscoped targeted receipts are rejected, with no conversion or fallback. A package is a scheduling unit; each AC remains an independent acceptance obligation.

## Work size and integration

Plan a bounded user capability (for example catalog create/edit/delete) with several related ACs. Group work that shares a component, editor, persistence aggregate or test harness. Split when dependencies, risk or context size warrant it. Skills are expertise routes, not a requirement to spawn a different agent for every layer or AC. Use independent agents only when the host permits delegation and they have useful non-overlapping work.

Create a real production root and one reachable save/read/restart flow in the first package. Each subsequent package connects to that root. Component verification alone does not prove a usable flow. Record entry-point, navigation and restart evidence plus a real successful integration receipt; report integrated flows separately from verified AC counts. Never present their ratio as percent application completion.

Package-internal dependencies may be implemented together, in dependency order. External dependencies must already be verified/waived. A package may be integrated while some ACs are implemented-unverified pending scheduled goldens; keep those obligations and checks explicit. Do not infer that a later action is safe if it depends on unresolved behavior. Never mark ACs verified just to unblock scheduling.

## JSON automation

Save each request under `.vibe/requests/<unique-id>.json`, then run:

```powershell
python <skills>/vibe-developer/scripts/delivery-work.py <repo> --request .vibe/requests/<unique-id>.json
```

Only the orchestrator executes ledger actions (`package`, `scope`, `assign`, `ingest`, `bind`, `integrate`) and `check`. Specialists may prepare check requests and execute `handoff` for their registered assignment. Helpers read the current digest once and use optimistic locking; conflicts are inspected, not automatically retried. A supplied `expectedLedgerDigest` tightens the caller's precondition. Initial ledger/request registration still uses init-delivery-ledger and checkpoint-delivery.

Start a package before edits:

```json
{
  "action": "package", "packageId": "catalog", "owner": "vibe-developer",
  "acceptanceScenarioIds": ["AC-001", "AC-002"], "qualityGateIds": [],
  "fileBoundaries": ["shared/component/catalog/**", "shared/data/**", "shared/compose/**", "androidApp/**"],
  "integrationGoal": "Launch the real catalog, save an item, reopen it after restart",
  "nextAction": "Implement the catalog contracts, persistence and production navigation"
}
```

Use actual IDs/paths. Register a verification scope only after reviewing its complete transitive inputs:

```json
{
  "action": "scope", "scopeId": "catalog-v1",
  "patterns": ["shared/domain/**", "shared/component/catalog/**", "shared/data/**", "shared/compose/src/commonMain/composeResources/**"],
  "dependencyRationale": "All source/test dependencies of catalog host tests, including resource keys and persistence fixtures",
  "toolchainIdentity": "Actual pinned JDK/Kotlin/Gradle and relevant external check versions"
}
```

The tool automatically adds build scripts, properties, build logic, version catalogs/wrapper files, the complete normative AppSpec and scoped AGENTS.md hashes. Patterns include future files and explicit missing paths; adding/removing an input invalidates evidence. Include configuration, native/resources, test fixtures and transitive modules when they influence the check. If unsure of the dependency closure, register a conservative whole-repository scope with `patterns: ["**"]`; never omit `inputScopeId` from a targeted check. Unpinned external tool/config changes require a new scope/toolchain identity and rerun. Scope IDs are immutable. This is an inspected input manifest, not automatic Gradle dependency analysis.

Assign one non-overlapping feature boundary per writer:

```json
{
  "action": "assign", "assignmentId": "catalog-component", "owner": "vibe-decompose-engineer",
  "acceptanceScenarioIds": ["AC-001", "AC-002"], "qualityGateIds": [],
  "allowedFiles": ["shared/component/catalog/**"], "inputScopeId": "catalog-v1"
}
```

Assignments capture their own immutable baseline under `.vibe/snapshots`. Related contract inputs should use an inputScopeId; the handoff records their current fingerprint for inspection. The orchestrator checks that relevant changed inputs were incorporated. Do not freeze an entire workspace while unrelated owners write. Conservative overlap detection may require narrower prefixes or serial ownership of a genuinely shared file.

## Fast feedback before handoff

Compile modified modules and run the smallest meaningful behavioral test as soon as code is ready to check. Do not wait for a final handoff. Specialist requests go to the orchestrator's existing serialized Gradle runner:

```json
{
  "action": "check", "runner": "gradle", "kind": "targeted", "inputScopeId": "catalog-v1",
  "tasks": [":shared:component:catalog:allTests"],
  "coveredObligations": [{"obligationId": "AC-001", "surfaces": ["component-test"]}],
  "timeoutSeconds": 1800
}
```

`run-gradle.ps1 -ProjectRoot <repo> -RequestPath <json>` also accepts this request directly, creates unique receipt/log paths and returns the receipt path. Arrays are parsed inside PowerShell. `delivery-work.py check` also binds the generated receipt without clearing pending checks or advancing AC status. Non-Gradle requests use `runner: "command"` and `argv: ["python", "verify.py"]`. Commands are executed once, including failures; do not claim a receipt proves checks it did not run. Scope failures preserve pending work.

After actual feedback and fixes, prepare a `handoff` request with assignmentId, productionEvidence, testEvidence, nonGradleChecks actually executed, remaining requestedCommands and blockers. The helper computes authored delta, result/input fingerprints and writes the immutable file; do not type fingerprints or cumulative AC drift by hand. `ingest` takes handoffRef and a non-empty inspectionNote after reviewing the diff. It imports and checkpoints in one ledger transaction. If an unimported attempt became stale, create a corrected handoff with `supersedes: [".vibe/handoffs/old-id.json"]`; inspect both attempts before ingest. The old bytes remain immutable, hash-bound history and cease blocking resume only when the replacement for the same assignment is accepted. `bind` takes receiptRef and records its coverage, including failures, without changing AC status or clearing pending checks. Clear resolved checks and verify ACs only after all their required surfaces have successful current evidence.

`integrate` takes packageId, receiptRef and integrationEvidence rows with `path`, `symbol`, and roles `entry-point`, `navigation`, `restart`. Record real production/navigation symbols and a restart test symbol; the independent auditor verifies the claimed behavior. This state does not replace AC verification. The next package may start after integration.

## Verification cadence

| Boundary | Required work |
| --- | --- |
| Edit/repair | Changed-module compile, new behavior test and affected regressions |
| Stable screen/capability | Combined relevant domain/component/persistence suite, reachable production flow, affected goldens |
| Final integration | Full required matrix with global `kind: integration` receipts, independent fresh audit using the same explicit global kind, then the post-audit `kind: final` receipt |

Build/scanner smoke-check a small production preview early, before expanding the state matrix. Compile previews during UI edits. Record/inspect/verify at a stable screen/package boundary and after approved visual changes, only for affected screenshots. Preserve every applicable primary state in light/dark; choose additional font/locale/device stress variants by risk/pairwise coverage. A deferred golden-test leaves its AC implemented-unverified, not verified or waived.

Run Lazyweb research before design. Run one complete ordered review of stable primary screens with exactly one report in flight; rerun affected screens only for material redesign or unresolved findings. Continue unrelated permitted work while a report is pending. No repeated full review solely because another AC closed. Preserve the user's one-screen-at-a-time constraint.

## Recovery and closure

Use `resume-delivery.py --compact` after interruption/compaction and at turn start. It omits repeated snapshot payloads while retaining IDs, blockers, pending checks and next action. Reread changed required inputs and lost context; do not reload unchanged contracts after every minor handoff. Use feature globs and package-level boundaries; checkpoint at assignment start, meaningful result, verification result and before interruption/return, not as a separate reasoning task for every file.

If the same failure category repeats twice, diagnose a minimal case and repair the shared harness/pattern before another identical attempt. Escalate the bounded diagnosis or reasoning effort when justified and allowed; do not change all model settings by default.

Targeted scope reuse is for implementation/pre-audit readiness only. Final completion retains global workspace/AppSpec fingerprints, current successful global checks, fresh independent audit and the post-audit covering final receipt. Historical artifacts are never upgraded or relabeled to make them current evidence. A user-authorized fresh iteration preserves its predecessor outside the active delivery state and starts with new evidence. Never remove architecture, privacy, localization, transaction or visual coverage obligations to improve throughput.
