# Quality

## Non-functional requirements

Keep reads deterministic and writes responsive.

## Test matrix

QG-001 covers AC-001 through AC-004 with `python verify_fixture.py`. The machine-readable gate inventory is `app-spec.json#qualityGates`.

## Preview and golden matrix

Require deterministic SCREEN-001 content and empty previews in light and dark, EN/RU, and 100%/200% font scale. ComposablePreviewScanner discovers stable preview IDs and Paparazzi verifies approved goldens.

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

This language-neutral forward fixture tests audit mechanics rather than Kotlin/Compose conformance. QG-002 and QG-003 both require a fresh zero-exit `python verify_fixture.py` receipt; a real KMP project must use its actual platform, preview, golden, design-review, and release checks. QG-004 applies only to external publication.
