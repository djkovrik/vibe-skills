---
name: vibe-visual-testing
description: Build and maintain deterministic Compose preview and screenshot-test infrastructure using mandatory primary-screen/state light/dark @Preview coverage, font-scale and locale stress variants, ComposablePreviewScanner, generated parameterized Paparazzi tests, stable screenshot IDs, record/verify/report/failure workflows, golden review, Git LFS, and CI artifacts. Use for every product UI delivery as well as previews, Paparazzi, screenshot goldens, visual regression failures, preview scanning, or golden CI.
---

# Vibe Visual Testing

## When to use

Own deterministic visual test mechanics for every product UI delivery after the preview matrix is approved. Do not make product design decisions or bless unrelated diffs.

## Inputs

Read approved screens/theme/locales, current previews, Paparazzi/scanner configuration, and target package/source sets. Apply the shared [localization contract](../vibe-developer/references/localization-contract.md). Use [preview-contract.md](references/preview-contract.md), [scanner-and-test-generation.md](references/scanner-and-test-generation.md), [paparazzi-rule-and-identifiers.md](references/paparazzi-rule-and-identifiers.md), [golden-review-and-ci.md](references/golden-review-and-ci.md), and [blinkly-visual-testing-adaptation.md](references/blinkly-visual-testing-adaptation.md). Local paths live in the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Reconcile AppSpec screens/states with preview declarations. Fail the hand-off when a primary screen or applicable state lacks light and dark previews, or when a Compose-rendered component contract lacks its component-module-owned `integration/*ComponentPreview`; require default-English, risk-based font-scale, longest-locale, and adaptive variants declared by Product Designer.
2. Create deterministic preview components/data with no real services, clocks, random values, network, database, permissions, ads, or native SDK dependencies. Compose previews instantiate the public sibling Preview implementation rather than a private Compose-local fake. Resolve bundled copy through production Compose string resources; fixture data carries stable IDs/keys, not convenient translated literals.
3. Put the Android-host screenshot-test surface in the Compose UI/resource-owning module by default. Use a dedicated module only for a documented aggregation or plugin/source-set constraint.
4. Scope preview scanning to project packages and required source sets.
5. Cache the discovered preview list and generate stable parameterized test source before test compilation.
6. Map preview parameters into Paparazzi theme, device, dimensions, simulated system locale, font scale, UI mode, and layout direction. Locale parameters are test-host inputs, not an in-app language control.
7. Build stable encoded snapshot IDs independent of scan or parameter order.
8. Run the generator/compile check, record only an approved baseline, inspect every PNG, then run verify from a clean-enough state.
9. Produce a machine-readable coverage inventory mapping `SCREEN/state/theme/fontScale/locale/device -> preview -> snapshot`.
10. Hand the approved golden paths and an explicit screen review order to Product Designer for the mandatory Lazyweb/full-UI review. The hand-off must require a strict one-screen-at-a-time queue with exactly one report in flight and no next submission before the previous report is received and recorded; do not split the queue across parallel reviewers. After approved fixes, re-record only affected goldens and re-run complete verification.
11. Verify in CI and publish failure/report artifacts.

## Decision rules

- Treat previews as a test surface.
- Co-locate preview discovery, Paparazzi rules, generated Android unit tests, resources, and snapshots with the Compose module that owns the previews; do not default to a separate `screenshot-tests` module.
- Include private previews only when intentionally compiled/scanned.
- Prefer a custom generator for project-specific theme/fonts/locales/devices.
- Add preview-safe seams for native views; test production native behavior elsewhere.
- Do not assume global `LocalInspectionMode`.
- Do not silently down-scope a missing theme/state because the matrix is large. Reduce redundant stress combinations explicitly while preserving every state in light and dark.
- Store large snapshot sets in Git LFS.
- Never update goldens merely to make verification pass.

## Validation

Verify screen/state matrix completeness, component-module Preview ownership for every Compose-rendered contract, documented navigation-only exceptions, absence of substitute Compose-local component fakes, light/dark coverage, English default/fallback rendering, production resource resolution and declared locale key completeness, font-scale/locale/device variants, screenshot-host ownership/rationale, generator determinism, Android unit-test compile dependency, stable IDs, filename encoding, package scope, each approved variant, record output, verify failure behavior, coverage inventory, Product Designer hand-off, CI artifacts, and Git LFS configuration.

## Escalation/hand-off

Product differences -> Product Designer. Compose rendering bugs -> Compose Expert. Native-view behavior -> Platform/Test Engineer. Non-visual assertions -> Test Engineer.

## Reusable learning

Propose reusable preview/golden infrastructure rules for [learned-patterns.md](references/learned-patterns.md); never auto-bless snapshots.
