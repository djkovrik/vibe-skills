# Durable recovery and accepted changes

Recover from repository artifacts at the start of a turn, immediately after context compaction (even within one turn), after interruption, and whenever remembered state is uncertain. This is an agent workflow rule, not a claim that the host provides a compaction hook.

## Orchestrator

Run `resume-delivery.py <repo> --compact` before editing. Reread inputs whose hashes changed and context actually lost; do not reload unchanged contracts on each handoff. Read `activeSlice`, `unresolvedObligations`, `pendingChecks`, `itemBlockers`, `decisions`, `recoveryPackets`, and `requiredReads`. `safeToContinue` permits the specified recovery action, not bypassing a blocker. `completionEligible` comes from aggregate validation; a clean workspace alone never implies completion. Stale evidence requires checks; unexpected drift requires inspection before edits.

Before implementation, save the actual user request and constraints in a repository file and bind it with `checkpoint-delivery.py --request-file docs/assignments/REQUEST.md`. Existing user authorization suffices; do not ask again to create this record. A saved AppSpec alone does not replace the request. The checkpoint requires a current request hash before starting an AC, gate or implementation phase. Later checkpoints inherit it; changing the saved request requires inspection and explicit `--request-file` recapture.

Use `delivery-work.py` to register a capability package and assignment-local boundaries; keep `checkpoint-delivery.py` for status updates and single-AC/gate checkpoints. Follow [flow-delivery-contract.md](flow-delivery-contract.md). Add specialist contracts and other task-specific inputs with `--required-read`; additions preserve earlier reads. The tool automatically includes app-spec.json, product/domain/data/design/quality prose, the active AC's FLOW/SCREEN files and the saved request, and captures their hashes. Resume and final validation reject missing or changed required inputs. Clear resolved items explicitly with `--clear-pending-checks ID` and `--clear-blockers ID` when checks actually completed or a decision arrived. `--reconcile-drift "inspected explanation"` acknowledges changes outside prior boundaries or a new Git HEAD; it never authorizes changing user files.

Checkpoint at assignment start, meaningful progress/check results and before interruption/return. Automate adjacent ingest/checkpoint operations and use feature globs; repeated filename bookkeeping is unnecessary. Commit before final audit/verification. A commit invalidates fingerprints even when code is unchanged; inspect the commit, checkpoint with an explanation and rerun verification. Do not rewrite old receipts to a new HEAD.

## Specialist and direct requests

Before a multi-step assignment, save the request and constraints in a repository file. Orchestrated assignments include assignment ID, obligation IDs, owner, base fingerprint and file boundaries. Direct tasks may use an explicit standalone assignment ID and task ID without creating a full application ledger.

Use the shared script at `vibe-developer/scripts/specialist-state.py`:

```text
python specialist-state.py checkpoint <repo> --assignment-id ASSIGN-1 --owner vibe-domain-engineer --obligation-id AC-001 --file-boundary domain/** --required-read docs/assignments/ASSIGN-1.md --pending-check "Run domain tests" --next-action "Finish the recurrence boundary case"
python specialist-state.py resume <repo> --assignment-id ASSIGN-1
```

Checkpoint after meaningful partial progress and before interruption/return. A command request may precede final handoff; do not republish unchanged recovery state for each short wait. Each packet is immutable and contains current files, pending checks, blockers, required reads and next action. After compaction, use the newest packet for that assignment, reread the request and decisions, inspect drift and continue only within its boundaries. On final hand-off, checkpoint with `--status returned`; an old active packet is not a new assignment. Specialists never edit the orchestrator ledger.

Specialist checkpoints inherit existing pending checks, blockers and required reads. `--pending-check` and `--blocker` add items; omitting them never clears saved state. Resolve an exact saved item with `--resolve-pending-check "saved check"` or `--resolve-blocker "saved blocker"` and `--resolution-reason "receipt or accepted decision"`. The lock serializes updates, and the new packet records its predecessor and resolutions. A returned assignment is terminal: resume reports `safeToContinue: false`; new work requires a new assignment ID. Returning preserves unresolved checks/blockers, which must also be transferred in the immutable hand-off for the orchestrator to handle; it does not claim application completion.

## User decisions

