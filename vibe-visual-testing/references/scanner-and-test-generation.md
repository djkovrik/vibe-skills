# Preview scanner and test generation

- Restrict scanning to project package trees.
- Include only intended source sets and private previews.
- Cache the scan/list; do not rediscover on every test method.
- Make generated test source depend on the scan/generation task and compile before tests.
- Map preview parameters into Paparazzi device, dimensions, locale, font scale, and UI mode.
- Generate stable ordering and deterministic output.
- Prefer a custom generator when project theme/fonts/locale/device setup exceeds generic plugin support.

Primary sources:

- https://github.com/sergio-sastre/ComposablePreviewScanner#paparazzi
- https://github.com/sergio-sastre/ComposablePreviewScanner/blob/master/paparazzi-plugin/README.md

