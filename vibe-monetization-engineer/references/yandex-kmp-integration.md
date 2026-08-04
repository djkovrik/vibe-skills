# Yandex Mobile Ads KMP integration

Before implementation, read the current quick start and repository/changelog. Use the documentation for integration requirements, but use Maven Central artifact metadata as the source of truth for version availability. Select the latest Yandex SDK version actually published there; never select a newer version mentioned only in the documentation. Do not hardcode a current version into this skill.

Checklist:

- read target version catalog/Gradle dependency;
- query Maven Central for the Yandex artifact and record the latest published version before editing dependencies;
- if the target project pins another version, reconcile the pin explicitly instead of silently copying either the project or documentation version;
- verify current Android minimum/compile requirements;
- align Compose Multiplatform artifact and native iOS SDK;
- configure the platform-specific setup;
- set approved privacy choices before initialization;
- initialize before loading;
- use per-platform/per-build ad unit IDs;
- run official integration diagnostics.

Primary sources:

- https://ads.yandex.com/helpcenter/ru/dev/compose-multiplatform
- https://ads.yandex.com/helpcenter/ru/dev/compose-multiplatform/quick-start
- https://ads.yandex.com/helpcenter/en/dev/compose-multiplatform/quick-start
- https://github.com/yandexmobile/yandex-ads-multiplatform
