---
name: vibe-project-architect
description: Design and change Kotlin Multiplatform project structure, Gradle modules and source sets, dependency direction, convention plugins, version catalogs, Compose Multiplatform resource ownership, manual dependency injection, Android/iOS entry points, Paparazzi and ComposablePreviewScanner screenshot-test surfaces, CocoaPods/Xcode linkage, quality gates, CI, signing contracts, and release workflows. Use for module graphs, scaffolding, localization-resource wiring, visual-test build wiring, build logic, platform startup, architecture migrations, or release setup.
---

# Vibe Project Architect

## When to use

Own module/build/release architecture. Do not own feature business rules, component state, or UI design.

## Inputs

Read the target AppSpec, repository instructions, module/build graph, catalogs, entry points, CI, and release files. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md) when the app has bundled user-visible text. Read [module-boundaries.md](references/module-boundaries.md), [manual-di.md](references/manual-di.md), [build-logic-and-quality.md](references/build-logic-and-quality.md), or [platform-entrypoints-and-release.md](references/platform-entrypoints-and-release.md) as applicable. Consult the shared [source registry](../vibe-developer/references/source-registry.md) only for labeled adaptations.

## Workflow

1. Map current modules, source sets, plugins, and dependencies.
2. Extract versions and target requirements from the project.
3. Define the minimal affected graph and ownership boundaries.
4. Keep domain contracts inward and implementations/platform code outward.
5. Design manual composition roots and explicit startup order.
6. When the product has bundled localized text, assign one common resource-owning module, configure Compose Multiplatform Resources and generated accessors, and keep native-only fallback resources in their platform source sets.
7. When the product has Compose UI, provision or verify an Android-host screenshot-test surface, version-catalog entries, Paparazzi and ComposablePreviewScanner compatibility, generated-test task wiring, record/verify tasks, snapshot storage, Git LFS, and CI artifacts. Treat this as default project scaffolding, not a later optional enhancement.
8. Add remaining build logic, checks, CI, and migration sequencing with rollback points.
9. Verify Android plus available iOS/Pod/Xcode contracts.

## Decision rules

- Keep domain and public feature contracts independent of UI/infrastructure.
- Keep generated Compose resource types at the presentation/resource boundary; domain and persistence depend only on stable language-neutral IDs/keys.
- Put platform implementations in platform source sets.
- Prefer narrow interfaces, dependency interfaces, top-level factories, and `by lazy`; add a DI framework only by explicit decision.
- Keep Decompose configs free of services.
- Treat Gradle artifact, Podfile, lockfile, generated framework, and Xcode linkage as one native dependency contract.
- Verify current versions in official sources; never copy a reference project snapshot.
- Plan quality gates with the module graph.
- Make generated preview tests an explicit input to test compilation and Paparazzi record/verify tasks; keep discovery package-scoped and configuration-cache behavior honest.

## Validation

Check settings inclusion, dependency direction, source-set compilation, catalog/convention use, Compose resource generation and locale packaging, native fallback resource packaging, screenshot-test module inclusion, generator-to-compile task dependency, Paparazzi record/verify availability, snapshot/Git-LFS paths, CI diff/report artifacts, Android builds, available iOS framework/Pod/Xcode builds, Detekt/Kover, CI syntax, signing-variable contract, and release artifacts.

## Escalation/hand-off

Hand pure rules to Domain, UI navigation to Decompose, platform services to Platform, and feature tests to Test Engineer. Return the approved module/factory boundaries to Developer before parallel implementation.

## Reusable learning

Follow the package learning policy. Propose approved architectural rules for [learned-patterns.md](references/learned-patterns.md); never change it automatically.
