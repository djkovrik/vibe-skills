# Preview scanner and test generation

- Restrict scanning to project package trees.
- Include only intended source sets and private previews.
- Cache the scan/list; do not rediscover on every test method.
- Make generated test source depend on the scan/generation task and compile before tests.
- Map preview parameters into Paparazzi device, dimensions, locale, font scale, and UI mode.
- Generate stable ordering and deterministic output.
- Prefer a custom generator when project theme/fonts/locale/device setup exceeds generic plugin support.
- Bootstrap the screenshot surface in the Compose UI/resource-owning module's Android unit-test source set when the target has none. Add compatible Paparazzi/ComposablePreviewScanner versions to the catalog, apply the plugin there, and keep generated sources under `build/`.
- Create a dedicated Android-host module only to aggregate multiple Compose artifacts or work around a verified plugin/source-set incompatibility. Document the reason, keep it dependent on public UI artifacts, and avoid copying production resources/theme setup.
- Make preview discovery/generation an explicit input and dependency of test compilation plus record/verify tasks. Never rely on task execution order by naming convention alone.
- Generate one parameterized test surface from the cached preview list instead of hand-maintaining a second screen matrix.
- Emit the discovered preview count and a stable coverage file so a missing preview is visible even when existing snapshots still verify.
- Run focused generator and test-compilation checks before record/verify. Verify configuration-cache compatibility honestly; document a scoped exception rather than hiding it.

Primary sources:

- https://github.com/sergio-sastre/ComposablePreviewScanner#paparazzi
- https://github.com/sergio-sastre/ComposablePreviewScanner/blob/master/paparazzi-plugin/README.md
- https://cashapp.github.io/paparazzi/
