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

Provide EN/RU labels, scalable text, and a screen-reader description.

## Security and privacy

Do not log the selected value.

## Release acceptance

Require unit tests, Android/iOS compilation, preview generation/compilation, Paparazzi record plus verify evidence, golden coverage inventory, and completed post-golden Lazyweb review.
