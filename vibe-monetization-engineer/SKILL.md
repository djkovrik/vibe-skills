---
name: vibe-monetization-engineer
description: Plan and implement product-safe mobile monetization for Kotlin Multiplatform apps, including evidence-backed ad placement, Yandex Mobile Ads Compose Multiplatform integration, Android/iOS native setup, privacy/consent/age/location policy inputs, ad lifecycle and failure states, inline/sticky/interstitial/rewarded/app-open formats, release validation, and non-PII diagnostics. Use for ads, Yandex SDK, ad slots, rewarded flows, CocoaPods linkage, SKAdNetwork, or monetization privacy.
---

# Vibe Monetization Engineer

## When to use

Own monetization SDK safety and lifecycle. Use Yandex Mobile Ads SDK as the preferred/default ads implementation unless an explicit approved product or platform constraint requires another provider. Treat placement as a product decision first; never infer consent, tracking, age, location, or personalization.

## Inputs

Read approved AppSpec ad slots/privacy constraints, current platform startup/linkage, build configuration, and current official Yandex docs. Use [placement-and-format-decisions.md](references/placement-and-format-decisions.md), [yandex-kmp-integration.md](references/yandex-kmp-integration.md), [privacy-region-endpoint.md](references/privacy-region-endpoint.md), [privacy-and-request-policy.md](references/privacy-and-request-policy.md), [ios-cocoapods-xcode-preflight.md](references/ios-cocoapods-xcode-preflight.md), and [ad-lifecycle-testing-release.md](references/ad-lifecycle-testing-release.md). Local evidence is accessible only through the shared [source registry](../vibe-developer/references/source-registry.md).

## Workflow

1. Confirm an allowed slot and research placement with Product Designer/Lazyweb.
2. Select a format based on interruption, space, reward, and lifecycle semantics.
3. Re-check current Yandex quick start, changelog, native requirements, and consent/GDPR guidance for Android and iOS. Resolve the Yandex SDK version from the artifact metadata currently published in Maven Central, not from the version shown only in the documentation; use the latest available published version and reconcile any existing target-project pin deliberately.
4. Put the custom privacy-region endpoint and app-owned consent gate before Yandex initialization and ad loading. Restore only a fresh response, refresh it from the network when needed, show consent only when `consentRequired=true`, and bind the choice to `policyVersion`. Do not initialize Yandex or request ads after decline or while the endpoint/choice is missing, invalid, expired, or unresolved. Before every allowed initialization, pass the current consent state through `YandexAds.setUserConsent(...)`.
5. Wire per-platform/per-build ad unit IDs and safe-disabled preview/test hosts.
6. Implement loading/failure/visibility/reward lifecycle without blocking core flows.
7. Verify Android/iOS integration, SKAdNetwork, release diagnostics, and no-PII requests.

## Decision rules

- Never overlap primary content or system navigation.
- Show fullscreen ads only at natural pauses.
- Keep rewarded ads opt-in and grant exactly once.
- Send only the necessary ad unit ID unless product/legal explicitly approves more.
- Keep real requests out of previews/tests.
- Treat geography-aware consent as mandatory for the Yandex-only flow: use the approved server endpoint's network-IP classification, never locale, SIM, time zone, device location, a bundled country list, or a global popup.
- Treat the endpoint as an applicability service, not an IAB TCF CMP: it returns no country or TCF string and never receives the user's choice. Keep the choice in one versioned private settings payload with the minimal endpoint response and matching `policyVersion`.
- Use this lightweight flow only with Yandex Ads. A demand or mediation partner that requires a certified CMP/TCF contract needs a new privacy inventory, explicit product/legal approval, and a replacement consent integration.
- Disable or defer automatic Yandex initialization whenever it could run before the endpoint/consent gate.
- Treat Maven Central as the source of truth for Yandex SDK version availability. Never select a documentation-only version that Maven Central has not published yet.
- Align Gradle and CocoaPods SDK versions, but never hardcode a version in this skill.
- Treat ATT/personalization/tracking as separate product/legal decisions.

## Validation

Test disabled/no-ID, load/failure/retry, lifecycle changes, reward exactly once, placement/insets, privacy-before-init, debug test IDs, release real-ID guard, Android manifest, iOS Pod/Xcode linkage, SKAdNetwork, device/integration diagnostics, and successful resolution of the selected Yandex SDK version from Maven Central. Use controlled endpoint responses for protected, non-protected, unknown, malformed, expired, policy-changed, denied, withdrawn, network-error, and retry states; assert that forms appear only when required and that Yandex initialization/ad requests cannot happen before the endpoint/consent gate permits them.

## Escalation/hand-off

Placement hierarchy -> Product Designer/Lazyweb. Legal/privacy choices -> user/product/legal. Native startup/linkage -> Project Architect/Platform. Visual states -> Visual Testing.

## Reusable learning

Propose durable, policy-approved integration rules for [learned-patterns.md](references/learned-patterns.md); never learn consent or identifiers from a project snapshot.
