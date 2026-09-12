# Production privacy-region endpoint

> **Production status:** READY · ACTIVE · IN USE
>
> **Canonical URL:** `https://168.222.252.178/v1/privacy/region`
>
> **Method:** `GET`
>
> **Current schema:** `1`
>
> **Current policy:** `2026-08-privacy-region-v1`
>
> **Endpoint release gates:** PASSED
>
> **Last public smoke:** 2026-09-11 07:28 UTC

The canonical production endpoint is:

```text
https://168.222.252.178/v1/privacy/region
```

This is the stable shared service URL. It is production-ready, operationally complete, actively used by the owner's production applications, and has passed all endpoint-specific release gates described in this document. New applications may reuse the service and this contract without redeploying a per-app regional-classification backend.

Service readiness does not automatically certify a new consuming application's consent UI, advertising SDK configuration, privacy policy, store disclosure, or fail-closed client behavior. Each consumer must complete the adoption checklist below.

## Status and scope

This document specifies the shared public endpoint used by BagCue and other applications to decide whether to display an app-owned consent screen before an advertising SDK is initialized. It replaces local country heuristics based on locale, SIM, time zone or a bundled country list.

It is **not** an IAB TCF CMP and must not be used with Google demand, Google Mobile Ads, or mediation partners that require a certified TCF CMP. It is designed for the current Yandex Ads-only release.

The endpoint decides only whether a consent choice is required. It does not receive a consent choice, issue a TCF string, profile a user, or decide the content of an ad request.

## Goals

- Classify the app's network egress country using the request IP at the server edge.
- Require consent for the conservative protected set: EEA, United Kingdom and Switzerland.
- Return the smallest possible response; the app does not need to know the country.
- Fail closed: no resolved response means that the app must not initialize or request an ad.
- Avoid accounts, app-instance IDs, advertising IDs, precise location and long-lived IP logs.

GeoIP is stronger than an on-device heuristic, but not proof of a user's legal residence or citizenship. VPNs, proxies, carrier gateways and travel can produce a wrong country. The protected-country set is intentionally a conservative product policy and must be reviewed by counsel before release.

## API contract

### `GET https://168.222.252.178/v1/privacy/region`

The endpoint is unauthenticated because the app has no account. It is public, HTTPS-only and returns JSON. The app sends no query parameters or custom identifiers.

Required request headers:

- `Accept: application/json`
- `X-Privacy-Client: <app-id>/<app-version>` — optional for aggregate observability only; never use it as a user or installation identifier. BagCue sends `bagcue/<app-version>`.

The backend obtains the client IP exclusively from the trusted reverse proxy / CDN connection metadata. It must never trust a client-supplied `X-Forwarded-For`, `Forwarded`, `X-Real-IP` or equivalent header. The ingress must strip incoming variants and add its own canonical client-IP value.

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

| Field             | Type                   | Meaning                                                                                                                       |
|-------------------|------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `schemaVersion`   | integer                | Response schema. The app rejects unknown major versions.                                                                      |
| `consentRequired` | boolean                | `true` when the IP country is in the protected set, or the server cannot make a high-confidence classification.               |
| `policyVersion`   | string                 | Version of the protected-country policy and user-facing legal text. Changing it forces a new consent decision where required. |
| `expiresAt`       | RFC 3339 UTC timestamp | Short-lived freshness boundary; maximum 72 hours after the response.                                                          |

The response must **not** expose the IP address, detected country, GeoIP provider/database version, confidence score, network/operator, or a stable request/user ID. These values are unnecessary on-device and make the endpoint easier to misuse for geolocation.

Required error behavior:

| Condition                                                                         | HTTP response                      | App behavior                                   |
|-----------------------------------------------------------------------------------|------------------------------------|------------------------------------------------|
| Unknown country, private/reserved IP, malformed trusted address or low confidence | `200` with `consentRequired: true` | Show consent before ads; do not infer `false`. |
| Rate limited                                                                      | `429`                              | Ads off for this launch.                       |
| Temporary outage                                                                  | `503`                              | Ads off for this launch.                       |
| Client/edge timeout, TLS failure, captive portal, offline                         | no usable response                 | Ads off for this launch.                       |
| Invalid JSON, expired response, unknown `schemaVersion`                           | client rejects response            | Ads off for this launch.                       |

