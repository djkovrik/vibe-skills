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

Read [app-spec-contract.md](references/app-spec-contract.md) before consuming an AppSpec. Read [localization-contract.md](references/localization-contract.md) whenever the app has user-visible bundled text or localized local data. Read [ci-release-contract.md](references/ci-release-contract.md) before the late-stage CI/release pass. Read [source-registry.md](references/source-registry.md) only when consulting the local Blinkly/Tackle adaptations. Read [spec-kit-mapping.md](references/spec-kit-mapping.md) only when the upstream artifacts came from Spec Kit or OpenSpec.

## Workflow

1. Validate the AppSpec with `scripts/validate-app-spec.py`. Stop on errors and unresolved blocking questions; surface warnings and non-blocking open questions.
2. Find the nearest `AGENTS.md` and other instruction files. Record their scope.
3. Inspect `git status`; preserve all user changes.
4. Read settings/root build files, version catalog, convention plugins, platform entry points, module build files, CI, and release configuration.
5. Map modules, source sets, dependency direction, targets, toolchains, minimum OS/API, variants, package IDs, and composition roots.
6. Locate domain contracts, Decompose components, Stores, Managers, persistence, network, sync, platform services, localization resources/key mappings, preview component implementations, screenshot host, and tests.
7. Detect installed `vibe-*`, Compose Expert, and Lazyweb capabilities.
8. Build a dependency-aware plan from the smallest affected subgraph. Assign one owner per change and explicit hand-offs. For every production component `Value<Model>`, require `Default component -> retained Store -> State-to-Model mapper -> immutable Value<Model>`; data-facing Stores use Managers, standard Kotlin `Result`, and cancellation-aware `unwrap`. Make Decompose component tests through public contracts the primary application test strategy, centralized in the separate `root` component module when structurally valid. For localized local data, make stable IDs/keys, Compose resource ownership, native fallbacks, and key-completeness checks explicit deliverables. For product UI, make component-module ownership, the Preview implementation, icon/asset decision, preview matrix, Compose-owned golden infrastructure, and post-golden design review explicit deliverables rather than optional polish. For ads, default to Yandex Mobile Ads and require the custom privacy-region endpoint plus app-owned consent gate before SDK initialization/loading: no global consent popup, only a fresh endpoint decision may establish applicability, protected-region acceptance is required, and unresolved/expired/error states fail closed for ads. Pass the current allowed consent state to Yandex before every initialization. Do not treat the endpoint as an IAB TCF CMP or use this lightweight flow with demand/mediation partners that require a certified CMP. Make the adapted baseline workflows and repository setup guide explicit late-stage deliverables owned by Project Architect.
9. Execute only necessary stages:

```text
AppSpec validation -> repository preflight -> architecture
-> product/design evidence -> icon and visual-asset gate
-> domain -> persistence/network/sync/platform
-> Decompose -> MVIKotlin -> Compose -> monetization
-> non-visual tests -> previews -> Paparazzi/scanner -> approved goldens
-> full-UI Lazyweb review -> approved fixes and golden re-verification
-> Detekt/Kover/build readiness gate -> baseline CI/release automation
-> quality/platform/release checks
```

10. When Detekt, Kover verification, numeric line coverage, and the required debug/platform builds pass, immediately apply [ci-release-contract.md](references/ci-release-contract.md). Create all five adapted baseline workflows under `.github/workflows/` and a project-specific `docs/CI-RELEASE-SETUP.md`; do not wait for external credentials. Leave unavailable external publication truthfully blocked and document the exact setup steps.
11. Run targeted checks first. Use `scripts/run-gradle.ps1` on Windows.
12. Reconcile implementation against requirement and acceptance IDs.
13. Report implementation, owners used, requirement coverage, changed modules, checks, unrun checks, risks, deviations, CI/release readiness, external setup blockers, and reusable-learning candidates.

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

## Validation

- Require zero exit codes for claimed checks.
- Use the target Gradle wrapper and focused tasks.
- Redirect stdout/stderr to a UTF-8 log. On success report only the task and exit code. On failure inspect the tail and targeted matches before requesting verbose diagnostics.
- Do not update goldens until the visual difference is approved.
- Treat product UI as incomplete until every primary screen and applicable state has deterministic light/dark previews, the required font-scale/locale/device stress variants exist, ComposablePreviewScanner-generated Paparazzi tests compile, approved goldens are recorded, and verification passes.
- Reject custom generic Success/Failure wrappers that duplicate Kotlin `Result`, production `MutableValue<Model>` state outside a Store, stateful components that call repositories directly, and nested `Result<Result<T>>` Manager boundaries.
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

Use Compose Expert through Product Designer for Compose APIs. Use Lazyweb before product UI design or critique.

## Reusable learning

Propose, but never auto-apply, a reusable pattern when it repeats across independent features, solves a stable cross-cutting problem, turns ambiguity into a testable contract, is supported by official docs plus target tests, or is explicitly declared by the user. Include target reference, evidence, scope, trade-offs, and migration impact. After approval, update the smallest specialist `learned-patterns.md`, a validation example, and [knowledge-index.md](references/knowledge-index.md).
