# Build logic and quality

- Extract versions from `gradle/libs.versions.toml` and plugin/build files.
- Prefer convention plugins for repeated, enforceable module configuration.
- Keep target/toolchain/minimum platform values centralized and verified.
- Add focused Detekt, Kover, tests, and build tasks to CI before broad aggregates.
- Resolve the newest official Detekt release at integration time and use that current version consistently for the Gradle plugin, CLI/tool version, and compatible first- or third-party rule plugins. Do not inherit the Detekt version from Blinkly or another reference project, and do not silently substitute an older stable line merely because the current release is a prerelease. If the current release cannot run with the target Kotlin/Gradle/AGP/JDK contract, record the exact incompatibility and use the newest compatible release as an explicit exception.
- Generate a complete default configuration with the selected Detekt version and commit it as `detekt/base-config.yml`. Generate into an absent destination (or a temporary path when migrating an existing config), because `detektGenerateConfig` does not overwrite an existing file. Do not hand-author a partial config as the starting point.
- When `BLINKLY_ROOT/detekt/base-config.yml` is available, merge only the following Blinkly-adapted policy values into the matching rules and property names in the newly generated current-version config; never replace the generated file with Blinkly's older schema:
  - complex conditions: `4`;
  - cyclomatic complexity per method: `25`;
  - class size: `600` lines;
  - method size: `90` lines;
  - function and constructor parameters: `12` and `12`;
  - nested block depth: `4`;
  - functions in files/classes/interfaces/objects/enums: `25/15/15/15/11`;
  - destructuring entries: `3`;
  - loop jump statements: `2`;
  - line length: `140`;
  - returns per function: `3`;
  - throws per function: `2`.
- Treat those values as semantic thresholds. Map them to the property names emitted by the selected Detekt version (for example, current `allowed...` names instead of obsolete 1.x `threshold...` names), retain every newly generated rule and default not overridden above, and review the selected version's migration guide before merging.
- Make Detekt an explicit quality gate: analyze all production Kotlin/Kotlin-script sources that belong to the project, exclude only generated/build output, keep `ignoreFailures = false`, enable configuration validation, fail configuration warnings, and configure the task to fail at `Warning` severity (therefore on Warning and Error findings) where the selected Detekt version supports severity-based failure. On Detekt 1.x use its zero-issue equivalent. Do not weaken the gate by parsing logs or allowing a successful task with gate-severity findings.
- Prefer fixing the initial findings. A baseline is allowed only for an existing project's explicitly accepted legacy debt; commit it, keep new findings blocking, document its size/owner/removal plan, and never regenerate it automatically in CI.
- Wire the exact strict Detekt task into `check` and `AnalysisAndTest.yml`, publish its machine-readable and human-readable reports on failure, and verify the gate with one controlled temporary violation before removing that violation.
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
- https://detekt.dev/docs/intro/
- https://detekt.dev/docs/introduction/configurations/
- https://detekt.dev/docs/introduction/migration/

Blinkly adaptation: inspect root build logic, convention plugins, catalog, Kover/Detekt configuration, and workflows through the shared source registry. Its Detekt config is threshold evidence only: it was generated for an older Detekt schema and must never be used as the current base file.