Capture material user steering as soon as it arrives, before depending on conversation memory. Save the exact message in `docs/decisions/DEC-ID-user.txt`, including its actual message identifier or a durable locally assigned capture identifier. Never invent consent. Existing user authorization is sufficient; do not ask again merely to populate the record.

```text
python record-decision.py <repo> --id DEC-1 --kind waiver --obligation-id AC-001 --source docs/decisions/DEC-1-user.txt --message-id captured-user-message-1 --quote "exact authorizing text" --rationale "Why this scope is waived"
```

Kinds: `steering`, `waiver`, `spec-change`. The immutable JSON has exact obligation IDs, rationale, accepted status, user quote and source hash. Use `--supersedes DEC-OLD` for a replacement; superseded records no longer authorize a waiver. Arbitrary Markdown/source-file references are invalid waivers. Validators establish provenance structure and scope; the auditor must still confirm the user's text authorizes the decision.

## AppSpec revision

When the user approves a changed specification, capture a `spec-change` decision with `--obligation-id AppSpec`, then run:

```text
python reconcile-spec.py <repo> --app-spec app-spec --decision-reference docs/decisions/DEC-2.json --expected-ledger-digest <digest>
```

The command strictly validates the new spec, archives the previous ledger under `.vibe/history`, records added/removed/reopened obligations, adopts the new fingerprint/inventory and clears current closure bindings. It conservatively reopens all current obligations because prose can change their meaning. Previous production/test evidence, decisions, receipts and audits remain in history. Inspect existing implementation and revalidate; do not blindly rebuild working code.

## Audit attempts and interruption

`create-audit-request.py` creates `.vibe/audits/<request-id>/request.json` under the ledger lock and binds its hash. Use an explicit `--request-id AUDIT-REQUEST-ID` to recover an orphan created before process termination; it is reusable only with the exact original state/digest/context. Resume lists orphan requests. If the ledger already contains the binding, continue that attempt rather than recreating it.

Run `run-acceptance-audit.py <repo> --request .vibe/audits/<request-id>/request.json`. It launches a fresh ephemeral Codex process, captures the host thread event, exact argv, input/output hashes, exit status, and before/after fingerprints. The child returns audit JSON; the launcher writes `audit.json` and `launch.json`. The child must not fabricate launch evidence. No implementation conversation is passed. If the CLI or required checks are unavailable, preserve the blocker.

After GAPS, interruption, failure or further code changes, retain the attempt, fix/revalidate locally and create a new request ID. Audits are immutable; current pointers live in the ledger and previous pointers in `auditHistory`. The request/launch/audit/final times must follow actual execution order. Render reports only after final ledger mutation so their parity remains current.

Receipts need `executionStatus`, `startWorkspaceFingerprint` and `workspaceFingerprint`. Missing fields are format errors. Targeted receipts also require registered inputScopeId and start/end input fingerprints; integration/final receipts use global inputs. The final receipt must start after the current audit completes and cover all verified obligation/surface pairs. Waived and externally blocked gates require their decisions/blockers, not fabricated successful commands. A later successful run may supersede a failed/interrupted run; preserve both files.

Each audit-time check also requires `receiptRef` and `receiptSha256` identifying its exact global `kind: integration` runner receipt under `.vibe/receipts`. Copy argv, outcome, timestamps, fingerprints and coverage from that receipt; the validator checks all fields and the captured log hash. Audit coverage includes the managed-operation IDs being proved, as well as AC/gate IDs. Inline-only audit checks and ledgers missing durable request/read hashes are unsupported. Never rewrite historical artifacts into the current format.

## Asset work

Across all assignments, an executed check is not necessarily a resolved check. After a failed run, retain the pending rerun/fix action until a successful result resolves it. Keep a partially implemented AC `in-progress`; use `implemented-unverified` only when its required implementation exists and verification is still outstanding. A narrative next action does not replace these structured fields.

For Assets Creator checkpoints preserve ASSET IDs, brief and manifest paths, completed output/source paths with hashes, pending variants/generation, reviewed evidence and next action. Resume by reading these files before generating again. Working evidence lives outside AppSpec; update the existing manifest instead of duplicating task status. Only Developer advances the linked AC/asset gate.
