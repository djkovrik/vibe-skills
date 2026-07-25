# iOS CocoaPods and Xcode preflight

Treat these as one contract:

- KMP Gradle artifact version;
- Podfile native SDK version and platform minimum;
- Podfile.lock and Pods manifest;
- static/dynamic linkage compatibility across all native SDKs;
- generated KMP framework and Xcode target linkage;
- Xcode/toolchain architecture support;
- Info.plist/SKAdNetwork and target membership;
- workspace build and Release Archive.

The current official Yandex guidance and a combined target graph may impose different `use_frameworks` constraints. Re-read current docs and resolve the complete target graph; never copy Blinkly static linkage blindly.

Primary sources:

- https://ads.yandex.com/helpcenter/en/dev/compose-multiplatform/quick-start
- https://github.com/yandexmobile/yandex-ads-multiplatform

Blinkly adaptation: its macOS guide documents a Firebase/Google/Yandex combined static graph and an Intel-simulator toolchain issue. Locate it through the shared source registry and revalidate every requirement.

