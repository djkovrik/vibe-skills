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

Read [app-spec-contract.md](references/app-spec-contract.md) before consuming an AppSpec and [delivery-ledger-contract.md](references/delivery-ledger-contract.md) before changing the target repository. Read [localization-contract.md](references/localization-contract.md) whenever the app has user-visible bundled text or localized local data. Read [ci-release-contract.md](references/ci-release-contract.md) before the late-stage CI/release pass. Read [source-registry.md](references/source-registry.md) only when consulting the local Blinkly/Tackle adaptations. Read [spec-kit-mapping.md](references/spec-kit-mapping.md) only when the upstream artifacts came from Spec Kit or OpenSpec.

## Workflow

1. At the beginning of every turn, if `.vibe/delivery-ledger.json` exists, run read-only `scripts/resume-delivery.py` before relying on prior conversation. Follow its active AC, drift classification, pending hand-offs, blockers, and mandatory next action. Preserve expected drift for reconciliation; do not edit on unexpected drift. If no ledger exists, strictly validate an approved AppSpec 2.0 with `scripts/validate-app-spec.py --require-current`. Any 1.x artifact is an unsupported protocol; do not migrate, delete, or reinitialize it automatically.
2. Rediscover every applicable `AGENTS.md` and other repository instruction file. Store scoped paths and SHA-256 hashes at the next checkpoint.
3. Inspect `git status`; preserve all user changes.
4. Read settings/root build files, version catalog, convention plugins, platform entry points, module build files, CI, and release configuration.
5. Map modules, source sets, dependency direction, targets, toolchains, minimum OS/API, variants, package IDs, and composition roots.
6. Locate domain contracts, Decompose components and their package roles, Stores, Managers, non-Decompose `di/*Module.kt` boundaries, composition roots, persistence, network, sync, platform services, localization resources/key mappings, component-module preview implementations, screenshot host, and tests.
7. Detect installed `vibe-*`, Compose Expert, and Lazyweb capabilities.
8. Before the first code edit, run `scripts/init-delivery-ledger.py`, compare the shared canonical inventory with normative prose, then use `checkpoint-delivery.py` with the current ledger digest, active AC, owner, boundaries, phase, and exact next action. Build a dependency-aware plan as vertical AC slices. Assign one owner per non-overlapping change and require the immutable JSON contract in [specialist-handoff-contract.md](references/specialist-handoff-contract.md). Keep all existing component, Store, Manager, preview, DI-module, localization, UI/golden, privacy, ads, and CI deliverables explicit.
9. Execute only necessary concerns inside each vertical slice. For each assigned AC, complete the production contract, data/domain path, Store/component path, UI/platform wiring, required tests, targeted verification, and evidence package before moving its ledger entry to `verified`:

```text
approved AppSpec 2.0 -> ledger initialization and checkpoint
-> vertical AC slices with immutable hand-offs and targeted receipts
-> repository gates -> immutable audit request -> fresh closure audit
-> one final receipt covering all obligations -> aggregate final validation
```

10. Treat the readiness stage as a real quality gate. Require the newest official Detekt release (or a documented newest-compatible toolchain exception), a complete generated `detekt/base-config.yml` with current-schema Blinkly threshold adaptations when available, configuration validation, and strict failure on Warning/Error findings. Require Kover filters limited to the declared domain and production Decompose scope, a recorded first filtered baseline, an immediately committed baseline-derived minimum, XML/numeric output, and passing verification. When those gates and the required debug/platform builds pass, immediately apply [ci-release-contract.md](references/ci-release-contract.md). Create all five adapted baseline workflows under `.github/workflows/` and a project-specific `docs/CI-RELEASE-SETUP.md`; do not wait for external credentials. Leave unavailable external publication truthfully blocked and document the exact setup steps.
11. Run targeted checks first. On Windows, this orchestrator is the only Gradle owner and uses `scripts/run-gradle.ps1` to write structured Protocol 2.0 receipts. A receipt names exact argv/tasks, covered obligation/surface pairs, timestamps, current fingerprint, real exit code, and log hash. Specialists request commands but never invoke Gradle themselves.
12. Checkpoint before boundary expansion, after hand-off ingestion, before and after long checks, and before every turn ends. After each milestone reread AppSpec and the ledger. Import only inspected immutable hand-offs with `ingest-handoff.py`; conversation is not evidence. Preserve every unfinished obligation as an individual status.
13. When every local entry is closed, checkpoint, create immutable `audit-request.json` with `create-audit-request.py`, stop implementation, and invoke `$vibe-acceptance-auditor` in its required fresh context. On `GAPS`, resume fixes and require a new request and clean audit. On `BLOCKED`, preserve the exact blocker. Without a separate context, do not claim completion.
14. After fresh `PASS`, run one explicit `final` receipt covering every applicable obligation and verification surface, atomically bind it into the ledger, render both reports, and invoke `validate-delivery-ledger.py` once. That validator performs strict AppSpec, inventory, receipt ordering, audit, and report-parity checks and reports `implementation-complete` and `release-ready` separately.

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

