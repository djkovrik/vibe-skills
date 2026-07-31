# Quality

## Non-functional requirements

Keep reads deterministic and writes responsive.

## Test matrix

Cover default, update, restart simulation, invalid legacy value, Android, and iOS.

## Preview and golden matrix

Require deterministic `@Preview` coverage for SCREEN-001 content and error states in light and dark. Add EN/RU, a 200% font-scale text-stress case, and the declared expanded-width layout. ComposablePreviewScanner must discover the declared previews and generate Paparazzi tests with stable IDs.

## Visual quality and design review

Record an approved Paparazzi baseline, inspect every PNG, and require a clean verify run. Then run the current Lazyweb improve workflow for every primary-screen coverage row and review the complete golden set for cross-screen consistency, font/glyph rendering, unintended line wrapping or clipping, typography hierarchy, light/dark color and contrast, Material 3 component/state use, icons, touch targets, insets, accessibility, localization, and responsive behavior. Resolve or explicitly waive every blocking finding before release.

## Accessibility and localization

Provide default EN and additional RU Compose Multiplatform `strings.xml` resources, scalable text, and a screen-reader description. Adding another `app.locales` entry must require only a matching locale resource set with the same keys, not a domain or database migration; `en` remains the default locale.

## Localization resource checks

Require a complete default EN key set and equal key coverage for every additional locale in `app.locales`, valid stable-ID/key-to-`Res.string.*` mappings, EN/RU locale-switch and unsupported-locale-to-EN-fallback coverage, and a production-source scan that rejects hardcoded user-visible strings. Persistence tests must prove that restart and locale changes preserve stable IDs/keys rather than resolved translations. Native `actual` text must resolve through Android/iOS localization resources and have matching locale coverage.

## Security and privacy

Do not log the selected value.

## Release acceptance

Require unit tests, Android/iOS compilation, preview generation/compilation, Paparazzi record plus verify evidence, golden coverage inventory, and completed post-golden Lazyweb review.
