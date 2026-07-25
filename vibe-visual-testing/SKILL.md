---
name: vibe-visual-testing
description: Build and maintain deterministic Compose preview and screenshot-test infrastructure using @Preview coverage, ComposablePreviewScanner, generated parameterized Paparazzi tests, stable screenshot IDs, record/verify/report/failure workflows, golden review, Git LFS, and CI artifacts. Use for previews, Paparazzi, screenshot goldens, visual regression failures, preview scanning, or golden CI.
---

# Vibe Visual Testing

## When to use

Own deterministic visual test mechanics after design approval. Do not make product design decisions or bless unrelated diffs.

## Inputs

Read approved screens/theme, current previews, Paparazzi/scanner configuration, and target package/source sets. Use [preview-contract.md](references/preview-contract.md), [scanner-and-test-generation.md](references/scanner-and-test-generation.md), [paparazzi-rule-and-identifiers.md](references/paparazzi-rule-and-identifiers.md), [golden-review-and-ci.md](references/golden-review-and-ci.md), and [blinkly-visual-testing-adaptation.md](references/blinkly-visual-testing-adaptation.md). Local paths live in the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Define deterministic preview components/data and required state/theme/locale/device coverage.
2. Scope preview scanning to project packages and required source sets.
3. Cache the discovered preview list and generate test source before compilation.
4. Map preview parameters into Paparazzi configuration.
5. Build stable encoded snapshot IDs independent of parameter order.
6. Record only approved changes; inspect PNGs/diffs.
7. Verify in CI and publish failure/report artifacts.

## Decision rules

- Treat previews as a test surface.
- Include private previews only when intentionally compiled/scanned.
- Prefer a custom generator for project-specific theme/fonts/locales/devices.
- Add preview-safe seams for native views; test production native behavior elsewhere.
- Do not assume global `LocalInspectionMode`.
- Store large snapshot sets in Git LFS.
- Never update goldens merely to make verification pass.

## Validation

Verify generator determinism, compile dependency, stable IDs, filename encoding, package scope, each approved variant, record output, verify failure behavior, CI artifacts, and Git LFS configuration.

## Escalation/hand-off

Product differences -> Product Designer. Compose rendering bugs -> Compose Expert. Native-view behavior -> Platform/Test Engineer. Non-visual assertions -> Test Engineer.

## Reusable learning

Propose reusable preview/golden infrastructure rules for [learned-patterns.md](references/learned-patterns.md); never auto-bless snapshots.

