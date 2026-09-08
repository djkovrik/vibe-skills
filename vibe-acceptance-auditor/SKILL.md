---
name: vibe-acceptance-auditor
description: Independently audit whether an AppSpec implementation is complete and evidence-backed. Use automatically for closure, completeness, release-readiness, or requirement-traceability audits of full or cross-cutting Vibe delivery; do not use to implement or fix findings.
---

# Vibe Acceptance Auditor

## Boundary

Audit only from the fresh context named by immutable `.vibe/audits/<request-id>/request.json`, after implementers have stopped. The orchestrator uses `run-acceptance-audit.py`, which records a host-issued `thread.started` event, exact argv, log/prompt hashes, process outcome and start/end fingerprints in this attemptвЂ™s `launch.json`. You must not author that receipt. The implementation conversation must be unavailable and `implementationContextAvailable` must be recorded as `false`. The ledger, generated reports, and implementer summary are claims to test, never inventory sources. If the requested context isolation is unavailable, return `BLOCKED`.

This skill is read-only except for:

- `<repo>/.vibe/audits/<request-id>/audit.json` (the launcher writes the final JSON once);
- `<repo>/docs/closure-audit.generated.md`;
- build-tool caches produced by completed verification commands.

Never edit the AppSpec, production code, tests, delivery ledger, generated delivery report, configuration, or dependencies. Do not fix a finding while auditing. Record it for a later implementation pass and require a different fresh auditor after any fix.

## Inputs

Require the target repository, approved AppSpec 2.0 directory, and `.vibe/audits/<request-id>/request.json`. Read the AppSpec contract and [audit-contract.md](references/audit-contract.md). Verify request bytes/hash, current fingerprints, required context ID, invocation kind, and the false implementation-context flag before auditing. Inspect repository instructions and `git status` without changing either.

## Independent inventory

Before opening `.vibe/delivery-ledger.json`, `docs/requirement-traceability.generated.md`, or an implementer report:

1. Fingerprint every regular AppSpec file, including assets, and compute the workspace fingerprint with the shared Protocol 2.0 helper. Both must equal the immutable request.
2. Parse `app-spec.json`, every referenced `FLOW-*.md`, every referenced `SCREEN-*.md`, and the normative product/domain/data/design/quality prose.
3. Build the shadow inventory with the shared canonical inventory module, independently from the ledger: approved and excluded requirements, every AC, required managed operation, and quality gate. Inspect prose for platform branches, states, actions, and failures. Treat domain-specific operations separately.
4. Reconcile JSON links with prose. Each acceptance scenario must have its own Given/When/Then and one observable outcome. Contradictory, missing, or ambiguous normative material is a finding even if the ledger omits it.

Use `inventory-sources.py` and include `sourceCoverage` for every heading in product/domain/data/design/quality prose and FLOW/SCREEN files. Map normative sections to obligation IDs; explain any contextual section. Inspect actions, states, failures and platform branches; text absent from JSON is still a finding. Only after freezing this shadow inventory may you inspect the ledger and generated reports. Compare them to the inventory and report omitted, grouped, stale, or overstated entries.

## Evidence audit

For every required acceptance scenario and repository quality gate, trace the full path appropriate to the obligation:

```text
public contract -> data/domain behavior -> Store/component state
-> UI or platform wiring -> required test surface -> completed verification
```

Use every declared `verificationSurface`; do not substitute a lower-level test for an observable public-contract, UI, platform, persistence, or release surface. Each surface needs matching evidence and a successful current integration check explicitly covering that obligation/surface pair. Verify paths and exact symbols/test names, including failure and lifecycle branches.

Independently inspect existing current integration receipts, their actual commands, assertions, coverage and log hashes. Reuse proven checks; execute missing or suspect checks. A check counts only if it actually completed before audit completion with its real exit code, `executionStatus: completed`, and matching `startWorkspaceFingerprint`/`workspaceFingerprint`. Record exact symbols and assertions. Use `run-check.py --kind integration` for non-Gradle checks; during the stopped implementation phase, hold the exclusive audit verification lease and use the shared serialized `run-gradle.ps1 -ReceiptKind integration` for Windows Gradle checks. Return the lease when auditing ends. Build caches are allowed; persistent changes to tracked source or other project files are not. Keep command logs/receipts under `.vibe/receipts`; the launcher writes attempt metadata. A stale receipt, skipped task, nonexistent symbol, unrelated assertion, or command recorded against another workspace fingerprint is not evidence.