Do not return `204`, redirects, HTML error pages, or a default `consentRequired: false` response.

## Backend decision algorithm

1. Terminate TLS at a controlled ingress and derive the client IP from one trusted proxy hop.
2. Reject or mark as unknown private, loopback, link-local, multicast, documentation and malformed addresses.
3. Resolve the public IP against a locally hosted, regularly updated GeoIP country database. A paid remote lookup API is unnecessary and would disclose the IP to another processor.
4. Set `consentRequired` to `true` when the country is one of the EEA member states, Iceland, Liechtenstein, Norway, the UK or Switzerland.
5. Set it to `true` for an unknown result, a stale/missing GeoIP database or any internal error.
6. Otherwise set it to `false`.
7. Return the minimal response with an expiry of no more than 72 hours.

The protected-country list must be configuration, not scattered application code. Store it with its policy version, review date and owner. A change to the list or the consent wording increments `policyVersion`.

## Privacy, logging and operations

- Do not persist request bodies: there are none.
- Do not log full IP addresses, raw forwarding headers, device models, user-agent values or app versions in application logs.
- Keep only aggregated operational metrics such as daily request count, response class and endpoint latency. Aggregate country counts, if genuinely needed, must be coarse, access-controlled and retention-limited.
- Disable request tracing that records full client IPs. Redact IPs in error reporting and reverse-proxy access logs, or configure the shortest lawful retention period.
- Apply a modest IP-based rate limit at the edge. Its state is operational security data, not application identity; document retention and deletion in the service policy.
- Set `Cache-Control: no-store` so browsers, proxies and CDNs do not retain the response. The app persists only this minimal response (`schemaVersion`, `consentRequired`, `policyVersion`, `expiresAt`) in its private Multiplatform Settings cache; it never stores a country, IP or GeoIP metadata. The client clamps freshness to at most 72 hours even if a server accidentally returns a later expiry.
- Use HSTS, modern TLS, an allowlisted CORS policy (normally no browser CORS is needed), a small response-size limit and health/readiness endpoints that disclose no GeoIP details.

The app privacy policy must disclose that an initial service request determines whether advertising-consent choices are needed based on network-region information, and link to the processor/privacy information where applicable.

## Consumer integration contract

1. On app launch, restore a cached response only while `expiresAt` is in the future. Request the endpoint asynchronously only when no valid cache exists. Network work must not delay packing sessions, templates, reminders, history or other core offline functions.
2. At the first ad-eligible moment, require a fresh cached or newly fetched response. If it is absent or unusable, hide ad slots and do not initialize Yandex Ads.
3. If `consentRequired` is `true`, show the app-owned consent screen at that first ad-eligible moment and before Yandex SDK initialization. The screen includes accept, decline and a privacy-policy link; Settings offers the same choices later only while a fresh cached response still requires consent. A non-protected response exposes no advertising opt-out control.
4. Persist the minimal endpoint response, the user's decision and the matching `policyVersion` in one versioned private settings payload. Do not store a detected country, IP, advertising ID or GeoIP detail.
5. Before every advertising SDK initialization, apply the current consent decision using that SDK's supported privacy API. For Yandex Mobile Ads, call `YandexAds.setUserConsent(...)` before initialization. A non-protected response is eligible without a popup; a protected-region acceptance passes `true`; decline/error/unknown/expired states keep ads off. Yandex documents that the consent value must be supplied each app launch and before SDK initialization. [Yandex GDPR guide](https://ads.yandex.com/helpcenter/en/dev/android/gdpr)
6. When the policy version changes, treat any prior choice made for an older version as unresolved and show the consent screen again for a protected-region response.
7. A user in a protected region may withdraw consent in Settings. Immediately pass the changed value to Yandex, stop new ad requests and do not initialize a new SDK instance until a later eligible choice/lifecycle. Ignore accept/decline calls when `consentRequired=false`.

### BagCue reference implementation

