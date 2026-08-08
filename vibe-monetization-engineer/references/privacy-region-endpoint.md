# Privacy-region endpoint

## Status and scope

This document specifies a small public endpoint used by the vibe apps to decide whether to display the app-owned consent screen before Yandex Ads is initialized. It replaces local country heuristics based on locale, SIM, time zone, device location, or a bundled country list.

It is **not** an IAB TCF CMP and must not be used with Google demand, Google Mobile Ads, or mediation partners that require a certified TCF CMP. It is designed for the current Yandex Ads-only release.

The endpoint decides only whether a consent choice is required. It does not receive a consent choice, issue a TCF string, profile a user, or decide the content of an ad request.

## Goals

- Classify the app's network egress country using the request IP at the server edge.
- Require consent for the conservative protected set: EEA, United Kingdom, and Switzerland.
- Return the smallest possible response; the app does not need to know the country.
- Fail closed: no resolved response means that the app must not initialize or request an ad.
- Avoid accounts, app-instance IDs, advertising IDs, precise location, and long-lived IP logs.

GeoIP is stronger than an on-device heuristic, but not proof of a user's legal residence or citizenship. VPNs, proxies, carrier gateways, and travel can produce a wrong country. The protected-country set is intentionally a conservative product policy and must be reviewed by counsel before release.

## API contract

### `GET /v1/privacy/region`

The endpoint is unauthenticated because the app has no account. It is public, HTTPS-only, and returns JSON. The app sends no query parameters or custom identifiers.

Required request headers:

- `Accept: application/json`
- `X-Privacy-Client: <app-id>/<app-version>` — optional for observability only; never use it as an identifier.

The backend obtains the client IP exclusively from trusted reverse-proxy/CDN connection metadata. It must never trust a client-supplied `X-Forwarded-For`, `Forwarded`, `X-Real-IP`, or equivalent header. The ingress must strip incoming variants and add its own canonical client-IP value.

Successful response (`200`):

```json
{
  "schemaVersion": 1,
  "consentRequired": true,
  "policyVersion": "2026-08-privacy-region-v1",
  "expiresAt": "2026-08-08T19:55:00Z"
}
```

Field contract:

| Field | Type | Meaning |
| --- | --- | --- |
| `schemaVersion` | integer | Response schema. The app rejects unknown major versions. |
| `consentRequired` | boolean | `true` when the IP country is in the protected set, or the server cannot make a high-confidence classification. |
| `policyVersion` | string | Version of the protected-country policy and user-facing legal text. Changing it forces a new consent decision where required. |
| `expiresAt` | RFC 3339 UTC timestamp | Short-lived freshness boundary; maximum 72 hours after the response. |

The response must **not** expose the IP address, detected country, GeoIP provider/database version, confidence score, network/operator, or a stable request/user ID. These values are unnecessary on-device and make the endpoint easier to misuse for geolocation.

Required error behavior:

| Condition | HTTP response | App behavior |
| --- | --- | --- |
| Unknown country, private/reserved IP, malformed trusted address, or low confidence | `200` with `consentRequired: true` | Show consent before ads; do not infer `false`. |
| Rate limited | `429` | Ads off for this launch. |
| Temporary outage | `503` | Ads off for this launch. |
| Client/edge timeout, TLS failure, captive portal, or offline | no usable response | Ads off for this launch. |
| Invalid JSON, expired response, or unknown `schemaVersion` | client rejects response | Ads off for this launch. |

Do not return `204`, redirects, HTML error pages, or a default `consentRequired: false` response.

## Backend decision algorithm

1. Terminate TLS at a controlled ingress and derive the client IP from one trusted proxy hop.
2. Reject or mark as unknown private, loopback, link-local, multicast, documentation, and malformed addresses.
3. Resolve the public IP against a locally hosted, regularly updated GeoIP country database. A paid remote lookup API is unnecessary and would disclose the IP to another processor.
4. Set `consentRequired` to `true` when the country is one of the EEA member states, Iceland, Liechtenstein, Norway, the UK, or Switzerland.
5. Set it to `true` for an unknown result, a stale/missing GeoIP database, or any internal error.
6. Otherwise set it to `false`.
7. Return the minimal response with an expiry of no more than 72 hours.

The protected-country list must be configuration, not scattered application code. Store it with its policy version, review date, and owner. A change to the list or consent wording increments `policyVersion`.

## Privacy, logging, and operations

