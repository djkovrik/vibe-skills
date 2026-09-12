---
name: vibe-developer
description: Orchestrate end-to-end Kotlin Multiplatform Android/iOS application delivery from an approved Vibe AppSpec or structured implementation brief. Use for "implement this app", "build this KMP feature", "execute this AppSpec", repository-wide delivery planning, multi-specialist routing, spec-to-code convergence, or coordinated architecture, localization, UI, previews, Paparazzi goldens, Lazyweb design review, data, platform, testing, CI, and release automation.
---

# Vibe Developer

## When to use

Use this skill as the entry point for a complete application or a cross-cutting feature. Accept an AppSpec path or a sufficiently structured implementation brief. Do not run a product interview or silently invent missing product decisions.

For a narrow task, route directly to the owning specialist using [routing-matrix.md](references/routing-matrix.md).

## Inputs

- AppSpec directory or structured task description
- target repository path
- explicit user decisions and constraints
- allowed build platforms and credentials

Read [flow-delivery-contract.md](references/flow-delivery-contract.md) for capability packages, assignment-local evidence, early integration and verification cadence. Read [app-spec-contract.md](references/app-spec-contract.md) before consuming an AppSpec and [delivery-ledger-contract.md](references/delivery-ledger-contract.md) before changing the target repository. Read [recovery-contract.md](references/recovery-contract.md) for durable decisions, specialist recovery, accepted spec revisions, and commit reconciliation. Read [localization-contract.md](references/localization-contract.md) whenever the app has user-visible bundled text or localized local data. Read [ci-release-contract.md](references/ci-release-contract.md) before the late-stage CI/release pass. Read [source-registry.md](references/source-registry.md) only when consulting the local Blinkly/Tackle adaptations. Read [spec-kit-mapping.md](references/spec-kit-mapping.md) only when the upstream artifacts came from Spec Kit or OpenSpec.

## Workflow

1. Run read-only `resume-delivery.py --compact` at turn start and after compaction/interruption. It establishes safety to continue, not completion. Read the saved active packages, pending jobs, decisions and changed/lost inputs. Discover scoped instructions and inspect Git state before editing.
2. Validate the approved current AppSpec, independently compare canonical IDs with normative prose, save the actual request, initialize the ledger and checkpoint. Use the host availability matrix to identify macOS/Xcode/credentials blockers at intake; never relabel repository failures as external.
3. Map modules, dependency direction, toolchains, entry points, component/Store/Manager/DI boundaries, resources, platform services and test hosts. Preserve the specialist architecture, localization, privacy and release obligations below.
4. Establish a foundation: reachable production root and save/read/restart flow, early Detekt/Kover configuration, and an actual production render smoke. Require nonzero scanner discovery, newly generated expected PNGs and working production resources in light/dark and RU/200% before expanding the matrix. Use `validate-render-smoke.py` with the inventory shape in the flow contract.
5. Schedule bounded capabilities with multiple related ACs. Register multiple independent packages and non-overlapping assignments through `delivery-work.py`; skills are expertise routes, not one agent per layer. Start a dependent package when its required behavioral contract is accepted/current (`contract-ready`) or its dependency AC is verified/waived. A deferred golden does not block unrelated behavior.
6. Give new independent agents `fork_turns: none` and the generated compact assignment packet: goal, obligations, write boundaries, contract inputs, required reads, commands and return criteria. Reuse the same agent for continuation. Publish contract readiness before the final handoff; keep shared root/resource/catalog writes with one named owner.
7. Register reviewed transitive check scopes for each capability/module. Use `**` only with an explicit uncertainty rationale, never by inheriting the first package's scope. Request compile and the smallest meaningful behavioral tests as soon as ready. Combine already-ready compatible Gradle checks with `check-batch`; do not delay useful feedback to fill a batch.
8. Keep one Gradle owner per workspace. Global Windows matrices default to `--max-workers=1 --no-parallel`; override only with measured resource evidence. Observe job stages and streaming logs. A receipt-written job has finished execution even if binding is pending. Recover via `retry-bind`, never rerun a successful command to repair bookkeeping.
9. Inspect and ingest immutable assignment handoffs. Evidence is registered once and linked by exact obligation/surface coverage. Replace accepted obsolete anchors through `reconcile-evidence`; retain history. Resolve pending checks/blockers by their IDs and actual evidence. Checkpoint meaningful implementation progress and before interruption, not each filename or short wait.
10. Integrate each completed capability into the production root. Compile previews during UI work; record/inspect/verify affected goldens at stable boundaries. Run the complete ordered Lazyweb review once on stable screens, one report in flight, while unrelated work continues; repeat affected screens after material fixes.
11. Complete repository/platform checks and the five CI/release workflows with project setup documentation. Measure the filtered Kover baseline and keep its minimum fixed. Run readiness (`validate-delivery-ledger.py --mode readiness`) before freeze; resolve cheap blockers before expensive checks.
12. Freeze implementation, run the full required integration checks once, and create an immutable audit request. `run-acceptance-audit.py` launches an independent fresh process that rebuilds inventory and reviews current receipts, commands, assertions, anchors and logs. It executes missing/suspect checks, not a mandatory duplicate matrix. Keep the exclusive runner lease with the auditor while it runs checks.
13. After a current PASS, use `delivery-work.py` action `close` to bind the audit and its integration receipts in `closureManifest`, render both reports, then run `validate-delivery-ledger.py --mode closure`. There is no post-audit full run. Report `locallyVerified`, `implementationComplete`, and `releaseReady` separately. A partial platform AC remains unverified globally; obtain a new audit when missing external evidence arrives.

