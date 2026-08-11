# Design-to-golden loop

1. Validate screen requirement/state coverage.
2. Gather Lazyweb evidence and approve a direction.
3. Select the Material canonical layout, breakpoint/pane behavior, navigation family, and per-element M3 component/variant map.
4. Define semantic tokens, complete interaction states, expressive scheme and baseline fallbacks, text line/overflow rules, inset/responsive/accessibility/localization behavior, and the interactive-element icon inventory.
5. Resolve standard icon-set approval and required custom/brand assets before implementation.
6. Define the preview matrix: every primary screen and applicable state in light and dark, plus risk-based font-scale, longest-locale, compact/adaptive, direction, and expressive-fallback variants.
7. Implement through the component contract and Compose Expert, including an API maturity/target-availability note and deterministic preview entry points.
8. Ask Visual Testing to scan previews, generate Paparazzi tests, produce the coverage inventory, and record an approved baseline.
9. Inspect every rendered PNG before accepting it.
10. Run the current Lazyweb improve workflow over all declared primary-screen coverage as a strict ordered queue: one screen per report, one report in flight, and no next submission until the previous report is complete, retrieved, and recorded. Finish any separate theme/state reports for the current screen sequentially before advancing. Never parallelize Lazyweb screen reviews.
11. Check cross-screen consistency; canonical layout and navigation adaptation; M3 component semantics/variants; token role pairing; interaction states; expressive restraint; fonts/glyphs; unintended line wrapping, clipping, and ellipsis; typography hierarchy; light/dark colors and contrast; shape, spacing, elevation, and motion; missing, incorrect, or inconsistent icons; text-only actions that need icon support; touch targets; insets; accessibility; localization; and responsive behavior.
12. Fix objective contract defects directly. Get a user decision for material product/design changes, experimental API adoption, or unresolved custom assets.
13. Re-record only approved diffs, re-run full verification, and close or explicitly waive every blocking review finding.
14. Verify goldens in CI and publish failure/diff artifacts.

Goldens are evidence of approved rendering, not an authority that overrides AppSpec or accessibility behavior.
