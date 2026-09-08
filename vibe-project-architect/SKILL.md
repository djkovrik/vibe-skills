---
name: vibe-project-architect
description: Design and change Kotlin Multiplatform project structure, Gradle modules and source sets, dependency direction, convention plugins, version catalogs, Compose Multiplatform resource ownership, manual dependency injection, Android/iOS entry points, Paparazzi and ComposablePreviewScanner screenshot-test surfaces, CocoaPods/Xcode linkage, quality gates, GitHub Actions CI, coverage reporting, signing contracts, Android release workflows, and GitHub/Firebase/Google Play/Google Cloud setup guides. Use for module graphs, scaffolding, localization-resource wiring, visual-test build wiring, build logic, platform startup, architecture migrations, CI pipelines, or release setup.
---

# Vibe Project Architect

## When to use

Own module/build/release architecture. Do not own feature business rules, component state, or UI design.

## Inputs

Read the target AppSpec, repository instructions, module/build graph, catalogs, entry points, CI, and release files. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md) when the app has bundled user-visible text. Read the shared [CI and release contract](../vibe-developer/references/ci-release-contract.md) for late-stage automation. Read [module-boundaries.md](references/module-boundaries.md), [manual-di.md](references/manual-di.md), [build-logic-and-quality.md](references/build-logic-and-quality.md), or [platform-entrypoints-and-release.md](references/platform-entrypoints-and-release.md) as applicable. Consult the shared [source registry](../vibe-developer/references/source-registry.md) only for labeled adaptations.

## Workflow

1. Map current modules, source sets, plugins, and dependencies.
2. Extract versions and target requirements from the project.
3. Define the minimal affected graph and ownership boundaries. Treat a screen-level Decompose component as a component-module boundary by default when that module can own its root contract, `integration` Default/Preview/mappers, `store` Store/provider, `domain` Manager/models, and wiring.
4. Keep domain contracts inward and implementations/platform code outward.
5. Design manual composition roots and explicit startup order. For every non-Decompose implementation module that provides constructed dependencies outward, define a `di/*Module.kt` output interface, optional `*ModuleDependencies` input interface, same-named top-level factory, and lazy-owned outputs.
6. When the product has bundled localized text, assign one common resource-owning module, configure Compose Multiplatform Resources and generated accessors, keep the complete English default/base set in `values`, and keep native-only EN-default fallback resources in their platform source sets. Do not scaffold locale-selection settings, app-specific overrides, or language-picker infrastructure.
7. When the product has Compose UI, host Paparazzi, ComposablePreviewScanner, generated Android unit tests, and snapshots in the Compose UI/resource-owning module by default. Create a dedicated Android-host screenshot module only for a documented constraint such as aggregating multiple UI artifacts or an incompatible plugin/source-set graph. Provision version-catalog entries, compatible tooling, task wiring, record/verify tasks, Git LFS, and CI artifacts as default scaffolding.
8. Install the newest official Detekt release, or the newest compatible release only with an explicit toolchain exception; generate its complete default config at `detekt/base-config.yml`, merge the Blinkly-adapted semantic thresholds when that source is available, and make Warning/Error findings plus configuration warnings fail the strict task. Configure Kover's positive scope around domain logic and production Decompose behavior, measure the filtered baseline, immediately commit a baseline-derived minimum, and pass Kover verification/XML/numeric line coverage. Then, after required debug/platform builds pass, create the five adapted baseline workflows and `docs/CI-RELEASE-SETUP.md` required by the shared CI/release contract. Scaffold credential-dependent publication immediately, but keep it truthfully blocked until external setup is complete.
9. Add remaining build logic, checks, CI, and migration sequencing with rollback points.
10. Verify Android plus available iOS/Pod/Xcode contracts.

## Decision rules

