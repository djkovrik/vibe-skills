# Build logic and quality

- Extract versions from `gradle/libs.versions.toml` and plugin/build files.
- Prefer convention plugins for repeated, enforceable module configuration.
- Keep target/toolchain/minimum platform values centralized and verified.
- Add focused Detekt, Kover, tests, and build tasks to CI before broad aggregates.
- Treat warnings as findings, but use process exit code as success/failure evidence.
- Never introduce a new library version without checking its current official release/migration documentation.

Primary references:

- https://docs.gradle.org/current/userguide/platforms.html
- https://docs.gradle.org/current/userguide/custom_plugins.html
- https://kotlinlang.org/docs/multiplatform/multiplatform-configure-compilations.html

Blinkly adaptation: inspect root build logic, convention plugins, catalog, Kover/Detekt configuration, and workflows through the shared source registry.

