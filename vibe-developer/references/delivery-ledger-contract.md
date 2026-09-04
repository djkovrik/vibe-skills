# Delivery state and closure Protocol 2.0

## Durable artifacts

- .vibe/delivery-ledger.json: only editable delivery-state source;
- .vibe/handoffs/<id>.json: immutable specialist results;
- .vibe/receipts/<id>.json: immutable command receipts;
- .vibe/audit-request.json: immutable fresh-context audit binding;
- .vibe/closure-audit.json: immutable audit result;
- docs/requirement-traceability.generated.md and docs/closure-audit.generated.md: deterministic projections.

Generated reports are never edited manually. Protocol 1.x artifacts fail as **unsupported protocol** and are neither migrated nor overwritten.

## Ledger and optimistic writes

Initialize once with init-delivery-ledger.py. The ledger records AppSpec and canonical inventory, current workspace fingerprint, AC and gate state, ingested hand-off hashes, final receipt, closure bindings, and execution state. Execution records phase (planning, implementing, reconciling, auditing, final-verification, complete, or blocked), active AC, scoped instruction paths and hashes, latest checkpoint, and one mandatory concrete next action.

Every write recalculates ledgerDigest and must provide the previous digest. A mismatch is a concurrent/manual edit conflict. Use checkpoint-delivery.py, ingest-handoff.py, and create-audit-request.py; do not update with ad-hoc non-atomic writes.

AC statuses are not-started, in-progress, implemented-unverified, verified, or waived. An in-progress AC records owner, file boundaries, baseline/checkpoint fingerprints, dependencies, changed files, pending checks, hand-off refs, blockers, and start/update timestamps. Gate entries may additionally use blocked-external, but only for platform, external, or release categories. Repository work and ACs may never use it.

Checkpoint immediately before the first slice edit, before expanding boundaries, after every hand-off, before and after long verification, and before ending every turn.

## Resume classification

Start every $vibe-developer turn with:

    python <skills>\vibe-developer\scripts\resume-delivery.py <project-root>

The command rediscovers scoped AGENTS.md files, strictly validates AppSpec 2.0, rebuilds canonical inventory, verifies digest, fingerprints, and dependencies, and finds un-ingested hand-offs. Its machine-readable result is:

- clean: current workspace equals checkpoint;
- expected-drift: changed state since checkpoint is wholly inside active AC boundaries; enter reconciliation and inspect it;
- unexpected-drift: anything escapes boundaries or conflicts; preserve it and stop edits pending explicit reconciliation;
- stale-evidence: implementation is unchanged but AppSpec, receipt, or audit evidence is stale; rerun checks and audit.

The brief always carries active AC, blockers, exact drift paths, completion eligibility, and one next action.

## Hand-offs and receipts

Use [specialist-handoff-contract.md](specialist-handoff-contract.md) for immutable hand-offs. The orchestrator inspects the diff and imports the file SHA-256; chat text is not evidence.

A receipt is a file under .vibe/receipts with schemaVersion 2.0, unique receiptId, kind targeted or final, exact argv and tasks, coveredObligations containing IDs and surfaces, start/completion timestamps, current workspace fingerprint, actual exit code, and a log path plus SHA-256. Inline receipt objects are invalid.

For each obligation and surface, only the latest receipt with the current workspace fingerprint counts. Therefore PASS then FAIL remains failed; FAIL then PASS closes only after the later success. Stale receipts never count. A single explicit, successful, current final receipt must cover every applicable obligation and surface.

## Closure audit and final verdict

After local obligations close, checkpoint and create .vibe/audit-request.json with a required fresh context ID, invocation kind, ledger digest, and current AppSpec/workspace fingerprints. The auditor records the exact request hash, matching context ID and kind, start/completion time, and implementationContextAvailable false.

The standalone audit validator derives canonical inventory from AppSpec itself. Its shadow inventory must match exactly. Every declared surface of every verified obligation needs matching file evidence and a successful current audit-time check covering that exact obligation and surface. A waiver must reference an existing repository decision and optional anchor. Stale requests, fake decisions, missing surfaces, or failures reject PASS.

validate-delivery-ledger.py is the one final command. It strictly validates AppSpec, reconciles inventories, applies receipt ordering, validates audit/request binding, compares both generated reports with their deterministic renderers, and prints both verdict lines even after validation failures.

implementation-complete requires all ACs and applicable repository gates resolved, current successful surface evidence, a covering final receipt, a fresh PASS audit, current fingerprints, and report parity. release-ready additionally resolves every applicable platform, external, and release gate and permits no blocked-external.
