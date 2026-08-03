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
3. Define the minimal affected graph and ownership boundaries. Treat a screen-level Decompose component as a component-module boundary by default when that module can own its contract, Default/Preview implementations, Store, Manager, mappers, and wiring.
4. Keep domain contracts inward and implementations/platform code outward.
5. Design manual composition roots and explicit startup order.
6. When the product has bundled localized text, assign one common resource-owning module, configure Compose Multiplatform Resources and generated accessors, keep the complete English default/base set in `values`, and keep native-only EN-default fallback resources in their platform source sets. Do not scaffold locale-selection settings, app-specific overrides, or language-picker infrastructure.
7. When the product has Compose UI, host Paparazzi, ComposablePreviewScanner, generated Android unit tests, and snapshots in the Compose UI/resource-owning module by default. Create a dedicated Android-host screenshot module only for a documented constraint such as aggregating multiple UI artifacts or an incompatible plugin/source-set graph. Provision version-catalog entries, compatible tooling, task wiring, record/verify tasks, Git LFS, and CI artifacts as default scaffolding.
8. After Detekt, Kover verification/XML/numeric line coverage, and required debug/platform builds pass, create the five adapted baseline workflows and `docs/CI-RELEASE-SETUP.md` required by the shared CI/release contract. Scaffold credential-dependent publication immediately, but keep it truthfully blocked until external setup is complete.
9. Add remaining build logic, checks, CI, and migration sequencing with rollback points.
10. Verify Android plus available iOS/Pod/Xcode contracts.

## Decision rules

- Keep domain and public feature contracts independent of UI/infrastructure.
- Keep generated Compose resource types at the presentation/resource boundary; domain and persistence depend only on stable language-neutral IDs/keys.
- Put platform implementations in platform source sets.
- Prefer narrow interfaces, dependency interfaces, top-level factories, and `by lazy`; add a DI framework only by explicit decision.
- Keep Decompose configs free of services.
- Prefer one module per screen-level Decompose component or cohesive nested flow when it enforces dependency/ownership/test boundaries. Group trivial callback-only leaves when a new module would enforce nothing; record the exception.
- Treat Gradle artifact, Podfile, lockfile, generated framework, and Xcode linkage as one native dependency contract.
- Verify current versions in official sources; never copy a reference project snapshot.
- Plan quality gates with the module graph.
- Co-locate screenshot tests with the module that owns production previews/resources unless a recorded build constraint requires aggregation/isolation.
- Make generated preview tests an explicit input to Android unit-test compilation and Paparazzi record/verify tasks; keep discovery package-scoped and configuration-cache behavior honest.

## Validation

Check settings inclusion, component-module boundaries/exceptions, dependency direction, source-set compilation, catalog/convention use, Compose resource generation, English default/fallback and locale packaging, native fallback resource packaging, screenshot host ownership/rationale, generator-to-compile task dependency, Paparazzi record/verify availability, snapshot/Git-LFS paths, CI diff/report artifacts, Android builds, available iOS framework/Pod/Xcode builds, Detekt/Kover, all five baseline workflow files, CI syntax, minimum permissions, concurrency, signing-variable contract, release artifacts, and the project-specific external setup guide. Distinguish local validation from credential-dependent end-to-end publication.

## Escalation/hand-off

Hand pure rules to Domain, UI navigation to Decompose, platform services to Platform, and feature tests to Test Engineer. Return the approved module/factory boundaries to Developer before parallel implementation.

## Reusable learning

Follow the package learning policy. Propose approved architectural rules for [learned-patterns.md](references/learned-patterns.md); never change it automatically.
