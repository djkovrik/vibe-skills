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
- run a geography-aware CMP update before initialization, use its network-region applicability and persisted consent state, and show a form only when required;
- for GDPR-applicable users, require the CMP to permit ad requests before initializing Yandex or loading ads;
- verify Yandex can read the CMP's IAB TCF v2.0 values from Android `SharedPreferences` and iOS `UserDefaults`;
- when needed, integrate Google UMP as a standalone CMP dependency without adding Google Mobile Ads/AdMob SDK;
- disable/defer Android automatic initialization if it could precede privacy resolution;
- initialize before loading;
- use per-platform/per-build ad unit IDs;
- run official integration diagnostics.

Primary sources:

- https://ads.yandex.com/helpcenter/ru/dev/compose-multiplatform
- https://ads.yandex.com/helpcenter/ru/dev/compose-multiplatform/quick-start
- https://ads.yandex.com/helpcenter/en/dev/compose-multiplatform/quick-start
- https://ads.yandex.com/helpcenter/en/dev/android/tcf-2-0
- https://ads.yandex.com/helpcenter/en/dev/ios/tcf-2-0
- https://github.com/yandexmobile/yandex-ads-multiplatform