- Do not persist request bodies: there are none.
- Do not log full IP addresses, raw forwarding headers, device models, user-agent values, or app versions in application logs.
- Keep only aggregated operational metrics such as daily request count, response class, and endpoint latency. Aggregate country counts, if genuinely needed, must be coarse, access-controlled, and retention-limited.
- Disable request tracing that records full client IPs. Redact IPs in error reporting and reverse-proxy access logs, or configure the shortest lawful retention period.
- Apply a modest IP-based rate limit at the edge. Its state is operational security data, not application identity; document retention and deletion in the service policy.
- Set `Cache-Control: no-store` so browsers, proxies, and CDNs do not retain the response. The app persists only this minimal response (`schemaVersion`, `consentRequired`, `policyVersion`, `expiresAt`) in its private Multiplatform Settings cache; it never stores a country, IP, or GeoIP metadata. The client clamps freshness to at most 72 hours even if a server accidentally returns a later expiry.
- Use HSTS, modern TLS, an allowlisted CORS policy (normally no browser CORS is needed), a small response-size limit, and health/readiness endpoints that disclose no GeoIP details.

The app privacy policy must disclose that an initial service request determines whether advertising-consent choices are needed based on network-region information, and link to the processor/privacy information where applicable.

## App integration contract

1. On app launch, restore a cached response only while `expiresAt` is in the future. Request the endpoint asynchronously only when no valid cache exists. Network work must not delay urgent operations, timers, history, photos, or other important app flows.
2. At the first ad-eligible moment, require a fresh cached or newly fetched response. If it is absent or unusable, hide ad slots and do not initialize Yandex Ads.
3. If `consentRequired` is `true`, show the app-owned consent screen at that first ad-eligible moment and before Yandex SDK initialization. The screen includes accept, decline, and a privacy-policy link; Settings offers the same choices later only while a fresh cached response still requires consent. A non-protected response exposes no advertising opt-out control.
4. Persist the minimal endpoint response, the user's decision, and the matching `policyVersion` in one versioned private settings payload. Do not store a detected country, IP, advertising ID, or GeoIP detail.
5. Before every Yandex SDK initialization, pass the current decision using `YandexAds.setUserConsent(...)`. A non-protected response is eligible without a popup; a protected-region acceptance passes `true`; decline/error/unknown/expired states keep ads off. Yandex documents that the consent value must be supplied each app launch and before SDK initialization: https://ads.yandex.com/helpcenter/en/dev/android/gdpr.
6. When the policy version changes, treat any prior choice made for an older version as unresolved and show the consent screen again for a protected-region response.
7. A user in a protected region may withdraw consent in Settings. Immediately pass the changed value to Yandex, stop new ad requests, and do not initialize a new SDK instance until a later eligible choice/lifecycle. Ignore accept/decline calls when `consentRequired=false`.

The shared `network` module owns `PrivacyRegionApi` and `KtorPrivacyRegionApi`, strict JSON/schema/status validation, redirects disabled, a 4 KiB response bound, and 5-second request/connect/socket timeouts. Android uses the Ktor OkHttp engine; iOS uses Darwin. Transport, HTTP, content-type, JSON, schema, and expiry failures all converge to the same fail-closed advertising state without affecting the product.

The endpoint does not itself guarantee non-personalized advertising. Before release, verify in the exact Yandex SDK version that the decline path and removal of `AD_ID` produce the intended ad behavior. Yandex's published API describes a consent boolean, not a product-level guarantee that every ad after a decline is non-personalized. Keep the conservative release fallback: if that behavior cannot be demonstrated and approved, do not show ads after a decline.

## Acceptance tests

### Backend

- A trusted IP from each protected country returns `200`, `consentRequired: true`, a current policy version, and an expiry within 72 hours.
- A trusted IP from a non-protected country returns `200`, `consentRequired: false`.
- Unknown, private, malformed, and unavailable-GeoIP inputs return `200`, `consentRequired: true`.
- Spoofed `X-Forwarded-For` and `Forwarded` headers cannot alter the decision.
- No successful response contains country, IP, request ID, or GeoIP metadata.
- Access/error logs and traces are checked for the absence of raw IP and forwarding-header values.
- Rate limiting yields `429`; failure paths yield `503`; neither can accidentally produce `false`.

### App

- A fresh cache avoids a network request; an expired cache triggers exactly one refresh path before advertising can become eligible.
- Offline, timeout, malformed/non-JSON response, redirect, `429`, `503`, expired response, and unknown schema result in no Yandex initialization and no visible ad container.
- A protected-region response with no current consent shows the choice screen before any Yandex SDK initialization.
- A non-protected response does not show the consent screen or Settings choice, ignores any obsolete stored decision, and may proceed through the Yandex privacy configuration before initialization.
- Changing `policyVersion` invalidates the previous decision and reopens the choice screen in a protected region.
- Withdraw in Settings is available only for a protected-region response, stops future ad requests, and preserves all core app functionality.
- Android and iOS are tested with controlled proxy countries, including a protected country, a non-protected country, and an unknown/failing route.

## Out of scope

- TCF string production, vendor-level choices, and certified CMP operation.
- Advertising mediation, Google demand, advertising IDs, ATT/IDFA, precise location, and account-based identity.
- Analytics, attribution, fraud profiling, or any storage of client geolocation.

Adding any item above requires a new privacy inventory, legal review, and replacement of this lightweight flow where the added ad partner requires one.
