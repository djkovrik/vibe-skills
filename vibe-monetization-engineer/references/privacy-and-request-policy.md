# Privacy and request policy

- Obtain product/legal decisions for age restriction, advertising ID, ATT, personalization, and any privacy behavior not determined by the applicable CMP configuration.
- Consent applicability must be geography-aware. At every app launch, let the CMP use the network region to refresh whether the relevant privacy regime applies and load/update its persisted consent state. Do not infer applicability from locale, SIM, a hardcoded country list, or a locally cached region.
- Do not show a global allow/deny popup to all users. Ask only when the CMP reports that a consent form or privacy-options entry point is required for that user and region.
- In GDPR-applicable regions, do not initialize Yandex Mobile Ads SDK or load/request ads until the CMP reports that requests are permitted. If applicability is unresolved and there is no valid persisted permission state, keep ads disabled until resolution.
- Prefer an IAB TCF-compatible CMP. Yandex Mobile Ads automatically reads the CMP's standard `IABTCF_*` values from Android `SharedPreferences` and iOS `UserDefaults`; do not maintain a second app-owned consent truth.
- If a CMP is needed and no other approved CMP is selected, integrate Google UMP SDK as a standalone consent collector. Add the UMP dependency/pod and required privacy-message/application configuration, but do not add or initialize Google Mobile Ads/AdMob SDK merely to use UMP.
- Apply the resolved choices before SDK initialization/ad loading. Disable or defer Yandex automatic initialization when it could precede the CMP gate.
- Default an ad request to the required ad unit ID only.
- Never send health, account, reminder, workout, sync, achievement, or other product data without explicit approved purpose.
- Remove/avoid platform identifiers when policy requires.
- Keep logs/analytics free of PII and tokens.
- Make ad absence/failure non-blocking.
- Use test IDs in debug/test and guard release against them.

Primary source:

- https://ads.yandex.com/helpcenter/en/dev/compose-multiplatform/quick-start
- https://ads.yandex.com/helpcenter/en/dev/android/tcf-2-0
- https://ads.yandex.com/helpcenter/en/dev/ios/tcf-2-0
- https://developers.google.com/admob/android/privacy
- https://developers.google.com/admob/ios/privacy

Blinkly's privacy-first request is a labeled adaptation, not automatic legal guidance.