Record observed validation, agent-wait and repair intervals through action `timing`; runner jobs record queue/execution/binding stages automatically. `delivery-timing.py` reports interval unions; overlapping categories must not be summed as elapsed time.

## Decision rules

Apply this trust order:

1. explicit user decisions and current AppSpec;
2. target-repository instructions, code, tests, catalog, and build logic;
3. current official library/platform documentation;
4. user-accepted entries in [knowledge-index.md](references/knowledge-index.md);
5. labeled Blinkly/Tackle adaptations;
6. general engineering heuristics.

Expose conflicts. Request a decision only for materially different outcomes, then add a test or check that fixes the chosen contract.

Prevent overlapping edits by giving each file/change one owner. Let the orchestrator sequence hand-offs; do not ask specialists to independently redesign the same boundary.

Treat `.vibe/delivery-ledger.json` as the only editable delivery-state source and mutate it atomically only with the previous digest. Generated reports are projections; hand-offs, receipts, the audit request, and the audit are immutable files. Record material user steering immediately with `record-decision.py` from a captured exact user message. A waiver requires an accepted decision JSON scoped to the exact obligation with captured user approval; arbitrary file links are invalid. `blocked-external` is legal only for platform/external/release gates and never with `release-ready`. Any normative AppSpec or input-content change makes closure evidence stale; intermediate targeted evidence is invalidated by its registered input scope, not unrelated files. Adopt an approved revision only with `reconcile-spec.py`; never reset the ledger to discard history. Commit metadata is provenance: an identical-content commit does not invalidate checks. Approved technical asset-path corrections use narrow reconciliation; normative changes invalidate affected closure.

## Validation

