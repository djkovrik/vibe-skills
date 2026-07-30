# Vibe AppSpec v1 contract

## Contents

- [Boundary](#boundary)
- [Required structure](#required-structure)
- [Identifiers and links](#identifiers-and-links)
- [UI quality contract](#ui-quality-contract)
- [Validation](#validation)

## Boundary

Consume an already prepared specification. Do not restart product discovery during implementation. Put unresolved choices in `openQuestions`; do not silently decide them.

## Required structure

```text
app-spec/
  app-spec.json
  product.md
  design.md
  domain.md
  data.md
  quality.md
  flows/FLOW-*.md
  screens/SCREEN-*.md
  assets/
```

`app-spec.json` declares app metadata, requirements, flow/screen IDs, capabilities, constraints, UI quality gates, and open questions. Additional fields are allowed. Reject any schema major other than `1`. `design.md` and `uiQuality` are required for AppSpec 1.1+; accept older 1.x specs as legacy inputs but surface their missing visual contract.

The Markdown files define product intent, design direction, domain semantics, data contracts, quality gates, flows, acceptance scenarios, screen states, accessibility, localization, iconography/assets, preview/golden coverage, and allowed monetization slots.

## Identifiers and links

- Use stable `REQ-NNN`, `FLOW-NNN`, `SCREEN-NNN`, and `AC-NNN` identifiers.
- Put each acceptance scenario in one flow and include Given/When/Then.
- Link requirements to acceptance IDs.
- Link screens to requirements and flows.
- Keep filenames equal to their stable flow/screen IDs.

## UI quality contract

For AppSpec 1.1+:

- `design.md` defines Lazyweb evidence, semantic tokens, typography and line behavior, iconography/assets, the preview/golden matrix, and the post-golden review gate.
- `uiQuality.previewThemes` includes `light` and `dark`.
- `uiQuality.fontScales` includes the default scale and any product-required stress scale.
- `uiQuality.goldenTesting` requires Paparazzi plus ComposablePreviewScanner.
- `uiQuality.designReview` requires the current Lazyweb workflow after approved goldens and declares Material 3 as a review standard where applicable.
- `uiQuality.iconography.inventoryStatus` is resolved before implementation. Standard actions may use an approved canonical icon set; custom/brand assets must be provided or explicitly waived.
- Every `screens/SCREEN-*.md` contains `Actions and iconography`, `Text layout expectations`, and `Preview and golden matrix`.

Do not start Compose implementation when an icon/asset decision can materially change the screen and remains unresolved. Add a structured `openQuestions` item with `blocking: true`, related screen IDs, and the requested user decision or asset. The validator rejects unresolved blocking questions; non-blocking questions remain warnings.

## Validation

Run:

```powershell
python .\vibe-developer\scripts\validate-app-spec.py <app-spec-directory>
```

The validator is read-only. Errors block implementation; warnings require review. It validates contract structure, references, blocking questions, and the machine-checkable UI quality contract, not full product correctness.
