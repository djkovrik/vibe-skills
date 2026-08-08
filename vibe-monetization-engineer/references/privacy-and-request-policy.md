# Privacy and request policy

- Obtain product/legal decisions for age restriction, advertising ID, ATT, personalization, consent copy, protected-region policy, and every privacy behavior not fixed by the approved Yandex-only contract.
- Use the custom privacy-region endpoint in [privacy-region-endpoint.md](privacy-region-endpoint.md) to decide applicability from the network IP. Do not infer it from locale, SIM, time zone, device location, a bundled country list, or a stored country.
- Do not show a global allow/deny popup. Ask only when a fresh endpoint response has `consentRequired=true`; keep the screen app-owned and include accept, decline, and privacy-policy actions.
- Persist only the minimal endpoint response, the app-owned choice, and its matching `policyVersion`. Clamp freshness to 72 hours and never store the IP, country, GeoIP data, advertising ID, or request identity.
- Do not initialize Yandex Mobile Ads SDK or load/request ads after decline or while applicability/choice is missing, invalid, expired, or unresolved. Endpoint and transport failures fail closed for ads without blocking the product.
- Before every allowed initialization, pass the current state through `YandexAds.setUserConsent(...)`. Disable or defer Yandex automatic initialization when it could precede this gate.
- Do not represent the endpoint as an IAB TCF CMP. Use this flow only for Yandex Ads; any partner requiring certified CMP/TCF behavior needs a new privacy inventory and approved integration.
- Default an ad request to the required ad unit ID only.
- Never send health, account, reminder, workout, sync, achievement, or other product data without explicit approved purpose.
- Remove/avoid platform identifiers when policy requires.
- Keep logs/analytics free of PII and tokens.
- Make ad absence/failure non-blocking.
- Use test IDs in debug/test and guard release against them.

Primary source:

- https://ads.yandex.com/helpcenter/en/dev/compose-multiplatform/quick-start
- https://ads.yandex.com/helpcenter/en/dev/android/gdpr

The custom privacy-region flow is a product-specific adaptation, not automatic legal guidance.
