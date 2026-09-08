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
8. Smoke-check scanner/Paparazzi with a small production preview early. Compile previews during edits; at a stable screen/capability boundary record only an approved baseline, inspect each new/changed PNG, then verify affected snapshots. Run the full required matrix at final integration. Deferred golden obligations remain implemented-unverified; no full record/verify cycle per AC or nonvisual edit.
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

## Orchestrated evidence hand-off

When `$vibe-developer` assigns work, accept explicit assignment, AC/gate IDs, assignment baseline reference, and non-overlapping file boundaries. Request compile/targeted checks from the orchestrator as soon as code is ready, before final handoff. Use the [flow delivery contract](../vibe-developer/references/flow-delivery-contract.md) for package assignments and automated assignment-local evidence. Before returning, follow [Specialist hand-off Protocol 2.0](../vibe-developer/references/specialist-handoff-contract.md): write one immutable `.vibe/handoffs/<id>.json` containing assignment-local baseline/result evidence, allowed/changed files, production and test evidence, completed non-Gradle checks, requested Gradle commands, and blockers. Do not edit the ledger or claim completion. The orchestrator alone inspects and ingests the hand-off, writes the ledger, and owns Gradle.

## Reusable learning

Propose reusable preview/golden infrastructure rules for [learned-patterns.md](references/learned-patterns.md); never auto-bless snapshots.

## Recovery of unfinished work

For multi-step work, including direct specialist requests, follow the shared [recovery contract](../vibe-developer/references/recovery-contract.md). Save the durable assignment before edits, checkpoint unfinished work with `specialist-state.py`, and resume from its packet after compaction or interruption, including inside the same turn. Preserve new user decisions immediately. A final hand-off does not replace intermediate checkpoints.

## Asset acceptance

Use the [asset contract](../vibe-assets-creator/references/asset-contract.md). Cover every ASSET ID through production screen/state/theme previews, including meaningful selected states, tint, optical size, alpha fringes and logo colors. Record actual reviewed artifacts in the asset manifest. Request the asset-check and asset-visual gate checks through Developer; a generated file without production usage or a reviewed screen is incomplete.

## Foundation feedback

Before expanding feature or preview matrices, establish a real render smoke with nonzero discovery and new expected PNGs from production resources, including light/dark and RU/200%. Missing resource classes or zero snapshots fail the smoke; do not execute every state against a broken harness. Configure Detekt and filtered Kover early; measure the coverage baseline once meaningful implementation exists. Keep full coverage obligations and defer only execution that depends on stable screens.

Use the current [flow coordination interfaces](../vibe-developer/references/flow-delivery-contract.md#current-coordination-and-evidence-interfaces) for compact assignment inputs, early contract readiness, exact evidence coverage and pending-work IDs.
