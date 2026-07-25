# Blinkly visual-testing adaptation

Locate the concrete implementation through the shared source registry.

Reusable evidence:

- project-scoped Compose preview scanning;
- generated parameterized Paparazzi test source;
- project wrapper around Paparazzi for fonts/theme/device handling;
- stable screenshot names;
- clean record then verify workflow;
- CI verification and snapshot storage.

Generalize package roots, theme, fonts, locales, devices, source sets, tasks, and output paths. The custom generator is an adaptation, not an official universal API.

