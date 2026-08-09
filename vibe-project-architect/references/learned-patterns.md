# Learned patterns

ID: ARCH-001
Status: accepted
Date: 2026-08-09
Scope: Decompose screen modules and Compose screenshot-test hosting.
Decision: Default each screen-level component or cohesive flow to a component module owning its root contract, `integration` Default/Preview/mappers, `store` Store/provider, and `domain` Manager/models. Require a component-module Preview for every Compose-rendered contract. Host Paparazzi/ComposablePreviewScanner in the Compose UI/resource-owning module. Group trivial leaves, omit navigation-only previews, or use a dedicated screenshot module only with a documented enforceable-boundary, render-surface, aggregation, or plugin/source-set reason.
Evidence: Blinkly `shared/component/**` and `shared/compose`; BulbMatch's monolithic `shared:app` and separate `screenshot-tests` add indirection without a demonstrated boundary; StainFirstAid flattened component packages and moved preview fakes into Compose.
Consequences: Clear feature ownership and simpler preview/resource wiring; avoids modules that enforce no boundary.
Validation: Review settings/dependency graph, module ownership, Android unit-test source wiring, generated-test dependencies, resource fidelity, and recorded exception rationale.
Supersedes: none

ID: ARCH-002
Status: accepted
Date: 2026-08-09
Scope: Manual dependency injection for non-Decompose implementation modules.
Decision: Each module that constructs dependencies for outward use exposes `di/*Module.kt` with a narrow `*Module` output interface, `*ModuleDependencies` input interface when inputs exist, a same-named top-level factory, and `by lazy` outputs. Platform/root composition retains module instances and consumes interfaces instead of constructing concrete repositories/services directly.
Evidence: Blinkly domain/database/settings/notifier/alarm/beeper/crashlytics/utils modules and platform root factories consistently use this boundary; StainFirstAid composition roots construct cross-module implementations directly and expose no module DI contracts.
Consequences: Additional small DI files and interfaces, with consistent dependency discovery, ownership, replaceability, and platform parity.
Validation: Inventory concrete providers per non-Decompose module; verify DI file/package, output and dependency interfaces, same-named factory, lazy outputs, and absence of duplicate direct construction in Android/iOS roots. Exclude only modules that construct no outward dependency or have a documented framework-owned lifecycle boundary.
Supersedes: none
