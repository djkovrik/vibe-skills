# Paparazzi rule and identifiers

- Configure Paparazzi from approved preview parameters and project theme/font setup.
- Build snapshot IDs from stable preview identity plus named parameter values, not scan/parameter order.
- Encode characters unsafe for filenames and enforce reasonable length.
- Avoid collisions and print a deterministic mapping when generation fails.
- Add a preview-safe seam for native/platform views.
- Do not rely on Paparazzi globally setting `LocalInspectionMode`.
- Preserve real theme, resources, fonts, locale, layout direction, font scale, and night mode from each preview instead of normalizing variants to one host configuration.
- Keep snapshot filenames human-navigable by screen/state/theme while encoding unsafe characters and hashing only when length requires it.

Primary sources:

- https://cashapp.github.io/paparazzi/
- https://github.com/cashapp/paparazzi