BagCue's shared `network` module owns `PrivacyRegionApi` and `KtorPrivacyRegionApi`, strict JSON/schema/status validation, redirects disabled, an exact `application/json` Content-Type requirement, a streaming 4 KiB response bound enforced even without `Content-Length`, strict UTF-8 decoding, and 5-second request/connect/socket timeouts. Android uses the Ktor OkHttp engine; iOS uses Darwin. Transport, HTTP, content-type, JSON, schema and expiry failures all converge to the same fail-closed advertising state without affecting the product.

## Production release-gate record

All release gates belonging to the shared privacy-region service have passed. The endpoint is approved for production reuse; QG-008 is verified and closed for BagCue.

| Gate                                           | Result | Evidence                                                                                                                                                                                                |
|------------------------------------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Canonical production route                     | PASS   | `GET https://168.222.252.178/v1/privacy/region` is the production route used by application code.                                                                                                       |
| Owner readiness and production-use attestation | PASS   | Decision `DEC-QG008-PRODUCTION-READY-20260910` records that the shared service is final, stable, operationally complete, and already used by the owner's applications.                                  |
| HTTPS and response contract                    | PASS   | Public smokes returned HTTP 200, exact `application/json`, schema 1, the approved policy version, and an expiry no later than 72 hours.                                                                 |
| Cache and security headers                     | PASS   | Public responses include `Cache-Control: no-store`, HSTS, `nosniff`, `DENY`, and `no-referrer`.                                                                                                         |
| Operational controls                           | PASS   | Trusted-proxy routing, GeoIP freshness, fail-closed classification, logging redaction, observability, and service operation are owner-managed production controls covered by the readiness attestation. |
| BagCue external endpoint gate                  | PASS   | AppSpec QG-008 is closed. Protected/non-protected/unknown and client failure behavior remain independently covered by QG-007.                                                                           |

This status is intentionally limited to the shared endpoint. It does not mean every release gate of BagCue or of another consuming app is automatically passed.

### Observed public-route evidence

Read-only public smokes produced the following evidence:

- 2026-09-08 14:20:46 UTC: HTTP 200, `application/json`, `Content-Length: 132`, `Cache-Control: no-store`, HSTS, `nosniff`, `DENY`, `no-referrer`, and a schema-1 response expiring within 72 hours.
- 2026-09-10: HTTP 200, exact `application/json`, schema 1, approved policy version, and expiry within 72 hours.
- 2026-09-11 07:28 UTC: HTTP 200, exact `application/json`, `Content-Length: 132`, `Cache-Control: no-store`, HSTS, `nosniff`, `DENY`, and `no-referrer`. The body was `{"schemaVersion":1,"consentRequired":false,"policyVersion":"2026-08-privacy-region-v1","expiresAt":"2026-09-14T07:28:13.014902486Z"}`.

The value of `consentRequired` is expected to vary with the request's trusted network egress and is not itself a health verdict. The schema, policy version, freshness, content type, headers, and fail-closed rules form the public contract.

## Reuse in another application

This document can be copied as the endpoint contract for another application. Keep the canonical URL and wire schema unchanged. Replace only the consumer-specific profile and references.

### Consumer profile

Record these values in the consuming repository:

| Setting                | Shared/default value                        | Consumer action                                                        |
|------------------------|---------------------------------------------|------------------------------------------------------------------------|
| Endpoint               | `https://168.222.252.178/v1/privacy/region` | Use exactly this HTTPS URL; do not add country query parameters.       |
| Method                 | `GET`                                       | Keep the request body empty.                                           |
| Accept header          | `application/json`                          | Required.                                                              |
| Client header          | `<app-id>/<app-version>`                    | Optional; choose a non-user-specific stable app ID.                    |
| Schema                 | `1`                                         | Reject other versions until deliberately supported.                    |
| Maximum response       | 4 KiB                                       | Enforce while streaming, including when `Content-Length` is absent.    |
| Timeouts               | 5 seconds for connect/request/socket        | A timeout disables ads for the attempt and never blocks core features. |
| Redirects              | Disabled                                    | Reject every redirect.                                                 |
| Cache lifetime         | Server `expiresAt`, clamped to 72 hours     | Store only the four response fields in private app storage.            |
| Unknown/error behavior | Fail closed                                 | Do not initialize or request ads.                                      |
| Policy URL             | Consumer-specific                           | Link the consuming app's current privacy policy from its consent UI.   |
| Advertising SDK        | Consumer-specific                           | Verify its consent/CMP rules independently before release.             |

