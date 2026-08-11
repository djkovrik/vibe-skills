# Design system and theme

Read [material3-foundations.md](material3-foundations.md) first. Material 3 is the base system; derive product identity by customizing its semantic color, typography, shape, spacing, elevation, icon, and motion roles rather than replacing its interaction grammar.

- Define the reference -> system -> component token mapping and identify any product-only extension.
- Keep semantic roles stable across light/dark/system themes.
- Prefer canonical Material 3 components and supported variants/slots over custom controls. Use [material3-component-selection.md](material3-component-selection.md) for the selection map.
- Prefer reusable tokenized primitives over screen-local magic numbers.
- Define content/disabled/focus/error/success states.
- Localize typography and icon direction where required.
- Check contrast, dynamic font scaling, and reduced motion.
- Keep native/system surfaces consistent with platform conventions.
- Choose static baseline, static brand, user-generated dynamic, content-based dynamic, or a documented combination. Always provide deterministic light/dark fallbacks for non-Android targets.
- Preserve M3 `container/onContainer` and `surface/onSurface` role pairings; use tonal surfaces before adding shadows.
- Assign M3 typography roles and emphasized counterparts intentionally. Use display/editorial treatment only for brief hero moments.
- Map rectangular shapes to the M3 shape scale. Use expressive shapes and morphing selectively and provide a reduced-motion/static alternative.
- Use the M3 spacing scale and elevation levels; avoid arbitrary radii, shadow stacks, and per-screen spacing systems.
- Choose standard or expressive motion at app level when supported; distinguish spatial motion from color/opacity effects.
- Define each text role's intended hierarchy, line-height, maximum normal-scale line count, overflow policy, and stress-scale wrapping behavior.
- Verify the real bundled fonts and every supported locale's glyphs in rendered goldens; a fallback font or missing glyph is a release defect.
- Keep one coherent icon family and weight. Inventory interactive elements and decide `icon`, `text`, `icon + text`, or `intentionally no icon`; do not mix arbitrary outline/filled styles except for meaningful states.
- Prefer standard Material Symbols for platform actions when approved. Ask for custom/brand assets before implementation, including light/dark variants or tintability, license/source, vector/raster format, and minimum-size behavior.
- Use matching semantic foreground/background roles and check actual contrast in light/dark plus enabled, disabled, selected, focus, error, and success states.

Use current Material/Compose guidance:

- https://m3.material.io/foundations
- https://m3.material.io/styles
- https://m3.material.io/building-with-m3-expressive
- https://developer.android.com/develop/ui/compose/designsystems
- https://www.w3.org/WAI/WCAG22/quickref/

Hand concrete Compose APIs and the [Material 3 Compose contract](material3-compose-contract.md) to Compose Expert.
