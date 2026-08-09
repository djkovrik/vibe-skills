# Manual dependency injection

For every non-Decompose implementation module that provides constructed dependencies to another module, define its public DI boundary in `di/<Feature>Module.kt`. Pure contract/model modules and presentation-only modules that construct nothing are excluded.

Use this exact shape:

```kotlin
interface FeatureModule {
    val service: FeatureService
}

interface FeatureModuleDependencies {
    val dependency: Dependency
}

fun FeatureModule(dependencies: FeatureModuleDependencies): FeatureModule =
    object : FeatureModule {
        override val service: FeatureService by lazy {
            FeatureServiceImpl(dependencies.dependency)
        }
    }
```

If the module has no inputs, omit `FeatureModuleDependencies` and expose `fun FeatureModule(): FeatureModule`. Keep outputs lazily owned either way. Build and retain these modules at the platform/root composition boundary; consumers depend on their output interfaces, not implementation constructors.

Rules:

- Inject interfaces, dispatchers, clock, and platform factories explicitly.
- Expose only dependencies the module owns and intentionally provides outward; keep implementation classes out of the module interface.
- Keep inputs on `*ModuleDependencies`; do not capture unrelated composition-root state or turn the module into a service locator.
- Instantiate non-Decompose implementations through their module factories. Do not duplicate repository, manager, database, settings, network-client, notifier, alarm, or platform-service construction directly in Android/iOS root factories.
- Use an anonymous or private module implementation so the interface plus top-level factory remains the public creation API.
- Make ownership/close lifecycle visible for databases and clients.
- Avoid service locators and dependencies in serialized navigation configs.
- Keep startup ordering explicit, especially native SDK initialization before shared graph creation.
- Add a DI framework only when the target project/user selects it and the migration benefit is measurable.

Validation: inventory every non-Decompose module with concrete providers; map it to `di/*Module.kt`, verify interface-only outputs, complete dependency inputs, same-named factory, `by lazy` ownership, and composition-root use. Record an exception only when the module constructs no outward dependency or a framework-owned lifecycle requires a different factory boundary.

Blinkly adaptation: its domain/database/settings/notifier/alarm/beeper/crashlytics/utils modules and platform `RootComponentFactory` are concrete references listed through the shared source registry; `sync` demonstrates the same shape in a component module but is not the mandatory non-Decompose case.