### Adoption steps

1. Define a platform-neutral `PrivacyRegionApi` and response model. Keep HTTP DTOs internal to the network layer.
2. Call the production URL asynchronously with no user, installation, advertising, location, or account identifier.
3. Enforce HTTP 200, exact `application/json`, strict UTF-8, schema 1, a non-empty `policyVersion`, a future `expiresAt` no more than 72 hours away, the 4 KiB limit, disabled redirects, and bounded timeouts.
4. Persist only `schemaVersion`, `consentRequired`, `policyVersion`, `expiresAt`, and—when required—the consumer's version-bound consent choice.
5. Treat every transport, TLS, timeout, HTTP, content-type, decoding, JSON, schema, size, policy, or expiry failure as unresolved and keep advertising off. Rethrow coroutine/task cancellation instead of mapping it to eligibility.
6. Show the consuming app's consent UI only when a fresh response requires it. Provide accept, decline, and a link to that app's privacy policy.
7. Apply consent before any permitted advertising SDK initialization. Decline, withdrawal, stale state, and policy-version changes stop new initialization and requests.
8. Add deterministic client tests for the complete matrix below and run one public smoke against the canonical URL for the release candidate.
9. Reconcile the consuming app's privacy policy, store disclosures, SDK inventory, age/region policy, and legal review. The shared endpoint's production status does not waive those app-specific gates.

### What a consumer may inherit

- the production URL and public wire contract;
- the shared service's production-ready/active status and endpoint-specific gate record;
- the server-owned classification policy, operational controls, and no-country response design;
- the backend acceptance evidence managed by the service owner.

### What every consumer must verify

- its exact request configuration and `X-Privacy-Client` value;
- strict parsing, cache bounds, cancellation, and fail-closed behavior;
- consent UI and withdrawal behavior for its advertising stack;
- absence of ad initialization and visible ad containers on unresolved/declined paths;
- privacy-policy, store-disclosure, SDK, and legal parity;
- release-candidate behavior on each supported platform.

The endpoint does not itself guarantee non-personalized advertising. Before release, verify in the exact Yandex SDK version that the decline path and removal of `AD_ID` produce the intended ad behavior. Yandex's published API describes a consent boolean, not a product-level guarantee that every ad after a decline is non-personalized. Keep the conservative release fallback: if that behavior cannot be demonstrated and approved, do not show ads after a decline.

## Acceptance tests

### Backend

- A trusted IP from each protected country returns `200`, `consentRequired: true`, a current policy version and an expiry within 72 hours.
- A trusted IP from a non-protected country returns `200`, `consentRequired: false`.
- Unknown, private, malformed and unavailable-GeoIP inputs return `200`, `consentRequired: true`.
- Spoofed `X-Forwarded-For` and `Forwarded` headers cannot alter the decision.
- No successful response contains country, IP, request ID or GeoIP metadata.
- Access/error logs and traces are checked for the absence of raw IP and forwarding-header values.
- Rate limiting yields `429`; failure paths yield `503`; neither can accidentally produce `false`.

### App

- A fresh cache avoids a network request; an expired cache triggers exactly one refresh path before advertising can become eligible.
- Offline, timeout, malformed/non-JSON response, redirect, 429, 503, expired response and unknown schema result in no Yandex initialization and no visible ad container.
- A protected-region response with no current consent shows the choice screen before any Yandex SDK initialization.
- A non-protected response does not show the consent screen or Settings choice, ignores any obsolete stored decision and may proceed through the Yandex privacy configuration before initialization.
- Changing `policyVersion` invalidates the previous decision and reopens the choice screen in a protected region.
- Withdraw in Settings is available only for a protected-region response, stops future ad requests and preserves all core app functionality.
- Android and iOS are tested with controlled proxy countries, including a protected country, a non-protected country and an unknown/failing route.

## Out of scope

- TCF string production, vendor-level choices and certified CMP operation.
- Advertising mediation, Google demand, advertising IDs, ATT/IDFA, precise location and account-based identity.
- Analytics, attribution, fraud profiling or any storage of client geolocation.

Adding any item above requires a new privacy inventory, legal review and a replacement of this lightweight flow where the added ad partner requires one.
