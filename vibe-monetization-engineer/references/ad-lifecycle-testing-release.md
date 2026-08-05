# Ad lifecycle, testing, and release

Cover:

- missing/invalid/test/production ID guards;
- load success/failure/cancel/retry;
- visibility and screen/background disposal;
- no core-flow blockage when ads fail;
- rewarded callback exactly once;
- no real requests in previews/tests;
- geography-aware CMP refresh before initialization, including forced GDPR-applicable and non-applicable test regions;
- required-form-only behavior rather than a global consent popup;
- persisted valid, expired, denied, unknown, network-error, and retry consent states;
- no Yandex initialization or ad request before the CMP permits requests in an applicable/unknown region;
- Android `SharedPreferences` and iOS `UserDefaults` IAB TCF values visible to Yandex;
- standalone Google UMP linkage without a Google Mobile Ads/AdMob SDK dependency when UMP is the selected CMP;
- Android manifest/diagnostic logs;
- iOS Pod/workspace/device and SKAdNetwork checks;
- Release Archive, privacy report/manifest, and no test IDs;
- non-PII technical diagnostics.

Use current official integration tools and target-specific task names. Report exit codes and manual device checks separately.
