# Delivery state and closure Protocol 2.0

## Durable artifacts

- .vibe/delivery-ledger.json: only editable delivery-state source;
- .vibe/handoffs/<id>.json: immutable specialist results;
- .vibe/receipts/<id>.json: immutable command receipts;
- .vibe/audits/<request-id>/request.json: immutable fresh-context audit binding;
- .vibe/audits/<request-id>/audit.json: immutable audit result;
- docs/requirement-traceability.generated.md and docs/closure-audit.generated.md: deterministic projections.

Generated reports are never edited manually. Protocol 1.x artifacts fail as **unsupported protocol** and are neither migrated nor overwritten.

## Capability packages and scoped evidence

New assignments use [flow-delivery-contract.md](flow-delivery-contract.md). Optional ledger `workPackages`, `assignments`, `verificationScopes` and `execution.activePackageId` group related ACs without changing their IDs or verification requirements. `delivery-work.py` registers and captures assignments, runs checks before final handoff, generates handoffs, ingests/checkpoints, binds receipts and records reachable flow integration. `.vibe/snapshots` stores shared immutable baselines; `.vibe/requests` stores durable command requests. Both are excluded from global code fingerprints. Assignment-local handoffs and input-scoped targeted receipts are the only intermediate evidence formats. Unsupported historical formats cannot be imported or counted.

## Ledger and optimistic writes

Initialize once with init-delivery-ledger.py. The ledger records AppSpec and canonical inventory, current workspace fingerprint, AC and gate state, ingested hand-off hashes, final receipt, closure bindings, and execution state. Execution records phase (planning, implementing, reconciling, auditing, final-verification, complete, or blocked), active AC, scoped instruction paths and hashes, latest checkpoint, and one mandatory concrete next action.

Every write holds an OS-owned file lock through digest comparison, mutation and atomic replacement, recalculates ledgerDigest and must provide the previous digest. A mismatch is a concurrent/manual edit conflict. Use checkpoint-delivery.py, ingest-handoff.py, and create-audit-request.py; do not update with ad-hoc non-atomic writes.

AC statuses are not-started, in-progress, implemented-unverified, verified, or waived. An in-progress AC records owner, file boundaries, baseline/checkpoint fingerprints, dependencies, changed files, pending checks, hand-off refs, blockers, and start/update timestamps. Gate entries may additionally use blocked-external, but only for platform, external, or release categories. Repository work and ACs may never use it.

Checkpoint at package/assignment start, meaningful implementation or verification result, and before interruption/return. Capture feature boundaries up front and automate ingest/checkpoint; do not create a separate reasoning round for each new filename.

## Resume classification

Start every $vibe-developer turn with:

    python <skills>\vibe-developer\scripts\resume-delivery.py <project-root> --compact

The command rediscovers scoped AGENTS.md files, strictly validates AppSpec 2.0, rebuilds canonical inventory, verifies digest, fingerprints, and dependencies, and finds un-ingested hand-offs and orphan audit requests. Also run it immediately after compaction or interruption, including within one turn. Its machine-readable result is:

- clean: current workspace equals checkpoint;
- expected-drift: changed state since checkpoint is wholly inside active AC boundaries; enter reconciliation and inspect it;
- unexpected-drift: anything escapes boundaries or conflicts; preserve it and stop edits pending explicit reconciliation;
- stale-evidence: implementation is unchanged but AppSpec, receipt, or audit evidence is stale; rerun checks and audit.

The brief carries the full active AC/gate, all unresolved obligations, saved blockers, pending checks, current specialist recovery packets, captured decisions and required rereads. `safeToContinue` is separate from aggregate-derived `completionEligible`. See [recovery-contract.md](recovery-contract.md).

## Hand-offs and receipts

Use [specialist-handoff-contract.md](specialist-handoff-contract.md) for immutable hand-offs. The orchestrator inspects the diff and imports the file SHA-256; chat text is not evidence.

Resume, pre-audit readiness and final aggregate validation all compare every on-disk hand-off by path and SHA-256 with inspected imports. Any unimported or changed hand-off blocks closure, including one arriving after an audit PASS. Preserve and inspect it; do not delete it to make validation pass.

A receipt is a file under .vibe/receipts with schemaVersion 2.0, unique receiptId, kind targeted, integration or final, exact argv and tasks, coveredObligations containing IDs and surfaces, start/completion timestamps, start/end workspace fingerprints, executionStatus, actual exit code, and a log path plus SHA-256. Inline receipt objects are invalid.

For each obligation and surface, only the latest current receipt counts. During implementation/pre-audit readiness, targeted receipts with a registered inputScopeId use current inputFingerprint and unchanged startInputFingerprint. The scope includes reviewed transitive sources/tests/configuration, automatic build/spec/instruction inputs and toolchain identity. Targeted receipts always require a registered scope; uncertain dependency closures use an explicit whole-repository input manifest. Global integration and audit checks use kind integration; only the post-audit closure run uses kind final. Final closure and audit checks still require current global workspace fingerprints. Therefore PASS then FAIL remains failed; FAIL then PASS closes only after the later success. Stale receipts never count. A single explicit, successful, current final receipt must cover every verified obligation and surface. The final run must start after the current audit completes; old attempts remain as history.

## Closure audit and final verdict

After local obligations close, checkpoint and create .vibe/audits/<request-id>/request.json with a required fresh context ID, invocation kind, ledger digest, and current AppSpec/workspace fingerprints. The auditor records the exact request hash, matching context ID and kind, start/completion time, and implementationContextAvailable false.

The standalone audit validator derives canonical inventory from AppSpec itself. Its shadow inventory must match exactly. Every declared surface of every verified obligation needs matching file evidence and a successful current audit-time check covering that exact obligation and surface. A waiver must reference an accepted `docs/decisions/DEC-*.json` scoped to that obligation with captured user approval. Stale requests, fake decisions, missing surfaces, or failures reject PASS.

validate-delivery-ledger.py is the one final command. It strictly validates AppSpec, reconciles inventories, applies receipt ordering, validates audit/request binding, compares both generated reports with their deterministic renderers, and prints both verdict lines even after validation failures.

implementation-complete requires all ACs and applicable repository gates resolved, current successful surface evidence, a covering final receipt, a fresh PASS audit, current fingerprints, and report parity. release-ready additionally resolves every applicable platform, external, and release gate and permits no blocked-external.

## Asset delivery

For specs declaring assetRequirements, aggregate validation (including pre-audit readiness) invokes the shared asset delivery validator. Track creation under the linked ACs and the required asset-check/asset-visual repository gate. `docs/assets/asset-manifest.json` is evidence, not a second status ledger; its bytes and output/use-site changes invalidate workspace-bound verification. Follow the [asset contract](../../vibe-assets-creator/references/asset-contract.md).
