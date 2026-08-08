# Ad lifecycle, testing, and release

Cover:

- missing/invalid/test/production ID guards;
- load success/failure/cancel/retry;
- visibility and screen/background disposal;
- no core-flow blockage when ads fail;
- rewarded callback exactly once;
- no real requests in previews/tests;
- fresh privacy-region endpoint resolution before initialization, including controlled protected, non-protected, and unknown/failing routes;
- app-owned required-form-only behavior rather than a global consent popup;
- minimal cached response plus policy-version-bound accepted, declined, withdrawn, expired, unknown, network-error, and retry states;
- no Yandex initialization or ad request before the endpoint and consent state permit it;
- `YandexAds.setUserConsent(...)` applied before every initialization on Android and iOS;
- absence of certified-CMP/TCF assumptions in the Yandex-only lightweight flow;
- Android manifest/diagnostic logs;
- iOS Pod/workspace/device and SKAdNetwork checks;
- Release Archive, privacy report/manifest, and no test IDs;
- non-PII technical diagnostics.

Use current official integration tools and target-specific task names. Report exit codes and manual device checks separately.
