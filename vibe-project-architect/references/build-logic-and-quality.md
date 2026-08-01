# Build logic and quality

- Extract versions from `gradle/libs.versions.toml` and plugin/build files.
- Prefer convention plugins for repeated, enforceable module configuration.
- Keep target/toolchain/minimum platform values centralized and verified.
- Add focused Detekt, Kover, tests, and build tasks to CI before broad aggregates.
- For every Compose product, put the Android-host Paparazzi/ComposablePreviewScanner surface in the Compose UI/resource-owning module by default. Use its Android unit-test source set, generated sources under `build/`, and snapshots beside that test surface.
- Use a dedicated screenshot-test module only when it aggregates previews from multiple UI modules, the UI module cannot apply the required Android/Paparazzi plugins, or isolation fixes a measured dependency/tooling conflict. Record the constraint and avoid duplicating resource/theme wiring.
- Keep Paparazzi, scanner, Android/Compose, Gradle, AGP, Kotlin, and JDK versions in one compatibility decision verified against current official release notes.
- Wire generated preview-test source into test compilation and make record/verify depend on generation through declared task inputs/outputs.
- Keep snapshots source-controlled, use Git LFS when the set is material, and upload Paparazzi reports/failures/diffs from CI.
- Treat warnings as findings, but use process exit code as success/failure evidence.
- Never introduce a new library version without checking its current official release/migration documentation.

Primary references:

- https://docs.gradle.org/current/userguide/platforms.html
- https://docs.gradle.org/current/userguide/custom_plugins.html
- https://kotlinlang.org/docs/multiplatform/multiplatform-configure-compilations.html

Blinkly adaptation: inspect root build logic, convention plugins, catalog, Kover/Detekt configuration, and workflows through the shared source registry.