Treat `.vibe/delivery-ledger.json` as the only editable delivery-state source and mutate it atomically only with the previous digest. Generated reports are projections; hand-offs, receipts, the audit request, and the audit are immutable files. A waiver requires a reference to an existing durable user decision. `blocked-external` is legal only for platform/external/release gates and never with `release-ready`. Any AppSpec file or workspace fingerprint change makes completion evidence stale.

## Validation

- Require zero exit codes for claimed checks.
- Use the target Gradle wrapper and focused tasks.
- Redirect stdout/stderr to a UTF-8 log. On success report only the task and exit code. On failure inspect the tail and targeted matches before requesting verbose diagnostics.
- Do not update goldens until the visual difference is approved.
- Treat product UI as incomplete until every primary screen and applicable state has deterministic light/dark previews, the required font-scale/locale/device stress variants exist, ComposablePreviewScanner-generated Paparazzi tests compile, approved goldens are recorded, and verification passes.
- Reject custom generic Success/Failure wrappers that duplicate Kotlin `Result`, production `MutableValue<Model>` state outside a Store, stateful components that call repositories directly, and nested `Result<Result<T>>` Manager boundaries.
- Reject flattened component packages that place Store/Default/Manager beside the public component contract, Compose-local preview fakes that replace the component module's `*ComponentPreview`, and non-Decompose composition roots that bypass required `*Module` factories by constructing outward-provided implementations directly.
- Host screenshot testing in the Compose UI/resource-owning module by default; require a written build/aggregation constraint for a dedicated screenshot module.
- After recording approved goldens, require Product Designer to run the current Lazyweb review workflow across the declared primary-screen/flow coverage as a strict ordered queue. Allow exactly one screen/report in flight for the task: never batch screens or parallelize review requests, and do not submit the next screen until the previous report reaches terminal completion, has been retrieved, and its URL, coverage, and findings are recorded. Do not claim a full-app review when only one screen was reviewed.
- Route objective rendering defects that violate the AppSpec (clipping, unintended wrapping, missing glyphs, insufficient contrast, missing/incorrect icons, inconsistent tokens) back to Compose/Product Designer. Request a user decision only when a fix changes approved product intent or requires unresolved custom assets.
- Re-record and re-verify only approved visual changes, then close or explicitly waive every blocking design-review finding with rationale.
- Require applicable domain, Store/component, persistence/network/sync, UI golden, Android, iOS, quality, and release checks. State why any check was unavailable.
- Require public-contract Decompose component tests to lead application acceptance coverage; prefer the separate `root` component module for their centralized suite unless dependency direction requires a documented alternative.
- For monetized apps, require Yandex Mobile Ads as the preferred/default and only provider supported by the lightweight privacy flow. Verify the custom privacy-region endpoint contract, a maximum 72-hour cache, policy-version-bound app-owned consent, required-form-only UX, privacy-before-init, `YandexAds.setUserConsent(...)` before every initialization, and blocked initialization/requests for declined, unresolved, expired, or error states. Require a new privacy inventory and explicit product/legal approval before adding a provider that needs a certified CMP or TCF strings.
- Treat the late-stage CI baseline as incomplete unless `AnalysisAndTest.yml`, `MeasureTestCoverage.yml`, `CodeCoverageBadge.yml`, `CreateAndroidRelease.yml`, `PublishAndroidRelease.yml`, and `docs/CI-RELEASE-SETUP.md` exist, are adapted to the target repository, and pass the static/runtime checks available without credentials.
- Do not claim release automation ready when GitHub/Firebase/Google Play/Google Cloud prerequisites remain unverified. Distinguish committed automation from configured external state.
- Require `en` as the default/base locale and complete fallback key set, with `ru` as the initial additional locale. Derive the active locale from the operating system only; reject an in-app language picker, persisted locale preference, or app-specific locale override. Require every declared locale to cover the shared keys, reject persisted/resolved translations for local catalogs, and scan production source for hardcoded user-visible strings. Native-only text must follow the same system-locale/EN-default contract in Android/iOS localization resources.
- Treat warnings separately from failures.
- Reject report-only Detekt integration, stale copied Detekt versions/configs, automatic baseline regeneration, whole-repository Kover denominators, and coverage thresholds chosen before measuring the filtered target repository.
- Reject completion when AppSpec/ledger fingerprints are stale, the latest current receipt for any obligation/surface fails, the covering final receipt is absent/failed, a hand-off is uninspected, a waiver reference is fictitious, either generated report drifts, or audit request/audit binding is missing or stale.

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
- Previews/Paparazzi/goldens: `$vibe-visual-testing`
- Ads/privacy integration: `$vibe-monetization-engineer`
- Non-visual tests/coverage: `$vibe-test-engineer`
- Independent completeness audit: fresh-context `$vibe-acceptance-auditor`

Use Compose Expert through Product Designer for Compose APIs. Use Lazyweb before product UI design or critique.

## Reusable learning

Propose, but never auto-apply, a reusable pattern when it repeats across independent features, solves a stable cross-cutting problem, turns ambiguity into a testable contract, is supported by official docs plus target tests, or is explicitly declared by the user. Include target reference, evidence, scope, trade-offs, and migration impact. After approval, update the smallest specialist `learned-patterns.md`, a validation example, and [knowledge-index.md](references/knowledge-index.md).
