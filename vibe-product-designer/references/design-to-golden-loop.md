# Design-to-golden loop

1. Validate screen requirement/state coverage.
2. Gather Lazyweb evidence and approve a direction.
3. Define hierarchy, semantic tokens, text line/overflow rules, responsive/accessibility/localization behavior, and the interactive-element icon inventory.
4. Resolve standard icon-set approval and required custom/brand assets before implementation.
5. Define the preview matrix: every primary screen and applicable state in light and dark, plus risk-based font-scale, longest-locale, compact/adaptive, and direction variants.
6. Implement through the component contract and Compose Expert, including deterministic preview entry points.
7. Ask Visual Testing to scan previews, generate Paparazzi tests, produce the coverage inventory, and record an approved baseline.
8. Inspect every rendered PNG before accepting it.
9. Run the current Lazyweb improve workflow over all declared primary-screen coverage as a strict ordered queue: one screen per report, one report in flight, and no next submission until the previous report is complete, retrieved, and recorded. Finish any separate theme/state reports for the current screen sequentially before advancing. Never parallelize Lazyweb screen reviews.
10. Check cross-screen consistency; fonts/glyphs; unintended line wrapping, clipping, and ellipsis; typography hierarchy; light/dark colors and contrast; Material 3 components/states; missing, incorrect, or inconsistent icons; text-only actions that need icon support; touch targets; insets; accessibility; localization; and responsive behavior.
11. Fix objective contract defects directly. Get a user decision for material product/design changes or unresolved custom assets.
12. Re-record only approved diffs, re-run full verification, and close or explicitly waive every blocking review finding.
13. Verify goldens in CI and publish failure/diff artifacts.

Goldens are evidence of approved rendering, not an authority that overrides AppSpec or accessibility behavior.
