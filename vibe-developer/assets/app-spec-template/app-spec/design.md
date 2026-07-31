# Design

## Lazyweb evidence and direction

Use current Lazyweb workflow guidance before approving the screen direction. Record the exact screen-pattern queries, reference links, report URLs, and the decisions they support. The implementation pass must review the rendered primary screens again after approved goldens exist.

## Design system and themes

Use Material 3 semantic color and typography roles with explicit light and dark schemes. Keep spacing, shape, elevation, motion, and icon tokens centralized. Respect the system theme by default unless the product requirements approve another policy.

## Typography and text layout

- Use production fonts and verify EN/RU glyph coverage.
- Resolve every bundled label, accessibility description, error, and local option title from Compose Multiplatform Resources `strings.xml` through the same key in each locale; do not use hardcoded production or preview text.
- Use semantic typography roles rather than screen-local sizes.
- The screen title and current-value label are one line at normal font scale.
- At 200% font scale, controls may wrap without clipping, overlap, missing glyphs, or hidden actions.
- Define `maxLines` and overflow behavior for every text element that has a line-count expectation.

## Iconography and assets

Standard icon source: Material Symbols, approved for platform actions.

| Element | Treatment | Semantic purpose | Source or asset | Accessibility | Status |
| --- | --- | --- | --- | --- | --- |
| Navigate back | icon | Return to the previous screen | Material Symbols `arrow_back` / auto-mirrored equivalent | Action label: Back | approved |
| Save preference | icon + text | Persist the selected value | Material Symbols `save` plus localized label | Button exposes one Save action | approved |

Custom or brand icon assets are not required for this example. When a real app needs them, list the exact files/variants here and add a blocking structured `openQuestions` item until the user provides or explicitly waives them. Do not begin Compose implementation with an unresolved material icon/asset decision.

## Preview and golden contract

- Create deterministic previews for every primary screen and applicable state in both light and dark.
- Add risk-based variants for 200% font scale, the longest supported locale, compact phone width, and adaptive layouts.
- Discover project previews with ComposablePreviewScanner and generate parameterized Paparazzi tests.
- Record only an approved baseline, inspect every PNG, verify it, and emit a screen/state/theme coverage inventory.

## Post-golden design review

Run the current Lazyweb improve workflow over every declared primary screen after approved Paparazzi goldens exist. Review both themes and include text-stress states where relevant. Audit the complete golden set for cross-screen consistency, fonts and glyphs, unintended wrapping/clipping/ellipsis, typography hierarchy, color and contrast, Material 3 components and states, icon correctness and missing icon opportunities, touch targets, insets, accessibility, localization, and responsive behavior. Re-record and re-verify only approved fixes.