- Keep domain and public feature contracts independent of UI/infrastructure.
- Keep generated Compose resource types at the presentation/resource boundary; domain and persistence depend only on stable language-neutral IDs/keys.
- Put platform implementations in platform source sets.
- Require narrow `*Module` output interfaces, `*ModuleDependencies` input interfaces when inputs exist, same-named top-level factories, and `by lazy` outputs for non-Decompose implementation modules that provide dependencies outward. A zero-input module omits only the dependencies interface. Add a DI framework only by explicit decision.
- Keep Decompose configs free of services.
- Prefer one module per screen-level Decompose component or cohesive nested flow when it enforces dependency/ownership/test boundaries. Group trivial callback-only leaves when a new module would enforce nothing; record the exception.
- Treat Gradle artifact, Podfile, lockfile, generated framework, and Xcode linkage as one native dependency contract.
- Verify current versions in official sources; never copy a reference project snapshot.
- Plan quality gates with the module graph. Detekt must fail on findings at the configured gate severity and Kover must measure only the declared domain/Decompose scope with a baseline-derived minimum; neither gate may be report-only.
- Co-locate screenshot tests with the module that owns production previews/resources unless a recorded build constraint requires aggregation/isolation.
- Make generated preview tests an explicit input to Android unit-test compilation and Paparazzi record/verify tasks; keep discovery package-scoped and configuration-cache behavior honest.

Create a reachable production root and one persistence/restart flow with the first capability package. Validate scanner/Paparazzi hosting early with a small production preview before growing the matrix; defer neither entry-point integration nor basic toolchain compatibility until the first golden-heavy AC.

## Validation

Check settings inclusion, component-module boundaries/exceptions and package roles, dependency direction, source-set compilation, catalog/convention use, per-module manual-DI contracts, composition-root use of module factories instead of direct concrete construction, lazy ownership, Compose resource generation, English default/fallback and locale packaging, native fallback resource packaging, screenshot host ownership/rationale, generator-to-compile task dependency, Paparazzi record/verify availability, snapshot/Git-LFS paths, CI diff/report artifacts, Android builds, available iOS framework/Pod/Xcode builds, the selected current Detekt version and generated `detekt/base-config.yml`, strict Detekt failure behavior, Kover scope inventory/baseline/committed minimum/verification, all five baseline workflow files, CI syntax, minimum permissions, concurrency, signing-variable contract, release artifacts, and the project-specific external setup guide. Distinguish local validation from credential-dependent end-to-end publication.

## Escalation/hand-off

Hand pure rules to Domain, UI navigation to Decompose, platform services to Platform, and feature tests to Test Engineer. Return the approved module/factory boundaries to Developer before parallel implementation.

## Orchestrated evidence hand-off

When `$vibe-developer` assigns work, follow [Specialist hand-off Protocol 2.0](../vibe-developer/references/specialist-handoff-contract.md). Accept assignment, AC/gate IDs, assignment baseline reference, and non-overlapping file boundaries. Write one immutable `.vibe/handoffs/<id>.json` with assignment-local baseline/result evidence, allowed/changed files, exact production/test evidence, completed non-Gradle checks, requested Gradle commands and blockers. The orchestrator alone inspects and ingests it, writes the ledger and owns Gradle. Do not claim completion.

## Reusable learning

Follow the package learning policy. Propose approved architectural rules for [learned-patterns.md](references/learned-patterns.md); never change it automatically.

## Recovery of unfinished work

For multi-step work, including direct specialist requests, follow the shared [recovery contract](../vibe-developer/references/recovery-contract.md). Save the durable assignment before edits, checkpoint unfinished work with `specialist-state.py`, and resume from its packet after compaction or interruption, including inside the same turn. Preserve new user decisions immediately. A final hand-off does not replace intermediate checkpoints.

## Asset resource wiring

For icons/logos/illustrations apply the [asset contract](../vibe-assets-creator/references/asset-contract.md). Own resource-module placement, Compose resource dependency/plugin and generated accessor visibility for Android/iOS and screenshot hosts. Assets Creator owns XML/PNG files; Compose Expert owns typed usage. Keep runtime artwork in commonMain Compose Resources. Platform-specific launcher/store derivatives are additional exports with their native constraints.

## Foundation feedback

Before expanding feature or preview matrices, establish a real render smoke with nonzero discovery and new expected PNGs from production resources, including light/dark and RU/200%. Missing resource classes or zero snapshots fail the smoke; do not execute every state against a broken harness. Configure Detekt and filtered Kover early; measure the coverage baseline once meaningful implementation exists. Keep full coverage obligations and defer only execution that depends on stable screens.

Use the current [flow coordination interfaces](../vibe-developer/references/flow-delivery-contract.md#current-coordination-and-evidence-interfaces) for compact assignment inputs, early contract readiness, exact evidence coverage and pending-work IDs.
