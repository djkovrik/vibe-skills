# Yandex Mobile Ads KMP integration

Before implementation, read the current quick start and repository/changelog. Use the documentation for integration requirements, but use Maven Central artifact metadata as the source of truth for version availability. Select the latest Yandex SDK version actually published there; never select a newer version mentioned only in the documentation. Do not hardcode a current version into this skill.

Checklist:

- read target version catalog/Gradle dependency;
- query Maven Central for the Yandex artifact and record the latest published version before editing dependencies;
- if the target project pins another version, reconcile the pin explicitly instead of silently copying either the project or documentation version;
- verify current Android minimum/compile requirements;
- align Compose Multiplatform artifact and native iOS SDK;
- configure the platform-specific setup;
- make Yandex the preferred/default ads provider unless an explicit approved constraint selects another provider;
- resolve a fresh custom privacy-region endpoint response before initialization and show the app-owned consent screen only when `consentRequired=true`;
- bind the persisted choice to `policyVersion`, clamp endpoint freshness to 72 hours, and fail closed for declined, expired, malformed, unknown, or transport-error states;
- call `YandexAds.setUserConsent(...)` before every permitted initialization and verify the exact selected SDK's consent behavior;
- keep this lightweight consent flow Yandex-only; replace it after a new privacy review if another demand/mediation partner requires certified CMP/TCF behavior;
- disable/defer Android automatic initialization if it could precede privacy resolution;
- initialize before loading;
- use per-platform/per-build ad unit IDs;
- run official integration diagnostics.

Primary sources:

- https://ads.yandex.com/helpcenter/ru/dev/compose-multiplatform
- https://ads.yandex.com/helpcenter/ru/dev/compose-multiplatform/quick-start
- https://ads.yandex.com/helpcenter/en/dev/compose-multiplatform/quick-start
- https://ads.yandex.com/helpcenter/en/dev/android/gdpr
- https://github.com/yandexmobile/yandex-ads-multiplatform