- Require zero exit codes for claimed checks.
- Use the target Gradle wrapper and focused tasks.
- Redirect stdout/stderr to a UTF-8 log. On success report only the task and exit code. On failure inspect the tail and targeted matches before requesting verbose diagnostics.
- Do not update goldens until the visual difference is approved.
- Treat product UI as incomplete until every primary screen and applicable state has deterministic light/dark previews, the required font-scale/locale/device stress variants exist, ComposablePreviewScanner-generated Paparazzi tests compile, approved goldens are recorded, and verification passes.
- Reject custom generic Success/Failure wrappers that duplicate Kotlin `Result`, production `MutableValue<Model>` state outside a Store, stateful components that call repositories directly, and nested `Result<Result<T>>` Manager boundaries.
- Reject flattened component packages that place Store/Default/Manager beside the public component contract, Compose-local preview fakes that replace the component module's `*ComponentPreview`, and non-Decompose composition roots that bypass required `*Module` factories by constructing outward-provided implementations directly.
- Host screenshot testing in the Compose UI/resource-owning module by default; require a written build/aggregation constraint for a dedicated screenshot module.
- Compile previews during UI edits; smoke-check scanner/Paparazzi early, then record/inspect/verify affected goldens at stable screen or capability boundaries. Keep deferred golden ACs implemented-unverified. After recording approved goldens, require Product Designer to run the current Lazyweb review workflow across the declared primary-screen/flow coverage as a strict ordered queue. Allow exactly one screen/report in flight for the task: never batch screens or parallelize review requests, and do not submit the next screen until the previous report reaches terminal completion, has been retrieved, and its URL, coverage, and findings are recorded. Do not claim a full-app review when only one screen was reviewed. Perform this complete queue once on stable screens; repeat affected screens only for material redesign or unresolved findings, not on each AC closure. Unrelated permitted work may continue during report waits.
- Route objective rendering defects that violate the AppSpec (clipping, unintended wrapping, missing glyphs, insufficient contrast, missing/incorrect icons, inconsistent tokens) back to Compose/Product Designer and asset-file defects to Assets Creator. Request a user decision only when a fix changes approved product intent or needs an unavailable exact external brand input; creation from an approved brief is already part of implementation.
- Re-record and re-verify only approved visual changes, then close or explicitly waive every blocking design-review finding with rationale.
- Require applicable domain, Store/component, persistence/network/sync, UI golden, Android, iOS, quality, and release checks. State why any check was unavailable.
- Require public-contract Decompose component tests to lead application acceptance coverage; prefer the separate `root` component module for their centralized suite unless dependency direction requires a documented alternative.
- For monetized apps, require Yandex Mobile Ads as the preferred/default and only provider supported by the lightweight privacy flow. Use the canonical production privacy-region endpoint from `$vibe-monetization-engineer` as-is; its service contract, operations, and endpoint-specific release readiness are accepted, so do not create a per-app backend, requalify/smoke-test the service, or add an endpoint release gate. Verify only the consuming app's maximum 72-hour cache, strict/fail-closed response handling, policy-version-bound app-owned consent, required-form-only UX, privacy-before-init, `YandexAds.setUserConsent(...)` before every initialization, and blocked initialization/requests for declined, unresolved, expired, or error states. Require a new privacy inventory and explicit product/legal approval before adding a provider that needs a certified CMP or TCF strings.
- Treat the late-stage CI baseline as incomplete unless `AnalysisAndTest.yml`, `MeasureTestCoverage.yml`, `CodeCoverageBadge.yml`, `CreateAndroidRelease.yml`, `PublishAndroidRelease.yml`, and `docs/CI-RELEASE-SETUP.md` exist, are adapted to the target repository, and pass the static/runtime checks available without credentials.
- Do not claim release automation ready when GitHub/Firebase/Google Play/Google Cloud prerequisites remain unverified. Distinguish committed automation from configured external state.
- Require `en` as the default/base locale and complete fallback key set, with `ru` as the initial additional locale. Derive the active locale from the operating system only; reject an in-app language picker, persisted locale preference, or app-specific locale override. Require every declared locale to cover the shared keys, reject persisted/resolved translations for local catalogs, and scan production source for hardcoded user-visible strings. Native-only text must follow the same system-locale/EN-default contract in Android/iOS localization resources.
- Treat warnings separately from failures.
- Reject report-only Detekt integration, stale copied Detekt versions/configs, automatic baseline regeneration, whole-repository Kover denominators, and coverage thresholds chosen before measuring the filtered target repository.
- Reject completion when AppSpec/ledger fingerprints are stale, the latest current receipt for any obligation/surface fails, the closure manifest is absent/invalid, a hand-off is uninspected, a waiver reference is fictitious, either generated report drifts, or audit request/audit binding is missing or stale.

## Escalation/hand-off

- Modules/build/release: `$vibe-project-architect`
- Business vocabulary/calculation: `$vibe-domain-engineer`
- Component tree/navigation: `$vibe-decompose-engineer`
- Store/state orchestration: `$vibe-mvikotlin-engineer`
- Permissions/notifications/alarms/native services: `$vibe-platform-engineer`
- REST/Ktor/OAuth transport: `$vibe-network-engineer`
- SQLDelight/settings: `$vibe-persistence-engineer`
- Snapshot/conflict coordination: `$vibe-sync-engineer`
- Product UI/design evidence: `$vibe-product-designer`
- Icons/logos/illustrations and Compose resource delivery: `$vibe-assets-creator`
- Previews/Paparazzi/goldens: `$vibe-visual-testing`
- Ads/privacy integration: `$vibe-monetization-engineer`
- Non-visual tests/coverage: `$vibe-test-engineer`
- Independent completeness audit: fresh-context `$vibe-acceptance-auditor`

Use Compose Expert through Product Designer for Compose APIs. Use Lazyweb before product UI design or critique.

## Reusable learning

Propose, but never auto-apply, a reusable pattern when it repeats across independent features, solves a stable cross-cutting problem, turns ambiguity into a testable contract, is supported by official docs plus target tests, or is explicitly declared by the user. Include target reference, evidence, scope, trade-offs, and migration impact. After approval, update the smallest specialist `learned-patterns.md`, a validation example, and [knowledge-index.md](references/knowledge-index.md).
