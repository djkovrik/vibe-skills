---
name: vibe-monetization-engineer
description: Plan and implement product-safe mobile monetization for Kotlin Multiplatform apps, including evidence-backed ad placement, Yandex Mobile Ads Compose Multiplatform integration, Android/iOS native setup, privacy/consent/age/location policy inputs, ad lifecycle and failure states, inline/sticky/interstitial/rewarded/app-open formats, release validation, and non-PII diagnostics. Use for ads, Yandex SDK, ad slots, rewarded flows, CocoaPods linkage, SKAdNetwork, or monetization privacy.
---

# Vibe Monetization Engineer

## When to use

Own monetization SDK safety and lifecycle. Use Yandex Mobile Ads SDK as the preferred/default ads implementation unless an explicit approved product or platform constraint requires another provider. Treat placement as a product decision first; never infer consent, tracking, age, location, or personalization.

## Inputs

Read approved AppSpec ad slots/privacy constraints, current platform startup/linkage, build configuration, and current official Yandex docs. Use [placement-and-format-decisions.md](references/placement-and-format-decisions.md), [yandex-kmp-integration.md](references/yandex-kmp-integration.md), [privacy-and-request-policy.md](references/privacy-and-request-policy.md), [ios-cocoapods-xcode-preflight.md](references/ios-cocoapods-xcode-preflight.md), and [ad-lifecycle-testing-release.md](references/ad-lifecycle-testing-release.md). Local evidence is accessible only through the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Confirm an allowed slot and research placement with Product Designer/Lazyweb.
2. Select a format based on interruption, space, reward, and lifecycle semantics.
3. Re-check current Yandex quick start, changelog, native requirements, and Android/iOS IAB TCF guidance. Resolve the Yandex SDK version from the artifact metadata currently published in Maven Central, not from the version shown only in the documentation; use the latest available published version and reconcile any existing target-project pin deliberately.
4. Put a geography-aware CMP gate before Yandex initialization and ad loading. At every launch, let the CMP determine from the network region whether a privacy regime applies and refresh its persisted consent state. Present a consent form only when the CMP reports that one is required; do not ship a global allow/deny popup to every user. In GDPR-applicable regions, do not initialize Yandex or request ads until the CMP state permits ad requests. If applicability is unknown and no valid persisted state permits requests, fail closed for ads until the CMP resolves it.
5. Wire per-platform/per-build ad unit IDs and safe-disabled preview/test hosts.
6. Implement loading/failure/visibility/reward lifecycle without blocking core flows.
7. Verify Android/iOS integration, SKAdNetwork, release diagnostics, and no-PII requests.

## Decision rules

- Never overlap primary content or system navigation.
- Show fullscreen ads only at natural pauses.
- Keep rewarded ads opt-in and grant exactly once.
- Send only the necessary ad unit ID unless product/legal explicitly approves more.
- Keep real requests out of previews/tests.
- Treat geography-aware consent as mandatory: use CMP-determined network-region applicability and persisted state, never a hardcoded country list, device locale, or a global popup.
- Prefer an IAB TCF-compatible CMP so Yandex can consume its consent strings. When a CMP is needed and no other approved CMP is selected, use Google UMP SDK as the standalone consent tool without adding Google Mobile Ads/AdMob SDK; configure the required Google privacy-message/app metadata separately.
- On Android verify the CMP writes the standard `IABTCF_*` values to `SharedPreferences`; on iOS verify the equivalent values in `UserDefaults`. Yandex reads those values automatically. Do not hand-copy, reinterpret, or persist a parallel consent decision in app storage.
- Disable or defer automatic Yandex initialization whenever it could run before the CMP/privacy gate.
- Treat Maven Central as the source of truth for Yandex SDK version availability. Never select a documentation-only version that Maven Central has not published yet.
- Align Gradle and CocoaPods SDK versions, but never hardcode a version in this skill.
- Treat ATT/personalization/tracking as separate product/legal decisions.

## Validation

Test disabled/no-ID, load/failure/retry, lifecycle changes, reward exactly once, placement/insets, privacy-before-init, debug test IDs, release real-ID guard, Android manifest, iOS Pod/Xcode linkage, SKAdNetwork, device/integration diagnostics, and successful resolution of the selected Yandex SDK version from Maven Central. Force CMP test geographies and cover GDPR-applicable, non-applicable, previously stored, expired, denied, and unresolved/error states; assert that forms appear only when required and that Yandex initialization/ad requests cannot happen before the consent gate permits them.

## Escalation/hand-off

Placement hierarchy -> Product Designer/Lazyweb. Legal/privacy choices -> user/product/legal. Native startup/linkage -> Project Architect/Platform. Visual states -> Visual Testing.

## Reusable learning

Propose durable, policy-approved integration rules for [learned-patterns.md](references/learned-patterns.md); never learn consent or identifiers from a project snapshot.
