---
name: vibe-acceptance-auditor
description: Independently audit whether an AppSpec implementation is complete and evidence-backed. Use automatically for closure, completeness, release-readiness, or requirement-traceability audits of full or cross-cutting Vibe delivery; do not use to implement or fix findings.
---

# Vibe Acceptance Auditor

## Boundary

Audit from a fresh context after implementers have stopped. The implementation conversation, delivery ledger, generated traceability report, and implementer summary are claims to test, never sources of truth. If a genuinely fresh context is unavailable, do not certify completion; return `BLOCKED` and require a separate `$vibe-acceptance-auditor` session.

This skill is read-only except for:

- `<repo>/.vibe/closure-audit.json`;
- `<repo>/docs/closure-audit.generated.md`;
- build-tool caches produced by completed verification commands.

Never edit the AppSpec, production code, tests, delivery ledger, generated delivery report, configuration, or dependencies. Do not fix a finding while auditing. Record it for a later implementation pass and require a different fresh auditor after any fix.

## Inputs

Require the target repository and approved AppSpec directory. Read the AppSpec contract and use the package's current AppSpec validator with `--require-current`. Read [audit-contract.md](references/audit-contract.md) before writing an audit artifact. Inspect repository instructions and `git status` without changing either.

## Independent inventory

Before opening `.vibe/delivery-ledger.json`, `docs/requirement-traceability.generated.md`, or an implementer report:

1. Fingerprint all normative AppSpec JSON and Markdown and compute the workspace fingerprint with the same package helper used by the ledger and receipts. Record both exact values.
2. Parse `app-spec.json`, every referenced `FLOW-*.md`, every referenced `SCREEN-*.md`, and the normative product/domain/data/design/quality prose.
3. Build a shadow inventory of every approved requirement, acceptance scenario, managed-entity operation, quality gate, platform branch, state, action, and failure outcome. Treat additional operations such as rename, reuse, restore, and delete-all as separate obligations. Do not infer closure from a broader CRUD label.
4. Reconcile JSON links with prose. Each acceptance scenario must have its own Given/When/Then and one observable outcome. Contradictory, missing, or ambiguous normative material is a finding even if the ledger omits it.

Only after freezing this shadow inventory may you inspect the ledger and generated reports. Compare them to the inventory and report omitted, grouped, stale, or overstated entries.

## Evidence audit

For every required acceptance scenario and repository quality gate, trace the full path appropriate to the obligation:

```text
public contract -> data/domain behavior -> Store/component state
-> UI or platform wiring -> required test surface -> completed verification
```

Use the scenario's declared `verificationSurfaces`; do not substitute a lower-level test for an observable public-contract, UI, platform, persistence, migration, or release surface. Verify that every cited path exists, every exact symbol/test name is present, and the assertion proves the stated outcome, including failure and lifecycle branches. Search for bypasses and negative evidence, not just matching names.

Re-run targeted checks when safe and available. A check counts only if it actually completes with its real exit code and an audit-time workspace fingerprint. Build caches are allowed; generated source or repository files outside the two audit artifacts are not. A stale receipt, skipped task, nonexistent symbol, unrelated assertion, or command recorded against another workspace fingerprint is not evidence.

Review waivers against an explicit recorded user decision. `blocked-external` may preserve `implementation-complete` only for external/platform/release gates; it never satisfies `release-ready` and cannot hide a repository-verifiable obligation.

## Verdict

Emit exactly one top-level verdict: `PASS`, `GAPS`, or `BLOCKED`.

- `PASS`: every required acceptance scenario and repository gate is independently substantiated or explicitly waived, no implementation gap remains, and both recorded fingerprints still match. `implementation-complete` is true. `release-ready` is true only when all required platform, external, and release gates are also closed and none is `blocked-external`.
- `GAPS`: one or more obligations are missing, miswired, weakly tested, stale, omitted from the ledger, or otherwise not proved. Both completion claims are false.
- `BLOCKED`: the auditor cannot form a reliable verdict because required source, access, tooling, a valid current AppSpec, or a completing check is unavailable. Do not use `BLOCKED` for a known implementation gap or merely for external release setup.

Write findings with obligation IDs, exact paths/symbols/tests, the failed link in the end-to-end chain, and the smallest observable proof needed to close the gap. Do not use aggregate labels such as `partial`, `mostly complete`, or `implemented baseline`; preserve one record per open obligation.

Immediately before writing, recompute both fingerprints. If either changed during the audit, discard any prospective `PASS`, return `BLOCKED`, and rerun from a fresh snapshot. A prior `PASS` is invalid after any AppSpec or workspace change.

Write `.vibe/closure-audit.json` to the schema in [closure-audit.schema.json](assets/closure-audit.schema.json), render the Markdown view with `scripts/render-closure-audit.py`, and validate it with `scripts/validate-closure-audit.py --app-spec-root <app-spec> --repository <repo>`. The JSON is the audit source of truth; the Markdown is deterministic output.

## Handoff

On `GAPS`, return the audit artifact to `$vibe-developer`, which assigns fixes without letting this auditor edit them. After fixes and local verification, a new clean-context auditor must rebuild the shadow inventory and audit again. No implementation workflow may claim `implementation-complete` or `release-ready` without a current fresh `PASS` matching the current AppSpec and workspace fingerprints.

For optional package regression checks against DishReady commits, use `scripts/run-dishready-regression.ps1` only on temporary `git archive` extracts; never switch or modify the live checkout.