Review waivers against accepted `docs/decisions/DEC-*.json` records scoped to the exact obligation, with an exact captured user quote and source hash. Verify the quote actually authorizes this waiver; a structured record does not replace semantic inspection. `blocked-external` is legal only for external/platform/release gates; it never satisfies `release-ready` and cannot hide a repository-verifiable obligation.

Bind every reused or newly executed check to its global `kind: integration` runner receipt with `receiptRef` and `receiptSha256`. Copy the actual command, timestamps, outcome, fingerprints and full coverage; include managed-operation IDs in runner coverage when proving those obligations. Validation also checks the receipt's log hash. A fresh auditor launch does not itself prove that its reported checks ran.

## Verdict

Emit exactly one top-level verdict: `PASS`, `GAPS`, or `BLOCKED`.

- `PASS`: all available surfaces are independently substantiated or explicitly waived, no local implementation gap remains, and both recorded fingerprints still match. Record `locallyVerified: true`. Use obligation result `locally-verified` only when the immutable request lists the exact unavailablePairs. Keep `implementationComplete: false` until every required AC and repository gate is fully verified/waived. `release-ready` is true only when all required platform, external, and release gates are also closed and none is `blocked-external`.
- `GAPS`: one or more obligations are missing, miswired, weakly tested, stale, omitted from the ledger, or otherwise not proved. Both completion claims are false.
- `BLOCKED`: the auditor cannot form a reliable verdict because required source, access, tooling, a valid current AppSpec, or a completing check is unavailable. Do not use `BLOCKED` for a known implementation gap or merely for external release setup.

Write findings with obligation IDs, exact paths/symbols/tests, the failed link in the end-to-end chain, and the smallest observable proof needed to close the gap. Do not use aggregate labels such as `partial`, `mostly complete`, or `implemented baseline`; preserve one record per open obligation.

Immediately before writing, recompute both fingerprints. If either changed during the audit, discard any prospective `PASS`, return `BLOCKED`, and rerun from a fresh snapshot. A prior PASS is invalid after input-content or AppSpec change. An identical-content commit only changes provenance.

Return the audit JSON to the launcher using [closure-audit.schema.json](assets/closure-audit.schema.json), including request path/ID/SHA-256, matching context fields, start/completion timestamps, and exact surface coverage. The orchestrator renders the Markdown view after the launcher has written audit and launch evidence, then validates with `scripts/validate-closure-audit.py --app-spec-root <app-spec> --repository <repo>`. The final delivery validator also checks report parity.

## Handoff

On `GAPS`, return the audit artifact to `$vibe-developer`, which assigns fixes without letting this auditor edit them. After fixes and local verification, a new audit request and clean-context auditor are required. No workflow may claim completion without a current request-bound `PASS`.

For optional package regression checks against DishReady commits, use `scripts/run-dishready-regression.ps1` only on temporary `git archive` extracts; never switch or modify the live checkout.

## Asset completeness

Apply the [asset contract](../vibe-assets-creator/references/asset-contract.md). Independently compare every required icon/logo/illustration in design/screens and state variants against assetRequirements, then inspect the delivered manifest, files, provenance and actual production usage through Compose Multiplatform Resources. Run the asset validator and inspect real preview/golden evidence at intended sizes in both themes. A prompt, placeholder, unused file, missing variant, opaque icon background or stale evidence is a gap. Follow shared resource mappings to reachable screens; static name matching does not prove use. The required inventory must match prose requirements.

For deliveries using capability packages, inspect their entry-point/navigation/restart evidence and actual production reachability independently. AC counts and component tests alone do not prove flow integration. Intermediate scoped receipts do not replace the globally current integration evidence required by the closure contract.
