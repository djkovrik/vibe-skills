# Preview contract

- Use the production composable with the sibling `*ComponentPreview` owned by the component module's `integration` package. Require one for every component contract rendered by production Compose, including stateless screens; do not replace it with a private ad-hoc fake in the Compose module.
- Keep data, clock, locale, theme, dimensions, and animation state deterministic.
- Avoid real network, database, SDK, permission, or platform services.
- Cover every primary screen and each applicable content, empty, error, loading, permission, and offline state in both light and dark.
- Add the largest AppSpec-required font scale, longest supported locale, RTL when applicable, and compact/adaptive variants where they expose distinct risk. These stress variants may be pairwise rather than a full cross-product, but may not replace state-by-theme coverage.
- Keep at least one realistic phone viewport for large variant boards.
- Treat preview compilation as a test obligation.
- Give previews stable names containing screen ID, state, theme, and non-default dimensions such as locale or font scale.
- Render production fonts, icons, and strings. Include fixtures that expose intended one-line labels, long titles, numeric formatting, missing-glyph risk, and intentional wrapping.
- Produce a coverage inventory from AppSpec screen/state rows to preview identities; fail review on unexplained gaps.

Primary source:

- https://developer.android.com/develop/ui/compose/tooling/previews

Blinkly adaptation: place static preview implementations beside `*ComponentDefault` in each component module's `integration` package; a preview may use `MutableValue`, but production component models remain Store-backed. A navigation-only component with no production Compose render surface may omit one only through a documented architecture exception.
