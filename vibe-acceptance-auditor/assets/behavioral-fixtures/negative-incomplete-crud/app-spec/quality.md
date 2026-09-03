# Quality

## Non-functional requirements

Keep reads deterministic and writes responsive.

## Test matrix

QG-001 requires one exact public-component test per AC and persistence after reload. The machine-readable gate inventory is `app-spec.json#qualityGates`.

## Preview and golden matrix

Require deterministic SCREEN-001 content, empty, and failure previews in light and dark, EN/RU, and 100%/200% font scale. ComposablePreviewScanner discovers stable preview IDs and Paparazzi verifies approved goldens.

## Visual quality and design review

Inspect approved goldens and complete one current Lazyweb review for SCREEN-001. Close or explicitly waive each blocking finding.

## Accessibility and localization

Expose localized roles and labels, scalable text, touch targets, EN base resources, and RU resources.

## Localization resource checks

Verify equal EN/RU keys, system-locale selection, EN fallback, stable persisted keys, native fallback resources, and no hardcoded user-visible production strings.

## Architecture checks

Verify the immutable Store-backed component model, Manager/Result boundary, component package roles, preview implementation, composition module, and Compose-owned screenshot host.

## Security and privacy

Collect and log no user data.

## Release acceptance

QG-002 and QG-003 require their platform checks. QG-004 requires repository, platform, preview, golden, design-review, and release checks. QG-005 applies only to external publication.
