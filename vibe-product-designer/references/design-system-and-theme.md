# Design system and theme

- Derive semantic color, typography, shape, spacing, elevation, icon, and motion tokens from approved product direction.
- Keep semantic roles stable across light/dark/system themes.
- Prefer reusable primitives and components over screen-local magic numbers.
- Define content/disabled/focus/error/success states.
- Localize typography and icon direction where required.
- Check contrast, dynamic font scaling, and reduced motion.
- Keep native/system surfaces consistent with platform conventions.
- Define each text role's intended hierarchy, line-height, maximum normal-scale line count, overflow policy, and stress-scale wrapping behavior.
- Verify the real bundled fonts and every supported locale's glyphs in rendered goldens; a fallback font or missing glyph is a release defect.
- Keep one coherent icon family and weight. Inventory interactive elements and decide `icon`, `text`, `icon + text`, or `intentionally no icon`; do not mix arbitrary outline/filled styles except for meaningful states.
- Prefer standard Material Symbols for platform actions when approved. Ask for custom/brand assets before implementation, including light/dark variants or tintability, license/source, vector/raster format, and minimum-size behavior.
- Use matching semantic foreground/background roles and check actual contrast in light/dark plus enabled, disabled, selected, focus, error, and success states.

Use current Material/Compose guidance:

- https://m3.material.io/
- https://developer.android.com/develop/ui/compose/designsystems
- https://www.w3.org/WAI/WCAG22/quickref/

Hand concrete Compose APIs to Compose Expert.
